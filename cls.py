import enum, re, datetime, pathlib, pandas as pd, numpy as np, os, asyncio, shutil
from exceptions import MaxOccurrenceError, FileNotSupported, UploadNotAllowed
from constants import DT_X, Q_X, SUPPORTED_EXT, Q_STR_X, SORT_STR_X
from sqlalchemy.exc import ProgrammingError, IntegrityError
from utils import schema_to_model, http_exception_detail
from sqlalchemy import and_, or_, func, distinct, Date
from inspect import Parameter, Signature, signature
from fastapi import Query, WebSocket, HTTPException
from psycopg2.errors import UndefinedTable
from services.aws import s3_upload
from sqlalchemy.orm import Session
from functools import wraps
from pathlib import Path
from typing import List
from passlib import pwd
from io import BytesIO
from PIL import Image
from config import *

class CRUD:
    def __init__(self, model, extra_models:list=None):
        self.model = model
        self.extra_models = extra_models

    async def create(self, payload, db:Session, **kw):
        try:
            obj = self.model(**schema_to_model(payload), **kw)
            db.add(obj)
            db.commit()
            db.refresh(obj) 
            return obj
        except Exception as e:
            # log here
            print(e)
            raise HTTPException(
                status_code=409 if isinstance(e, IntegrityError) or isinstance(e, MaxOccurrenceError) else 400 if isinstance(e, UndefinedTable) or isinstance(e, AssertionError) else 500, 
                detail=http_exception_detail(
                    msg=f"{'(psycopg2.errors.UndefinedTable) This may be due to missing tenant' if isinstance(e, UndefinedTable) else  e}", 
                    type=f"{e.__class__}"
                ),
            )

    def _base(self, fields, db:Session, use_extra_models:bool=False):
        b_fields = [getattr(self.model, field.strip()) for field in fields]  if fields!=None else [self.model] 
        base = db.query(*b_fields)
        if use_extra_models and self.extra_models:
            if all([self.model.c()==model.c() for model in self.extra_models]):
                q_fields = [db.query(*[getattr(model, field.strip()) for field in fields]) for model in self.extra_models] if fields!=None else [db.query(model) for model in self.extra_models]
                return base.union(*q_fields)
            raise ValueError('conflicts in model classes')
        return base

    async def read(self, params, db:Session, use_extra_models:bool=False):
        try:
            # fields = [getattr(self.model, field.strip()) for field in params["fields"]]  if params["fields"]!=None else [self.model]

            base = self._base(params['fields'], db, use_extra_models)   
            dt_cols = [col[0] for col in self.model.c() if col[1]==datetime.datetime]
            ex_cols = [col[0] for col in self.model.c() if col[1]==int or col[1]==bool or issubclass(col[1], enum.Enum)]
            
            dte_filters = {x:params[x] for x in params if x in dt_cols and params[x] is not None} 
            ex_filters = {x:params[x] for x in params if x  in ex_cols and  params[x] is not None}
            ext_filters = {x:params[x] for x in params if x not in ["offset", "limit", "q", "sort", "action", "fields", *dt_cols, *ex_cols] and params[x] is not None}
            filters = [ getattr(self.model, k).match(v) if v!='null' else getattr(self.model, k)==None for k,v in ext_filters.items()]
            filters.extend([getattr(self.model, k)==v if v!='null' else getattr(self.model, k)==None for k,v in ex_filters.items()])
            filters.extend([
                getattr(self.model, k) >= str_to_datetime(val.split(":", 1)[1]) if val.split(":", 1)[0]=='gte'
                else getattr(self.model, k) <= str_to_datetime(val.split(":", 1)[1]) if val.split(":", 1)[0]=='lte'
                else getattr(self.model, k) > str_to_datetime(val.split(":", 1)[1]) if val.split(":", 1)[0]=='gt'
                else getattr(self.model, k) < str_to_datetime(val.split(":", 1)[1]) if val.split(":", 1)[0]=='lt'
                else getattr(self.model, k) == str_to_datetime(val)
                for k,v in dte_filters.items() for val in v 
            ])

            base = base.filter(*filters)

            if params['sort']:
                sort = [f'{item[1:]} desc' if re.search(SORT_STR_X, item) else f'{item} asc' for item in params['sort']]
                base = base.order_by(text(*sort))
            if params['q']:
                q_or, fts = [], []
                [ q_or.append(item) if re.search(Q_STR_X, item) else fts.append(item) for item in params['q'] ]
                q_or = or_(*[getattr(self.model, q.split(':')[0]).match(q.split(':')[1]) if q.split(':')[1]!='null' else getattr(self.model, q.split(':')[0])==None for q in q_or])
                fts = or_(*[getattr(self.model, col[0]).ilike(f'%{val}%') for col in self.model.c() if col[1]==str for val in fts])
                
                base = base.filter(fts).filter(q_or)
            data = base.offset(params['offset']).limit(params['limit']).all()
            return {'bk_size':base.count(), 'pg_size':data.__len__(), 'data':data}
        except Exception as e:
            # log here
            print(e)
            raise HTTPException(
                status_code=400 if isinstance(e.__class__, UndefinedTable) else 500, 
                detail=http_exception_detail(
                    msg=f"{'(psycopg2.errors.UndefinedTable) This may be due to missing tenant' if isinstance(e.__class__, UndefinedTable) else  e}", 
                    type=f"{e.__class__}"
                ),
            )

    async def read_by_id(self, id, db:Session, fields:List[str]=None, use_extra_models:bool=False):
        try:
            # fields = [getattr(self.model, field.strip()) for field in fields]  if fields!=None else [self.model]
            return self._base(fields, db, use_extra_models).filter(self.model.id==id).first()
        except Exception as e:
            # log here
            print(e)
            raise HTTPException(
                status_code=400 if isinstance(e.orig, UndefinedTable) else 500, 
                detail=http_exception_detail(
                    msg=f"{'(psycopg2.errors.UndefinedTable) This may be due to missing tenant' if isinstance(e.orig, UndefinedTable) else  e.orig}", 
                    type=f"{e.__class__}"
                ),
            )

    async def update(self, id, payload, db:Session, images=None):
        try:
            rows = db.execute(self.model.__table__.update().returning(self.model).where(self.model.__table__.c.id==id).values(**schema_to_model(payload,exclude_unset=True)))
            db.commit()
            return rows.first()
        except Exception as e:
            # log here
            raise HTTPException(
                status_code=409 if isinstance(e, IntegrityError) or isinstance(e, MaxOccurrenceError) else 400 if isinstance(e.orig, UndefinedTable) or isinstance(e, AssertionError) else 500, 
                detail=http_exception_detail(
                    msg=f"{'(psycopg2.errors.UndefinedTable) This may be due to missing tenant' if isinstance(e.orig, UndefinedTable) else  e.orig}", 
                    type=f"{e.__class__}"
                ),
            )
      
    async def delete(self, id, db:Session):
        try:
            rows = db.query(self.model).filter(self.model.id==id).delete(synchronize_session=False)
            db.commit()
            return "success", {"info":f"{rows} row(s) deleted"}
        except Exception as e:
            # log here
            raise HTTPException(
                status_code=400 if isinstance(e.orig, UndefinedTable) else 500, 
                detail=http_exception_detail(
                    msg=f"{'(psycopg2.errors.UndefinedTable) This may be due to missing tenant' if isinstance(e.orig, UndefinedTable) else  e.orig}", 
                    type=f"{e.__class__}"
                ),
            )

    async def bk_create(self, payload, db:Session):
        try:
            rows = db.execute(self.model.__table__.insert().returning(self.model).values([payload.dict() for payload in payload]))
            db.commit()
            return rows.fetchall()
        except Exception as e:
            # log here
            raise HTTPException(
                status_code=409 if isinstance(e, IntegrityError) or isinstance(e, MaxOccurrenceError) else 400 if isinstance(e.orig, UndefinedTable) or isinstance(e, AssertionError) else 500, 
                detail=http_exception_detail(
                    msg=f"{'(psycopg2.errors.UndefinedTable) This may be due to missing tenant' if isinstance(e.orig, UndefinedTable) else  e.orig}", 
                    type=f"{e.__class__}"
                ),
            )

    async def bk_update(self, payload, db:Session, **kwargs):
        try:
            rows = db.query(self.model).filter_by(**kwargs).update(payload.dict(exclude_unset=True), synchronize_session="fetch")
            db.commit()
            return "success", {"info":f"{rows} row(s) updated"}
        except Exception as e:
            # log here
            raise HTTPException(
                status_code=409 if isinstance(e, IntegrityError) or isinstance(e, MaxOccurrenceError) else 400 if isinstance(e.orig, UndefinedTable) or isinstance(e, AssertionError) else 500, 
                detail=http_exception_detail(
                    msg=f"{'(psycopg2.errors.UndefinedTable) This may be due to missing tenant' if isinstance(e.orig, UndefinedTable) else  e.orig}", 
                    type=f"{e.__class__}"
                ),
            )

    async def bk_delete(self, ids:list, db:Session):
        try:
            rows = db.query(self.model).filter(self.model.id.in_(ids)).delete(synchronize_session=False)
            db.commit()
            return "success", {"info":f"{rows} row(s) deleted"}
        except Exception as e:
            # log here
            raise HTTPException(
                status_code=400 if isinstance(e.orig, UndefinedTable) else 500, 
                detail=http_exception_detail(
                    msg=f"{'(psycopg2.errors.UndefinedTable) This may be due to missing tenant' if isinstance(e.orig, UndefinedTable) else  e.orig}", 
                    type=f"{e.__class__}"
                ),
            )

    async def bk_delete_2(self, db:Session, **kwargs):
        try:
            rows = db.query(self.model).filter_by(**kwargs).delete(synchronize_session=False)
            db.commit()
            return "success", {"info":f"{rows} row(s) deleted"}
        except Exception as e:
            # log here
            raise HTTPException(
                status_code=409 if isinstance(e, IntegrityError) or isinstance(e, MaxOccurrenceError) else 400 if isinstance(e.orig, UndefinedTable) or isinstance(e, AssertionError) else 500, 
                detail=http_exception_detail(
                    msg=f"{'(psycopg2.errors.UndefinedTable) This may be due to missing tenant' if isinstance(e.orig, UndefinedTable) else  e.orig}", 
                    type=f"{e.__class__}"
                ),
            )

    async def exists(self, db, **kwargs):
        try:
            return db.query(self.model).filter_by(**kwargs).first() is not None
        except Exception as e:
            # log here
            raise HTTPException(
                status_code=400 if isinstance(e.orig, UndefinedTable) else 500, 
                detail=http_exception_detail(
                    msg=f"{'(psycopg2.errors.UndefinedTable) This may be due to missing tenant' if isinstance(e.orig, UndefinedTable) else  e.orig}", 
                    type=f"{e.__class__}"
                ),
            )

