from pydantic import BaseModel, confloat, conint, validator, ValidationError
from utils import as_form, timestamp_to_datetime
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

class Validator:
    # _service_date_ = validator('service_date', allow_reuse=True)(timestamp_to_datetime)
    # _purchase_date_ = validator('purchase_date', allow_reuse=True)(timestamp_to_datetime)
    # _warranty_deadline_ = validator('warranty_deadline', allow_reuse=True)(timestamp_to_datetime)
    
    # CheckConstraint('salvage_price<=price', name='_price_salvage_price_'),
    # CheckConstraint('decommission is TRUE AND decommission_justification IS NOT NULL'),
    # CheckConstraint('numerable is TRUE AND quantity IS NOT NULL', name='_quantity_numerable_'),
    # CheckConstraint('COALESCE(inventory_id, department_id) IS NOT NULL', name='_at_least_inv_or_dep_'),
    # CheckConstraint("depreciation_algorithm='declining_balance_depreciation' AND dep_factor IS NOT NULL", name='_verify_dpa_'),
   
    @validator('department_id')
    def _inv_dep_(cls, v, values):
        if values['inventory_id']:
            return None
        return v
    
    @validator('numerable')
    def _num_quan_(cls, v, values):
        if v and not values['quantity']:
            raise ValueError('quantity required')
        return v

    @validator('depreciation_algorithm', allow_reuse=True)
    def _df_dal_(cls, v, values):
        if v==DepreciationAlgorithm.dbp and not values['dep_factor']:
            raise ValueError('declining balance depreciation requires dep_factor')
        return v

class AssetBase(BaseModel):
    make:str
    title: str
    model: str
    numerable:bool
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
    service_date:datetime.datetime
    quantity:Optional[conint(ge=0)]
    purchase_date:datetime.datetime
    vendor_id:Optional[conint(gt=0)]
    inventory_id:Optional[conint(gt=0)]
    dep_factor:Optional[confloat(gt=0)]
    department_id:Optional[conint(gt=0)]
    decommission_justification:Optional[str]
    warranty_deadline:Optional[datetime.datetime] 
    depreciation_algorithm:Optional[DepreciationAlgorithm]
    
    class Config:
        orm_mode = True

    class Meta:
        model = m.Asset

@as_form  
class CreateAsset(AssetBase, Validator):
    pass
    
class UpdateAsset(BaseModel, Validator):
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