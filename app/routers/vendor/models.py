from sqlalchemy import Column, String, CheckConstraint
from sqlalchemy.orm import validates, relationship
from constants import EMAIL, PHONE, URL
from mixins import BaseMixin
from database import Base
from routers.category.models import CategoryVendor
import re

class Vendor(BaseMixin, Base):
    '''Vendor Model'''
    __tablename__ = "vendors"
    __table_args__ = (CheckConstraint('coalesce(contact,email,url) is not null', name='_either_contact_email_url_'),)
    
    url = Column(String, nullable=True)
    email = Column(String, unique=True)
    contact = Column(String, unique=True)
    title =  Column(String, nullable=False)
    metatitle = Column(String, nullable=True)
    description = Column(String, nullable=True)
   
    assets_sold = relationship("Asset", back_populates="sold_by")
    categories = relationship("Category", secondary=CategoryVendor.__table__, back_populates="vendors")

    @validates('email')
    def validate_email(self, key, value):
        assert re.search(EMAIL, value), 'invalid email format'
        return value
    
    @validates('contact')
    def validate_phone(self, key, value):
        assert re.search(PHONE, value), 'invalid phone format'
        return value

    @validates('url')
    def validate_url(self, key, value):
        assert re.search(URL, value), 'invalid url format'
        return value