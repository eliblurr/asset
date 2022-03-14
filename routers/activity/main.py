from fastapi import APIRouter, Depends, HTTPException
from utils import r_fields, logger, raise_exc
from sqlalchemy.orm import Session
from exceptions import NotFound
from dependencies import get_db
from typing import Union, List
from . import crud, schemas

router = APIRouter()

@router.get('/', response_model=schemas.ActivityList, name='Activity')
async def read(offset:int=0, limit:int=100, db:Session=Depends(get_db)):
    params = {
        'status': None, 'id': None, 'title': None, 'metatitle': None, 
        'description': None, 'index': None, 'created': None, 'updated': None, 
        'offset': offset, 'limit': limit, 'fields': None, 'q': None, 'sort': ['created']}
    return await crud.activity.read(params, db)

@router.get('/{id}', response_model=Union[schemas.Activity, dict], name='Activity')
async def read_by_id(id:int, fields:List[str]=r_fields(crud.activity.model), db:Session=Depends(get_db)):
    return await crud.activity.read_by_id(id, db, fields)

@router.get('/{resource}/{resource_id}', response_model=schemas.ActivityList, name='Activity') # 
async def read(resource:crud.resources, resource_id:int, offset:int=0, limit:int=100, db:Session=Depends(get_db)):
    return await crud.read(resource, resource_id, offset, limit, db)
   
@router.delete('/{id}', name='Activity', status_code=204)
async def delete(id:int, db:Session=Depends(get_db)):
    await crud.activity.delete(id, db)