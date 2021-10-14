from routers.user.account.schemas import User
from routers.tenant.schemas import Tenant
from pydantic import BaseModel, constr
from typing import Optional, Union
from constants import EMAIL
from enum import Enum

class UserType(str, Enum):
    users = 'users'
    tenants = 'tenants'

class Users(BaseModel):
    user: Union[User, Tenant]

class Email(BaseModel):
    email: constr(regex=EMAIL)

class Login(Email):
    password: constr(min_length=8)

class LoginResponse(Users):
    access_token: str
    refresh_token: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    refresh_token: str

class Logout(Token):pass
    

# class AccessToken(BaseModel):
#     access_token: str

# class RefreshToken(BaseModel):
#     refresh_token: str


# class AccessToken(BaseModel):
#     access_token: str

# class RefreshToken(BaseModel):
#     refresh_token: str