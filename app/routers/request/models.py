from sqlalchemy import Column, DateTime, Integer, Enum, CheckConstraint, ForeignKey, event, String, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from routers.asset.models import Asset
from mixins import BaseMixin
from database import Base
import enum

class RequestStatus(enum.Enum):
    active = 'active'
    expired = 'expired'
    declined = 'declined'
    accepted = 'accepted'

class ConsumableTransferAction(enum.Enum):
    ready = 'ready'
    picked = 'picked'

class AssetTransferAction(enum.Enum):
    returned = 'returned'
    picked = 'picked'
    ready = 'ready'
    
def inventory_id(context):
    with context.connection.begin() as conn:
        id = conn.execute(select(Asset.inventory_id).where(Asset.__table__.c.id==context.get_current_parameters()["asset_id"])).scalar()
        if id:raise IntegrityError('no inventory available for asset', 'inventory_id', 'could not resolve inventory_id from asset')
        return id

class Request(BaseMixin, Base):
    '''Request Model'''
    __tablename__ = "requests"
    __table_args__ = (CheckConstraint('COALESCE(department_id, inventory_id) IS NOT NULL', name='_target_handlers_'),) 

    status = Column(Enum(RequestStatus), default=RequestStatus.active, nullable=False) 
    justication = Column(String, nullable=True)

    inventory_id = Column(Integer, ForeignKey("inventories.id"), nullable=True, default=inventory_id)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    priority_id = Column(Integer, ForeignKey('priorities.id'), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    departments = relationship("Department", back_populates="requests")
    inventory = relationship("Inventory", back_populates="requests")
    author = relationship("User", back_populates="requests")
    consumables = relationship("ConsumableRequest")
    assets = relationship("AssetRequest")
    priority = relationship("Priority")

class AssetRequest(BaseMixin, Base):
    '''Asset Request Model'''
    __tablename__ = "asset_requests"
    
    asset_id = Column(Integer, ForeignKey('assets.id'), primary_key=True)
    request_id = Column(Integer, ForeignKey('requests.id'), primary_key=True)
    catalogue_id = Column(Integer, ForeignKey('catalogues.id'))
    pickup_deadline = Column(DateTime, nullable=True)
    returned_at = Column(DateTime, nullable=True)
    start_date = Column(DateTime, nullable=False)
    picked_at = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    action = Column(Enum(AssetTransferAction)) 
    id=None

class ConsumableRequest(BaseMixin, Base):
    '''Consumable Request Model'''
    __tablename__ = "consumable_requests"

    consumable_id = Column(Integer, ForeignKey('consumables.id'), primary_key=True)
    request_id = Column(Integer, ForeignKey('requests.id'), primary_key=True)
    pickup_deadline = Column(DateTime, nullable=True)
    action = Column(Enum(ConsumableTransferAction)) 
    start_date = Column(DateTime, nullable=False)
    picked_at = Column(DateTime, nullable=True)
    quantity = Column(Integer, nullable=False)
    id=None

# use set for date fields for scheduling

@event.listens_for(Request, 'before_insert') 
@event.listens_for(Request, 'before_update') 
def one_active_request_per_user_per_asset(mapper, connection, target):
    with connection.begin():
        pass
    # res = connection.execute(
#         Request.__table__.select().where(
#             Request.__table__.c.asset_id==target.asset_id, Request.__table__.c.author_id==target.author_id, Request.__table__.c.status==RequestStatus.active, 
        # )
#     ).rowcount
#     if res: raise IntegrityError('Author already has an active request for given Asset...', '[asset_id, author_id, status]', 'IntegrityError')

# # transfer actions
# class Action(enum.Enum):
#     ready = 'ready'
#     picked = 'picked'
#     created = 'created'
#     returned = 'returned'
#     accepted = 'accepted'
#     declined = 'declined'
#     completed = 'completed'