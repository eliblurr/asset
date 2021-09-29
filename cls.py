from inspect import Parameter, Signature, signature
from fastapi import Query, WebSocket
from sqlalchemy.orm import Session
from utils import schema_to_model
from constants import DT_X, Q_X
from functools import wraps
import enum, re, datetime
from typing import List

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

    async def read_by_id(self, id, db:Session, fields:List[str]=None):
        fields = [getattr(self.model, field.strip()) for field in fields]  if fields!=None else [self.model]
        return db.query(*fields).filter(self.model.id==id).first()

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
            Parameter('fields', Parameter.KEYWORD_ONLY, annotation=List[str], default=Query(None, regex=f'({q_str})$')),
            Parameter('q', Parameter.KEYWORD_ONLY, annotation=List[str], default=Query(None, regex=Q_X.format(cols=f'({q_str})') if q_str else '^[\w]+$|^[\w]+:[\w]+$')),
            Parameter('sort', Parameter.KEYWORD_ONLY, annotation=List[str], default=Query(None, regex=sort_str if sort_str else '(^-)?\w')),])  
        if self._actions:
            params.extend([Parameter('action', Parameter.KEYWORD_ONLY, annotation=str, default=Query(None))])
        wrapper.__signature__ = Signature(params)
        return wrapper

class SocketConnectionManager:
    def __init__(self):
        self.active_connections:List[WebSocket] = []

    async def connect(self, websocket:WebSocket, client_id:int):
        websocket._cookies['client_id']=client_id
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket:WebSocket):
        self.active_connections.remove(websocket)

    def client_connection(self, client_id:int):
        return [websocket for websocket in self.active_connections if websocket._cookies.get('client_id', None) == client_id]

    async def send_personal_message(self, message:(str, dict), client_id:int):
        client_connections = self.client_connection(client_id)
        for websocket in client_connections:
            if isinstance(message, str):
                return await websocket.send_text(message)
            return await websocket.send_json(message)

    async def broadcast(self, message: (str, dict)):
        for websocket in self.active_connections:
            if isinstance(message, str):
                return await websocket.send_text(message)
            return await websocket.send_json(message)