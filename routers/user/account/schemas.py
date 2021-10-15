from typing import Optional, List, Union
import routers.user.account.models as m
from pydantic import BaseModel, constr
from constants import EMAIL, PHONE
import datetime

# phone = Column(String, nullable=True)
# is_active = Column(Boolean, default=False)
# last_name = Column(String, nullable=False)
# middle_name = Column(String, nullable=True)
# first_name = Column(String, nullable=False)
# email = Column(String, unique=True, index=True)
# password = Column(String, nullable=False, default=pwd.genword)

class UserBase(BaseModel):
    email: constr(regex=EMAIL)
    phone: Optional[constr(regex=PHONE)]
    last_name: Optional[str]
    first_name: Optional[str]
    middle_name: Optional[str]
   
    class Config:
        orm_mode = True

    class Meta:
        model = m.User
      
class CreateUser(UserBase):
    pass

class UpdatePassword(BaseModel):
    code: str
    password: constr(min_length=8)
    
class UpdateUser(BaseModel):
    last_name: Optional[str]
    first_name: Optional[str]
    is_active: Optional[bool]
    middle_name: Optional[str]
    phone: Optional[constr(regex=PHONE)]
    password: Optional[UpdatePassword]
    
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