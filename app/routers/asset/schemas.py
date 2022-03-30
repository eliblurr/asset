from pydantic import BaseModel, ValidationError, validator
from typing import Optional, List, Union, Callable
import datetime, routers.asset.models as m
from utils import timestamp_to_datetime
from fastapi import HTTPException

class Validator(BaseModel):
    _service_date_ = validator('service_date', allow_reuse=True, check_fields=False)(timestamp_to_datetime)
    _purchase_date_ = validator('purchase_date', allow_reuse=True, check_fields=False)(timestamp_to_datetime)
    _warranty_deadline_ = validator('warranty_deadline', allow_reuse=True, check_fields=False)(timestamp_to_datetime)

    @validator('salvage_price', check_fields=False)
    def _check_price_(cls, v, values):
        if v>=values['price']:           
            raise ValueError('salvage_price must be lower than price')
        return v
   
    @validator('decommission_justification', check_fields=False)
    def _check_decommission_(cls, v, values):
        if v==None and values['decommission']:
            raise ValueError('decommission_justification required for decommission')
        return v
    
    @validator('depreciation_algorithm', check_fields=False)
    def _check_d_a_(cls, v, values):
        bool(values['dep_factor'])
        print(v)
        if v==m.DepreciationAlgorithm.declining_balance_depreciation and not values['dep_factor']:
            raise ValueError('declining balance depreciation requires dep_factor')
        return v

class AssetBase(BaseModel):
    make: str
    title: str
    model: str
    price: float
    lifespan: float
    serial_number: str
    code: Optional[str]
    dep_factor: Optional[float]
    metatitle: Optional[str]
    description: Optional[str]
    salvage_price: float
    service_date: Optional[int]
    purchase_date: Optional[int]
    warranty_deadline: Optional[int]
    purchase_order_number: Optional[str]
    depreciation_algorithm:Optional[m.DepreciationAlgorithm]

    class Config:
        orm_mode=True

    class Meta:
        model=m.Asset

class CreateAsset(Validator, AssetBase):
    category_ids:List[int]=[]
    currency_id: int
    vendor_id: Optional[int]
    inventory_id: Optional[int]
    author_id: int

class UpdateAsset(Validator, AssetBase):
    make: Optional[str]
    title: Optional[str]
    model: Optional[str]
    lifespan: Optional[str]
    salvage_price: Optional[float]
    price: Optional[float]
    serial_number: Optional[str]  
    decommission: Optional[bool] 
    decommission_justification:Optional[bool]

class Asset(AssetBase):
    id: int
    created: datetime.datetime
    updated: datetime.datetime
    depreciation: Optional[dict]
    formatted_price: Callable[[str], None]
    formatted_salvage_price: Callable[[str], None]
    service_date: Optional[datetime.datetime]
    purchase_date: Optional[datetime.datetime]
    warranty_deadline: Optional[datetime.datetime]

    @validator('formatted_price')
    def format_price(cls, v):
        return v()
    
    @validator('formatted_salvage_price')
    def format_salvage_price(cls, v):
        return v()

class AssetSummary(BaseModel):
    id: int
    make: str
    title: str
    model: str
    serial_number: str
    metatitle: Optional[str]
    description: Optional[str]

    class Config:
        orm_mode = True

class AssetList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[Asset], list]

ASSET_HEADER = list(CreateAsset.__fields__.keys())