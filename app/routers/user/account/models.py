from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from mixins import BaseMixin, HashMethodMixin
from sqlalchemy.orm import relationship
from sqlalchemy.orm import validates
from constants import PHONE, EMAIL
from utils import gen_code
from database import Base
import re, uuid

class User(BaseMixin, HashMethodMixin, Base):
    '''User Model'''
    __tablename__ = "users"

    phone = Column(String, nullable=True)
    password = Column(String, nullable=True)
    last_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    first_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    email = Column(String, unique=True, index=True)
    role = relationship('Role', back_populates="users")
    branch = relationship("Branch", back_populates="staff")
    branch_id = Column(Integer, ForeignKey('branches.id'))
    role_id  = Column(Integer, ForeignKey('roles.id'), nullable=False)
    push_id = Column(String, unique=True, nullable=False, default=uuid.uuid4)
    department_id = Column(Integer, ForeignKey('departments.id', use_alter=True))
    department = relationship("Department", back_populates="staff", foreign_keys="User.department_id")
    proposals = relationship("Proposal", back_populates="author")
    requests = relationship("Request", back_populates="author", foreign_keys="[Request.author_id]")    

    @validates('password', include_removes=True)
    def validate_password(self, key, value, is_remove):
        assert len(value) > 7, 'unacceptable password length'
        return self.__class__.generate_hash(value)

    @validates('email')
    def validate_email(self, key, value):
        assert re.search(EMAIL, value), 'invalid email format'
        return value

    @validates('phone')
    def validate_phone(self, key, value):
        assert re.search(PHONE, value), 'invalid phone format'
        return value

    def full_name(self):
        return f'{self.first_name} {f"{self.middle_name} "}{self.last_name}'

    status = None

class Administrator(BaseMixin, HashMethodMixin, Base):
    '''System Administrator Model'''
    __tablename__ = "administrators"
    __table_args__ = ({'schema':'public'},)

    is_active = Column(Boolean, default=False)
    email = Column(String, unique=True, index=True)
    is_verified = Column(Boolean, default=False)
    password = Column(String, nullable=True)
    push_id = Column(String, unique=True, nullable=False, default=uuid.uuid4)

    @validates('password', include_removes=True)
    def validate_password(self, key, value, is_remove):
        assert len(value) > 7, 'unacceptable password length'
        return self.__class__.generate_hash(value)

    @validates('email')
    def validate_email(self, key, value):
        assert re.search(EMAIL, value), 'invalid email format'
        return value
    
    status = None