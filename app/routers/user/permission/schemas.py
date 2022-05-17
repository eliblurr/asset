from pydantic import BaseModel
from typing import Optional, List, Union
import routers.user.permission.models as m
import datetime

class ContentTypeBase(BaseModel):
    id: int
    model: str

    class Config:
        orm_mode = True

    class Meta:
        model = m.ContentType

class PermissionBase(BaseModel):
    name: str
    description: Optional[str]

    class Config:
        orm_mode = True

    class Meta:
        model = m.Permission
      
class CreatePermission(PermissionBase):
    name: Optional[str]
    content_type_id:Optional[int]
    
class Permission(PermissionBase):
    id: int
    created: datetime.datetime
    updated: datetime.datetime
    content_type: Optional[ContentTypeBase]

class PermissionList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[Permission], list]

class PermissionSummary(BaseModel):
    id: int
    name: str
    code_name: str

    class Config:
        orm_mode = True

    class Meta:
        model = m.Permission

class PermissionSummaryList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[PermissionSummary], list]

class ContentType(ContentTypeBase):
    permissions: Optional[List[PermissionSummary]]

class ContentTypeList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[ContentType], list]

class PermissionSummaryWithHasPerm(PermissionSummary):
    pass

class ContentTypeWithHasPerm(ContentTypeBase):
    permissions: Optional[List[PermissionSummaryWithHasPerm]]

class ContentTypeWithHasPermList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[ContentTypeWithHasPerm], list]