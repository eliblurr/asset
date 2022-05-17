from typing import Optional, List, Union
import routers.user.role.models as m
from pydantic import BaseModel
import datetime, enum

class Operation(enum.Enum):
    add = 'add'
    remove = 'remove'

class RoleBase(BaseModel):
    title: str
    description: Optional[str]

    class Config:
        orm_mode = True

    class Meta:
        model = m.Role
      
class CreateRole(RoleBase):
    permissions: List[int]

# class AddOrRemovePermission(BaseModel):
#     permissions: List[int]
#     operation:Operation
    
class UpdateRole(BaseModel):
    title: Optional[str]
    status: Optional[bool]
    description: Optional[str]

    # permissions:Optional[AddOrRemovePermission]
    
class Role(RoleBase):
    id: int
    created: datetime.datetime
    updated: datetime.datetime

class RoleList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[Role], list]

class RoleWithPerm(Role):
    permissions: list = []