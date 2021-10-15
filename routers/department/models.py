from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from database import TenantBase
from mixins import BaseMixin
import re

class Department(BaseMixin, TenantBase):
    '''Department Model'''
    __tablename__ = 'departments'

    title = Column(String, nullable=False)
    branch = relationship('Branch', back_populates="departments")
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=False)