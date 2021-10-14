from fastapi import APIRouter, Depends,  HTTPException
from utils import decode_jwt, http_exception_detail
from sqlalchemy.orm import Session
from dependencies import get_db
from . import crud, schemas

router = APIRouter()

from utils import create_jwt
import jwt

from config import settings

token = create_jwt(
    data={'id':'tenant.id'}
)

# print(token)
# authenticate ? user/tenant
# logout
# refresh
# request-password-reset-code or forgot-password or reset-pass
# current-user
# activate?activation_token=aksjdniajdsaudsbadu
@router.post('/login')
async def authenticate():
    return settings.BASE_URL

@router.post('/logout')
async def logout(token:str):
    pass

@router.post('/token/refresh')
async def refresh_token(token:str):
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

@router.get('/current-user')
async def get_current_user(token:str):
    pass

@router.get('/forgot-pass')
async def pass_reset_code(token:str):
    pass
