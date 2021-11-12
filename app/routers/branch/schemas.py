from pydantic import BaseModel, conint, constr
from typing import Optional, List, Union
from constants import PHONE, EMAIL
import routers.branch.models as m
import datetime

class BranchBase(BaseModel):
    title: str
    metatitle: Optional[str]
    phone: constr(regex=PHONE)
    email: constr(regex=EMAIL)
    description: Optional[str]
    postal_address: Optional[str]
    digital_address: Optional[str]
    
    class Config:
        orm_mode = True

    class Meta:
        model = m.Branch
      
class CreateBranch(BranchBase):
    pass
    
class UpdateBranch(BranchBase):
    title: Optional[str]
    metatitle: Optional[str]
    description: Optional[str]
    postal_address: Optional[str]
    digital_address: Optional[str]
    phone: Optional[constr(regex=PHONE)]
    email: Optional[constr(regex=EMAIL)]
    
class Branch(BranchBase):
    id: int
    created: datetime.datetime
    updated: datetime.datetime

class BranchList(BaseModel):
    bk_size: int
    pg_size: int
    data: Union[List[Branch], list]