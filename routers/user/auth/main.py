from fastapi import APIRouter, Depends,  HTTPException, Query, Body, Request
from utils import http_exception_detail, create_jwt
from dependencies import get_db, validate_bearer
from sqlalchemy.orm import Session
from datetime import timedelta
from . import crud, schemas
from config import settings

router = APIRouter()

@router.post('/login', description='', response_model=schemas.LoginResponse, name='Login')
async def authenticate(payload:schemas.Login, userType:schemas.UserType, db:Session=Depends(get_db)):
    # make sure user is_active=True
    data = {"user":await crud.verify_user(payload, db), "userType":userType.value}
    return {
        "access_token": create_jwt(data=data, exp=timedelta(minutes=settings.ACCESS_TOKEN_DURATION_IN_MINUTES)),
        "refresh_token": create_jwt(data=data, exp=timedelta(minutes=settings.REFRESH_TOKEN_DURATION_IN_MINUTES)),
        "user": data["user"],
    }

@router.post('/logout', description='', name='Logout')
async def logout(payload:schemas.Logout, db:Session=Depends(get_db)):
    return await crud.revoke_token(payload, db)

@router.post('/token/refresh', description='', response_model=schemas.Token, name='Refresh Token')
async def refresh_token(token:str=Depends(validate_bearer), db:Session=Depends(get_db)):
    await revoke_token(token[0], db)
    return {
        "access_token":create_jwt(data=token[1], exp=timedelta(minutes=settings.ACCESS_TOKEN_DURATION_IN_MINUTES)),
        "refresh_token":create_jwt(data=token[1], exp=timedelta(minutes=settings.REFRESH_TOKEN_DURATION_IN_MINUTES)),
    }

@router.post('/activate')
async def activate(password:str=Body(...), token:str=Depends(validate_bearer), db:Session=Depends(get_db)):
    return await crud.activate_user(token[1].get('id'), token[1].get('userType'), password, db)

@router.post('/forgot-password')
async def forgot_pass(request:Request, payload:schemas.Email, userType:schemas.UserType=Query(...), db:Session=Depends(get_db)):
    user = await crud.read_user(payload, userType, db)
    if user:
        url = f"""{request.base_url}{settings.RESET_PASSWORD_PATH}?token={create_jwt(
            data={'id':user.id, "userType":userType.value},
            exp=timedelta(minutes=settings.RESET_TOKEN_DURATION_IN_MINUTES))}
        """
        return "success", {"info":"reset link sent to your email"}
    return "failed", {"info":"no user found"}

@router.get('/api-user', description='', response_model=schemas.Users, name='Get Current API User')
async def get_current_user(userType:schemas.UserType, token:str=Depends(validate_bearer), db:Session=Depends(get_db)):
    return await crud.read_user_by_id(token[1].get('user').id, userType, db)