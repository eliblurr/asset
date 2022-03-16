from exceptions import MaxOccurrenceError, FileNotSupported, UploadNotAllowed, NotFound, BadRequestError
import enum, re, datetime, pathlib, pandas as pd, numpy as np, os, asyncio, shutil
from sqlalchemy import and_, or_, func, distinct, Date, union_all, extract
from utils import schema_to_model, raise_exc, logger, parse_activity_meta
from constants import DT_X, Q_X, SUPPORTED_EXT, Q_STR_X, SORT_STR_X
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.exc import ProgrammingError, IntegrityError
from sqlalchemy.types import Date, DateTime, DATE, DATETIME
from inspect import Parameter, Signature, signature
from fastapi import Query, WebSocket, HTTPException
from pydantic import BaseModel, conint, constr
from psycopg2.errors import UndefinedTable
from sqlalchemy.exc import DBAPIError
from services.aws import s3_upload
from sqlalchemy.orm import Session
from config import UPLOAD_ROOT
from functools import wraps
from pathlib import Path
from typing import List
from passlib import pwd
from io import BytesIO
from PIL import Image
from config import *
import enum

class D(BaseModel):
    field: str = 'created'
    months: List[conint(gt=0, lt=13)]=[]
    years:List[constr(regex=r'(\d\d\d\d)$')]=[]

