import routers.currency.models as m
from pydantic import BaseModel
from typing import List, Union
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
    status: bool
    created: datetime.datetime
    updated: datetime.datetime

class CurrencyList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[Currency], list]