from routers.priority.schemas import Priority
from pydantic import BaseModel, validator
from typing import Optional, List, Union
from utils import timestamp_to_datetime
import routers.request.models as m
import datetime, enum

class Items(str, enum.Enum):
    assets = 'assets'
    consumables = 'consumables'
    catalogues = 'catalogues'

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

    class Config:
        orm_mode = True

    class Meta:
        model = m.AssetRequest

class ConsumableRequestBase(BaseModel):
    quantity: int
    consumable_id: int
    start_date: int

    class Config:
        orm_mode = True

    class Meta:
        model = m.ConsumableRequest

class CreateAssetRequest(AssetRequestBase):
    pass

class CreateConsumableRequest(ConsumableRequestBase):
    pass

class CreateRequest(RequestBase):
    author_id: int
    priority_id: int
    obj: Union[CreateAssetRequest, CreateConsumableRequest]

class Request(RequestBase):
    updated: datetime.datetime
    start_date: datetime.datetime 
    action: m.AssetTransferAction
    end_date: Optional[datetime.datetime]
    pickup_date: Optional[datetime.datetime]
    return_date: Optional[datetime.datetime]
    created: datetime.datetime
    status: m.RequestStatus
    priority: Priority
    id: int

class AssetRequest(Request):
    assets: dict
    
class ConsumableRequest(Request):
    consumables: dict
 
class RequestList(BaseModel):
    bk_size: int
    pg_size: int
    data: Union[List[ConsumableRequest], List[AssetRequest], list]

# class CreateCatalogueRequest(BaseModel):
#     catalogue_id: int
   
# class CreateAssetRequest(AssetRequestBase):
#     asset_id: int
   
# class CreateConsumableRequest(ConsumableRequestBase):
#     consumable_id: int
#     quantity: int

#     class Config:
#         orm_mode = True

#     class Meta:
#         model = m.ConsumableRequest

# class CreateRequest(BaseModel):
#     author_id: int
#     start_date: int
#     priority_id: int
#     end_date: Optional[int]
#     obj: Union[CreateAssetRequest, CreateCatalogueRequest, CreateConsumableRequest]

#     _normalize_start_date_ = validator('start_date', allow_reuse=True)(timestamp_to_datetime)
#     _normalize_end_date_ = validator('end_date', allow_reuse=True)(timestamp_to_datetime)

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



