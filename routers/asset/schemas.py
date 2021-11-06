from typing import Optional, List, Union
from pydantic import BaseModel, confloat, conint
import routers.asset.models as m
from utils import as_form
import datetime, enum

class DepreciationAlgorithm(str, enum.Enum):
    sld = 'straight_line_depreciation'
    dbp = 'declining_balance_depreciation'

class Upload(BaseModel):
    id:int
    url: str
    created: datetime.datetime
    updated: datetime.datetime

    class Config:
        orm_mode = True

class AssetBase(BaseModel):
    make:str
    price:confloat(ge=0)
    title: str
    model: str
    description: Optional[str]
    metatitle: Optional[str]
    lifespan:confloat(gt=0)
    dep_factor:Optional[confloat(gt=0)]
    numerable:bool
    consumable:bool
    salvage_price:confloat(ge=0)
    service_date:datetime.datetime
    purchase_date:datetime.datetime
    warranty_deadline:Optional[datetime.datetime]
    available:Optional[bool]=True
    decommission_justification:Optional[str]
    serial_number:str
    decommission:Optional[bool]
    code:Optional[str]
    quantity:Optional[conint(ge=0)]
    depreciation_algorithm:Optional[DepreciationAlgorithm]
    department_id:Optional[conint(gt=0)]
    inventory_id:Optional[conint(gt=0)]
    vendor_id:Optional[conint(gt=0)]
    author_id:conint(gt=0)

    class Config:
        orm_mode = True

    class Meta:
        model = m.Asset

@as_form  
class CreateAsset(AssetBase):
    pass

    # validations here
    
class UpdateAsset(BaseModel):
    make:Optional[str]
    code:Optional[str]
    title: Optional[str]
    metatitle: Optional[str]
    numerable:Optional[bool]
    consumable:Optional[bool]
    description: Optional[str]
    serial_number:Optional[str]
    decommission:Optional[bool]
    available:Optional[bool]=True
    price:Optional[confloat(ge=0)]
    quantity:Optional[conint(ge=0)]
    vendor_id:Optional[conint(gt=0)]
    author_id:Optional[conint(gt=0)]
    lifespan:Optional[confloat(gt=0)]
    dep_factor:Optional[confloat(gt=0)]
    inventory_id:Optional[conint(gt=0)]
    department_id:Optional[conint(gt=0)]
    salvage_price:Optional[confloat(ge=0)]
    service_date:Optional[datetime.datetime]
    decommission_justification:Optional[str]
    purchase_date:Optional[datetime.datetime]
    warranty_deadline:Optional[datetime.datetime]
    depreciation_algorithm:Optional[DepreciationAlgorithm]

    # validations here
    
class Asset(AssetBase):
    id: int
    images: List[Upload] = []
    created: datetime.datetime
    updated: datetime.datetime
    documents: List[Upload] = []
    depreciation: Optional[dict]

class AssetList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[Asset], list]

ASSET_HEADER = list(CreateAsset.__fields__.keys())