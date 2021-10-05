from sqlalchemy import Column, DateTime, Boolean, Integer
from datetime import datetime

class BaseMethodMixin(object):
    @classmethod
    def c(cls):
        return [(c.name, c.type.python_type) if c.name!='__ts_vector__' else (c.name, None) for c in cls.__table__.columns]

class BaseMixin(BaseMethodMixin):    
    status = Column(Boolean, default=True)
    created = Column(DateTime, default=datetime.utcnow)
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)