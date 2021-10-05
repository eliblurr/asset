from sqlalchemy.ext.declarative import declared_attr
from constants import EMAIL, PHONE, URL
from sqlalchemy import Column, String
from database import Base, TenantBase
from sqlalchemy.orm import validates
from mixins import BaseMixin
import re

class ManufacturerMixin(object):
    @declared_attr
    def __tablename__(cls):
        return "manufacturers"
    
    email = Column(String, nullable=True)
    contact = Column(String, nullable=True)
    website = Column(String, nullable=True)
    metatitle = Column(String, nullable=True)
    description = Column(String, nullable=True)
    title =  Column(String, nullable=False, unique=True)

    @validates('email')
    def validate_email(self, key, address):
        assert re.search(EMAIL, address), 'invalid email format'
        return address
    
    @validates('contact')
    def validate_phone(self, key, address):
        assert re.search(PHONE, address), 'invalid phone format'
        return address

    @validates('website')
    def validate_website(self, key, address):
        assert re.search(URL, address), 'invalid url format'
        return address

class Manufacturer(ManufacturerMixin, BaseMixin, Base):
    '''Manufacturer Model for public schema'''

class Manufacturer(ManufacturerMixin, BaseMixin, TenantBase):
    '''Manufacturer Model for tenant schema'''

class ManufacturerView():
    pass