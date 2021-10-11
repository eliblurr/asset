from sqlalchemy import Column, DateTime, Boolean, Integer
from passlib.hash import pbkdf2_sha256 as sha256
from datetime import datetime
from utils import gen_code

class BaseMethodMixin(object):
    @classmethod
    def c(cls):
        return [(c.name, c.type.python_type) if c.name!='__ts_vector__' else (c.name, None) for c in cls.__table__.columns]

class BaseMixin(BaseMethodMixin):    
    status = Column(Boolean, default=True)
    created = Column(DateTime, default=datetime.utcnow)
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HashMethodMixin(object):
    @classmethod
    def generate_hash(self, data):
        return sha256.hash(data)

    @classmethod
    def verify_hash(self, data, hash):
        return sha256.verify(data, hash)