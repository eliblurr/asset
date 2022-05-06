from fastapi import APIRouter, Depends, HTTPException, Request
from dependencies import get_db, validate_bearer
from utils import r_fields, urljoin, logger
from rds.tasks import async_send_email
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from typing import Union, List
from config import settings
from . import crud, schemas
import re

router = APIRouter()

def verify_payload(account:schemas.Account, payload:Union[schemas.CreateUser, schemas.CreateAdmin, list]):
    if not payload:
        raise HTTPException(status_code=422, detail="payload cannot be empty")
    obj = payload[0] if isinstance(payload, list) else payload
    case1 = account.value=='users' and isinstance(obj, schemas.CreateUser)
    case2 = account.value=='administrators' and isinstance(obj, schemas.CreateAdmin)
    if not any((case1, case2)):
        raise HTTPException(status_code=422, detail="payload mismatch with account type")
    return {'payload':payload, 'account':account.value}

@router.post('/{account}', response_model=Union[
    schemas.User, List[schemas.User],
    schemas.Admin, List[schemas.Admin], list
], status_code=201, name='Accounts')
async def create(request:Request, data=Depends(verify_payload), db:Session=Depends(get_db)):
    c = crud.administrator if data['account']=="administrators" else crud.user

    if await c.exists(db, email=data['payload'].email):
        raise HTTPException(status_code=409, detail='account with email already exists')
   
    users = await crud.bk_create(data['payload'], db) if isinstance(data['payload'], list) else await c.create(data['payload'], db)
    mailing_list = users if isinstance(users, list) else [users]

    for user in mailing_list:
        token = await crud.gen_token(user.id, data['account'], revoke_after=True)

        try:
            async_send_email(mail={
                "subject":"Account Activation",
                "recipients":[user.email],
                "body":{'verification_link': f'{urljoin(request.base_url, settings.VERIFICATION_PATH)}?token={token}', 'base_url':request.base_url}, # "request": request
                "template_name":'email-verify.html'
            })
        except Exception as e:
            logger(__name__, e, 'critical')

    return users

@router.get('/users', response_model=schemas.UserOrAdminList, name='User')
@ContentQueryChecker(crud.user.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.user.read(params, db)

@router.get('/administrators', response_model=schemas.UserOrAdminList, name='Administrator')
@ContentQueryChecker(crud.administrator.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.administrator.read(params, db)

@router.get('/users/{id}', response_model=Union[schemas.User, dict], name='User')
async def read_by_id(id:int, fields:List[str]=r_fields(crud.user.model), db:Session=Depends(get_db)):
    return await crud.user.read_by_id(id, db, fields)

@router.get('/administrators/{id}', response_model=Union[schemas.User, dict], name='Administrator')
async def read_by_id(id:int, fields:List[str]=r_fields(crud.administrator.model), db:Session=Depends(get_db)):
    return await crud.administrator.read_by_id(id, db, fields)

@router.patch('/{account}/{id}', response_model=Union[schemas.User, schemas.Admin, dict], name='User Account')
async def update(id:int, account:schemas.Account, payload:schemas.UpdateUser, db:Session=Depends(get_db)):
    obj = crud.administrator if account.value == "administrators" else crud.user
    if payload.password:
        await crud.update_password_with_code(id, account, payload.password, db)
    return await obj.update(id, payload.copy(exclude={'password'}), db)

@router.patch('/update-password', name='User Account')
@router.patch('/activate-account', name='Activate/Verify Account')
async def update(request:Request, payload:schemas.PasswordBase, data=Depends(crud.decode_token), db:Session=Depends(get_db)):

    c = crud.administrator if data['account']=="administrators" else crud.user
    obj = c.read_by_id(data['id'], db)

    if not obj:
        raise HTTPException(status_code=404, detail='account no longer exits')

    obj.password = payload.password
    if re.search('(activate-account)', request.url.path):
        obj.is_active, obj.is_verified = True, True
    db.commit()
    return 'password updated'

@router.delete('/{account}/{id}', name='User/Administrator', status_code=204)
async def delete(id:int, account:schemas.Account, db:Session=Depends(get_db)):
    if account.value == "administrators":
        await crud.administrator.delete(id, db)
    await crud.user.delete(id, db)