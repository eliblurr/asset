from sqlalchemy import Column, String, Integer, CheckConstraint, Float
from sqlalchemy.orm import relationship
from config import THUMBNAIL
from mixins import BaseMixin
from utils import today_str
from database import Base
from ctypes import File

# from routers.category.models import Category

class Consumable(BaseMixin, Base):
    '''Consumable Model'''
    __tablename__ = "consumables"
    
    metatitle = Column(String, nullable=True)
    unit_price = Column(Float, nullable=True)
    quantity = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    title = Column(String, nullable=False, unique=True)
    quantity_base_limit = Column(Integer, nullable=True) #send notification when quantity reaches here
    quantity_given_away = Column(Integer, nullable=True)
    thumbnail = Column(File(upload_to=f'{today_str()}/images/', size=THUMBNAIL), nullable=True)
    categories = relationship("Category", secondary=Base.metadata.tables['consumable_categories'], back_populates="consumables")

    # quantity operation functions
    # def give_away(self, quantity, db):
    #     return get_currency_symbol(self.currency)

    # def format_currency(self, value:float):
    #     return format_currency(value, self.currency)

# 'set' event on quantity