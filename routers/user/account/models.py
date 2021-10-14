from sqlalchemy import Column, String, Boolean, event
from mixins import BaseMixin, HashMethodMixin
from database import Base, TenantBase
from sqlalchemy.orm import validates
from constants import EMAIL, PHONE
import re

from passlib import pwd

class User(BaseMixin, HashMethodMixin, Base):
    '''User Model'''
    __tablename__ = "users"

    phone = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=False)
    middle_name = Column(String, nullable=True)
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

    @validates('phone')
    def validate_phone(self, key, address):
        assert re.search(PHONE, address), 'invalid phone format'
        return address

@event.listens_for(User, 'before_insert')
@event.listens_for(User, 'before_update')
def deactivate_account(mapper, connection, target):
    if target.password:
        target.password = target.generate_hash(target.password)