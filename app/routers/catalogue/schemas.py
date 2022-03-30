from typing import Optional, List, Union
from pydantic import BaseModel, Field
import routers.catalogue.models as m
import datetime

class CatalogueBase(BaseModel):
    title: str
    metatitle: Optional[str]
    description: Optional[str]
    
    class Config:
        orm_mode = True

    class Meta:
        model = m.Catalogue
      
class CreateCatalogue(CatalogueBase):
    pass
    
class UpdateCatalogue(CatalogueBase):
    title: Optional[str]
    status: Optional[bool]
    
class Catalogue(CatalogueBase):
    id: int
    created: datetime.datetime
    updated: datetime.datetime

class CatalogueList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[Catalogue], list]

class CatalogueAsset(BaseModel):
    asset_ids: List[int]
    catalogue_id: int
