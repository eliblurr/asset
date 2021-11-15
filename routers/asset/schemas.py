from pydantic import BaseModel, confloat, conint, validator, ValidationError
from utils import as_form, timestamp_to_datetime, money
from typing import Optional, List, Union
import routers.asset.models as m
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

class Validator(BaseModel):
    _service_date_ = validator('service_date', allow_reuse=True, check_fields=False)(timestamp_to_datetime)
    _purchase_date_ = validator('purchase_date', allow_reuse=True, check_fields=False)(timestamp_to_datetime)
    _warranty_deadline_ = validator('warranty_deadline', allow_reuse=True, check_fields=False)(timestamp_to_datetime)

    @validator('salvage_price', check_fields=False)
    def _check_price_(cls, v, values):
        if v<=values['price']:
            raise ValueError('salvage_price must be lower than price')
        return v
   
    @validator('decommission_justification', check_fields=False)
    def _check_decommission_(cls, v, values):
        if v == None and values['decommission']:
            raise ValueError('decommission_justification required for decommission')
        return v

    @validator('numerable', check_fields=False)
    def _check_numerable_(cls, v, values):
        if v and not values['quantity']:
            raise ValueError('quantity required for numerable')
        return v

    @validator('department_id', check_fields=False)
    def _check_inv_dep_(cls, v, values):
        if v == None and values['inventory_id'] == None:
            raise ValueError('either department_id or inventory_id is required')
        if values['inventory_id']:
            return None
        return v
    
    @validator('depreciation_algorithm', check_fields=False)
    def _check_d_a_(cls, v, values):
        if v==DepreciationAlgorithm.dbp and not values['dep_factor']:
            raise ValueError('declining balance depreciation requires dep_factor')
        return v

class AssetBase(BaseModel):
    make:str
    title: str
    model: str
    consumable:bool
    serial_number:str
    code:Optional[str]
    price:confloat(ge=0)
    author_id:conint(gt=0)
    lifespan:confloat(gt=0)
    metatitle: Optional[str]
    description: Optional[str]
    decommission:Optional[bool]
    salvage_price:confloat(ge=0)
    available:Optional[bool]=True
    service_date:int
    quantity:Optional[conint(ge=0)]
    purchase_date:int
    vendor_id:Optional[conint(gt=0)]
    inventory_id:Optional[conint(gt=0)]
    dep_factor:Optional[confloat(gt=0)]
    department_id:Optional[conint(gt=0)]
    decommission_justification:Optional[str]
    warranty_deadline:Optional[int] 
    depreciation_algorithm:Optional[DepreciationAlgorithm]
    numerable:bool
    
    class Config:
        orm_mode = True

    class Meta:
        model = m.Asset

@as_form  
class CreateAsset(Validator, AssetBase):
    category_ids:List[int]
    currency: m.CurrencyChoice
    
class UpdateAsset(Validator, BaseModel):
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
    currency:Optional[m.CurrencyChoice]
    service_date:Optional[int]
    decommission_justification:Optional[str]
    purchase_date:Optional[int]
    warranty_deadline:Optional[int]
    depreciation_algorithm:Optional[DepreciationAlgorithm]
    category_ids:List[int]

class Asset(AssetBase):
    id: int
    images: List[Upload] = []
    created: datetime.datetime
    updated: datetime.datetime
    documents: List[Upload] = []
    depreciation: Optional[dict]
    price:Union[confloat(ge=0), str]
    salvage_price:Union[confloat(ge=0), str]

    @validator('price', allow_reuse=True, check_fields=False)
    def format_price(cls, v, values):
        return money(v, values["currency"])

    @validator('price', allow_reuse=True, check_fields=False)
    def format_price(cls, v, values):
        return money(v, values["currency"])

class AssetList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[Asset], list]

ASSET_HEADER = list(CreateAsset.__fields__.keys())