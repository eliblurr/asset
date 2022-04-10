from sqlalchemy import Column, String, Enum, ForeignKey, Integer, event, select
from rds.tasks import async_send_email, async_send_message
from routers.department.models import Department
from routers.inventory.models import Inventory
from routers.user.account.models import User
from sqlalchemy.orm import relationship
from utils import instance_changes
from mixins import BaseMixin
from database import Base
import enum, config

class ProposalStatus(enum.Enum):
    active = 'active'
    accepted = 'accepted'
    declined = 'declined'
    procured = 'procured'

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

    inventory = relationship("Inventory", back_populates="proposals") # inventory in charge of procurement
    inventory_id = Column(Integer, ForeignKey('inventories.id'), nullable=True)

    department = relationship("Department", back_populates="proposals")
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=False)

    procured_asset = relationship("Asset")
    procured_asset_id = Column(Integer, ForeignKey('assets.id'), nullable=True)

@event.listens_for(Proposal.status, 'set', propagate=True)
def receive_set(target, value, oldvalue, initiator):
    if value!=oldvalue and value=='procured' and target.author:
        async_send_email(mail={
            "subject":"Recommended Asset Procured",
            "recipients":[target.author.email],
            "template_name":"asset-procurement.html",
            "body":{'title': f'{target.title}', 'base_url':config.settings.BASE_URL},
        })

    if value!=oldvalue and value=='declined' and target.author:
        async_send_email(mail={
            "subject":f"Proposal For {target.title} Declined",
            "recipients":[target.author.email],
            "template_name":"proposal-declined.html",
            "body":{'title': f'{target.title}', 'base_url':config.settings.BASE_URL},
        })

@event.listens_for(Proposal, "after_update")
@event.listens_for(Proposal, "after_insert")
def propagate_status(mapper, connection, target):

    changes = instance_changes(target)
    inventory, department = changes.get('inventory_id', [None]), changes.get('department_id', [None])

    if inventory[0]:
        stmt = select(User.push_id, User.id.label('user_id'), User.first_name, User.last_name, Inventory.id.label('Inventory_id'), Inventory.title).join(Inventory, Inventory.manager_id==User.id).where(Inventory.id==inventory[0])
        with connection.begin():
            data = connection.execute(stmt)
            data = dict(data.mappings().first())
        push_id = data.pop('push_id', None)
        if push_id:async_send_message(channel=push_id, message={'key':'proposal', 'message': "proposal operations for {user} has been transfered to this {inventory}", 'meta': data})
    
    if department[0]:
        stmt = select(User.push_id, User.id.label('user_id'), User.first_name, User.last_name, Department.id).join(Department, Department.head_of_department_id==User.id).where(Department.id==1)
        with connection.begin():
            data = connection.execute(stmt)
            data = dict(data.mappings().first())
        push_id = data.pop('push_id', None)
        if push_id:async_send_message(channel=push_id, message={'key':'proposal', 'message': "{user} has made a proposal for item {title}", 'meta': data.update({'title':target.title})})

    # statu
     
# alternative
# https://stackoverflow.com/questions/27025473/cascade-updates-after-sqlalchemy-after-update-event
# https://stackoverflow.com/questions/29921260/tracking-model-changes-in-sqlalchemy