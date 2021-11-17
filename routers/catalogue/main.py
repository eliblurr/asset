from fastapi import APIRouter, Depends, Query, Body
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List
from . import crud, schemas
import re

router = APIRouter()

@router.post('/', description='', response_model=schemas.Catalogue, status_code=201, name='Catalogue')
async def create(payload:schemas.CreateCatalogue, db:Session=Depends(get_db)):
    return await crud.catalogue.create(payload, db)

@router.get('/', description='', response_model=schemas.CatalogueList, name='Catalogue')
@ContentQueryChecker(crud.catalogue.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.catalogue.read(params, db)

@router.get('/{id}', description='', response_model=Union[schemas.Catalogue, dict], name='Catalogue')
async def read_by_id(id:int, fields:List[str]=Query(None, regex=f'({"|".join([x[0] for x in crud.catalogue.model.c()])})$'), db:Session=Depends(get_db)):
    return await crud.catalogue.read_by_id(id, db, fields)

@router.patch('/{id}', description='', response_model=schemas.Catalogue, name='Catalogue')
async def update(id:int, payload:schemas.UpdateCatalogue, db:Session=Depends(get_db)):
    return await crud.catalogue.update(id, payload, db)

@router.delete('/{id}', description='', name='Catalogue')
async def delete(id:int, db:Session=Depends(get_db)):
    return await crud.catalogue.delete(id, db)

@router.post('/{id}', description='', status_code=200, name='Catalogue Assets/Vendors')
async def add_to_catalogue(id:int, ids:List[int] = Body(...), db:Session=Depends(get_db)):
    return await crud.add_to_catalogue(id, ids, db)

@router.delete('/{id}', description='', status_code=204, name='Catalogue Assets/Vendors')
async def rem_from_catalogue(id:int, ids:List[int] = Body(...), db:Session=Depends(get_db)):
    return await crud.rem_from_catalogue(id, ids, db)