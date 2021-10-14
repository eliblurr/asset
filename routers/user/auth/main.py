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
    data = {"user":await crud.verify_user(payload, db)}
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

@router.get('/api-user', description='', response_model=schemas.Users, name='Get Current User')
async def get_current_user(userType:schemas.UserType, token:str=Depends(validate_bearer), db:Session=Depends(get_db)):
    return await crud.read_user_by_id(token[1].get('id'), userType, db)
    
@router.get('/forgot-pass')
async def pass_reset_code(token:str):
    pass

@router.post('/activate')
async def activate(token:str):
    # reset password and change is_active to True on creation
    try:
        res = decode_jwt(token)
        return res
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail=http_exception_detail(loc=['token', 'Query Parameter'], type=f'{e.__class__}', msg=f'{e}'))




token = create_jwt(
    data={'id':'tenant.id'}
)

# 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6InRlbmFudC5pZCIsImV4cCI6MTYzNDIxMDY2OX0.1aXwCXgQnGjaerK5r7hJmGl7_6aOG_GU9eem_9CtEm8'
# print(token)
# request-password-reset-code or forgot-password or reset-pass
# activate?activation_token=aksjdniajdsaudsbadu
