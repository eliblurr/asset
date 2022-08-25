from sqlalchemy import Column, DateTime, Integer, Enum, CheckConstraint, ForeignKey, event, String, select, func
from rds.tasks import async_send_email, async_send_message, async_send_web_push
from sqlalchemy.exc import IntegrityError, ArgumentError
from sqlalchemy.orm import relationship, aliased
from routers.consumable.models import Consumable
from routers.department.models import Department
from routers.activity.crud import add_activity_2
from routers.inventory.models import Inventory
from routers.user.account.models import User
from .utils import emit_action, messages
from routers.asset.models import Asset
from utils import instance_changes
from scheduler import scheduler
from mixins import BaseMixin
from utils import gen_code
from database import Base
import enum, config

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
    holder_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    departments = relationship("Department", back_populates="requests")
    inventory = relationship("Inventory", back_populates="requests")
    author = relationship("User", back_populates="requests", foreign_keys="Request.author_id")
    consumable_rq = relationship("ConsumableRequest", uselist=False, back_populates='request')
    asset_rq = relationship("AssetRequest", uselist=False, back_populates='request')
    holder = relationship("User", foreign_keys="Request.holder_id") # foreign_keys="[Request.holder_id]" / foreign_keys=[holder_id]
    priority = relationship("Priority")

    # head_of_department = relationship('User', foreign_keys="Department.head_of_department_id")


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
    request = relationship('Request', back_populates='asset_rq')
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
    request = relationship('Request', back_populates='consumable_rq')
    returned_at=None
    id=None

@event.listens_for(Request, 'before_insert', propagate=True) 
def one_active_request_per_user_per_asset(mapper, connection, target):
    join = (AssetRequest, Request.asset_rq) if target.asset_rq else (ConsumableRequest, Request.consumable_rq)
    stmt = select(func.count(Request.id)).join(*join).where(
        Request.author_id==target.author_id, Request.status==RequestStatus.active, 
       AssetRequest.asset_id==target.asset_rq.asset_id if target.asset_rq else ConsumableRequest.consumable_id==target.consumable_rq.consumable_id 
    )
    with connection.begin():res = connection.execute(stmt).scalar()
    if res: raise IntegrityError('IntegrityError', '[object, author, status]', 'author already has an active request for object')

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
            
            email_list = [email['email'] for email in res.mappings().all()]

            async_send_email(mail={
                "subject":"DECLINED Request",
                "recipients":list(set(email_list)),
                "template_name":"request.html",
                "body":{'title': f'{target.asset_rq.asset.title}', 'code':target.code, 'item_code':target.asset_rq.asset.code, 'base_url':config.settings.BASE_URL, 'status':'DECLINED'},
            })

@event.listens_for(AssetRequest.action, 'set', propagate=True)
def receive_set(target, value, oldvalue, initiator):
    if value != oldvalue:
        if value=='returned':
            target.asset.available=True
            add_activity_2(Asset, 'asset.return', {'user':f'{target.request.author.first_name} {target.request.author.last_name}', 'user_id':target.request.author.id})

        if value=='picked':
            add_activity_2(Asset, 'asset.assign', {'user':f'{target.request.author.first_name} {target.request.author.last_name}', 'user_id':target.request.author.id})

        emit_action(target.request, target, value.value)

@event.listens_for(AssetRequest.return_deadline, 'set', propagate=True)
def receive_set(target, value, oldvalue, initiator):
    if value != oldvalue:
        scheduler.add_job(
            async_send_email,
            kwargs = {
                'subject':'smr-return-deadline',
                'template_name':'request-transfer-return-reminder.html',
                'recipients':[target.request.author],
                'body':{
                    'title':target.asset.title,
                    'item_code':target.asset.code,
                    'base_url': config.settings.BASE_URL,
                    'return_deadline': value
                }
            }, 
            id=f'{target.id}_ID{gen_code(10)}',
            trigger='date',
            run_date=value,
            name='smr-return-deadline'
        )

@event.listens_for(AssetRequest.pickup_deadline, 'set', propagate=True)
@event.listens_for(ConsumableRequest.pickup_deadline, 'set', propagate=True)
def receive_set(target, value, oldvalue, initiator):
    if value != oldvalue:
        scheduler.add_job(
            async_send_email,
            kwargs = {
                'subject':'Asset pick up reminder',
                'template_name':'request-transfer-pickup-reminder.html',
                'recipients':[target.request.author],
                'body':{
                    'title':target.asset.title if isinstance(target, AssetRequest) else target.consumable.title,
                    'item_code':target.asset.code if isinstance(target, AssetRequest) else target.consumable.code,
                    'base_url': config.settings.BASE_URL,
                    'pickup_deadline': value
                }
            }, 
            id=f'{target.id}_ID{gen_code(10)}',
            trigger='date',
            run_date=value,
            name='smr-pickup-deadline'
        )

