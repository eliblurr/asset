from sqlalchemy import Column, String, Boolean, event, Integer, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from mixins import BaseMixin, HashMethodMixin
from sqlalchemy.orm import relationship
from database import Base, TenantBase
from sqlalchemy.orm import validates
from constants import EMAIL, PHONE
from passlib import pwd
import re

class User(BaseMixin, HashMethodMixin, TenantBase):
    '''User Model'''
    __tablename__ = "users"

    phone = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=False)
    middle_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)
    role_id  = Column(Integer, ForeignKey('roles.id'))
    role = relationship('Role', back_populates="users")
    password = Column(String, nullable=False, default=pwd.genword)
    status = 1

    @validates('email')
    def validate_email(self, key, value):
        assert re.search(EMAIL, value), 'invalid email format'
        return value

    @validates('phone')
    def validate_phone(self, key, address):
        assert re.search(PHONE, address), 'invalid phone format'
        return address

@event.listens_for(User, 'after_insert')
@event.listens_for(User, 'before_update')
def hash_password(mapper, connection, target):
    if target.password:
        connection.execute(User.__table__.update().values(password=target.generate_hash(target.password)))