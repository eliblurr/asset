from fastapi import APIRouter, Depends, Query, Body, File, UploadFile
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List
from . import crud, schemas
import re

router = APIRouter()

@router.post('/', description='', response_model=schemas.Manufacturer, status_code=201, name='Manufacturer')
async def create(logo:UploadFile=File(None), payload:schemas.CreateManufacturer=Depends(schemas.CreateManufacturer.as_form), db:Session=Depends(get_db)):
    return await crud.manufacturer.create(payload, db)

@router.get('/', description='', response_model=schemas.ManufacturerList, name='Manufacturer')
@ContentQueryChecker(crud.manufacturer.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.manufacturer.read(params, db)

@router.get('/{id}', description='', response_model=Union[schemas.Manufacturer, dict], name='Manufacturer')
async def read_by_id(id:int, fields:List[str]=Query(None, regex=f'({"|".join([x[0] for x in crud.manufacturer.model.c()])})$'), db:Session=Depends(get_db)):
    return await crud.manufacturer.read_by_id(id, db, fields)

@router.patch('/{id}', description='', response_model=schemas.Manufacturer, name='Manufacturer')
async def update(id:int, payload:schemas.UpdateManufacturer, db:Session=Depends(get_db)):
    return await crud.manufacturer.update(id, payload, db)

@router.delete('/{id}', description='', name='Manufacturer')
async def delete(id:int, db:Session=Depends(get_db)):
    return await crud.manufacturer.delete(id, db)