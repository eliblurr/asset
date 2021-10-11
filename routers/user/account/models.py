from sqlalchemy import Column, String, Boolean, event
from database import Base, TenantBase
from sqlalchemy.orm import validates
from mixins import BaseMixin, HashMethodMixin
from constants import EMAIL
from utils import gen_code
import re

from passlib import pwd

class User(BaseMixin, HashMethodMixin, Base):
    '''User Model'''
    __tablename__ = "users"

    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False, default=pwd.genword)
    # password = Column(String, nullable=False, default=gen_code)
    
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
def deactivate_account(mapper, connection, target):
    if target.password == None:
        target.status = False

# from sqlalchemy.orm import Session

@event.listens_for(User, 'before_insert')
@event.listens_for(User, 'before_update')
def hash_password(mapper, connection, target):
    # session = Session.object_session(target)
    # if session.is_modified(target, include_collections=False):
    #     print('update detected')
    print('sdds')
    print(target.password)
    if target.password:
        target.password = target.generate_hash(target.password)

# event.listen(User, 'before_update', hash_password)