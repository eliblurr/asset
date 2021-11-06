from fastapi import APIRouter, Depends, Query, Request, File, UploadFile
from cls import ContentQueryChecker, FileReader
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import List, Union
from . import crud, schemas
from utils import act_url

router = APIRouter()

@router.post('/', description='', response_model=Union[schemas.User, List[schemas.User], list], status_code=201, name='User Account')
async def create(request:Request, payload:Union[schemas.CreateUser, List[schemas.CreateUser]], file:UploadFile=File(None), db:Session=Depends(get_db)):
    # gen_payload here -> rows = await FileReader(file, ['email', 'password']).read()
    obj = await crud.bk_create(payload, db) if isinstance(payload, list) else await crud.user.create(payload, db)
    if obj:
        urls = [act_url(request.base_url, user.id, "users") for user in obj] if isinstance(obj, list) else act_url(request.base_url, obj.id, "users")
    return obj

# @router.post('/files', description='create users from file', response_model=Union[schemas.User, List[schemas.User], list], status_code=201, name='User Account')
# async def create_from_file(request:Request, file:UploadFile=File(...), db:Session=Depends(get_db)):
#     rows = await FileReader(file, ['email', 'password']).read()
#     obj = await crud.bk_create(rows, db)
#     if obj:
#         urls = [act_url(request.base_url, user.id, "users") for user in obj] if isinstance(obj, list) else act_url(request.base_url, obj.id, "users")
#     return obj
        
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