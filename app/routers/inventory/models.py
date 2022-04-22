from sqlalchemy import Column, String, Integer, ForeignKey, event, select
from routers.user.account.models import User
from rds.tasks import async_send_message
from sqlalchemy.orm import relationship
from utils import instance_changes
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
    consumables = relationship("Consumable", back_populates="inventory")
    proposals = relationship("Proposal", back_populates="inventory")
    requests = relationship("Request", back_populates="inventory")
    department_id = Column(Integer, ForeignKey('departments.id'))
    assets = relationship("Asset", back_populates="inventory")

@event.listens_for(Inventory, "after_update")
@event.listens_for(Inventory, "after_insert")
def alert_inventory(mapper, connection, target):

    changes = instance_changes(target)
    manager_id = changes.get('manager_id', [None])   
    
    if manager_id[0]:
        stmt = select(User.push_id, User.first_name, User.last_name, Inventory.title, Inventory.updated, Inventory.id, Inventory.manager_id).join(Inventory, Inventory.manager_id==User.id).where(Inventory.id==target.id)
        with connection.begin():
            data = connection.execute(stmt)
            data = dict(data.mappings().first())

        if data:
            async_send_message(
                channel=data.get('push_id'),
                message={
                    'key':'inventory',
                    'message': "inventory assigned to {manager} on {datetime}",
                    'meta': {
                        'id':data.get('id'), 
                        'title':data.get('title'),    
                        'datetime':data.get('updated'),               
                        'manager_id':data.get('manager_id'), 
                        'manager':f'{data.get("first_name")} {data.get("last_name")}'
                    }
                }
            )