from fastapi import APIRouter, Depends,  HTTPException
from utils import http_exception_detail, create_jwt
from dependencies import get_db, validate_bearer
from sqlalchemy.orm import Session
from datetime import timedelta
from . import crud, schemas
from config import settings

router = APIRouter()

@router.post('/login', description='', response_model=schemas.LoginResponse, name='Login')
async def authenticate(payload:schemas.Login, userType:schemas.UserType, db:Session=Depends(get_db)):
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
async def activate(token:str=Depends(validate_bearer), db:Session=Depends(get_db)):
    return await crud.activate_user(token[1].get('user').id, token[1].get('userType'), db)
    
@router.post('/forgot-password')
async def pass_reset_code(token:str=Depends(validate_bearer), db:Session=Depends(get_db)):
    code = await crud.password_reset_code.create(schemas.Email(email=token[1].get("user").email), db)
    if code:
        # schedule delete and send code
        pass
    return 'success' if code else 'failed', {'info': 'password reset verification code sent' if code else 'could not generate password reset verification code'}

@router.get('/api-user', description='', response_model=schemas.Users, name='Get Current API User')
async def get_current_user(userType:schemas.UserType, token:str=Depends(validate_bearer), db:Session=Depends(get_db)):
    return await crud.read_user_by_id(token[1].get('user').id, userType, db)