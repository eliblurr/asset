from sqlalchemy import Column, String, CheckConstraint
from sqlalchemy.orm import validates
from constants import EMAIL, PHONE
from database import TenantBase
from mixins import BaseMixin
import re

class Vendor(BaseMixin, TenantBase):
    '''Vendor Model'''
    __tablename__ = "vendors"
    __table_args__ = (CheckConstraint('coalesce(contact , email) is not null', name='_email_or_contact_'),)

    title =  Column(String, nullable=False)
    website = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)
    contact = Column(String, unique=True, nullable=True)

    @validates('email')
    def validate_email(self, key, address):
        assert re.search(EMAIL, address), 'invalid email format'
        return address
    
    @validates('contact')
    def validate_phone(self, key, address):
        assert re.search(PHONE, address), 'invalid phone format'
        return address
