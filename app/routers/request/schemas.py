from routers.priority.schemas import Priority
from routers.asset.schemas import AssetSummary
from routers.consumable.schemas import ConsumableSummary
from pydantic import BaseModel, validator, root_validator
from typing import Optional, List, Union
from utils import timestamp_to_datetime
import routers.request.models as m
import datetime, enum

class Items(str, enum.Enum):
    consumables = 'consumables'
    catalogues = 'catalogues'
    assets = 'assets'

class RequestBase(BaseModel):
    justication: Optional[str]

    class Config:
        orm_mode = True

    class Meta:
        model = m.Request

class AssetRequestBase(BaseModel):
    asset_id: int
    start_date: int
    end_date: Optional[int]

    _normalize_start_date_ = validator('start_date', allow_reuse=True)(timestamp_to_datetime)
    _normalize_end_date_ = validator('end_date', allow_reuse=True)(timestamp_to_datetime)

    class Config:
        orm_mode = True

    class Meta:
        model = m.AssetRequest

class ConsumableRequestBase(BaseModel):
    quantity: int
    consumable_id: int
    start_date: int

    _normalize_start_date_ = validator('start_date', allow_reuse=True)(timestamp_to_datetime)

    class Config:
        orm_mode = True

    class Meta:
        model = m.ConsumableRequest

'''class CatalogueRequestBase(BaseModel):
    catalogue_id: int
    start_date: int
    end_date: Optional[int]

    _normalize_start_date_ = validator('start_date', allow_reuse=True)(timestamp_to_datetime)
    _normalize_end_date_ = validator('end_date', allow_reuse=True)(timestamp_to_datetime)

    class Config:
        orm_mode = True

    class Meta:
        model = m.CatalogueRequest'''

class CreateAssetRequest(AssetRequestBase):
    pass

class CreateConsumableRequest(ConsumableRequestBase):
    pass

'''class CreateCatalogueRequest(CatalogueRequestBase):
    pass'''

class CreateRequest(RequestBase):
    author_id: int
    priority_id: int
    obj: Union[CreateAssetRequest, CreateConsumableRequest] # CreateCatalogueRequest

    @root_validator
    def rename_obj(cls, values):
        if isinstance(values['obj'], CreateAssetRequest):
            values['asset'] = values['obj']
        elif isinstance(values['obj'], CreateConsumableRequest):
            values['consumable'] = values['obj']
        return values

class UpdateRequest(RequestBase):
    pass

class AssetRequest(BaseModel):
    asset: AssetSummary
    start_date: Optional[datetime.datetime]
    action: Optional[m.AssetTransferAction]
    end_date: Optional[datetime.datetime]
    pickup_date: Optional[datetime.datetime]
    return_date: Optional[datetime.datetime]

    class Config:
        orm_mode=True

class ConsumableRequest(BaseModel):
    consumable: ConsumableSummary
    start_date: Optional[datetime.datetime]
    pickup_deadline: Optional[datetime.datetime]
    action: Optional[m.ConsumableTransferAction]
    picked_at: Optional[datetime.datetime]
    quantity: int

    class Config:
        orm_mode=True

class Request(RequestBase):
    updated: datetime.datetime
    created: datetime.datetime
    status: m.RequestStatus
    priority: Priority
    code: str
    id: int

    asset: Optional[AssetRequest]
    consumable: Optional[ConsumableRequest]
    info: Optional[Union[AssetRequest, ConsumableRequest]]

    @root_validator
    def get_obj(cls, values):
        asset = values.pop('asset')
        consumable = values.pop('consumable')
        values['info'] = asset if asset else consumable if consumable else values['info']
        return values
 
class RequestList(BaseModel):
    bk_size: int
    pg_size: int
    data: Union[List[Request], list]



# class RequestBase(BaseModel):
#     justication: Optional[str]
#     priority_id: int
#     author_id: int # to be retrieved from request
    
#     class Config:
#         orm_mode = True

#     class Meta:
#         model = m.Request

# class CreateRequestForAsset(RequestBase):
#     assets: List[CreateAssetRequest]

# class CreateRequestForConsumable(RequestBase):
#     consumables: List[CreateConsumableRequest]

# class UpdateRequestForAsset(BaseModel):pass

# class UpdateRequestForConsumable(BaseModel):pass

# class AssetRequest(RequestBase):pass

# class ConsumableRequest(BaseModel):pass

# class RequestCatalogue(BaseModel):pass



