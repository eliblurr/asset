from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, String, event
from constants import EMAIL, PHONE, URL
from database import Base, TenantBase
from sqlalchemy.orm import validates
from mixins import BaseMixin
import re

class ManufacturerMixin(object):
    @declared_attr
    def __tablename__(cls):
        return "manufacturers"
    
    metatitle = Column(String, nullable=True)
    description = Column(String, nullable=True)
    email = Column(String, nullable=True, unique=True)
    contact = Column(String, nullable=True, unique=True)
    website = Column(String, nullable=True, unique=True)
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

class Manufacturer2(ManufacturerMixin, BaseMixin, TenantBase):
    '''Manufacturer Model for tenant schema'''

@event.listens_for(Manufacturer, 'before_insert')
@event.listens_for(Manufacturer, 'before_update')
def ensure_unique(mapper, connection, target):
    pass
#     if connection.get_execution_options().get('schema_translate_map', None):
#         print('tenant')
    # print(
    #     dir(connection),
    #     connection.get_execution_options(),
    #     sep='\n\n'
    # )
    # print(target.password)
    # if target.password:
    #     target.password = target.generate_hash(target.password)
