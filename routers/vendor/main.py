from fastapi import APIRouter, Depends, Query
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List
from . import crud, schemas

router = APIRouter()

@router.post('/', description='', response_model=schemas.Vendor, status_code=201, name='Vendor')
async def create(payload:schemas.CreateVendor, db:Session=Depends(get_db)):
    return await crud.vendor.create(payload, db)

@router.get('/', description='', response_model=schemas.VendorList, name='Vendor')
@ContentQueryChecker(crud.vendor.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.vendor.read(params, db)

@router.get('/{id}', description='', response_model=Union[schemas.Vendor, dict], name='Vendor')
async def read_by_id(id:str, fields:List[str]=Query(None, regex=f'^({"|".join([x[0] for x in crud.vendor.model.c()])})$'), db:Session=Depends(get_db)):
    return await crud.vendor.read_by_id(id, db, fields)

@router.patch('/{id}', description='', response_model=schemas.Vendor, name='Vendor')
async def update(id:str, payload:schemas.UpdateVendor, db:Session=Depends(get_db)):
    return await crud.vendor.update(id, payload, db)

@router.delete('/{id}', description='', name='Vendor')
async def delete(id:str, db:Session=Depends(get_db)):
    return await crud.vendor.delete(id, db)