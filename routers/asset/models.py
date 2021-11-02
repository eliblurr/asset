from sqlalchemy import Column, String, Integer, CheckConstraint, Boolean, Float
from sqlalchemy.ext.hybrid import hybrid_property
from dateutil.relativedelta import relativedelta
from mixins import BaseMixin
from database import Base
from passlib import pwd
import enum, datetime

class DepreciationAlgorithm(enum.Enum):
    straight_line_depreciation = 'straight_line_depreciation'
    declining_balance_depreciation = 'declining_balance_depreciation'

class Asset(BaseMixin, Base):
    '''Asset Model'''
    __tablename__ = "assets"
    __table_args__ = (
        CheckConstraint('salvage_price<=price', name='_price_salvage_price_'),
        CheckConstraint('decommission id TRUE AND decommission_justification IS NOT NULL'),
        CheckConstraint('numerable is TRUE AND quantity IS NOT NULL', name='_quantity_numerable_'),
        CheckConstraint('depreciation_algorithm="declining_balance_depreciation" AND dep_factor IS NOT NULL'),
    )

    make = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    title = Column(String, nullable=False)
    model = Column(String, nullable=False)
    dep_factor = Column(Float, nullable=True)
    quantity = Column(Integer, nullable=True)
    metatitle = Column(String, nullable=True)
    lifespan = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    numerable = Column(Boolean, nullable=False)
    consumable = Column(Boolean, nullable=False)
    salvage_price = Column(Float, nullable=False)
    service_date = Column(DateTime, nullable=False)
    purchase_date = Column(DateTime, nullable=False)
    warranty_deadline = Column(DateTime, nullable=True)
    available = Column(Boolean, default=True, nullable=False)
    decommission_justification = Column(String, nullable=True)
    serial_number = Column(String, nullable=False, unique=True)
    decommission = Column(Boolean, default=False, nullable=False)
    code = Column(String, nullable=False, unique=True, default=pwd.genword)
    depreciation_algorithm = Column(Enum(DepreciationAlgorithm), nullable=True)
    department = relationship("Department", back_populates="assets")
    inventory = relationship("Inventory", back_populates="assets")
    vendor = relationship("Vendor", back_populates="assets_sold")
    department_id = Column(Integer, ForeignKey('departments.id'))
    inventory_id = Column(Integer, ForeignKey('inventories.id'))
    vendor_id = Column(Integer, ForeignKey('vendors.id'))
    author_id = Column(Integer, ForeignKey('users.id'))
    author = relationship("User")

    @hybrid_property
    def depreciation(self):
        amount, percentage=0, 0
        years = relativedelta(datetime.datetime.utcnow(), self.created_at).years
        if years >= self.lifespan:
            return {'percentage':(self.amount-self.salvage_amount)/self.amount, 'amount':self.salvage_amount}

        if self.depreciation_algorithm == DepreciationAlgorithm.declining_balance_depreciation:
            bal = self.amount
            annual_dep_rate = 1/self.lifespan
            for i in range(years):   
                annual_dep_amount = bal * annual_dep_rate * self.dep_factor
                bal -= annual_dep_amount     
            percentage = (self.amount-bal)/self.amount
            amount = self.amount-bal
        elif self.depreciation_algorithm == DepreciationAlgorithm.straight_line_depreciation:
            percentage = years * (((self.amount-self.salvage_amount)/self.lifespan)/self.amount)
            amount = years * ((self.amount-self.salvage_amount)/self.lifespan)
        
        return {'percentage':percentage, 'amount':amount}


#     folder = Column(String, nullable=True)
#     images = relationship('ItemImage', backref="item", uselist=True, cascade="all, delete")
#     documents

# class ItemImage(BaseMixin, Base):
#     '''Item Images Model'''
#     __tablename__ = "item_images"

#     item_id = Column(Integer, ForeignKey('items.id'), primary_key=True)
#     small = Column(String, nullable=True)
#     detail = Column(String, nullable=True)
#     listquad = Column(String, nullable=True)
#     thumbnail = Column(String, nullable=True)