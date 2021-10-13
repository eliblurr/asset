from sqlalchemy import Column, String, Boolean, event
from mixins import BaseMixin, HashMethodMixin
from database import Base, TenantBase
from sqlalchemy.orm import validates
from constants import EMAIL
import re

from passlib import pwd

class User(BaseMixin, HashMethodMixin, Base):
    '''User Model'''
    __tablename__ = "users"

    is_active = Column(Boolean, default=False)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False, default=pwd.genword)
    status = 1
    
    @validates('email')
    def validate_email(self, key, value):
        assert re.search(EMAIL, value), 'invalid email format'
        return value

    @validates('password')
    def validate_password(self, key, value):
        if value:
            assert len(value) > 7, 'password length not supported, must contain at least 8 characters'
            return value

@event.listens_for(User, 'before_insert')
@event.listens_for(User, 'before_update')
def deactivate_account(mapper, connection, target):
    if target.password:
        target.password = target.generate_hash(target.password)