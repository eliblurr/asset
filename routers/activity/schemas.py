from pydantic import BaseModel, validator
import routers.activity.models as m
from typing import List, Union
import datetime, json

class ActivityBase(BaseModel):
    msg: str
    meta: dict

    class Config:
        orm_mode = True

    class Meta:
        model = m.Activity

    @validator('meta')
    def json_to_dict(cls, v):
        return json.loads(v)
          
class Activity(ActivityBase):
    id: int
    created: datetime.datetime
    updated: datetime.datetime

class ActivityList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[Activity], list]