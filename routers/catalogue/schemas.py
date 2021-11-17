from routers.asset.schemas import Upload
from typing import Optional, List, Union
from pydantic import BaseModel, conint, confloat, Field
import routers.catalogue.models as m
import datetime

class Asset(BaseModel):
    id: int
    make:str
    title: str
    serial_number:str
    metatitle: Optional[str]
    images: List[Upload] = []
    description: Optional[str]
    available:Optional[bool]=True
    price:Union[confloat(ge=0), str]

    class Config:
        orm_mode = True

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
    
class UpdateCatalogue(BaseModel):
    title: Optional[str]
    status: Optional[bool]
    metatitle: Optional[str]
    description: Optional[str]
    index: Optional[conint(gt=0)]
    
class Catalogue(CatalogueBase):
    id: int
    created: datetime.datetime
    updated: datetime.datetime
    assets: Optional[Asset] = []

class CatalogueList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[Catalogue], list]

class CatalogueAsset(BaseModel):
    asset_id:int = Field(..., gt=0, alias='c_id')
    catalogue_id: int
