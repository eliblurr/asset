from inspect import Parameter, Signature, signature
from sqlalchemy.orm import Session
from utils import schema_to_model
from functools import wraps
import re, datetime
from fastapi import Query
from typing import List

from constants import DT_X, Q_X


class CRUD:
    def __init__(self, model):
        self.model = model

    async def create(self, payload, db:Session, images=None):
        obj = self.model(**schema_to_model(payload))
        if images:
            pass
        db.add(obj)
        db.commit()
        db.refresh(obj) 
        return obj  

    async def read(self, params, db:Session):
        pass

    async def read_by_id(self, id, db:Session):
        return db.query(self.model).filter(self.model.id==id).first()

    async def update(self, id, payload, db:Session, images=None):
        rows = db.query(self.model).filter(self.model.id==id).delete(synchronize_session=False)
        db.commit()
        return "success", {"info":f"{rows} row(s) updated"}

    async def delete(self, id, db:Session):
        rows = db.query(self.model).filter(self.model.id==id).delete(synchronize_session=False)
        db.commit()
        return "success", {"info":f"{rows} row(s) deleted"}

    async def bk_create(self, payload, db:Session):
        db.add_all([self.model(**schema_to_model(payload)) for payload in payload])
        db.commit()
        return "success", {"info":f"row(s) created"}

    async def bk_update(self, payload, db:Session, **kwargs):
        rows = db.query(self.model).filter_by(**kwargs).update(payload.dict(exclude_unset=True), synchronize_session="fetch")
        db.commit()
        return "success", {"info":f"{rows} row(s) updated"}

    async def bk_delete(self, ids:list, db:Session):
        rows = db.query(self.model).filter(self.model.id.in_(ids)).delete(synchronize_session=False)
        db.commit()
        return "success", {"info":f"{rows} row(s) deleted"}



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
            Parameter('q', Parameter.KEYWORD_ONLY, annotation=List[str], default=Query(None, regex=Q_X.format(cols=f'({q_str})') if q_str else '^[\w]+$|^[\w]+:[\w]+$')),
            Parameter('sort', Parameter.KEYWORD_ONLY, annotation=List[str], default=Query(None, regex=sort_str if sort_str else '(^-)?\w')),])  
        if self._actions:
            params.extend([Parameter('action', Parameter.KEYWORD_ONLY, annotation=str, default=Query(None))])
        wrapper.__signature__ = Signature(params)
        return wrapper