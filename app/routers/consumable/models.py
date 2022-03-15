from sqlalchemy import Column, String, Integer, CheckConstraint, Float, ForeignKey, event
from sqlalchemy.orm import relationship
from config import THUMBNAIL
from mixins import BaseMixin
from utils import today_str
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

@event.listens_for(Consumable.quantity_base_limit, 'set', propagate=True)
def set_quantity(target, value, oldvalue, initiator):
    if value <= target.quantity:
        'send notification here'
        pass

@event.listens_for(Consumable.quantity, 'set', propagate=True)
def set_quantity(target, value, oldvalue, initiator):
    if value <= target.quantity_base_limit:
        'send notification here'
        pass

@event.listens_for(Consumable.inventory_id, 'set', propagate=True)
def set_quantity(target, value, oldvalue, initiator):
    'notify inventory owner that consumable has been added to inventory'
