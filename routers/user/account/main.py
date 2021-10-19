from fastapi import APIRouter, Depends, Query, Request
from typing import Union, List, Union
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from datetime import timedelta
from dependencies import get_db
from utils import create_jwt
from config import settings
from . import crud, schemas

router = APIRouter()

@router.post('/', description='', response_model=Union[schemas.User, List[schemas.User], list], status_code=201, name='User Account')
async def create(request:Request, payload:Union[schemas.CreateUser, List[schemas.CreateUser]], db:Session=Depends(get_db)):
    try:
        users = await crud.user.bk_create(payload, db) if isinstance(payload, list) else await crud.user.create(payload, db)
        for user in users:
            url = f"""{request.base_url}{settings.ACCOUNT_ACTIVATION_PATH}?token={create_jwt(
                data={'id':user.id, "userType":"users"},
                exp=timedelta(minutes=settings.ACTIVATION_TOKEN_DURATION_IN_MINUTES))}"""
            print(url)
        return users
    except Exception as e:
        print(e)
        
@router.get('/', description='', response_model=schemas.UserList, name='User Account')
@ContentQueryChecker(crud.user.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.user.read(params, db)

@router.get('/{id}', description='', response_model=Union[schemas.User, dict], name='User Account')
async def read_by_id(id:int, fields:List[str]=Query(None, regex=f'({"|".join([x[0] for x in crud.user.model.c()])})$'), db:Session=Depends(get_db)):
    return await crud.user.read_by_id(id, db, fields)

@router.patch('/{id}', description='', response_model=schemas.User, name='User Account')
async def update(id:int, payload:schemas.UpdateUser, db:Session=Depends(get_db)):
    if payload.password:
        await crud.update_password(id, payload.password.password, db)
    return await crud.user.update(id, payload.copy(exclude={'password'}), db)

@router.delete('/{id}', description='', name='User Account')
async def delete(id:int, db:Session=Depends(get_db)):
    return await crud.user.delete(id, db)