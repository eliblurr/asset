from sqlalchemy.schema import CreateSchema, DropSchema
from sqlalchemy import Column, String, event, Boolean
from rds.tasks import async_remove_file
from sqlalchemy.orm import validates
from utils import gen_hex, today_str
from constants import PHONE, EMAIL
from database import Base, engine
from mixins import BaseMixin
from ctypes import File
import re

class Tenant(BaseMixin, Base):
    __tablename__ = 'tenants'
    __table_args__ = ({'schema':'public'},)

    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    metatitle = Column(String, nullable=True)
    is_active = Column(Boolean, default=False)
    description = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    street_address = Column(String, nullable=True)
    postal_address = Column(String, nullable=True)
    digital_address = Column(String, nullable=True)
    title = Column(String, nullable=False, unique=True)
    sub_domain = Column(String, nullable=False, unique=True)
    bg_image = Column(File(upload_to=f'{today_str()}'), nullable=True)
    scheme = Column(String, nullable=False, unique=True, default=gen_hex)
    logo = Column(File(upload_to=f'{today_str()}', size=(100,100)), nullable=False)

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
    with connection.begin():
        connection.engine.execute(CreateSchema(target.scheme))
        connection = engine.connect().execution_options(schema_translate_map={None: target.scheme,})
        Base.metadata.create_all(bind=connection, tables=[table for table in Base.metadata.sorted_tables if table.schema==None or table.schema=='global'])

@event.listens_for(Tenant, 'after_delete')
def receive_after_delete(mapper, connection, target):
    if target.logo:async_remove_file(target.logo)
    if target.bg_image:async_remove_file(target.bg_image)
    with connection.begin():connection.engine.execute(DropSchema(target.scheme, cascade=True))

@event.listens_for(Tenant.logo, 'set', propagate=True)
@event.listens_for(Tenant.bg_image, 'set', propagate=True)
def receive_set(target, value, oldvalue, initiator):
    if oldvalue:async_remove_file(oldvalue)