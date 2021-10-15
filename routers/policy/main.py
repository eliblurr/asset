from fastapi import APIRouter, Depends, Query
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from . import crud, schemas
from typing import Union, List

router = APIRouter()

@router.post('/', description='', response_model=schemas.Policy, status_code=201, name='Policy')
async def create(payload:schemas.CreatePolicy, db:Session=Depends(get_db)):
    return await crud.policy.create(payload, db)

@router.get('/', description='', response_model=schemas.PolicyList, name='Policy')
@ContentQueryChecker(crud.policy.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.policy.read(params, db)

@router.get('/{id}', description='', response_model=Union[schemas.Policy, dict], name='Policy')
async def read_by_id(id:str, fields:List[str]=Query(None, regex=f'^({"|".join([x[0] for x in crud.policy.model.c()])})$'), db:Session=Depends(get_db)):
    return await crud.policy.read_by_id(id, db, fields)

@router.patch('/{id}', description='', response_model=schemas.Policy, name='Policy')
async def update(id:str, payload:schemas.UpdatePolicy, db:Session=Depends(get_db)):
    return await crud.policy.update(id, payload, db)

@router.delete('/{id}', description='', name='Policy')
async def delete(id:str, db:Session=Depends(get_db)):
    return await crud.policy.delete(id, db)