from sqlalchemy.exc import ProgrammingError, IntegrityError
from utils import schema_to_model, http_exception_detail
from inspect import Parameter, Signature, signature
import enum, re, datetime, pathlib, pandas as pd, numpy as np
from exceptions import MaxOccurrenceError, FileNotSupported
from fastapi import Query, WebSocket, HTTPException
from constants import DT_X, Q_X, SUPPORTED_EXT
from psycopg2.errors import UndefinedTable
from sqlalchemy.orm import Session
from functools import wraps
from typing import List

class CRUD:
    def __init__(self, model):
        self.model = model

    async def create(self, payload, db:Session, images=None):
        try:
            obj = self.model(**schema_to_model(payload))
            if images:
                pass
            db.add(obj)
            db.commit()
            db.refresh(obj) 
            return obj
        except Exception as e:
            # log here
            raise HTTPException(
                status_code=409 if isinstance(e, IntegrityError) or isinstance(e, MaxOccurrenceError) else 400 if isinstance(e.orig, UndefinedTable) or isinstance(e, AssertionError) else 500, 
                detail=http_exception_detail(
                    msg=f"{'(psycopg2.errors.UndefinedTable) This may be due to missing tenant' if isinstance(e.orig, UndefinedTable) else  e.orig}", 
                    type=f"{e.__class__}"
                ),
            )

    async def read(self, params, db:Session):
        try:
            fields = [getattr(self.model, field.strip()) for field in params["fields"]]  if params["fields"]!=None else [self.model]

            base = db.query(*fields)
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
            raise HTTPException(
                status_code=400 if isinstance(e.orig, UndefinedTable) else 500, 
                detail=http_exception_detail(
                    msg=f"{'(psycopg2.errors.UndefinedTable) This may be due to missing tenant' if isinstance(e.orig, UndefinedTable) else  e.orig}", 
                    type=f"{e.__class__}"
                ),
            )

    async def read_by_id(self, id, db:Session, fields:List[str]=None):
        try:
            fields = [getattr(self.model, field.strip()) for field in fields]  if fields!=None else [self.model]
            return db.query(*fields).filter(self.model.id==id).first()
        except Exception as e:
            # log here
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
        q_str = "|".join([x[0] for x in self._cols]) if self._cols else None
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
    def __init__(self, supported_extensions:list=[]):
        self._supported_ext = SUPPORTED_EXT
        self._supported_ext.extend(supported_extensions)
        self._supported_ext = list(set(self._supported_ext))

    def _ext(self, file):
        return pathlib.Path(file.filename).suffix

    def _csv(self, file, header, to_dict:bool=True):
        df = pd.read_csv(file.file, usecols=header)[header]
        return self.validate_rows(df, header, to_dict)
       
    def _excel(self, file, header, to_dict:bool=True):
        
        df = pd.read_excel(file.file, usecols=header)[header]
        return self.validate_rows(df, header, to_dict)
    
    def verify_ext(self, file):
        return self._ext(file) in self._supported_ext

    def validate_rows(self, df, header, to_dict:bool=True):
        if to_dict:
            return [*df.to_dict(orient="index").values()]
        return np.array(df[header].replace(np.nan, None).drop_duplicates())

    async def read(self, file, header, to_dict:bool=True):
        try:
            if not self.verify_ext(file):
                raise FileNotSupported('file extension not supported')
            if self._ext(file) in [".csv",".CSV"]:
                rows = self._csv(file, header, to_dict)
            else:
                rows = self._excel(file, header, to_dict)
            return rows
        finally:
            await file.close()

# from starlette.endpoints import WebSocketEndpoint

# class App(WebSocketEndpoint):
#     encoding = 'bytes'

#     async def on_connect(self, websocket):
#         await websocket.accept()

#     async def on_receive(self, websocket, data):
#         await websocket.send_bytes(b"Message: " + data)

#     async def on_disconnect(self, websocket, close_code):
#         pass

# from sqlalchemy.schema import Column
# from sqlalchemy import Integer, String

# class FileField(Column):
#     def __init__(self, *args, upload_to, **kwargs):
#         super(FileField, self).__init__(type_=String, default='some', *args, **kwargs)
#         # self.__call__()
#         # self._value_map = None
#         # self.value_map = None
#         # self._excel_column_name = None
#         # self.excel_column_name = 'some'
        
#     def __call__(self):
#         print('ds')
#     # @property
#     # def excel_column_name(self):
#     #     if self._excel_column_name is None:
#     #         return self.name
#     #     else:
#     #         return self._excel_column_name

#     # @excel_column_name.setter
#     # def excel_column_name(self, n):
#     #     self._excel_column_name = n

#     @property
#     def value_map(self):
#         return (lambda x: x+'some_data') if self._value_map is None else self._value_map

#     @value_map.setter
#     def value_map(self, fn):
#         # print(fn)
#         if callable(fn) or fn is None:
#             self._value_map = fn
#         else:
#             raise ValueError('ExcelColumn.value_map must be callable.')

# class Storage(str, enum.Enum):
#     s3 = 's3'
#     fs = 'fs'

# class Upload:
#     def __init__(self, loc, extension_allowed, name, ext):
#         self.loc = loc
#         self.ext = ext
#         self.name = name
#         # content_type, mimetype
#         # self.storage = storage -> storage:Storage,
#         self.extension_allowed = extension_allowed
        
#     def path(self, filename):
#         '''This returns the absolute path of a file uploaded to this set. It doesn’t actually check whether said file exists.
#         Parameters:	
#         filename – The filename to return the path for.
#         '''

#     def resolve_conflict(self,):
#         '''If a file with the selected name already exists in the target folder, this method is called to resolve the conflict. It should return a new basename for the file.

#         The default implementation splits the name and extension and adds a suffix to the name consisting of an underscore and a number, and tries that until it finds one that doesn’t exist.

#         Parameters:	
#         target_folder – The absolute path to the target.
#         basename – The file’s original basename.'''
#         pass

#     def url(self, filename):
#         '''This function gets the URL a file uploaded to this set would be accessed at. It doesn’t check whether said file exists.
#         Parameters:	
#         filename – The filename to return the URL for.
#         '''
#         pass

#     def save(self, storage:Storage, folder=None, name=None):
#         '''This saves a werkzeug.FileStorage into this upload set. If the upload is not allowed, an UploadNotAllowed error will be raised. 
#         Otherwise, the file will be saved and its name (including the folder) will be returned.
#         Parameters:	
#         storage – The uploaded file to save.
#         folder – The subfolder within the upload set to save to.
#         name – The name to save the file as. If it ends with a dot, the file’s extension will be appended to the end.'''
#         pass

#     def file_allowed(storage, basename):
#         '''This tells whether a file is allowed. It should return True if the given werkzeug.FileStorage object can be saved with the given basename, and False if it can’t. 
#         The default implementation just checks the extension, so you can override this if you want.

#         Parameters:	
#         storage – The werkzeug.FileStorage to check.
#         basename – The basename it will be saved under.'''

#     def extension_allowed(self, ext):
#         '''This determines whether a specific extension is allowed. It is called by file_allowed, so if you override that but still want to check extensions, 
#         call back into this.

#         Parameters:	
#         ext – The extension to check, without the dot.'''
