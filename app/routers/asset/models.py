from sqlalchemy import Column, String, Float, event, DateTime, Enum, Boolean, CheckConstraint, ForeignKey, Integer, select
from utils import today_str, gen_code, instance_changes
from routers.subscription.models import Subscription
from sqlalchemy.ext.hybrid import hybrid_property
from dateutil.relativedelta import relativedelta
from routers.user.account.models import User
from sqlalchemy.exc import IntegrityError
from rds.tasks import async_remove_file
from sqlalchemy.orm import relationship
from rds.tasks import async_send_email
from scheduler import scheduler
import enum, datetime, config
from mixins import BaseMixin
from config import THUMBNAIL
from database import Base

class DepreciationAlgorithm(enum.Enum):
    straight_line_depreciation = 'straight_line_depreciation'
    declining_balance_depreciation = 'declining_balance_depreciation'

class Asset(BaseMixin, Base):
    '''Asset Model'''
    __tablename__ = "assets"
    __table_args__ = (
        CheckConstraint('salvage_price<=price', name='_price_salvage_price_'), # tbd
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
    [scheduler.remove_job(job.id) for job in scheduler.get_jobs() if job.split('_',1)[0]==str(target.id)]

@event.listens_for(Asset.depreciation_algorithm, 'set', propagate=True)
def check_dep_factor(target, value, oldvalue, initiator):
    if value==DepreciationAlgorithm.declining_balance_depreciation and target.dep_factor is None:
        raise IntegrityError('Unacceptable Operation', '[depreciation_algorithm, dep_factor]', 'dep_factor must be set for declining balance depreciation')

@event.listens_for(Asset, "after_update")
@event.listens_for(Asset, "after_insert")
def alert_inventory(mapper, connection, target):

    changes = instance_changes(target)
    warranty_deadline, service_date, inventory_id = changes.get('warranty_deadline', [None]), changes.get('service_date', [None]), changes.get('inventory_id', [None])
    from routers.inventory.models import Inventory
    stmt = select(User.email, Inventory.title).join(Inventory).join(Asset).where(Asset.id==target.id)

    with connection.begin():
        data = connection.execute(stmt)
        data = dict(data.mappings().first())

    # print(inventory_id[0])
    # if inventory_id[0]:
    #     from routers.activity.crud import add_activity_2
    #     if hasattr(target, 'inventory'):
    #         add_activity_2(Asset, 'asset.transfer_inv', {'inventory':target.inventory.title, 'inventory_id':inventory[0]})

    if service_date[0]:
        name = 'smr-service-date' 
        subject = 'Asset Servicing Reminder'

        scheduler.add_job(
            async_send_email,
            id=f'{target.id}_ID{gen_code(10)}',
            trigger='date', 
            run_date=service_date[0], 
            name=name,
            kwargs={
                'subject':subject,
                'template_name':'service-reminder.html',
                'recipients':[data.get('email')],
                'body':{
                    'title':target.title, 
                    'code':target.code, 
                    'date':service_date[0],
                    'inventory_name':data.get('title'),
                    'base_url':config.settings.BASE_URL
                }
            }
        )

    if warranty_deadline[0]:
        name = 'smr-warranty-deadline' 
        subject = 'Warranty Deadline Reminder'

        scheduler.add_job(
            async_send_email,
            id=f'{target.id}_ID{gen_code(10)}',
            trigger='date', 
            run_date=warranty_deadline[0], 
            name=name,
            kwargs={
                'subject':subject,
                'template_name':'warranty-reminder.html',
                'recipients':[data.get('email')],
                'body':{
                    'title':target.title, 
                    'code':target.code, 
                    'date':warranty_deadline[0],
                    'inventory_name':data.get('title'),
                    'base_url':config.settings.BASE_URL
                }
            }
        )