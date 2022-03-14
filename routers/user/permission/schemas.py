from pydantic import BaseModel
from typing import Optional, List, Union
import routers.user.permission.models as m
import datetime

class PermissionBase(BaseModel):
    name: str
    description: Optional[str]
    content_type: Optional[str]

    class Config:
        orm_mode = True

    class Meta:
        model = m.Permission
      
class CreatePermission(PermissionBase):
    content_type_id:Optional[int]
    
class Permission(PermissionBase):
    id: int
    created: datetime.datetime
    updated: datetime.datetime

class PermissionList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[Permission], list]