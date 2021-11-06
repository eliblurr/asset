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


from sqlalchemy import MetaData
    
def merge_metadata(*original_metadata) -> MetaData:
    merged = MetaData()

    for original_metadatum in original_metadata:
        for table in original_metadatum.tables.values():
            table.to_metadata(merged)
    
    return merged

# print(merge_metadata(TenantBase.metadata, Base.metadata).tables.keys())

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
