from pydantic import BaseModel, validator
from typing import Optional, List, Union
import routers.user.role.models as m
from utils import v_2n, sum_ls
import datetime

class RoleBase(BaseModel):
    title: str
    description: Optional[str]

    class Config:
        orm_mode = True

    class Meta:
        model = m.Role
      
class CreateRole(RoleBase):
    permissions: List[int]
    _v_perm_ = validator('permissions', allow_reuse=True, each_item=True)(v_2n)
    _s_perm_ = validator('permissions', allow_reuse=True)(sum_ls)
    
class UpdateRole(BaseModel):
    title: Optional[str]
    status: Optional[bool]
    description: Optional[str]
    in_perm: Optional[List[int]]
    ex_perm: Optional[List[int]]
    _v_ex_perm_ = validator('ex_perm', allow_reuse=True, each_item=True)(v_2n)
    _v_in_perm_ = validator('in_perm', allow_reuse=True, each_item=True)(v_2n)
    _s_ex_perm_ = validator('ex_perm', allow_reuse=True)(sum_ls)
    _s_in_perm_ = validator('in_perm', allow_reuse=True)(sum_ls)

class Role(RoleBase):
    id: int
    created: datetime.datetime
    updated: datetime.datetime

class RoleList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[Role], list]