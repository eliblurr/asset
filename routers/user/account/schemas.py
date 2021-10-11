from typing import Optional, List, Union
import routers.user.account.models as m
from pydantic import BaseModel, constr
from constants import EMAIL
import datetime

class UserBase(BaseModel):
    email: constr(regex=EMAIL)
   
    class Config:
        orm_mode = True

    class Meta:
        model = m.User
      
class CreateUser(UserBase):
    password: Optional[constr(min_length=8)]
    
class UpdateUser(BaseModel):
    status: Optional[bool]
    password: Optional[constr(min_length=8)]
    
    class Meta:
        model = m.User
    
class User(UserBase):
    id: int
    created: datetime.datetime
    updated: datetime.datetime

class UserList(BaseModel):
    bk_size: int
    pg_size: int
    data: Union[List[User], list]