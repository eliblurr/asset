from fastapi import APIRouter, Depends, File, UploadFile, Query
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List
from utils import create_jwt
from . import crud, schemas
from config import settings
import datetime

router = APIRouter()

@router.post('/', description='', response_model=schemas.Tenant, status_code=201, name='Tenant/Organization')
async def create(payload:schemas.CreateTenant=Depends(schemas.CreateTenant.as_form), logo:UploadFile=File(None), bg_image:UploadFile=File(None), db:Session=Depends(get_db)):
    tenant = await crud.tenant.create(payload, db)
    if tenant: 
        token = create_jwt(
            data={'id':tenant.id},
            exp=datetime.timedelta(
                seconds=settings.ACTIVATION_TOKEN_DURATION_IN_MINUTES
            )
        )
    return tenant

@router.get('/', description='', response_model=schemas.TenantList, name='Tenant/Organization')
@ContentQueryChecker(crud.tenant.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.tenant.read(params, db)

@router.get('/{id}', description='', response_model=Union[schemas.Tenant, dict], name='Tenant/Organization')
async def read_by_id(id:str, fields:List[str]=Query(None, regex=f'({"|".join([x[0] for x in crud.tenant.model.c()])})$'), db:Session=Depends(get_db)):
    return await crud.tenant.read_by_id(id, db, fields)

@router.patch('/{id}', description='', response_model=schemas.Tenant, name='Tenant/Organization')
async def update(id:int, payload:schemas.UpdateTenant, db:Session=Depends(get_db)):
    if payload.password:
        await crud.update_password(id, payload.password, db)
    return await crud.tenant.update(id, payload.copy(exclude={'password'}), db)
   
@router.delete('/{id}', description='', name='Tenant/Organization')
async def delete(id:str, db:Session=Depends(get_db)):
    return await crud.tenant.delete(id, db)