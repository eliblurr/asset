from typing import Optional, List, Union
from pydantic import BaseModel, constr
import routers.department.models as m
from constants import EMAIL, PHONE
import datetime, enum

class DResource(str, enum.Enum):
    staff='staff'
    assets='assets'
    requests='requests'
    proposals='proposals'
    inventories='inventories'

class HOD(BaseModel):
    last_name: Optional[str]
    first_name: Optional[str]
    middle_name: Optional[str]
    email: constr(regex=EMAIL)
    phone: Optional[constr(regex=PHONE)]
   
    class Config:
        orm_mode = True

class DepartmentBase(BaseModel):
    title: str

    class Config:
        orm_mode = True

    class Meta:
        model = m.Department
      
class CreateDepartment(DepartmentBase):
    branch_id: int
    head_of_department_id: int
    
class UpdateDepartment(BaseModel):
    title: Optional[str]
    status: Optional[bool]
    branch_id: Optional[int]
    head_of_department_id: Optional[int]
    
class Department(DepartmentBase):
    id: int
    head_of_department: HOD
    created: datetime.datetime
    updated: datetime.datetime
    
class DepartmentList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[Department], list]