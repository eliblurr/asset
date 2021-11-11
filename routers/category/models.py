from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint, event, func, CheckConstraint
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from mixins import BaseMixin
from database import Base

class CategoryVendor(Base):
    '''Category Vendor Model'''
    __tablename__ = 'vendor_categories'

    vendor_id = Column(Integer, ForeignKey('vendors.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('public.categories.id'), primary_key=True)

class CategoryAsset(Base):
    '''Category Vendor Model'''
    __tablename__ = 'asset_categories'

    asset_id = Column(Integer, ForeignKey('assets.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('public.categories.id'), primary_key=True)

class Category(BaseMixin, Base):
    '''Category Model'''
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint('title', 'tenant_key', name='uix_tnt_key'),
        {'schema':'public'},
    )

    title = Column(String, nullable=False)
    metatitle = Column(String, nullable=True)
    tenant_key = Column(String, nullable=True)
    description = Column(String, nullable=False)
    vendors = relationship("Vendor", secondary=CategoryVendor.__table__, back_populates="categories")
    assets = relationship("Asset", secondary=CategoryAsset.__table__, back_populates="categories")

@event.listens_for(Category, 'before_insert')
@event.listens_for(Category, 'before_update')
def check_integrity(mapper, connection, target):
    res = connection.execute(
        Category.__table__.select().where(func.lower(Category.__table__.c.title) == target.title.lower(), Category.__table__.c.tenant_key==None)
    ).rowcount
    if res: raise IntegrityError('Unacceptable Operation', 'title', 'IntegrityError')

# CheckConstraint(
#     '''
#         tenant_key IS NULL AND lower(title) NOT IN (SELECT lower(title) from public.categories)
#     '''
# ),