from dependencies import get_db, validate_bearer
from fastapi import APIRouter, Depends, Query
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from typing import Union, List
from . import crud, schemas
from utils import r_fields

router = APIRouter()

@router.post('/', response_model=schemas.Priority, status_code=201, name='Priority') # is authenticated, role in [admin]
async def create(payload:schemas.CreatePriority, db:Session=Depends(get_db)):
    return await crud.priority.create(payload, db)

@router.get('/', response_model=schemas.PriorityList, name='Priority') # is authenticated
@ContentQueryChecker(crud.priority.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.priority.read(params, db)

@router.get('/{id}', response_model=Union[schemas.Priority, dict], name='Priority') # is authenticated
async def read_by_id(id:int, fields:List[str]=r_fields(crud.priority.model), db:Session=Depends(get_db)):
    return await crud.priority.read_by_id(id, db, fields)

@router.patch('/{id}', response_model=schemas.Priority, name='Priority') # is authenticated, role in [admin]
async def update(id:int, payload:schemas.UpdatePriority, db:Session=Depends(get_db)):
    return await crud.priority.update(id, payload, db)

@router.delete('/{id}', name='Priority', status_code=204) # is authenticated, role in [admin]
async def delete(id:int, db:Session=Depends(get_db)):
    await crud.priority.delete(id, db)