@event.listens_for(Request, "after_update")
@event.listens_for(Request, "after_insert")
def update_handler(mapper, connection, target):

    hod = aliased(User)
    author = aliased(User)
    manager = aliased(User)
    
    _messages, stmt = messages(), ''
    changes = instance_changes(target)
    inventory, department, status = changes.get('inventory_id', [None]), changes.get('department_id', [None]), changes.get('status', [None])

    if isinstance(target.tag, str):
        asset_case = target.tag==Tag.asset.value
        consumable_case = target.tag==Tag.consumable.value
    else:
        asset_case = target.tag==Tag.asset
        consumable_case = target.tag==Tag.consumable

    if status[0]:

        if asset_case:
            stmt = select(Asset, manager.push_id.label('push_id')).join(Inventory, Asset.inventory_id==Inventory.id).join(manager, manager.id==Inventory.manager_id).join(AssetRequest, AssetRequest.asset_id==Asset.id).join(Request, Request.id==AssetRequest.request_id)
        
        if consumable_case:
            stmt = select(Consumable).join(ConsumableRequest, ConsumableRequest.consumable_id==Consumable.id).join(Request, Request.id==ConsumableRequest.request_id)
        
        with connection.begin():
            data = connection.execute(stmt)
            data = dict(data.mappings().first())

            if status[0].value=='accepted':
                stmt = Asset.__table__.update().where(Asset.id==data['id']).values(available=False)
                connection.execute(stmt)

            stmt = Request.__table__.update().where(Request.id==target.id).values(inventory_id=data['inventory_id'])
            connection.execute(stmt)

        push_id = data.pop('push_id', None)

        if asset_case:
            try:
                emit_action(target, Asset(**data), status[0].value, push_id=push_id)
            except Exception as e:
                raise ArgumentError('ArgumentError', f'{status[0].value}', 'something went wrong in emit_action for status. see LN220')

        if consumable_case:
            try:
                emit_action(target, Consumable(**data), status[0].value, push_id=push_id)
            except Exception as e:
                raise ArgumentError('ArgumentError', f'{status[0].value}', 'something went wrong in emit_action for status. see LN227')
    
    if department[0]:

        args = (Request.code, Request.id.label('request_id'), author.first_name, author.last_name, author.id.label('author_id'), manager.push_id) 

        if asset_case:
            stmt = select(*args, Asset.title, Asset.id.label('asset_id')).join(Request, Request.author_id==author.id).join(Department, author.department_id==Department.id).join(manager, manager.id==Department.head_of_department_id).join(AssetRequest, Request.id==AssetRequest.request_id).join(Asset, AssetRequest.asset_id==Asset.id)
        
        if consumable_case:
            stmt = select(*args, Asset.title, Consumable.id.label('consumable_id')).join(Request, Request.author_id==author.id).join(Department, author.department_id==Department.id).join(manager, manager.id==Department.head_of_department_id).join(ConsumableRequest, Request.id==ConsumableRequest.request_id).join(Consumable, ConsumableRequest.consumable_id==Consumable.id)

        with connection.begin():
            data = connection.execute(stmt)
            if data.rowcount:
                data = dict(data.mappings().first())
            else:
                data = None
        if data:
            push_id = data.pop('push_id', None)

            try:
                async_send_message(
                    channel=push_id,
                    message={
                        'key':'request',
                        'message': _messages['request']['department'],
                        'meta':data.update({'type':target.tag})
                    }
                )
            except:
                pass

    if inventory[0]:
        
        args = (Request.code, Request.id.label('request_id'), author.first_name, author.last_name, author.id.label('author_id'), manager.push_id)

        if asset_case:
            stmt = select(*args, Asset.title, Asset.id.label('asset_id')).join(Request, Request.author_id==author.id).join(AssetRequest, Request.id==AssetRequest.request_id).join(Asset, AssetRequest.asset_id==Asset.id).join(Inventory, Asset.inventory_id==Inventory.id).join(manager, manager.id==Inventory.manager_id)

        if consumable_case:
            stmt = select(*args, Consumable.title,  Consumable.id.label('consumable_id')).join(Request, Request.author_id==author.id).join(AssetRequest, Request.id==AssetRequest.request_id).join(Asset, AssetRequest.asset_id==Asset.id).join(Inventory, Asset.inventory_id==Inventory.id).join(manager, manager.id==Inventory.manager_id)

        with connection.begin():
            data = connection.execute(stmt)
            if data.rowcount:
                data = dict(data.mappings().first())
            else:
                data = None

        if data:
            push_id = data.pop('push_id', None)
            try:
                async_send_message(
                    channel=push_id,
                    message={
                        'key':'request',
                        'message': _messages['request']['inventory'],
                        'meta':data.update({'type':target.tag})
                    }
                )
            except:
                pass