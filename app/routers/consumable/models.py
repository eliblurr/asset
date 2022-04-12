from sqlalchemy import Column, String, Integer, CheckConstraint, Float, ForeignKey, event, select
from rds.tasks import async_send_email, async_send_message
from utils import today_str, gen_code, instance_changes
from routers.inventory.models import Inventory
from routers.user.account.models import User
from sqlalchemy.orm import relationship
from config import THUMBNAIL
from mixins import BaseMixin
from database import Base
from ctypes import File

class Consumable(BaseMixin, Base):
    '''Consumable Model'''
    __tablename__ = "consumables"
    
    metatitle = Column(String, nullable=True)
    unit_price = Column(Float, nullable=True)
    quantity = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    title = Column(String, nullable=False, unique=True)
    quantity_base_limit = Column(Integer, nullable=True) # send notification when quantity reaches here
    quantity_given_away = Column(Integer, nullable=True)
    thumbnail = Column(File(upload_to=f'{today_str()}/images/', size=THUMBNAIL), nullable=True)
    categories = relationship("Category", secondary='consumable_categories', back_populates="consumables")
    inventory_id = Column(Integer, ForeignKey('inventories.id'), nullable=False)
    inventory = relationship("Inventory", back_populates="consumables")
    currency_id = Column(Integer, ForeignKey('currencies.id'))
    currency = relationship("Currency")
    code = Column(String, nullable=False, unique=True, default=gen_code)

    def give_away(self, quantity, db):
        self.validate_quantity(quantity, db)
        self.quantity-=quantity 
        db.commit()

    def validate_quantity(self, quantity, db):
        if self.quantity < quantity:
            raise OperationNotAllowed('requested quantity greater than available quantity')

    def sub_total(self):
        price = self.unit_price * self.quantity
        if self.currency:
            return self.currency.format_currency(price)
        return price

@event.listens_for(Consumable.quantity, 'set', propagate=True)
@event.listens_for(Consumable.quantity_base_limit, 'set', propagate=True)
def restock_reminder(target, value, oldvalue, initiator):

    obj = target.quantity_base_limit if bool(initiator.parent_token==Consumable.quantity_base_limit) else target.quantity

    if target.quantity_base_limit:
        if value<=int(obj) and target.inventory:
            async_send_email({
                'subject':f'{target.title} is below base quantity',
                'template_name':'consumable-quantity.html',
                'recipients':[target.inventory.manager.email],
                'body':{'title':target.title, 'code':target.code}
            })

@event.listens_for(Consumable, "after_update")
@event.listens_for(Consumable, "after_insert")
def alert_inventory(mapper, connection, target):

    changes = instance_changes(target)
    inventory = changes.get('inventory_id', [None])

    if inventory[0]:
        stmt = select(User.push_id, Inventory.id.label('Inventory_id'), Inventory.title).join(Inventory, Inventory.manager_id==User.id).where(Inventory.id==inventory[0])
        with connection.begin():
            data = connection.execute(stmt)
            data = dict(data.mappings().first())
        push_id = data.pop('push_id', None)
        data.update({'consumable_id':target.id, 'code':target.code})
        if push_id:
            try:
                async_send_message(channel=push_id, message={'key':'consumable', 'message': "This {inventory} is now in charge of {consumable} with code: {code}", 'meta': data})
            except Exception as e: 
                pass