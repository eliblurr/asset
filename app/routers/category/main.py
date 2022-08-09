from dependencies import get_db, validate_bearer
from fastapi import APIRouter, Depends, Request
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from typing import Union, List
from . import crud, schemas
from utils import r_fields
import re

router = APIRouter()

@router.post('/', response_model=schemas.Category, status_code=201, name='Categories')
async def create(payload:Union[schemas.CreateCategory, List[schemas.CreateCategory]], db:Session=Depends(get_db)):
    if isinstance(payload, list):
        return await crud.category.bk_create(payload, db)
    return await crud.category.create(payload, db)

@router.get('/', response_model=schemas.CategoryList, name='Categories')
@ContentQueryChecker(crud.category.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.category.read(params, db)

@router.get('/{id}', response_model=Union[schemas.Category, dict], name='Categories')
async def read_by_id(id:int, fields:List[str]=r_fields(crud.category.model), db:Session=Depends(get_db)):
    return await crud.category.read_by_id(id, db, fields)

@router.patch('/{id}', response_model=schemas.Category, name='Categories')
async def update(id:int, payload:schemas.UpdateCategory, db:Session=Depends(get_db)):
    return await crud.category.update(id, payload, db)

@router.delete('/{id}', name='Categories', status_code=204)
async def delete(id:int, db:Session=Depends(get_db)):
    await crud.category.delete(id, db)

@router.delete('/', name='Categories', status_code=204)
async def delete(ids:int, db:Session=Depends(get_db)):
    await crud.category.bk_delete(ids, db)

@router.put('/{resource_id}/remove-{resource}', name='Categories')
@router.put('/{resource_id}/append-{resource}', name='Categories')
async def update(request:Request, resource_id:int, resource:schemas.RelatedResource, related_resource_ids:List[int], db:Session=Depends(get_db)):
    if re.search(r'(remove-)', request.url.path):
        return await crud.rem_resource_from_category(resource_id, related_resource_ids, resource, db)
    return await crud.add_resource_to_category(resource_id, related_resource_ids, resource, db)

from routers.vendor.crud import vendor
from routers.asset.crud import asset

@router.get('/{resource_id}/vendors', name='Category Vendors')
@ContentQueryChecker(vendor.model.c(), None)
async def read(resource_id:int, db:Session=Depends(get_db), **params):
    return await crud.category.read(params, db, related_name='vendors', resource_id=resource_id)

@router.get('/{resource_id}/assets', description='', name='Category Assets')
@ContentQueryChecker(asset.model.c(), None)
async def read(resource_id:int, db:Session=Depends(get_db), **params):
    return await crud.category.read(params, db, related_name='assets', resource_id=resource_id)