from sqlalchemy import Column, String, Integer, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship, backref
from database import Base, TenantBase, GlobalBase
from mixins import BaseMixin

class Category(BaseMixin, GlobalBase):
    '''Category Model'''
    __tablename__ = "categories"

    title = Column(String, nullable=False)
    metatitle = Column(String, nullable=True)
    description = Column(String, nullable=False)
    assets = relationship('Asset', secondary='category_assets', backref=backref('categories'), lazy='dynamic')
    vendors = relationship('Vendor', secondary='category_vendors', backref=backref('categories'), lazy='dynamic')

class CategoryAsset(TenantBase):
    '''Category Item Model'''
    __tablename__ = 'category_assets'

    asset_id = Column(Integer, ForeignKey('assets.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'), primary_key=True)
    
class CategoryVendor(TenantBase):
    '''Category Vendor Model'''
    __tablename__ = 'category_vendors'

    vendor_id = Column(Integer, ForeignKey('vendors.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'), primary_key=True)
    
from database import engine
GlobalBase.metadata.create_all(bind=engine)
# print(
#     dir(GlobalBase.metadata),
#     GlobalBase.metadata.tables.keys(),
#     sep='\n'
# )
# OR

# class Category(BaseMixin, TenantBase):
#     '''Category Model'''
#     __tablename__ = "categories"

#     title = Column(String, nullable=False)
#     metatitle = Column(String, nullable=True)
#     description = Column(String, nullable=False)
#     assets = relationship('Asset', secondary='category_assets', backref=backref('categories'), lazy='dynamic')
#     vendors = relationship('Vendor', secondary='category_vendors', backref=backref('categories'), lazy='dynamic')
#     tenant_key=Column(String, nullable=False, default='public')