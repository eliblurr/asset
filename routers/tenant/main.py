from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.schema import DropSchema
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from . import crud, schemas
from database import engine
from uuid import uuid4

router = APIRouter()

@router.post('/', description='', response_model=schemas.Tenant, status_code=201, name='Tenant/Organization')
async def create(payload:schemas.CreateTenant=Depends(schemas.CreateTenant.as_form), logo:UploadFile=File(...), bg_image:UploadFile=File(...), db:Session=Depends(get_db)):
    payload.id = f"{uuid4()}"
    return await crud.tenant.create(payload, db)

@router.get('/', description='', response_model=schemas.TenantList, name='Tenant/Organization')
@ContentQueryChecker(crud.tenant.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.tenant.read(params, db)

@router.get('/{id}', description='', response_model=schemas.Tenant, name='Tenant/Organization')
async def read_by_id(id:int, db:Session=Depends(get_db)):
    return await crud.tenant.read_by_id(id, db)

@router.patch('/{id}', description='', response_model=schemas.Tenant, name='Tenant/Organization')
async def update(id:int, payload:schemas.UpdateTenant, db:Session=Depends(get_db)):
    return await crud.tenant.update(id, payload, db)

@router.delete('/{id}', description='', name='Tenant/Organization')
async def delete(id:str, db:Session=Depends(get_db)):
    res = await crud.tenant.delete(id, db)
    if int(res[1]["info"].split(' ', 1)[0]):
        engine.execute(DropSchema(id, cascade=True))
    return res