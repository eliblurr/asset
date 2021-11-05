from sqlalchemy import Column, String, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship
from database import TenantBase
from mixins import BaseMixin
import enum

class RequestStatus(enum.Enum):
    active = 'active'
    expired = 'expired'
    inactive = 'inactive'

class TransferAction(enum.Enum):
    ready = 'ready'
    picked = 'picked'
    created = 'created'
    returned = 'returned'
    accepted = 'accepted'
    declined = 'declined'
    completed = 'completed'

class Flag(enum.Enum):
    pass

class Request(BaseMixin, TenantBase):
    '''Request Model'''
    __tablename__ = 'requests'

    # end_date = Column(DateTime, nullable=True)
    # start_date = Column(DateTime, nullable=False)
    pickup_date = Column(DateTime, nullable=True)
    return_date = Column(DateTime, nullable=True)

   