from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from mixins import BaseMixin
from database import Base
import re

class Department(BaseMixin, Base):
    '''Department Model'''
    __tablename__ = 'departments'

    title = Column(String, nullable=False)
    assets = relationship("Asset", back_populates="department")
    branch = relationship('Branch', back_populates="departments")
    proposals = relationship('Proposal', back_populates="department")
    inventories = relationship('Inventory', back_populates="department")
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    head_of_department_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    head_of_department = relationship('User', foreign_keys="Department.head_of_department_id")
    staff = relationship('User', back_populates="department", foreign_keys="[User.department_id]")
#     requests = relationship("Request", uselist=True, backref='department', cascade=("all, delete")

# https://stackoverflow.com/questions/64807850/sqlalchemy-multiple-one-to-one-and-one-to-many-relationships