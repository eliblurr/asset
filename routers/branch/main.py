from fastapi import APIRouter, Depends, Query
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List
from . import crud, schemas

router = APIRouter()

@router.post('/', description='', response_model=schemas.Branch, status_code=201, name='Branch')
async def create(payload:schemas.CreateBranch, db:Session=Depends(get_db)):
    return await crud.branch.create(payload, db)

@router.get('/', description='', response_model=schemas.BranchList, name='Branch')
@ContentQueryChecker(crud.branch.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.branch.read(params, db)

@router.get('/{id}', description='', response_model=Union[schemas.Branch, dict], name='Branch')
async def read_by_id(id:str, fields:List[str]=Query(None, regex=f'^({"|".join([x[0] for x in crud.branch.model.c()])})$'), db:Session=Depends(get_db)):
    return await crud.branch.read_by_id(id, db, fields)

@router.patch('/{id}', description='', response_model=schemas.Branch, name='Branch')
async def update(id:str, payload:schemas.UpdateBranch, db:Session=Depends(get_db)):
    return await crud.branch.update(id, payload, db)

@router.delete('/{id}', description='', name='Branch')
async def delete(id:str, db:Session=Depends(get_db)):
    return await crud.branch.delete(id, db)