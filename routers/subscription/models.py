from sqlalchemy import Column, String, Integer, ForeignKey, Float
from sqlalchemy.orm import validates, relationship
from constants import EMAIL, PHONE, URL
from config import THUMBNAIL
from mixins import BaseMixin
from utils import today_str
from database import Base
from ctypes import File
import re

class Package(BaseMixin, Base):
    '''Package Model'''
    __tablename__ = "packages"

    title = Column(String, nullable=False)
    metatitle = Column(String, nullable=True)
    description = Column(String, nullable=True)
    service_owner_url = Column(String, nullable=True)
    service_owner_email = Column(String, nullable=True)
    service_owner_phone = Column(String, nullable=True)
    logo = Column(File(upload_to=f'{today_str()}', size=THUMBNAIL), nullable=True)

    @validates('service_owner_email')
    def validate_email(self, key, value):
        assert re.search(EMAIL, value), 'invalid email format'
        return value

    @validates('service_owner_phone')
    def validate_phone(self, key, value):
        assert re.search(PHONE, value), 'invalid phone format for phone'
        return value

    @validates('service_owner_url')
    def validate_phone(self, key, value):
        assert re.search(URL, value), 'invalid url format for phone'
        return value

class Subscription(BaseMixin, Base): 
    '''Subscription Model'''
    __tablename__ = "subscriptions"

    asset_id = Column(Integer, ForeignKey('assets.id'), primary_key=True, nullable=False)
    package_id = Column(Integer, ForeignKey('packages.id'), primary_key=True, nullable=False)
    price = Column(Float, nullable=False, default=0.0)
  
    asset = relationship("Asset", back_populates="subscriptions")
    package = relationship("Package")

    id = None
