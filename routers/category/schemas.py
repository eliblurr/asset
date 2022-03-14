from typing import Optional, List, Union
from pydantic import BaseModel, Field
import routers.category.models as m
import datetime, enum

class RelatedResource(str, enum.Enum):
    assets = 'assets'
    vendors = 'vendors'
    consumables = 'consumables'

class CategoryBase(BaseModel):
    title: str
    scheme: Optional[str]
    metatitle: Optional[str]
    description: Optional[str]
    
    class Config:
        orm_mode = True

    class Meta:
        model = m.Category
      
class CreateCategory(CategoryBase):
    pass
    
class UpdateCategory(CategoryBase):
    title: Optional[str]
    metatitle: Optional[str]
    description: Optional[str]
    
class Category(CategoryBase):
    id: int
    created: datetime.datetime
    updated: datetime.datetime

class CategoryList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[Category], list]

class CategoryVendor(BaseModel):
    category_id:int
    vendor_id:int = Field(..., gt=0, alias='c_id')

class CategoryConsumable(BaseModel):
    category_id:int
    consumable_id:int = Field(..., gt=0, alias='c_id')

class CategoryAsset(BaseModel):
    category_id:int
    asset_id:int = Field(..., gt=0, alias='c_id')