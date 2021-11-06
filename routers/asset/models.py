from sqlalchemy import Column, String, Integer, CheckConstraint, Boolean, Float, DateTime, Enum, ForeignKey, event
from clry.tasks import s3_delete_bg, _delete_path
from sqlalchemy.ext.hybrid import hybrid_property
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import relationship
from database import TenantBase
from mixins import BaseMixin
from utils import today_str
from passlib import pwd
from ctypes import File
import enum, datetime

class DepreciationAlgorithm(enum.Enum):
    straight_line_depreciation = 'straight_line_depreciation'
    declining_balance_depreciation = 'declining_balance_depreciation'

class Asset(BaseMixin, TenantBase):
    '''Asset Model'''
    __tablename__ = "assets"
    __table_args__ = (
        CheckConstraint('salvage_price<=price', name='_price_salvage_price_'),
        CheckConstraint('decommission is TRUE AND decommission_justification IS NOT NULL'),
        CheckConstraint('numerable is TRUE AND quantity IS NOT NULL', name='_quantity_numerable_'),
        CheckConstraint('COALESCE(inventory_id, department_id) IS NOT NULL', name='_at_least_inv_or_dep_'),
        CheckConstraint("depreciation_algorithm='declining_balance_depreciation' AND dep_factor IS NOT NULL", name='_verify_dpa_'),
    )

    make = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    title = Column(String, nullable=False)
    model = Column(String, nullable=False)
    dep_factor = Column(Float, nullable=True)
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
    quantity = Column(Integer, CheckConstraint('quantity>0'), nullable=True)
    depreciation_algorithm = Column(Enum(DepreciationAlgorithm), nullable=True)
    documents = relationship("AssetDocument", uselist=True, cascade="all, delete")
    images = relationship("AssetImage", uselist=True, cascade="all, delete")
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

class AssetImage(BaseMixin, TenantBase):
    '''Asset Images Model'''
    __tablename__ = "asset_images"

    url = Column(File(upload_to=f'{today_str()}/images/'))
    asset_id = Column(Integer, ForeignKey('assets.id'))

class AssetDocument(BaseMixin, TenantBase):
    __tablename__ = "asset_documents"

    url = Column(File(upload_to=f'{today_str()}/'))
    asset_id = Column(Integer, ForeignKey('assets.id'))

@event.listens_for(AssetImage, 'after_delete')
def receive_after_delete(mapper, connection, target):
    if target.url[:3]=='S3:':
        s3_delete.delay(target.url[3:])
    _delete_path(target.url[3:])

@event.listens_for(AssetDocument, 'after_delete')
def receive_after_delete(mapper, connection, target):
    if target.url[:3]=='S3:':
        s3_delete.delay(target.url[3:])
    _delete_path(target.url[3:])