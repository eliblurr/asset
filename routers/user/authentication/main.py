from fastapi import APIRouter, Depends,  HTTPException
from utils import decode_jwt, http_exception_detail
from sqlalchemy.orm import Session
from dependencies import get_db
from . import crud, schemas

router = APIRouter()

# authenticate ? user/tenant
# logout
# refresh
# request-password-reset-code or forgot-password or reset-pass
# current-user
# activate?activation_token=aksjdniajdsaudsbadu
@router.post('/authenticate')
async def authenticate(token:str):
    pass

@router.post('/activate')
async def activate(token:str):
    try:
        res = decode_jwt(code)
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail=http_exception_detail(loc=['token', 'Query Parameter'], type='ExpiredSignatureError',  msg=e))

@router.get('/current-user')
async def get_current_user(token:str):
    pass

@router.post('/logout')
async def logout(token:str):
    pass

@router.post('/token/refresh')
async def refresh_token(token:str):
    pass

@router.get('/forgot-pass')
async def pass_reset_code(token:str):
    pass