from sqlalchemy.schema import CreateSchema, DropSchema
from sqlalchemy import Column, String, event, Boolean
from database import Base, TenantBase, engine
from mixins import BaseMixin, HashMethodMixin
from sqlalchemy.orm import validates
from constants import PHONE, EMAIL
from utils import gen_hex
from passlib import pwd
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
    logo_url = Column(String, nullable=False, unique=True, default=pwd.genword)
    bg_image_url = Column(String, nullable=False, unique=True, default=pwd.genword)
    sub_domain_id = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False, default=pwd.genword)
    key = Column(String, nullable=False, unique=True, default=gen_hex)
    
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
    TenantBase.metadata.create_all(bind=connection)

@event.listens_for(Tenant, 'before_insert')
@event.listens_for(Tenant, 'before_update')
def hash_password(mapper, connection, target):
    if target.password:
        target.password = target.generate_hash(target.password)

@event.listens_for(Tenant, 'after_delete')
def receive_after_delete(mapper, connection, target):
    connection.engine.execute(DropSchema(target.key, cascade=True))