class CRUD:
    def __init__(self, model, extra_models:list=None):
        self.model = model
        self.extra_models = extra_models

    async def create(self, payload, db:Session, exclude_unset=False, activity:list=[], **kw):
        try:
            obj = self.model(**schema_to_model(payload, exclude_unset=exclude_unset), **kw)
            db.add(obj)
            db.commit()
            db.refresh(obj) 
        except Exception as e:
            
            # print(e)

            status_code, msg, class_name = 500, f'{e}' , f"{e.__class__.__name__}"
            if isinstance(e, DBAPIError):
                status_code = 409 if isinstance(e, IntegrityError) else 400 if isinstance(e.orig, UndefinedTable) else 500
                msg=f'(UndefinedTable) This may be due to missing tenant_key in request header' if isinstance(e.orig, UndefinedTable) else f'{e.orig}'
            else:
                status_code = 400 if isinstance(e, (BadRequestError, FileNotSupported, UploadNotAllowed, AssertionError)) else 404 if isinstance(e, NotFound) else 409 if isinstance(e, MaxOccurrenceError) else status_code
                msg = f"{e._message()}" if isinstance(e, (BadRequestError, NotFound, MaxOccurrenceError,FileNotSupported,UploadNotAllowed,)) else msg  
            logger(__name__, e, 'critical')
            raise HTTPException(status_code=status_code, detail=raise_exc(msg=msg, type=class_name))
            
        else:
            if activity:
                for activity in activity:
                    message, meta = activity['args']
                    await activity['func'](obj, message, parse_activity_meta(obj, meta))

        return obj

    def get_related_model(self, use_related_name:str):
        relation = getattr(self.model, use_related_name)
        if not isinstance(relation.prop, RelationshipProperty):
            raise AttributeError(f"{use_related_name} is not a valid relation")
        return relation, relation.prop.mapper.class_

    def _base(self, db:Session, fields=None, use_related_name:str=None, resource_id:int=None, joins:dict=None):  
        if use_related_name and resource_id:
            relation, related_model = self.get_related_model(use_related_name)
            b_fields = [getattr(related_model, field.strip()) for field in fields] if fields!=None else [related_model]  
            base = db.query(*b_fields).join(related_model, relation).filter(self.model.id==resource_id)
            model = related_model
        else:
            b_fields = [getattr(self.model, field.strip()) for field in fields]  if fields!=None else [self.model] 
            base = db.query(*b_fields)
            model = self.model
        
        if joins:
            target, filters, joins = self.model, joins.get('filters', {}), joins.get('joins', [])
            base = db.query(target).filter_by(**filters)
            for join in joins:
                base = base.join(join['target']).filter_by(**join.get('filters', {}))
            model = target    
        return model, base

    async def read(self, params, db:Session, use_related_name:str=None, resource_id:int=None, joins:dict={}):
        try:
            model_to_filter, base = self._base(db, params.get('fields', None), use_related_name=use_related_name, resource_id=resource_id, joins=joins)             
            dt_cols = [col[0] for col in model_to_filter.c() if col[1]==datetime.datetime]
            ex_cols = [col[0] for col in model_to_filter.c() if col[1]==int or col[1]==bool or issubclass(col[1], enum.Enum)]
            dte_filters = {x:params[x] for x in params if x in dt_cols and params[x] is not None} 
            ex_filters = {x:params[x] for x in params if x  in ex_cols and  params[x] is not None}
            ext_filters = {x:params[x] for x in params if x not in ["offset", "limit", "q", "sort", "action", "fields", *dt_cols, *ex_cols] and params[x] is not None}
            # filters = [ getattr(model_to_filter, k).match(v) if v!='null' else getattr(model_to_filter, k)==None for k,v in ext_filters.items()]
            filters = [ getattr(model_to_filter, k)==v if v!='null' else getattr(model_to_filter, k)==None for k,v in ext_filters.items()]
            filters.extend([getattr(model_to_filter, k)==v if v!='null' else getattr(model_to_filter, k)==None for k,v in ex_filters.items()])
            filters.extend([
                getattr(model_to_filter, k) >= str_to_datetime(val.split(":", 1)[1]) if val.split(":", 1)[0]=='gte'
                else getattr(model_to_filter, k) <= str_to_datetime(val.split(":", 1)[1]) if val.split(":", 1)[0]=='lte'
                else getattr(model_to_filter, k) > str_to_datetime(val.split(":", 1)[1]) if val.split(":", 1)[0]=='gt'
                else getattr(model_to_filter, k) < str_to_datetime(val.split(":", 1)[1]) if val.split(":", 1)[0]=='lt'
                else getattr(model_to_filter, k) == str_to_datetime(val)
                for k,v in dte_filters.items() for val in v 
            ])

            base = base.filter(*filters)

            if params['sort']:
                sort = [getattr(model_to_filter, key[1:]).desc() if re.search(SORT_STR_X, key) else getattr(model_to_filter, key).asc()for key in params['sort']]
                base = base.order_by(*sort)
            
            if params['q']:
                
                q_or, fts = [], []
                [ q_or.append(item) if re.search(Q_STR_X, item) else fts.append(item) for item in params['q'] ]

                # if db.bind.dialect.name=='sqlite':
                q_or = or_(*[getattr(model_to_filter, q.split(':')[0])==q.split(':')[1] if q.split(':')[1]!='null' else getattr(model_to_filter, q.split(':')[0])==None for q in q_or])
                # else:
                #     q_or = or_(*[getattr(model_to_filter, q.split(':')[0]).match(q.split(':')[1]) if q.split(':')[1]!='null' else getattr(model_to_filter, q.split(':')[0])==None for q in q_or])                
                
                fts = or_(*[getattr(model_to_filter, col[0]).ilike(f'%{val}%') for col in model_to_filter.c() if any((col[1]==str, issubclass(col[1], enum.Enum))) for val in fts])
                base = base.filter(fts).filter(q_or)
            data = base.offset(params['offset']).limit(params['limit']).all()
            return {'bk_size':base.count(), 'pg_size':data.__len__(), 'data':data}
        except Exception as e:

            # print(e)

            status_code, msg, class_name = 500, f'{e}' , f"{e.__class__.__name__}"
            if isinstance(e, DBAPIError):
                status_code = 409 if isinstance(e, IntegrityError) else 400 if isinstance(e.orig, UndefinedTable) else 500
                msg=f'(UndefinedTable) This may be due to missing tenant_key in request header' if isinstance(e.orig, UndefinedTable) else f'{e.orig}'
            else:
                status_code = 400 if isinstance(e, (BadRequestError, FileNotSupported, UploadNotAllowed, AssertionError)) else 404 if isinstance(e, NotFound) else 409 if isinstance(e, MaxOccurrenceError) else status_code
                msg = f"{e._message()}" if isinstance(e, (BadRequestError, NotFound, MaxOccurrenceError,FileNotSupported,UploadNotAllowed,)) else msg  
            logger(__name__, e, 'critical')
            raise HTTPException(status_code=status_code, detail=raise_exc(msg=msg, type=class_name))
            # print(e)
            # # if getattr(e, 'orig'):
            #     # status_code = 400 if isinstance(e.orig, UndefinedTable) else 500
            
            # # msg = 'tenant header required for this op' if isinstance(e.orig, UndefinedTable) else f"{e._message()}"
            # raise HTTPException(status_code=status_code, detail=raise_exc(msg=f'{e}', type= e.__class__.__name__))

    async def read_by_id(self, id, db:Session, fields:List[str]=None, use_extra_models:bool=False):
        try:
            fields = [getattr(self.model, field.strip()) for field in fields] if fields!=None else [self.model]
            obj = db.query(*fields).filter(self.model.id==id).first()
            if not obj:
                raise NotFound(f'object with id:{id} not found')
            return obj
        except Exception as e:

            # print(e)

            status_code, msg, class_name = 500, f'{e}' , f"{e.__class__.__name__}"
            if isinstance(e, DBAPIError):
                status_code = 409 if isinstance(e, IntegrityError) else 400 if isinstance(e.orig, UndefinedTable) else 500
                msg=f'(UndefinedTable) This may be due to missing tenant_key in request header' if isinstance(e.orig, UndefinedTable) else f'{e.orig}'
            else:
                status_code = 400 if isinstance(e, (BadRequestError, FileNotSupported, UploadNotAllowed, AssertionError)) else 404 if isinstance(e, NotFound) else 409 if isinstance(e, MaxOccurrenceError) else status_code
                msg = f"{e._message()}" if isinstance(e, (BadRequestError, NotFound, MaxOccurrenceError,FileNotSupported,UploadNotAllowed,)) else msg  
            logger(__name__, e, 'critical')
            raise HTTPException(status_code=status_code, detail=raise_exc(msg=msg, type=class_name))
    
    async def read_by_kwargs(self, db:Session, fields:List[str]=None, **kwargs):
        try:
            fields = [getattr(self.model, field.strip()) for field in fields] if fields!=None else [self.model]
            return db.query(*fields).filter_by(**kwargs).first()
        except Exception as e:
            raise HTTPException(status_code=500, detail=raise_exc(msg=f'{e}', type= e.__class__.__name__))

    async def update(self, id, payload, db:Session, images=None):
        try:
            rows = db.execute(self.model.__table__.update().returning(self.model).where(self.model.__table__.c.id==id).values(**schema_to_model(payload,exclude_unset=True)))
            if db.bind.dialect.name=='sqlite':
                rows = db.execute(self.model.__table__.update().where(self.model.__table__.c.id==id).values(**schema_to_model(payload,exclude_unset=True)))
            db.commit()
            return rows.first()
        except Exception as e:

            # print(e)

            status_code, msg, class_name = 500, f'{e}' , f"{e.__class__.__name__}"
            if isinstance(e, DBAPIError):
                status_code = 409 if isinstance(e, IntegrityError) else 400 if isinstance(e.orig, UndefinedTable) else 500
                msg=f'(UndefinedTable) This may be due to missing tenant_key in request header' if isinstance(e.orig, UndefinedTable) else f'{e.orig}'
            else:
                status_code = 400 if isinstance(e, (BadRequestError, FileNotSupported, UploadNotAllowed, AssertionError)) else 404 if isinstance(e, NotFound) else 409 if isinstance(e, MaxOccurrenceError) else status_code
                msg = f"{e._message()}" if isinstance(e, (BadRequestError, NotFound, MaxOccurrenceError,FileNotSupported,UploadNotAllowed,)) else msg  
            logger(__name__, e, 'critical')
            raise HTTPException(status_code=status_code, detail=raise_exc(msg=msg, type=class_name))

            # raise HTTPException(
            #     status_code=409 if isinstance(e, IntegrityError) or isinstance(e, MaxOccurrenceError) else 400 if isinstance(e, AssertionError) else 500,
            #     detail=raise_exc(msg=e._message(), type= e.__class__.__name__)
            # )
            # raise HTTPException(
            #     status_code=409 if isinstance(e, IntegrityError) or isinstance(e, MaxOccurrenceError) else 400 if isinstance(e.orig, UndefinedTable) or isinstance(e, AssertionError) else 500, 
            #     detail=raise_exc(
            #         msg=f"{'(psycopg2.errors.UndefinedTable) This may be due to missing tenant' if isinstance(e.orig, UndefinedTable) else  e.orig}", 
            #         type=f"{e.__class__}"
            #     ),
            # )
    
    async def update_2(self, id, payload, db:Session, activity:list=[], **kwargs):
        try:
            obj = db.query(self.model).filter(self.model.id==id).first()
            if not obj:
                raise NotFound(f'object with id:{id} not found')
            data = schema_to_model(payload, exclude_unset=True)
            data.update({k:v for k,v in kwargs.items() if v is not None})
            [setattr(obj, k, v) for k, v in data.items()]
            db.commit()
            db.refresh(obj)  
        # except NotFound as e:
        #     print(e)
        #     raise HTTPException(status_code=404, detail=raise_exc(msg=e._message(), type= e.__class__.__name__))
        # except IntegrityError as e:
        #     print(e)
        #     raise HTTPException(status_code=409, detail=raise_exc(msg=e._message(), type= e.__class__.__name__))
        # except MaxOccurrenceError as e:
        #     print(e)
        #     raise HTTPException(status_code=409, detail=raise_exc(msg=e._message(), type= e.__class__.__name__))
        # except AssertionError as e:
        #     print(e)
        #     raise HTTPException(status_code=400, detail=raise_exc(msg=f"{e}", type= e.__class__.__name__))
        except Exception as e:
            # print(e)
            # raise HTTPException(status_code=500, detail=raise_exc(msg=f"{e}", type= e.__class__.__name__))

            # print(e)

            status_code, msg, class_name = 500, f'{e}' , f"{e.__class__.__name__}"
            if isinstance(e, DBAPIError):
                status_code = 409 if isinstance(e, IntegrityError) else 400 if isinstance(e.orig, UndefinedTable) else 500
                msg=f'(UndefinedTable) This may be due to missing tenant_key in request header' if isinstance(e.orig, UndefinedTable) else f'{e.orig}'
            else:
                status_code = 400 if isinstance(e, (BadRequestError, FileNotSupported, UploadNotAllowed, AssertionError)) else 404 if isinstance(e, NotFound) else 409 if isinstance(e, MaxOccurrenceError) else status_code
                msg = f"{e._message()}" if isinstance(e, (BadRequestError, NotFound, MaxOccurrenceError,FileNotSupported,UploadNotAllowed,)) else msg  
            logger(__name__, e, 'critical')
            raise HTTPException(status_code=status_code, detail=raise_exc(msg=msg, type=class_name))

        else: 
            if activity:
                for activity in activity:
                    message, meta = activity['args']
                    await activity['func'](obj, message, parse_activity_meta(obj, meta))
        return obj
      
    async def delete(self, id, db:Session):
        try:
            rows = db.query(self.model).filter(self.model.id==id).delete(synchronize_session=False)
            db.commit()
            return "success", {"info":f"{rows} row(s) deleted"}
        except Exception as e:
            # log here
            # raise HTTPException(
            #     status_code=500, 
            #     detail=raise_exc(
            #         msg=f"{e}", 
            #         type=f"{e.__class__}"
            #     ),
            # )

            # print(e)

            status_code, msg, class_name = 500, f'{e}' , f"{e.__class__.__name__}"
            if isinstance(e, DBAPIError):
                status_code = 409 if isinstance(e, IntegrityError) else 400 if isinstance(e.orig, UndefinedTable) else 500
                msg=f'(UndefinedTable) This may be due to missing tenant_key in request header' if isinstance(e.orig, UndefinedTable) else f'{e.orig}'
            else:
                status_code = 400 if isinstance(e, (BadRequestError, FileNotSupported, UploadNotAllowed, AssertionError)) else 404 if isinstance(e, NotFound) else 409 if isinstance(e, MaxOccurrenceError) else status_code
                msg = f"{e._message()}" if isinstance(e, (BadRequestError, NotFound, MaxOccurrenceError,FileNotSupported,UploadNotAllowed,)) else msg  
            logger(__name__, e, 'critical')
            raise HTTPException(status_code=status_code, detail=raise_exc(msg=msg, type=class_name))

    async def delete_2(self, id, db:Session, use_field:str=None):
        try:
            # obj = await self.read_by_id(id, db)
            obj = db.query(self.model).filter(self.model.id==id).first()
            if not obj:return
            subq = getattr(self.model, use_field)==use_field if use_field else self.model.id==id
            db.delete(obj)
            db.commit()
            return
        except Exception as e:
            # raise HTTPException(status_code=500, detail=raise_exc(msg=f"{e}", type= e.__class__.__name__))

            # print(e)

            status_code, msg, class_name = 500, f'{e}' , f"{e.__class__.__name__}"
            if isinstance(e, DBAPIError):
                status_code = 409 if isinstance(e, IntegrityError) else 400 if isinstance(e.orig, UndefinedTable) else 500
                msg=f'(UndefinedTable) This may be due to missing tenant_key in request header' if isinstance(e.orig, UndefinedTable) else f'{e.orig}'
            else:
                status_code = 400 if isinstance(e, (BadRequestError, FileNotSupported, UploadNotAllowed, AssertionError)) else 404 if isinstance(e, NotFound) else 409 if isinstance(e, MaxOccurrenceError) else status_code
                msg = f"{e._message()}" if isinstance(e, (BadRequestError, NotFound, MaxOccurrenceError,FileNotSupported,UploadNotAllowed,)) else msg  
            logger(__name__, e, 'critical')
            raise HTTPException(status_code=status_code, detail=raise_exc(msg=msg, type=class_name))

    async def bk_create(self, payload, db:Session):
        try:
            if db.bind.dialect.name=='sqlite':
                db.add_all([self.model(**payload.dict()) for payload in payload])
                db.commit()
            else:
                rows = db.execute(self.model.__table__.insert().returning(self.model).values([payload.dict() for payload in payload]))
                db.commit()
                return rows.fetchall()
        except Exception as e:
            # code = 400 if isinstance(e, AssertionError) else 409 if any((
            #     isinstance(e, IntegrityError),
            #     isinstance(e, MaxOccurrenceError)
            # )) else 500
            # raise HTTPException(status_code=code, detail=http_exception_detail(msg=e._message(), type= e.__class__.__name__))

            # print(e)

            status_code, msg, class_name = 500, f'{e}' , f"{e.__class__.__name__}"
            if isinstance(e, DBAPIError):
                status_code = 409 if isinstance(e, IntegrityError) else 400 if isinstance(e.orig, UndefinedTable) else 500
                msg=f'(UndefinedTable) This may be due to missing tenant_key in request header' if isinstance(e.orig, UndefinedTable) else f'{e.orig}'
            else:
                status_code = 400 if isinstance(e, (BadRequestError, FileNotSupported, UploadNotAllowed, AssertionError)) else 404 if isinstance(e, NotFound) else 409 if isinstance(e, MaxOccurrenceError) else status_code
                msg = f"{e._message()}" if isinstance(e, (BadRequestError, NotFound, MaxOccurrenceError,FileNotSupported,UploadNotAllowed,)) else msg  
            logger(__name__, e, 'critical')
            raise HTTPException(status_code=status_code, detail=raise_exc(msg=msg, type=class_name))

    async def bk_update(self, payload, db:Session, **kwargs):
        try:
            rows = db.query(self.model).filter_by(**kwargs).update(payload.dict(exclude_unset=True), synchronize_session="fetch")
            db.commit()
            return "success", {"info":f"{rows} row(s) updated"}
        except Exception as e:
            # log here
            # raise HTTPException(
            #     status_code=409 if isinstance(e, IntegrityError) or isinstance(e, MaxOccurrenceError) else 400 if isinstance(e.orig, UndefinedTable) or isinstance(e, AssertionError) else 500, 
            #     detail=raise_exc(
            #         msg=f"{'(psycopg2.errors.UndefinedTable) This may be due to missing tenant' if isinstance(e.orig, UndefinedTable) else  e.orig}", 
            #         type=f"{e.__class__}"
            #     ),
            # )

            # print(e)

            status_code, msg, class_name = 500, f'{e}' , f"{e.__class__.__name__}"
            if isinstance(e, DBAPIError):
                status_code = 409 if isinstance(e, IntegrityError) else 400 if isinstance(e.orig, UndefinedTable) else 500
                msg=f'(UndefinedTable) This may be due to missing tenant_key in request header' if isinstance(e.orig, UndefinedTable) else f'{e.orig}'
            else:
                status_code = 400 if isinstance(e, (BadRequestError, FileNotSupported, UploadNotAllowed, AssertionError)) else 404 if isinstance(e, NotFound) else 409 if isinstance(e, MaxOccurrenceError) else status_code
                msg = f"{e._message()}" if isinstance(e, (BadRequestError, NotFound, MaxOccurrenceError,FileNotSupported,UploadNotAllowed,)) else msg  
            logger(__name__, e, 'critical')
            raise HTTPException(status_code=status_code, detail=raise_exc(msg=msg, type=class_name))

    async def bk_delete(self, ids:list, db:Session, use_field:str=None, **kwargs):
        try:
            subq = getattr(self.model, use_field).in_(ids) if use_field else self.model.id.in_(ids)
            rows = db.query(self.model).filter(subq).filter_by(**kwargs).delete(synchronize_session=False)
            db.commit()
            return f"{rows} row(s) deleted"
        # except IntegrityError as e:
        #     raise HTTPException(status_code=409, detail=http_exception_detail(msg=e._message().split('DETAIL:  ', 1)[1], type= e.__class__.__name__))
        # except MaxOccurrenceError as e:
        #     raise HTTPException(status_code=409, detail=http_exception_detail(msg=e._message(), type= e.__class__.__name__))
        except Exception as e:
            # raise HTTPException(status_code=500, detail=http_exception_detail(msg=f"{e}", type= e.__class__.__name__))

            # print(e)

            status_code, msg, class_name = 500, f'{e}' , f"{e.__class__.__name__}"
            if isinstance(e, DBAPIError):
                status_code = 409 if isinstance(e, IntegrityError) else 400 if isinstance(e.orig, UndefinedTable) else 500
                msg=f'(UndefinedTable) This may be due to missing tenant_key in request header' if isinstance(e.orig, UndefinedTable) else f'{e.orig}'
            else:
                status_code = 400 if isinstance(e, (BadRequestError, FileNotSupported, UploadNotAllowed, AssertionError)) else 404 if isinstance(e, NotFound) else 409 if isinstance(e, MaxOccurrenceError) else status_code
                msg = f"{e._message()}" if isinstance(e, (BadRequestError, NotFound, MaxOccurrenceError,FileNotSupported,UploadNotAllowed,)) else msg  
            logger(__name__, e, 'critical')
            raise HTTPException(status_code=status_code, detail=raise_exc(msg=msg, type=class_name))

    async def bk_delete_2(self, db:Session, **kwargs):
        try:
            rows = db.query(self.model).filter_by(**kwargs).delete(synchronize_session=False)
            db.commit()
            return "success", {"info":f"{rows} row(s) deleted"}
        except Exception as e:
            # log here
            # raise HTTPException(
            #     status_code=409 if isinstance(e, IntegrityError) or isinstance(e, MaxOccurrenceError) else 400 if isinstance(e.orig, UndefinedTable) or isinstance(e, AssertionError) else 500, 
            #     detail=raise_exc(
            #         msg=f"{'(psycopg2.errors.UndefinedTable) This may be due to missing tenant' if isinstance(e.orig, UndefinedTable) else  e.orig}", 
            #         type=f"{e.__class__}"
            #     ),
            # )

            # print(e)

            status_code, msg, class_name = 500, f'{e}' , f"{e.__class__.__name__}"
            if isinstance(e, DBAPIError):
                status_code = 409 if isinstance(e, IntegrityError) else 400 if isinstance(e.orig, UndefinedTable) else 500
                msg=f'(UndefinedTable) This may be due to missing tenant_key in request header' if isinstance(e.orig, UndefinedTable) else f'{e.orig}'
            else:
                status_code = 400 if isinstance(e, (BadRequestError, FileNotSupported, UploadNotAllowed, AssertionError)) else 404 if isinstance(e, NotFound) else 409 if isinstance(e, MaxOccurrenceError) else status_code
                msg = f"{e._message()}" if isinstance(e, (BadRequestError, NotFound, MaxOccurrenceError,FileNotSupported,UploadNotAllowed,)) else msg  
            logger(__name__, e, 'critical')
            raise HTTPException(status_code=status_code, detail=raise_exc(msg=msg, type=class_name))

    async def exists(self, db, **kwargs):
        try:
            return db.query(self.model).filter_by(**kwargs).first() is not None
        except Exception as e:
            # log here
            raise HTTPException(
                status_code=400 if isinstance(e.orig, UndefinedTable) else 500, 
                detail=raise_exc(
                    msg=f"{'(psycopg2.errors.UndefinedTable) This may be due to missing tenant' if isinstance(e.orig, UndefinedTable) else  e.orig}", 
                    type=f"{e.__class__}"
                ),
            )

