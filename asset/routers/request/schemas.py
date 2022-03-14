from pydantic import BaseModel, validator
from typing import Optional, List, Union
from utils import timestamp_to_datetime
import routers.request.models as m
import datetime

class AssetRequestBase(BaseModel):
    asset_id: int

    class Config:
        orm_mode = True

    class Meta:
        model = m.AssetRequest

class ConsumableRequestBase(BaseModel):
    consumable_id: int

    class Config:
        orm_mode = True

    class Meta:
        model = m.ConsumableRequest

class CreateAssetRequest(AssetRequestBase):
    end_date: Optional[int]
    start_date: int

    _normalize_start_date_ = validator('start_date', allow_reuse=True)(timestamp_to_datetime)
    _normalize_end_date_ = validator('end_date', allow_reuse=True)(timestamp_to_datetime)

class CreateConsumableRequest(ConsumableRequestBase):
    start_date: int
    quantity: int

    _normalize_start_date_ = validator('start_date', allow_reuse=True)(timestamp_to_datetime)
    
class RequestBase(BaseModel):
    justication: Optional[str]
    priority_id: int
    author_id: int # to be retrieved from request
    
    class Config:
        orm_mode = True

    class Meta:
        model = m.Request

class CreateRequestForAsset(RequestBase):
    assets: List[CreateAssetRequest]

class CreateRequestForConsumable(RequestBase):
    consumables: List[CreateConsumableRequest]

class UpdateRequestForAsset(BaseModel):pass

class UpdateRequestForConsumable(BaseModel):pass

class RequestForAsset(RequestBase):pass

class RequestForConsumable(BaseModel):pass

class RequestList(BaseModel):
    bk_size: int
    pg_size: int
    data: Union[List[RequestForConsumable], List[RequestForAsset], list]