class Analytics:
    def __init__(self, model):
        self.model = model

    async def sum(self, fields:list, db:Session, group_by=None, order_by=None, **kw):
        sums = [
            func.sum(
                getattr(self.model, field[0])
            ).label(
                field[1]
            ) for field in fields
        ]
        base = db.query(*sums).filter(**kw)
        if group_by:
            attr = getattr(self.model, group_by)
            base = db.query(*sums, attr).filter(**kw).group_by(attr)
        return base.subquery() if subq else base.all()

    async def count(self, fields:list, db:Session, group_by=None, order_by=None, subq=False, **kw):
        cnts = [
            func.count(
                getattr(self.model, field[0])
            ).label(
                field[1]
            ) for field in fields
        ]
        base = db.query(*cnts).filter(**kw)
        if group_by:
            attr = getattr(self.model, group_by)
            base = db.query(*cnts, attr).filter(**kw).group_by(attr)
        return base.subquery() if subq else base.all()

    async def min(self, fields:list, db:Session, group_by=None, order_by=None, subq=False, **kw):
        mins = [
            func.min(
                getattr(self.model, field[0])
            ).label(
                field[1]
            ) for field in fields
        ]
        base = db.query(*mins).filter(**kw)
        if group_by:
            attr = getattr(self.model, group_by)
            base = db.query(*mins, attr).filter(**kw).group_by(attr)
        return base.subquery() if subq else base.all()
    
    async def max(self, fields:list, db:Session, group_by=None, order_by=None, subq=False, **kw):
        maxs = [
            func.max(
                getattr(self.model, field[0])
            ).label(
                field[1]
            ) for field in fields
        ]
        base = db.query(*maxs).filter(**kw)
        if group_by:
            attr = getattr(self.model, group_by)
            base = db.query(*maxs, attr).filter(**kw).group_by(attr)
        return base.subquery() if subq else base.all()

    async def avg(self, fields:list, db:Session, group_by=None, order_by=None, subq=False,**kw):
        avgs = [
            func.avg(
                getattr(self.model, field[0])
            ).label(
                field[1]
            ) for field in fields
        ]
        base = db.query(*avgs).filter(**kw)
        if group_by:
            attr = getattr(self.model, group_by)
            base = db.query(*avgs, attr).filter(**kw).group_by(attr)
        return base.subquery() if subq else base.all()

    async def years_available(self, field, db:Session):
        dates = db.query(getattr(self.model, field).cast(Date)).distinct().all()
        return [date[0].year for date in dates]

