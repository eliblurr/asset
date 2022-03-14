from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from mixins import BaseMixin
from database import Base

class Inventory(BaseMixin, Base):
    '''Inventory Model'''
    __tablename__ = "inventories"
    
    manager = relationship("User")
    metatitle = Column(String, nullable=True)
    description = Column(String, nullable=True)
    title = Column(String, nullable=False, unique=True)
    manager_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    department = relationship("Department", back_populates="inventories")
    proposals = relationship("Proposal", back_populates="inventory")
    requests = relationship("Request", back_populates="inventory")
    department_id = Column(Integer, ForeignKey('departments.id'))
    assets = relationship("Asset", back_populates="inventory")
