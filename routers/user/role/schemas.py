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

class AddOrRemovePermission(BaseModel):
    permissions: List[int]
    operation:Operation
    
class UpdateRole(BaseModel):
    title: Optional[str]
    status: Optional[bool]
    description: Optional[str]

    permissions:Optional[AddOrRemovePermission]
    # in_perm: Optional[List[int]]
    # ex_perm: Optional[List[int]]
    
class Role(RoleBase):
    id: int
    created: datetime.datetime
    updated: datetime.datetime

class RoleList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[Role], list]

# from pydantic import BaseModel, validator
# from utils import v_2n, sum_ls
# _v_ex_perm_ = validator('ex_perm', allow_reuse=True, each_item=True)(v_2n)
# _v_in_perm_ = validator('in_perm', allow_reuse=True, each_item=True)(v_2n)
# _s_ex_perm_ = validator('ex_perm', allow_reuse=True)(sum_ls)
# _s_in_perm_ = validator('in_perm', allow_reuse=True)(sum_ls)
# _v_perm_ = validator('permissions', allow_reuse=True, each_item=True)(v_2n)
# _s_perm_ = validator('permissions', allow_reuse=True)(sum_ls)