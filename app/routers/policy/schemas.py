from typing import Optional, List, Union
from pydantic import BaseModel, conint
import routers.policy.models as m
import datetime

class PolicyBase(BaseModel):
    title: str
    description: str
    index: conint(gt=0)
    status: Optional[bool]
    metatitle: Optional[str]

    class Config:
        orm_mode = True

    class Meta:
        model = m.Policy
    
class CreatePolicy(PolicyBase):
    pass
    
class UpdatePolicy(BaseModel):
    title: Optional[str]
    status: Optional[bool]
    metatitle: Optional[str]
    description: Optional[str]
    index: Optional[conint(gt=0)]

class Policy(PolicyBase):
    id: int
    created: datetime.datetime
    updated: datetime.datetime

class PolicyList(BaseModel):
    bk_size: int
    pg_size: int
    data: Union[List[Policy], list]