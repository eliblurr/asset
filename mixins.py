from sqlalchemy import Column, DateTime, Boolean, String
from datetime import datetime
from uuid import uuid4

class BaseMethodMixin(object):
    @classmethod
    def c(cls):
        return [(c.name, c.type.python_type) if c.name!='__ts_vector__' else (c.name, None) for c in cls.__table__.columns]

class BaseMixin(BaseMethodMixin):    
    status = Column(Boolean, default=True)
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    id = Column(String, primary_key=True, index=True, default=uuid4)