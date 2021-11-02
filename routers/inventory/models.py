from sqlalchemy import Column, String, Integer, CheckConstraint
from database import TenantBase
from mixins import BaseMixin

class Inventory(BaseMixin, TenantBase):
    '''Inventory Model'''
    __tablename__ = "inventories"
    __table_args__ = (CheckConstraint('coalesce(department_id , branch_id) is not null', name='_department_or_branch_'),)
    
    manager = relationship("User")
    title = Column(String, nullable=False)
    metatitle = Column(String, nullable=True)
    description = Column(String, nullable=True)
    department_id = Column(Integer, ForeignKey('departments.id'))
    manager_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    department = relationship("Department", back_populates="inventories")
    proposals = relationship("Proposal", back_populates="inventory")
    branch = relationship("Branch", back_populates="inventories")
    assets = relationship("Asset", back_populates="inventory")
    branch_id = Column(Integer, ForeignKey('branches.id'))
    # requests

#     requests = relationship("Request", uselist=True, backref='inventory')
#     items = relationship('Item', backref='inventory', uselist=True, lazy='dynamic')