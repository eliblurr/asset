from sqlalchemy import Column, String, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship
from database import TenantBase, Base
from mixins import BaseMixin
import  enum

class ProposalStatus(enum.Enum):
    active = 'active'
    accepted = 'accepted'
    declined = 'declined'
    delivered = 'delivered'

class Proposal(BaseMixin, Base):
    '''Proposal Model'''
    __tablename__ = "proposals"

    priority = relationship("Priority")
    title = Column(String, nullable=False)
    metatitle = Column(String, nullable=True)
    description = Column(String, nullable=True)
    justification = Column(String, nullable=False)
    author = relationship("User", back_populates="proposals")
    inventory = relationship("Inventory", back_populates="proposals")
    activities = relationship("Activity", order_by="Activity.created")
    department = relationship("Department", back_populates="proposals")
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    priority_id = Column(Integer, ForeignKey('priorities.id'), nullable=False)
    inventory_id = Column(Integer, ForeignKey('inventories.id'), nullable=True)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=False)
    status = Column(Enum(ProposalStatus), default=ProposalStatus.active, nullable=False)