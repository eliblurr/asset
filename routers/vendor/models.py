from sqlalchemy import Column, String, CheckConstraint, Integer, ForeignKey
from sqlalchemy.orm import validates, relationship
from routers.category.models import CategoryVendor
from database import TenantBase, Base
from constants import EMAIL, PHONE
from mixins import BaseMixin
import re

class Vendor(BaseMixin, Base):
    '''Vendor Model'''
    __tablename__ = "vendors"
    __table_args__ = (CheckConstraint('coalesce(contact , email) is not null', name='_email_or_contact_'),)

    title =  Column(String, nullable=False)
    website = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)
    contact = Column(String, unique=True, nullable=True)
    assets_sold = relationship("Asset", back_populates="vendor")
    categories = relationship("Category", secondary=CategoryVendor.__table__, back_populates="vendors")

    @validates('email')
    def validate_email(self, key, address):
        assert re.search(EMAIL, address), 'invalid email format'
        return address
    
    @validates('contact')
    def validate_phone(self, key, address):
        assert re.search(PHONE, address), 'invalid phone format'
        return address