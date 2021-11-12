from sqlalchemy.schema import CreateSchema, DropSchema
from sqlalchemy import Column, String, event, Boolean
from database import Base, TenantBase, engine, GlobalBase
from mixins import BaseMixin, HashMethodMixin
from sqlalchemy.orm import validates
from utils import gen_hex, today_str
from constants import PHONE, EMAIL
from passlib import pwd
from ctypes import File
import re

class Tenant(BaseMixin, HashMethodMixin, Base):
    __tablename__ = 'tenants'
    __table_args__ = ({'schema':'public'},)

    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    metatitle = Column(String, nullable=True)
    is_active = Column(Boolean, default=False)
    description = Column(String, nullable=True)
    street_address = Column(String, nullable=True)
    postal_address = Column(String, nullable=True)
    digital_address = Column(String, nullable=True)
    title = Column(String, nullable=False, unique=True)
    sub_domain_id = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False, default=pwd.genword)
    key = Column(String, nullable=False, unique=True, default=gen_hex)
    bg_image = Column(File(upload_to=f'tenants/{today_str()}/images/background/'))
    logo = Column(File(upload_to=f'tenants/{today_str()}/images/logo/', size=(100,100)))
    
    @validates('email')
    def validate_email(self, key, value):
        assert re.search(EMAIL, value), 'invalid email format'
        return value

    @validates('phone')
    def validate_phone(self, key, value):
        assert re.search(PHONE, value), 'invalid phone format for phone'
        return value

@event.listens_for(Tenant, "after_insert")
def create_tenant_schema(mapper, connection, target):
    connection.engine.execute(CreateSchema(target.key))
    connection = engine.connect().execution_options(schema_translate_map={None: target.key,})
    Base.metadata.create_all(bind=connection, tables=[table for table in Base.metadata.sorted_tables if table.schema==None])

@event.listens_for(Tenant, 'before_insert')
@event.listens_for(Tenant, 'before_update')
def hash_password(mapper, connection, target):
    if target.password:
        target.password = target.generate_hash(target.password)

@event.listens_for(Tenant, 'after_delete')
def receive_after_delete(mapper, connection, target):
    connection.engine.execute(DropSchema(target.key, cascade=True))
    if target.url[:3]=='S3:':
        s3_delete.delay(target.url[3:])
    _delete_path(target.url[3:])