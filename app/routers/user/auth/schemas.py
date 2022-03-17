from ..account.schemas import User, Admin, EmailBase, Account
from pydantic import BaseModel, constr
from typing import Optional, Union

class Login(EmailBase):
    password: constr(min_length=8)

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    account: Optional[str]
    user: Union[User, Admin] 

    class Config:
        orm_mode = True

class AccessToken(BaseModel):
    access_token: str

class RefreshToken(BaseModel):
    refresh_token: str

class Logout(BaseModel):
    access_token: str
    refresh_token: str

class Token(BaseModel):
    access_token: Optional[str]
    refresh_token: Optional[str]