from sqlalchemy.schema import CreateSchema, DropSchema
from sqlalchemy import Column, String, event
from sqlalchemy.orm import validates
from constants import PHONE, EMAIL
from database import Base, engine
from mixins import BaseMixin
import re

class Tenant(BaseMixin, Base):
    __tablename__ = 'tenants'
    __table_args__ = ({'schema':'public'},)

    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    metatitle = Column(String, nullable=True)
    description = Column(String, nullable=True)
    street_address = Column(String, nullable=True)
    postal_address = Column(String, nullable=True)
    digital_address = Column(String, nullable=True)
    title = Column(String, nullable=False, unique=True)
    logo_url = Column(String, nullable=False, unique=True, default='/sdds')
    bg_image_url = Column(String, nullable=False, unique=True, default='/sdds')
    sub_domain_id = Column(String, nullable=False, unique=True)
    
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
    connection.engine.execute(CreateSchema(target.id))
    connection = engine.connect().execution_options(schema_translate_map={None: target.id,})
    Base.metadata.create_all(bind=connection, tables=[table for table in Base.metadata.sorted_tables if table.schema==None])

# print(Base.metadata.tables.keys())