from sqlalchemy import Column, String, Integer, ForeignKey, event, func, select
from sqlalchemy.orm import relationship
from mixins import BaseMixin
from database import Base

# from routers.consumable.models import Consumable

class CategoryVendor(Base):
    '''Category Vendor Model'''
    __tablename__ = 'vendor_categories'

    vendor_id = Column(Integer, ForeignKey('vendors.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('public.categories.id'), primary_key=True) # public.categories.id

class CategoryConsumable(Base):
    '''Category Consumable Model'''
    __tablename__ = 'consumable_categories'
    
    consumable_id = Column(Integer, ForeignKey('consumables.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('public.categories.id'), primary_key=True) # public.categories.id

class CategoryAsset(Base):
    '''Category Vendor Model'''
    __tablename__ = 'asset_categories'

    asset_id = Column(Integer, ForeignKey('assets.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('public.categories.id'), primary_key=True) # public.categories.id

class Category(BaseMixin, Base):
    '''Category Model'''
    __tablename__ = "categories"
    __table_args__ = ({'schema':'public'},)

    title = Column(String, nullable=False)
    scheme = Column(String, nullable=True)
    metatitle = Column(String, nullable=True)
    description = Column(String, nullable=False)
    
    vendors = relationship("Vendor", secondary=CategoryVendor.__table__, back_populates="categories")
    consumables = relationship("Consumable", secondary=CategoryConsumable.__table__, back_populates="categories")
    assets = relationship("Asset", secondary=CategoryAsset.__table__, back_populates="categories")

@event.listens_for(Category, 'before_insert')
@event.listens_for(Category, 'before_update')
def check_integrity(mapper, connection, target):
    with connection.begin():
        table = Category.__table__
        res = connection.execute(select(func.count()).select_from(table).where(func.lower(table.c.title)==target.title.lower(), or_(table.c.scheme==target.scheme, table.c.scheme==None))).scalar()
        connection.execute(table.update().where(func.lower(table.c.title)==target.title.lower(), table.c.scheme!=None), {"status": False})
        if target.id:
            res = connection.execute(select(func.count()).select_from(table).where(func.lower(table.c.title)==target.title.lower(), or_(table.c.scheme==target.scheme, table.c.scheme==None), table.c.id!=target.id)).scalar()
        if res:raise IntegrityError('Unacceptable Operation', 'title', 'title and scheme must be unique together')