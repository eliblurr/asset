from fastapi import APIRouter, Depends, File, UploadFile, Query, Request
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List
from . import crud, schemas
from utils import act_url

router = APIRouter()

@router.post('/', description='', response_model=schemas.Tenant, status_code=201, name='Tenant/Organization')
async def create(request:Request, payload:schemas.CreateTenant=Depends(schemas.CreateTenant.as_form), logo:UploadFile=File(None), bg_image:UploadFile=File(None), db:Session=Depends(get_db)):
    tenant = await crud.tenant.create(payload, db, logo=logo, bg_image=bg_image)
    if tenant: 
        url = act_url(request.base_url, tenant.id, "tenants")
    return tenant

@router.get('/', description='', response_model=schemas.TenantList, name='Tenant/Organization')
@ContentQueryChecker(crud.tenant.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.tenant.read(params, db)

@router.get('/{id}', description='', response_model=Union[schemas.Tenant, dict], name='Tenant/Organization')
async def read_by_id(id:int, fields:List[str]=Query(None, regex=f'({"|".join([x[0] for x in crud.tenant.model.c()])})$'), db:Session=Depends(get_db)):
    return await crud.tenant.read_by_id(id, db, fields)

@router.patch('/{id}', description='', response_model=schemas.Tenant, name='Tenant/Organization')
async def update(id:int, payload:schemas.UpdateTenant, db:Session=Depends(get_db)):
    if payload.password:
        await crud.update_password(id, payload.password, db)
    return await crud.tenant.update(id, payload.copy(exclude={'password'}), db)
   
@router.delete('/{id}', description='', name='Tenant/Organization')
async def delete(id:int, db:Session=Depends(get_db)):
    return await crud.tenant.delete(id, db)