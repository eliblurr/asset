import routers.branch.models as m, datetime, enum
from typing import Optional, List, Union
from constants import PHONE, EMAIL, URL
from pydantic import BaseModel, constr

class BranchDepartment(BaseModel):
    branch_id:int
    department_id:int

class BranchBase(BaseModel):
    title: str
    phone:constr(regex=PHONE)
    email:constr(regex=EMAIL)
    metatitle: Optional[str]
    description: Optional[str]
    postal_address: Optional[str]
    street_address: Optional[str]
    digital_address: Optional[str]
    url: Optional[constr(regex=URL)]
    
    class Config:
        orm_mode = True

    class Meta:
        model = m.Branch

class CreateBranch(BranchBase):pass
    
class UpdateBranch(BranchBase):
    title: Optional[str]
    status: Optional[bool]
    phone: Optional[constr(regex=PHONE)]
    email: Optional[constr(regex=EMAIL)]
    
class Branch(BranchBase):
    id: int
    created: datetime.datetime
    updated: datetime.datetime

class BranchSummary(BaseModel):
    id: int
    title: str

    class Config:
        orm_mode = True
    
class BranchList(BaseModel):
    bk_size: int
    pg_size: int
    data: Union[List[Branch], list]