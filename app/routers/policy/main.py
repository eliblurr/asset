from fastapi import APIRouter, Depends
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List
from . import crud, schemas
from utils import r_fields

router = APIRouter()

@router.post('/', response_model=schemas.Policy, status_code=201, name='Policy') # is authenticated, is system admin
async def create(payload:schemas.CreatePolicy, db:Session=Depends(get_db)):
    return await crud.policy.create(payload, db)

@router.get('/', response_model=schemas.PolicyList, name='Policy')
@ContentQueryChecker(crud.policy.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.policy.read(params, db)

@router.get('/{id}', response_model=Union[schemas.Policy, dict], name='Policy') 
async def read_by_id(id:int, fields:List[str]=r_fields(crud.policy.model), db:Session=Depends(get_db)):
    return await crud.policy.read_by_id(id, db, fields)

@router.patch('/{id}', response_model=schemas.Policy, name='Policy') # is authenticated, is system admin
async def update(id:int, payload:schemas.UpdatePolicy, db:Session=Depends(get_db)):
    return await crud.policy.update(id, payload, db)

@router.delete('/{id}', name='Policy', status_code=204) # is authenticated, is system admin
async def delete(id:int, db:Session=Depends(get_db)):
    await crud.policy.delete(id, db)