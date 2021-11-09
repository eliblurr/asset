from typing import Optional, List, Union
import routers.category.models as m
from pydantic import BaseModel
import datetime

class CategoryBase(BaseModel):
    title: str
    metatitle: Optional[str]
    tenant_key: Optional[str]
    description: Optional[str]
    
    class Config:
        orm_mode = True

    class Meta:
        model = m.Category
      
class CreateCategory(CategoryBase):
    pass
    
class UpdateCategory(BaseModel):
    title: Optional[str]
    metatitle: Optional[str]
    tenant_key: Optional[str]
    description: Optional[str]
    
class Category(CategoryBase):
    id: int
    created: datetime.datetime
    updated: datetime.datetime

class CategoryList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[Category], list]