class Aggregator:
    """
        A simple Aggregator class
        fields = ['id']
        q_type = QueryType.res -> [
            res = "res" -> return actual results
            subq = "subq" -> returns subquery
            query = "query" -> returns query
        ]
        group_by = ['status']
        op = 'sum' -> [
            count = 'count' -> for sql COUNT function
            sum = 'sum' -> for sql SUM function
            min = 'min' -> for sql MIN function
            max = 'max' -> for sql MAX function
            avg = 'avg' -> for sql AVG function
        ]
        res = zx.op(
            fields, list(sessions), op, q_type, group_by
        )
    """
    Op = enum.Enum('Op', {v:v for v in ["sum","min","max","avg","count"]})
    QueryType = enum.Enum('QueryType', {v:v for v in ["res","subq","query"]})
    
    def __init__(self, model):
        self.model = model

    def op(self, fields:list, dbs:List[Session], op:Op, date:D=None, q_type:QueryType='res', group_by:List[str]=[], and_filters:dict={}, or_filters:dict={}, **kw):
        queryset, d_fields = self.get_queryset(fields, dbs, date, group_by, and_filters, or_filters, **kw), []

        obj = [getattr(func, op)(queryset.c[field]) for field in fields]

        if date:
            if date.months:
                d_fields.append(queryset.c.month)
            if date.years:
                d_fields.append(queryset.c.year)
            obj.extend(d_fields)
        
        if group_by:
            group_by = [queryset.c[group_by] for group_by in group_by]
            obj.extend(group_by)
            d_fields.extend(group_by)

        base = dbs[0].query(*obj).group_by(*d_fields)
        return base if q_type=='query' else base.subquery() if q_type=='subq' else base.all()
   
    def get_queryset(self, fields:list, dbs:List[Session], date:D=None, group_by:List[str]=[], and_filters:dict={}, or_filters:dict={}, **kw):
        fields = [getattr(self.model, field).label(field) for field in fields]
        
        if group_by:
            fields += [getattr(self.model, group_by).label(group_by) for group_by in group_by]

        d_fields,d_filters = [],[]
        if date:
            d_fields,d_filters = self.year_filter(date)
            fields.extend(d_fields)
        
        querysets = [
            db.query(*fields).filter(or_(**or_filters)).filter(and_(**and_filters)).filter(**kw).filter(*d_filters)
            for db in dbs
        ]

        return union_all(*querysets).subquery()

    def year_filter(self, obj:D):
        if not self.is_date(obj.field):
            raise ValueError(f'{obj.field} not date_type')
        fields,filters,yObj,mObj = [],[],None,None
        if obj.months:
            mObj = extract('month', getattr(self.model, obj.field)).label('month')
            filters.append(or_(*[mObj==int(month) for month in obj.months])) 
        if obj.years:
            yObj = extract('year', getattr(self.model, obj.field)).label('year')
            filters.append(or_(*[yObj==int(year) for year in obj.years])) 
        fields.extend([yObj, mObj])
        return fields, filters

    def years(self, db:Session, field='created'):
        if not self.is_date(field):
            raise ValueError(f'{field} not date_type')
        return [date[0].year for date in db.query(getattr(self.model, field).cast(Date)).distinct().all()]

    def is_date(self, field):
        return isinstance(self.model.__table__.c[field].type, (DATETIME, DATE, Date, DateTime))

