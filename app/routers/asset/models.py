from sqlalchemy import Column, String, Float, event, DateTime, Enum, Boolean, CheckConstraint, ForeignKey, Integer
from routers.subscription.models import Subscription
from sqlalchemy.ext.hybrid import hybrid_property
from dateutil.relativedelta import relativedelta
from rds.tasks import async_remove_file
from sqlalchemy.orm import relationship
from utils import today_str, gen_code
from mixins import BaseMixin
from config import THUMBNAIL
from database import Base
import enum, datetime

class DepreciationAlgorithm(enum.Enum):
    straight_line_depreciation = 'straight_line_depreciation'
    declining_balance_depreciation = 'declining_balance_depreciation'

class Asset(BaseMixin, Base):
    '''Asset Model'''
    __tablename__ = "assets"
    __table_args__ = (
        CheckConstraint('salvage_price<=price', name='_price_salvage_price_'), # tbd
        # CheckConstraint('decommission is TRUE AND decommission_justification IS NOT NULL', name='_decommission_justification_'),
        CheckConstraint("depreciation_algorithm='declining_balance_depreciation' AND dep_factor IS NOT NULL", name='_verify_dpa_'),
    )

    make = Column(String, nullable=False)
    title = Column(String, nullable=False)
    model = Column(String, nullable=False)
    lifespan = Column(Float, nullable=False)
    dep_factor = Column(Float, nullable=True)
    metatitle = Column(String, nullable=True)
    description = Column(String, nullable=True)
    salvage_price = Column(Float, nullable=False)
    service_date = Column(DateTime, nullable=True)
    purchase_date = Column(DateTime, nullable=True)
    warranty_deadline = Column(DateTime, nullable=True)
    available = Column(Boolean, default=True, nullable=False)
    decommission_justification = Column(String, nullable=True)
    serial_number = Column(String, nullable=False, unique=True)
    decommission = Column(Boolean, default=False, nullable=False)
    price = Column(Float, CheckConstraint('price>=0'), nullable=False)
    purchase_order_number = Column(String, nullable=True, unique=True)
    code = Column(String, nullable=False, unique=True, default=gen_code)
    depreciation_algorithm = Column(Enum(DepreciationAlgorithm), nullable=True)
    
    categories = relationship("Category", secondary='asset_categories', back_populates="assets")
    catalogues = relationship("Catalogue", secondary='catalogue_assets', back_populates="assets")
    subscriptions = relationship("Subscription", back_populates="asset")
    inventory = relationship("Inventory", back_populates="assets")
    sold_by = relationship("Vendor", back_populates="assets_sold")
    currency = relationship("Currency")
    author = relationship("User")

    inventory_id = Column(Integer, ForeignKey('inventories.id'), nullable=False)
    currency_id = Column(Integer, ForeignKey('currencies.id'), nullable=False)
    vendor_id = Column(Integer, ForeignKey('vendors.id'))
    author_id = Column(Integer, ForeignKey('users.id'))

    @hybrid_property
    def depreciation(self):
        amount, percentage=0, 0
        years = relativedelta(datetime.datetime.utcnow(), self.created).years
        if years >= self.lifespan:
            return {'percentage':(self.price-self.salvage_price)/self.price, 'amount':self.salvage_price}   
        if self.depreciation_algorithm == DepreciationAlgorithm.declining_balance_depreciation:
            bal = self.price
            annual_dep_rate = 1/self.lifespan
            for i in range(years):   
                annual_dep_amount = bal * annual_dep_rate * self.dep_factor
                bal -= annual_dep_amount     
            percentage = (self.price-bal)/self.price
            amount = self.price-bal
        elif self.depreciation_algorithm == DepreciationAlgorithm.straight_line_depreciation:
            percentage = years * (((self.price-self.salvage_price)/self.lifespan)/self.price)
            amount = years * ((self.price-self.salvage_price)/self.lifespan) 
        return {'percentage':percentage, 'amount':amount}

    def formatted_price(self):
        return self.currency.format_currency(self.price)

    def formatted_salvage_price(self):
        return self.currency.format_currency(self.salvage_price)

@event.listens_for(Asset, 'after_delete')
def remove_file(mapper, connection, target):
    if target.url:async_remove_file(target.url) 
    from routers.upload.models import Upload
    with connection.begin():
        connection.execute(Upload.__table__.delete().where(Upload.object==target))

@event.listens_for(Asset.service_date, 'set', propagate=True)
@event.listens_for(Asset.purchase_date, 'set', propagate=True)
@event.listens_for(Asset.warranty_deadline, 'set', propagate=True)
def set_up_notification(target, value, oldvalue, initiator):
    # servicing, warranty
    # if value > today: schedule join and add activity
    pass

# def validate_phone(target, value, oldvalue, initiator):
#     "Strip non-numeric characters from a phone number"
#     return re.sub(r'\D', '', value)
# event.listen(UserContact.phone, 'set', validate_phone, retval=True)
