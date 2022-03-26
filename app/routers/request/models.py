from sqlalchemy import Column, DateTime, Integer, Enum, CheckConstraint, ForeignKey, event, String, select, func
from routers.user.account.models import User
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from routers.asset.models import Asset
from .utils import emit_action
from mixins import BaseMixin
from utils import gen_code
from database import Base
import enum

class Tag(enum.Enum):
    consumable = 'consumable'
    asset = 'asset'

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

class Request(BaseMixin, Base):
    '''Request Model'''
    __tablename__ = "requests"
    __table_args__ = (CheckConstraint('COALESCE(department_id, inventory_id) IS NOT NULL', name='_target_handlers_'),) 

    status = Column(Enum(RequestStatus), default=RequestStatus.active, nullable=False) 
    code = Column(String, nullable=False, unique=True, default=gen_code)
    justication = Column(String, nullable=True)

    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    inventory_id = Column(Integer, ForeignKey("inventories.id"), nullable=True)
    priority_id = Column(Integer, ForeignKey('priorities.id'), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    departments = relationship("Department", back_populates="requests")
    inventory = relationship("Inventory", back_populates="requests")
    author = relationship("User", back_populates="requests")
    consumable_rq = relationship("ConsumableRequest", uselist=False)
    asset_rq = relationship("AssetRequest", uselist=False)
    priority = relationship("Priority")

    tag = Column(Enum(Tag), nullable=False)

class AssetRequest(BaseMixin, Base):
    '''Asset Request Model'''
    __tablename__ = "asset_requests"
    
    request_id = Column(Integer, ForeignKey('requests.id'), primary_key=True) #unique=True
    asset_id = Column(Integer, ForeignKey('assets.id'), primary_key=True)
    pickup_deadline = Column(DateTime, nullable=True)
    return_deadline = Column(DateTime, nullable=True)
    returned_at = Column(DateTime, nullable=True) # replace this with activity
    start_date = Column(DateTime, nullable=False)
    picked_at = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    action = Column(Enum(AssetTransferAction)) 
    asset = relationship('Asset', uselist=False)
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
    consumable = relationship('Consumable')
    returned_at=None
    id=None

@event.listens_for(Request.inventory_id, 'set', propagate=True)
def receive_set(target, value, oldvalue, initiator):
    if value != oldvalue:
        emit_action(target, 'notify', message={
            'key':'request',
        }) 

        # 'key':'request', 
        #             'id':target.id,
        #             'title':target.asset_rq.asset.title if target.asset_rq else target.consumable_rq.consumable.title, 
        #             f'{"asset" if target.asset_rq else "consumable"}_code':target.asset_rq.asset.code if target.asset_rq else target.consumable_rq.consumable.code,
        #             f'{"asset" if target.asset_rq else "consumable"}_id':target.asset_rq.asset.id if target.asset_rq else target.consumable_rq.consumable.id,
        #         }
        'notify inventory owner of request'

@event.listens_for(Request.department_id, 'set', propagate=True)
def receive_set(target, value, oldvalue, initiator):
    if value != oldvalue:
        emit_action(target, 'notify', message={
            'key':'request',
        }) 
        'notify department head of request'

@event.listens_for(Request.status, 'set', propagate=True)
def receive_set(target, value, oldvalue, initiator):    
    if value != oldvalue:
        emit_action(target, value)
        if value=='accepted':
            target.asset_rq.asset.available = False
            target.inventory_id = target.asset_rq.asset.inventory_id

'for only assets, no consumables'
@event.listens_for(Request, 'before_update', propagate=True) 
def cancel_all_other_active_request_for_obj(mapper, connection, target):
    if target.status==RequestStatus.accepted:
        if target.asset_rq:
            join = (AssetRequest, Request.asset_rq)
            filters = (
                Request.tag==target.tag,
                Request.id != target.id, Request.author_id==target.author_id, Request.status==RequestStatus.active, 
                AssetRequest.asset_id==target.asset_rq.asset_id
            )
            u_stmt = Request.__table__.update().where(*filters).values(status=RequestStatus.declined)
            s_stmt = select(User.email).join(Request).where(Request.id != target.id, Request.author_id==target.author_id, Request.status==RequestStatus.active, ).join(*join).where(*filters)
            
            connection.execute(u_stmt)
            res = connection.execute(s_stmt)

            email_list = [email[0] for email in res.all()]
            emit_action(target, 'bk_notify', email_list=email_list) # add kwargs
            'notify all reciepients of declined requests'
    
@event.listens_for(Request, 'before_insert', propagate=True) 
def one_active_request_per_user_per_asset(mapper, connection, target):
    join = (AssetRequest, Request.asset_rq) if target.asset_rq else (ConsumableRequest, Request.consumable_rq)
    stmt = select(func.count(Request.id)).join(*join).where(
        Request.author_id==target.author_id, Request.status==RequestStatus.active, 
       AssetRequest.asset_id==target.asset_rq.asset_id if target.asset_rq else ConsumableRequest.consumable_id==target.consumable_rq.consumable_id 
    )
    with connection.begin():res = connection.execute(stmt).scalar()
    if res: raise IntegrityError('IntegrityError', '[object, author, status]', 'author already has an active request for object')

@event.listens_for(AssetRequest.pickup_deadline, 'set', propagate=True)
@event.listens_for(ConsumableRequest.pickup_deadline, 'set', propagate=True)
def receive_set(target, value, oldvalue, initiator):
    if value != oldvalue:
        emit_action(target, 'schedule-job', ) # add kwargs
        'schedule notification reminder job for author'

@event.listens_for(AssetRequest.return_deadline, 'set', propagate=True)
def receive_set(target, value, oldvalue, initiator):
    if value != oldvalue:
        emit_action(target, 'schedule-job', ) # add kwargs
        'schedule notification reminder job for author'

@event.listens_for(AssetRequest.action, 'set', propagate=True)
def receive_set(target, value, oldvalue, initiator):
    if action is returned:
        target.asset.available=True