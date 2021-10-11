from sqlalchemy import Column, String
from database import TenantBase
from mixins import BaseMixin
import re

class Branch(BaseMixin, TenantBase):
    '''Branch Model'''
    __tablename__ = 'branches'

    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    metatitle = Column(String, nullable=True)
    description = Column(String, nullable=True)
    postal_address = Column(String, nullable=True)
    street_address = Column(String, nullable=True)
    digital_address = Column(String, nullable=True)
    title = Column(String, nullable=False, unique=True)
    
    

    # email = Column(String, nullable=False)
    # phone = Column(String, nullable=False)
    # metatitle = Column(String, nullable=True)
    # description = Column(String, nullable=True)
    # street_address = Column(String, nullable=True)
    # postal_address = Column(String, nullable=True)
    # digital_address = Column(String, nullable=True)
    # title = Column(String, nullable=False, unique=True)
    # logo_url = Column(String, nullable=False, unique=True, default='/sdds')
    # bg_image_url = Column(String, nullable=False, unique=True, default='/sdds')
    # sub_domain_id = Column(String, nullable=False, unique=True)
    # key = Column(String, nullable=False, unique=True, default=gen_hex)
    # password
    # country
    # ghana_post = Column(String)
    # city_id = Column(Integer, ForeignKey('cities.id')) 
    # users = relationship('User', uselist=True, cascade="all, delete", backref=backref("location"))
    # inventories = relationship('Inventory', uselist=True, cascade="all, delete", backref=backref("location"))
    # departments = relationship('Department', uselist=True, cascade="all, delete", backref=backref("location"))