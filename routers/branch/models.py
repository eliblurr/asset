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
    staff = relationship("User", back_populates="branch")
    inventories = relationship('Inventory', back_populates="branch", cascade="all, delete", lazy='dynamic') # include join through departements
    departments = relationship('Department', back_populates="branch", cascade="all, delete", lazy='dynamic')
    # inventories = relationship('Inventory', back_populates="branch", uselist=True, cascade="all, delete", lazy='dynamic')
    # boston_addresses = relationship("Address",
    #                 primaryjoin="and_(User.id==Address.user_id, "
    #                     "Address.city=='Boston')")
    # inventories = relationship("Address", primaryjoin="and_(Branch.id==Inventory.branch_id, Department.branch_id==Branch.id)")