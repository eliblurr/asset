from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from mixins import BaseMixin
from database import Base

class CatalogueAsset(Base):
    '''Catalogue Asset Model'''
    __tablename__ = 'catalogue_assets'

    asset_id = Column(Integer, ForeignKey('assets.id'), primary_key=True)
    catalogue_id = Column(Integer, ForeignKey('catalogues.id'), primary_key=True)

class Catalogue(BaseMixin, Base):
    '''Catalogue Model'''
    __tablename__ = "catalogues"

    title = Column(String, nullable=False)
    metatitle = Column(String, nullable=True)
    description = Column(String, nullable=True)
    assets = relationship("Asset", secondary=CatalogueAsset.__table__, back_populates="catalogues")
