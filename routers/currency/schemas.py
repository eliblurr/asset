from pydantic import BaseModel, conint, validator
from typing import Optional, List, Union
import routers.currency.models as m
import datetime, enum

class CurrencyBase(BaseModel):
    currency: m.CurrencyChoice

    class Config:
        orm_mode=True

    class Meta:
        model = m.Currency
      
class AddCurrency(CurrencyBase):
    pass

class UpdateCurrency(BaseModel):
    status: bool
        
class Currency(CurrencyBase):
    id: int
    created: datetime.datetime
    updated: datetime.datetime

class CurrencyList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[Currency], list]