class ContentQueryChecker:
    def __init__(self, cols=None, actions=None):
        self._cols = cols
        self._actions = actions
    
    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        sig = signature(wrapper)
        params = list(sig._parameters.values())
        del params[-1]
        sort_str = "|".join([f"{x[0]}|-{x[0]}" for x in self._cols]) if self._cols else None
        q_str = "|".join([x[0] for x in self._cols if x[0]!='password']) if self._cols else None
        if self._cols:
            params.extend([Parameter(param[0], Parameter.KEYWORD_ONLY, annotation=param[1], default=Query(None)) for param in self._cols if param[1]!=datetime.datetime])
            params.extend([
                Parameter(param[0], Parameter.KEYWORD_ONLY, annotation=List[str], default=Query(None, regex=DT_X)) for param in self._cols if param[1]==datetime.datetime
            ])
        params.extend([
            Parameter('offset', Parameter.KEYWORD_ONLY, annotation=int, default=Query(0, gte=0)),
            Parameter('limit', Parameter.KEYWORD_ONLY, annotation=int, default=Query(100, gt=0)),
            Parameter('fields', Parameter.KEYWORD_ONLY, annotation=List[str], default=Query(None, regex=f'({q_str})$')),
            Parameter('q', Parameter.KEYWORD_ONLY, annotation=List[str], default=Query(None, regex=Q_X.format(cols=f'({q_str})') if q_str else '^[\w]+$|^[\w]+:[\w]+$')),
            Parameter('sort', Parameter.KEYWORD_ONLY, annotation=List[str], default=Query(None, regex=sort_str if sort_str else '(^-)?\w')),])  
        if self._actions:
            params.extend([Parameter('action', Parameter.KEYWORD_ONLY, annotation=str, default=Query(None))])
        wrapper.__signature__ = Signature(params)
        return wrapper

