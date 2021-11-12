from typing import Optional, List, Union
from pydantic import BaseModel, conint
import routers.priority.models as m
import datetime

class PriorityBase(BaseModel):
    title: str
    color_hex: str
    index: Optional[conint(gt=0)]

    class Config:
        orm_mode = True

    class Meta:
        model = m.Priority

class CreatePriority(PriorityBase):
    default: Optional[bool]

class UpdatePriority(BaseModel):
    title: Optional[str]
    default: Optional[bool]
    color_hex: Optional[str]
    index: Optional[conint(gt=0)]

class Priority(PriorityBase):
    id: int
    default: bool
    created: datetime.datetime
    updated: datetime.datetime

class PriorityList(BaseModel):
    bk_size: int
    pg_size: int
    data: Union[List[Priority], list]