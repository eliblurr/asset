from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List
from . import crud, schemas
from utils import r_fields

router = APIRouter()

@router.post('/packages', response_model=schemas.Package, status_code=201, name='Package')
async def create(payload:schemas.CreatePackage=Depends(schemas.CreatePackage.as_form), logo:UploadFile=File(None), db:Session=Depends(get_db)):
    return await crud.package.create(payload, db, exclude_unset=True, logo=logo)

@router.get('/packages', response_model=schemas.PackageList, name='Package')
@ContentQueryChecker(crud.package.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.package.read(params, db)

@router.get('/packages/{id}', response_model=Union[schemas.Package, dict], name='Package')
async def read_by_id(id:int, fields:List[str]=r_fields(crud.package.model), db:Session=Depends(get_db)):
    return await crud.package.read_by_id(id, db, fields)

@router.patch('/packages/{id}', response_model=schemas.Package, name='Package')
async def update(id:int, payload:schemas.UpdatePackage, db:Session=Depends(get_db)):
    return await crud.package.update(id, payload, db)

@router.delete('/packages/{id}', name='Package')
async def delete(id:int, db:Session=Depends(get_db)):
    return await crud.package.delete(id, db)

@router.post('/', response_model=schemas.Subscription, status_code=201, name='Subscription')
async def create(payload:schemas.CreateSubscription, db:Session=Depends(get_db)):
    return await crud.subscription.create(payload, db)

@router.get('/', response_model=schemas.SubscriptionList, name='Subscription')
@ContentQueryChecker(crud.subscription.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.subscription.read(params, db)

@router.get('/{asset_id}/{package_id}', response_model=Union[schemas.Subscription, dict], name='Subscription') #, response_model=Union[schemas.Subscription, dict] schemas.Subscription, 
async def read_by_id(asset_id:int, package_id:int, fields:List[str]=r_fields(crud.subscription.model), db:Session=Depends(get_db)):
    return await crud.subscription.read_by_kwargs(db, fields, asset_id=asset_id, package_id=package_id)

@router.patch('/{asset_id}/{package_id}', response_model=schemas.Subscription, name='Subscription')
async def update(asset_id:int, package_id:int, payload:schemas.UpdateSubscription, db:Session=Depends(get_db)):
    try:return await crud.update_subscription(asset_id, package_id, payload, db)
    except Exception as e:raise HTTPException(status_code=404 if isinstance(e, crud.NotFound) else 500, detail=f'{e}')

@router.delete('/{asset_id}/{package_id}', name='Subscription')
async def delete(asset_id:int, package_id:int, db:Session=Depends(get_db)):
    return await crud.subscription.bk_delete_2(db, asset_id=asset_id, package_id=package_id)
