from routers.user.account.schemas import UserSummary
from routers.branch.schemas import BranchSummary
from typing import Optional, List, Union
from pydantic import BaseModel, constr
import routers.department.models as m
from constants import EMAIL, PHONE
import datetime, enum

class BaseDepartmentBase(BaseModel):
    title: str
    description:Optional[str]

    class Config:
        orm_mode = True

    class Meta:
        model = m.BaseDepartment

class UpdateBaseDepartment(BaseDepartmentBase):
    title: Optional[str]

class BaseDepartment(BaseModel):
    id: int

class BaseDepartmentList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[BaseDepartment], list]

class DepartmentBase(BaseModel):
    info: BaseDepartmentBase

    class Config:
        orm_mode = True

    class Meta:
        model = m.Department

class CreateDepartment(DepartmentBase):
    head_of_department_id: int

class CreateDepartment2(BaseModel):
    base_department_id: int
    branch_id: int
    head_of_department_id: int

class UpdateDepartment(BaseModel):    
    head_of_department_id: Optional[int]
    status: Optional[bool]

class Department(DepartmentBase):
    id: int
    created: datetime.datetime
    updated: datetime.datetime
    branch: Optional[BranchSummary]
    head_of_department: Optional[UserSummary]
    
class DepartmentList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[Department], list]

# class DepartmentRelatedResource(str, enum.Enum): since relations are on to many use ?parent_id=<id> to get children
#     staff='staff'
#     assets='assets'
#     requests='requests'
#     proposals='proposals'
#     inventories='inventories'