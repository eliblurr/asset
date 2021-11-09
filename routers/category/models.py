from sqlalchemy import Column, String, Integer, CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from database import Base, TenantBase, GlobalBase
from mixins import BaseMixin

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
    __table_args__ = ({'schema':'public'},)
    # __table_args__=(UniqueConstraint('title', 'tenant_key', name='uix_tnt_key'),)

    title = Column(String, nullable=False)
    metatitle = Column(String, nullable=True)
    tenant_key = Column(String, nullable=True)
    description = Column(String, nullable=False)
    vendors = relationship("Vendor", secondary=CategoryVendor.__table__, back_populates="categories")
    assets = relationship("Asset", secondary=CategoryAsset.__table__, back_populates="categories")