class ConnectionManager:
    def __init__(self):
        self.active_connections:List[WebSocket] = []

    async def connect(self, websocket:WebSocket, client_id:int):
        websocket._cookies['client_id']=client_id
        await websocket.accept()
        self.active_connections.append(websocket)
        # check if any pending messages then send

    def disconnect(self, websocket:WebSocket):
        self.active_connections.remove(websocket)

    def client_connection(self, client_id:int):
        return [websocket for websocket in self.active_connections if websocket._cookies.get('client_id', None) == client_id]

    async def send_personal_message(self, message:(str, dict), client_id:int):
        # if websocket not in client_connections save message
        client_connections = self.client_connection(client_id)
        for websocket in client_connections:
            if isinstance(message, str):
                return await websocket.send_text(message)
            return await websocket.send_json(message)

    async def broadcast(self, message: (str, dict)):
        # if websocket not in client_connections save message
        for websocket in self.active_connections:
            if isinstance(message, str):
                return await websocket.send_text(message)
            return await websocket.send_json(message)

    async def on_verify(self, client_id:int):
        pass

class FileReader:
    def __init__(self, file, header, supported_extensions:list=[]):
        self.file=file
        self.header = header
        self._supported_ext = SUPPORTED_EXT
        self._supported_ext.extend(supported_extensions)
        self._supported_ext = list(set(self._supported_ext))

    def _ext(self):
        return pathlib.Path(self.file.filename).suffix

    def _csv(self, to_dict:bool=True, replace_nan_with=None):
        df = pd.read_csv(self.file.file, usecols=self.header)[self.header]
        return self.validate_rows(df, to_dict, replace_nan_with=replace_nan_with)
       
    def _excel(self, to_dict:bool=True, replace_nan_with=None):
        df = pd.read_excel(self.file.file, usecols=self.header)[self.header]
        return self.validate_rows(df, to_dict, replace_nan_with=replace_nan_with)
    
    def verify_ext(self):
        return self._ext() in self._supported_ext

    def validate_rows(self, df, to_dict:bool=True, replace_nan_with=None):
        if to_dict:
            return [{k:None if pd.isna(v) else v for (k,v) in row.items()} for row in df.to_dict(orient="records")] if not replace_nan_with else df.fillna(replace_nan_with).to_dict(orient="records")
        return [[None if pd.isna(item) else item for item in row] for row in np.array(df[self.header].drop_duplicates())] if not replace_nan_with else np.array(df[self.header].fillna(replace_nan_with).drop_duplicates())

    async def read(self, to_dict:bool=True, replace_nan_with=None):
        try:
            if not self.verify_ext():
                raise FileNotSupported('file extension not supported')
            if self._ext() in [".csv",".CSV"]:
                rows = self._csv(to_dict=to_dict, replace_nan_with=replace_nan_with)
            else:
                rows = self._excel(to_dict=to_dict, replace_nan_with=replace_nan_with)
            return rows
        finally:
            await self.file.close()

