from fastapi import APIRouter, Depends, Query, Request
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List
from . import crud, schemas

router = APIRouter()

@router.post('/', description='', response_model=schemas.Category, status_code=201, name='Category')
async def create(request:Request, payload:schemas.CreateCategory, db:Session=Depends(get_db)):
    return await crud.category.create(payload, db)

@router.get('/', description='', response_model=schemas.CategoryList, name='Category')
@ContentQueryChecker(crud.category.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.category.read(params, db)

@router.get('/{id}', description='', response_model=Union[schemas.Category, dict], name='Category')
async def read_by_id(id:int, fields:List[str]=Query(None, regex=f'({"|".join([x[0] for x in crud.category.model.c()])})$'), db:Session=Depends(get_db)):
    return await crud.category.read_by_id(id, db, fields)

@router.patch('/{id}', description='', response_model=schemas.Category, name='Category')
async def update(id:int, payload:schemas.UpdateCategory, db:Session=Depends(get_db)):
    return await crud.category.update(id, payload, db)

@router.delete('/{id}', description='', name='Category')
async def delete(id:int, db:Session=Depends(get_db)):
    return await crud.category.delete(id, db)

# @router.post('/assets', description='', response_model=schemas.Category, status_code=201, name='Category Assets')
# @router.post('/vendors', description='', response_model=schemas.Category, status_code=201, name='Category Vendors')
# if re.search('assets$', '/asdsd/load'):
#     pass