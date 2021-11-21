from sqlalchemy import Column, DateTime, Boolean, Integer, BigInteger, JSON
from passlib.hash import pbkdf2_sha256 as sha256
from datetime import datetime
from utils import gen_code
from ctypes import File

class BaseMethodMixin(object):
    @classmethod
    def c(cls):
        return [
            (c.name, c.type.python_type) if not isinstance(c.type, File) else (c.name, str) for c in cls.__table__.columns
            # if c.name!='__ts_vector__' 
            # or not isinstance(c.type, File)
            # if any((c.name=='__ts_vector__', not isinstance(c.type, File))) # needs fixing
            # else (c.name, None) for c in cls.__table__.columns
        ]

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

class PermissionMixin(object):
    permissions = Column(BigInteger, nullable=False, default=0)

    def has(self, perm):
        return self.permissions & perm == perm

    def add(self, perm):
        if not self.has(perm):
            self.permissions += perm

    def delete(self, perm):
        if self.has(perm):
            self.permissions -= perm

    def reset(self):
        self.permissions = 0    