from sqlalchemy import Column, String, Integer, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship, backref
from database import Base, TenantBase, GlobalBase
from mixins import BaseMixin
from routers.vendor.models import Vendor

class CategoryAsset(TenantBase):
    '''Category Item Model'''
    __tablename__ = 'category_assets'

    asset_id = Column(Integer, ForeignKey('assets.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('%s.categories.id'%Base.metadata.schema), primary_key=True)
    
class CategoryVendor(TenantBase):
    '''Category Vendor Model'''
    __tablename__ = 'category_vendors'

    vendor_id = Column(Integer, ForeignKey('vendors.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('%s.categories.id'%Base.metadata.schema), primary_key=True)

from routers.asset.models import Asset

class Category(BaseMixin, Base):
    '''Category Model'''
    __tablename__ = "categories"

    title = Column(String, nullable=False)
    metatitle = Column(String, nullable=True)
    tenant_key = Column(String, nullable=True)
    description = Column(String, nullable=False)
    vendors = relationship(Vendor)
    # boston_addresses = relationship("Address",
    #                 primaryjoin="and_(User.id==Address.user_id, "
    #                     "Address.city=='Boston')")
    # , back_populates="categories"
    # , secondary=CategoryVendor.__table__
    # assets = relationship("Asset", secondary=CategoryAsset.__table__, backref=backref('categories'), lazy='dynamic')
    # vendors = relationship("Vendor", secondary=CategoryVendor.__table__, backref=backref('categories'), lazy='dynamic')

# print(
#     Base.metadata.tables.keys()
# )

from database import engine
from sqlalchemy import Table

# from routers.asset.models import Asset
# association = Table('association', Base.metadata,
#     Column('left_id', ForeignKey('left.id')),
#     Column('right_id', ForeignKey('right.id'))
# )

# print(dir(GlobalBase.metadata), print(Base.metadata.schema))
# original_metadatum.tables.values()

Base.metadata.create_all(bind=engine)
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