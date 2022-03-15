from typing import Optional, List, Union, Callable
from pydantic import BaseModel, conint, validator
import routers.consumable.models as m
from utils import as_form
import datetime

class ConsumableBase(BaseModel):
    title: str
    inventory_id: int
    quantity: conint(gt=0)
    metatitle: Optional[str]
    description: Optional[str]
    unit_price: Optional[float]

    class Config:
        orm_mode = True

    class Meta:
        model = m.Consumable

@as_form   
class CreateConsumable(ConsumableBase):
    pass
    
class UpdateConsumable(ConsumableBase):
    title: Optional[str]
    inventory_id: Optional[int]
    quantity: Optional[conint(gt=0)]
    status: Optional[bool]
   
class Consumable(ConsumableBase):
    id: int
    thumbnail: Optional[str]
    created: datetime.datetime
    updated: datetime.datetime
    # sub_total: Callable[str, None]

    # @validator('sub_total')
    # def total(cls, v):
    #     return v()
    
class ConsumableList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[Consumable], list]