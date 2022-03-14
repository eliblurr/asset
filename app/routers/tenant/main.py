from fastapi import APIRouter, Depends, Request, UploadFile, File
from routers.user.account.crud import gen_token, decode_token
from utils import r_fields, urljoin, logger
from rds.tasks import async_send_email
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List
from . import crud, schemas
from config import settings

router = APIRouter()

@router.post('/', response_model=schemas.Tenant, status_code=201, name='Tenant/Organization')
async def create(request:Request, payload:schemas.CreateTenant=Depends(schemas.CreateTenant.as_form), logo:UploadFile=File(...), bg_image:UploadFile=File(None), db:Session=Depends(get_db)):
    tenant = await crud.tenant.create(payload, db, logo=logo, bg_image=bg_image)
    if tenant: 
        token = await gen_token(tenant.id, account='tenant', revoke_after=True)   
        try:     
            async_send_email(mail={
                "subject":"Account Activation", "recipients":[tenant.email],
                "body":f"your password reset link is: {urljoin(request.base_url, settings.VERIFICATION_PATH)}?token={token}" 
            })
        except Exception as e:logger(__name__, e, 'critical')
    return tenant

@router.get('/', response_model=schemas.TenantList, name='Tenant/Organization')
@ContentQueryChecker(crud.tenant.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.tenant.read(params, db)

@router.get('/{id}', response_model=Union[schemas.Tenant, dict], name='Tenant/Organization')
async def read_by_id(id:int, fields:List[str]=r_fields(crud.tenant.model), db:Session=Depends(get_db)):
    return await crud.tenant.read_by_id(id, db, fields)

@router.patch('/activate-tenant', name='Activate/Verify Tenant')
async def update(data=Depends(decode_token), db:Session=Depends(get_db)):
    obj = await crud.tenant.read_by_id(data['id'], db)
    if not obj:
        raise HTTPException(status_code=404, detail='tenant not found')
    obj.is_active, obj.is_verified = True, True
    db.commit()
    return {'status':'success', 'message':'tenant verified and activated'}

@router.patch('/{id}', response_model=schemas.Tenant, name='Tenant/Organization')
async def update(id:int, payload:schemas.UpdateTenant=Depends(schemas.UpdateTenant.as_form), logo:UploadFile=File(None), bg_image:UploadFile=File(None), db:Session=Depends(get_db)):
    return await crud.tenant.update_2(id, payload, db, logo=logo, bg_image=bg_image)
   
@router.delete('/{id}', description='', name='Tenant/Organization', status_code=204)
async def delete(id:int, db:Session=Depends(get_db)):
    return await crud.tenant.delete_2(id, db)