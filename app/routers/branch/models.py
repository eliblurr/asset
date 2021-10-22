from routers.department.models import Department
from sqlalchemy.orm import relationship
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
    departments = relationship('Department', back_populates="branch", uselist=True, cascade="all, delete", lazy='dynamic')
    # users = relationship('User', back_populates="branch", uselist=True, cascade="all, delete", lazy='dynamic')
    # inventories = relationship('Inventory', back_populates="branch", uselist=True, cascade="all, delete", lazy='dynamic')