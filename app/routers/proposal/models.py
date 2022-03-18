from sqlalchemy import Column, String, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship
from mixins import BaseMixin
from database import Base
import  enum

class ProposalStatus(enum.Enum):
    active = 'active'
    accepted = 'accepted'
    declined = 'declined'
    delivered = 'delivered' # procured = 'procured' change delivered to procured

class Proposal(BaseMixin, Base):
    '''Proposal Model'''
    __tablename__ = "proposals"

    title = Column(String, nullable=False)
    metatitle = Column(String, nullable=True)
    description = Column(String, nullable=True)
    justification = Column(String, nullable=False)
    status = Column(Enum(ProposalStatus), default=ProposalStatus.active, nullable=False)
    
    priority = relationship("Priority")
    priority_id = Column(Integer, ForeignKey('priorities.id'), nullable=False)

    author = relationship("User", back_populates="proposals")
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    inventory = relationship("Inventory", back_populates="proposals")
    inventory_id = Column(Integer, ForeignKey('inventories.id'), nullable=True)

    department = relationship("Department", back_populates="proposals")
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=False)
