from typing import Optional, List, Union
from pydantic import BaseModel, conint
import routers.asset.models as m
from utils import as_form
import datetime

class AssetBase(BaseModel):
    title: str
    description: str
    status: Optional[bool]
    metatitle: Optional[str]

    class Config:
        orm_mode = True

    class Meta:
        model = m.Asset

@as_form  
class CreateAsset(AssetBase):
    pass
    
class UpdateAsset(BaseModel):
    title: Optional[str]
    status: Optional[bool]
    metatitle: Optional[str]
    description: Optional[str]
    index: Optional[conint(gt=0)]
    
class Asset(AssetBase):
    id: int
    created: datetime.datetime
    updated: datetime.datetime

class AssetList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[Asset], list]

ASSET_HEADER = ['title', 'description']