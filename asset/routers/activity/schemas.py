import datetime, json, routers.activity.models as m
from pydantic import BaseModel, validator
from typing import Union, List

class ActivityBase(BaseModel):
    meta: dict
    message: str

    class Config:
        orm_mode=True

    class Meta:
        model = m.Activity
    
class Activity(ActivityBase):
    id: int
    created: datetime.datetime

class ActivityList(BaseModel):
    bk_size: int
    pg_size: int
    data: Union[List[Activity], list]