class Upload:
    def __init__(self, file, upload_to, size=None):
        self.file = file
        self.upload_to = upload_to
        self.size = size

    def _ext(self):
        return pathlib.Path(self.file.filename).suffix

    def file_allowed(self, ext=None):
        ext=ext if ext else self._ext()
        if ext in UPLOAD_EXTENSIONS["IMAGE"]:
            return True, "images/"
        elif ext in UPLOAD_EXTENSIONS["AUDIO"]:
            return True, "audio/"
        elif ext in UPLOAD_EXTENSIONS["VIDEO"]:
            return True, "videos/"
        elif ext in UPLOAD_EXTENSIONS["DOCUMENT"]:
            return True, "documents/"
        raise UploadNotAllowed('Unsupported file extension')
    
    def _path(self):
        _, url = self.file_allowed()
        root = DOCUMENT_ROOT if url=='documents/' else MEDIA_ROOT
        path = os.path.join(root, f'{self.upload_to}')
                
        if not os.path.isdir(path):
            os.makedirs(path)
        return path
        
    def _url(self):
        name, cnt = os.path.splitext(self.file.filename)[0], 1
        url = os.path.join(self._path(), f'{self.file.filename}')
        while Path(url).exists():
            filename = f"{name}_{cnt}{self._ext()}"
            url = os.path.join(self._path(), f'{filename}')
            cnt+=1
        return url
    
    def path(self):
        self._path()

    def _image(self):
        url = self._url()
        try:
            with Image.open(BytesIO(self.file.file.read())) as im:
                im.thumbnail(self.size if self.size else im.size)
                im.save(url)
        finally:
            self.file.file.close()
            return url

    def _save_file(self):
        url = self._url()
        try:
            with open(url, "wb") as buffer:
                shutil.copyfileobj(self.file.file, buffer)
        finally:
            self.file.file.close()
            return url

    def save(self, *args, **kwargs):
        if settings.USE_S3:
            url = '/'+os.path.relpath(self._url(), BASE_DIR) 
            s3_upload(self.file, object_name=url) # push to celery to upload
        else:
            if self.file:
                url = self._image() if self.file.content_type.split("/")[0]=="image" else self._save_file()
                url = '/'+os.path.relpath(url, BASE_DIR) 
            else:
                url = None
        return f"S3:{url}" if settings.USE_S3 else f"LD:{url}" if url else None