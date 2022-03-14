from sqlalchemy import Column, DateTime, Boolean, Integer, BigInteger, JSON, String
from passlib.hash import pbkdf2_sha256 as sha256
from datetime import datetime
from utils import gen_code
from ctypes import File

class BaseMethodMixin(object):
    @classmethod
    def c(cls):
        return [
            (c.name, c.type.python_type) if not isinstance(c.type, File) else (c.name, str) for c in cls.__table__.columns
        ]

class BaseMixin(BaseMethodMixin):    
    status = Column(Boolean, default=True)
    created = Column(DateTime, default=datetime.utcnow)
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GenCodeMixin(object):
    code = Column(String, unique=False, default=gen_code)

class HashMethodMixin(object):
    @classmethod
    def generate_hash(self, data):
        return sha256.hash(data)

    @classmethod
    def verify_hash(self, data, hash):
        return sha256.verify(data, hash)

# from sqlalchemy.orm import declared_attr, declarative_mixin, relationship

# @declarative_mixin
# class RefTargetMixin:
#     # @declared_attr
#     # def target_id(cls):
#     #     return Column('target_id', ForeignKey('target.id'))

#     @declared_attr
#     def target(cls):
#         return relationship("Permission")

#     def has_perm(self, perm):
#         return perm in self.permissions

#     def add_perm(self, perm):
#         if not self.has(perm):
#             self.permissions += perm