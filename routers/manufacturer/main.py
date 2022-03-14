from fastapi import APIRouter, Depends, Request, UploadFile, File
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List
from . import crud, schemas
from utils import r_fields

router = APIRouter()

@router.post('/', response_model=schemas.Manufacturer, status_code=201, name='Manufacturer')
async def create(payload:schemas.CreateManufacturer=Depends(schemas.CreateManufacturer.as_form), logo:UploadFile=File(None),  db:Session=Depends(get_db)):
    return await crud.manufacturer.create(payload, db, exclude_unset=True, logo=logo)

# use q=scheme:null&q=scheme:some_scheme for exact or -> request should be sent as main public user 
@router.get('/', response_model=schemas.ManufacturerList, name='Manufacturer')
@ContentQueryChecker(crud.manufacturer.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.manufacturer.read(params, db)

@router.get('/{id}', response_model=Union[schemas.Manufacturer, dict], name='Manufacturer')
async def read_by_id(id:int, fields:List[str]=r_fields(crud.manufacturer.model), db:Session=Depends(get_db)):
    return await crud.manufacturer.read_by_id(id, db, fields)

@router.patch('/{id}', response_model=schemas.Manufacturer, name='Manufacturer')
async def update(id:int, payload:schemas.UpdateManufacturer=Depends(schemas.UpdateManufacturer.as_form), logo:UploadFile=File(None), db:Session=Depends(get_db)):
    return await crud.manufacturer.update_2(id, payload, db, logo=logo)

@router.delete('/{id}', name='Manufacturer', status_code=204)
async def delete(id:int, db:Session=Depends(get_db)):
    return await crud.manufacturer.delete_2(id, db)