class ContentQueryChecker:
    def __init__(self, cols=None, actions=None, exclude:List[str]=[]):
        self._cols = [col for col in cols if col[0] not in exclude]
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
            return IMAGE_URL
        elif ext in UPLOAD_EXTENSIONS["AUDIO"]:
            return AUDIO_URL
        elif ext in UPLOAD_EXTENSIONS["VIDEO"]:
            return VIDEO_URL
        elif ext in UPLOAD_EXTENSIONS["DOCUMENT"]:
            return DOCUMENT_URL
        raise UploadNotAllowed('Unsupported file extension')
    
    def _path(self):
        url = self.file_allowed()
        tmp_path = os.path.join(UPLOAD_ROOT, url)
        path = os.path.join(tmp_path, f'{self.upload_to}')  
        if not os.path.isdir(path):
            os.makedirs(path)
        return path
        
    def _url(self):
        name, cnt = "_".join(os.path.splitext(self.file.filename)[0].split()), 1
        url = os.path.join(self._path(), f'{name}{self._ext()}')
        while pathlib.Path(url).exists():
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
                self.file.file.close()
        finally:
            return url

    def _save_file(self):
        url = self._url()
        try:
            with open(url, "wb") as buffer:
                shutil.copyfileobj(self.file.file, buffer)
                self.file.file.close()
        finally:
            return url

    def save(self, *args, **kwargs):
        if settings.USE_S3:
            url = os.path.relpath(self._url(), BASE_DIR) 
            async_s3_upload(self.file, object_name=url) # push to celery to upload
        else:
            if self.file:
                url = self._image() if self.file.content_type.split("/")[0]=="image" else self._save_file()
                url = os.path.relpath(url, BASE_DIR) 
            else:
                url = None
        return f"S3:/{url}" if settings.USE_S3 else f"LD:/{url}" if url else None