from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, event, Enum
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from database import TenantBase, Base
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

class Request(BaseMixin, Base):
    '''Request Model'''
    __tablename__ = 'requests'
    __table_args__ = (
        # check constraint on item being returnable to have certain fields eg. return date 
    )

    # end_date = Column(DateTime, nullable=True)
    # start_date = Column(DateTime, nullable=False)
    pickup_date = Column(DateTime, nullable=True)
    return_date = Column(DateTime, nullable=True)

    pickup_deadline = Column(DateTime, nullable=True)

    status = Column(Enum(RequestStatus), default=RequestStatus.active, nullable=False) 
    
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    priority_id = Column(Integer, ForeignKey('priorities.id'), nullable=False)
    priority = relationship("Priority")

    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    department = relationship("Parent", back_populates="requests")

@event.listens_for(Request, 'before_insert') 
@event.listens_for(Request, 'before_update') 
def one_req_per_user_per_item(mapper, connection, target):
    res = connection.execute(
        Request.__table__.select().where(
            Request.__table__.c.asset_id==target.asset_id, Request.__table__.c.author_id==target.author_id, Request.__table__.c.status==RequestStatus.active, 
        )
    ).rowcount
    if res: raise IntegrityError('Author already has an active request for given Asset...', '[asset_id, author_id, status]', 'IntegrityError')