from fastapi import APIRouter, Depends, Query
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List
from . import crud, schemas

router = APIRouter()

@router.post('/', description='', response_model=schemas.Role, status_code=201, name='Role')
async def create(payload:schemas.CreateRole, db:Session=Depends(get_db)):
    return await crud.role.create(payload, db)

@router.get('/', description='', response_model=schemas.RoleList, name='Role')
@ContentQueryChecker(crud.role.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.role.read(params, db)

@router.get('/{id}', description='', response_model=Union[schemas.Role, dict], name='Role')
async def read_by_id(id:int, fields:List[str]=Query(None, regex=f'({"|".join([x[0] for x in crud.role.model.c()])})$'), db:Session=Depends(get_db)):
    return await crud.role.read_by_id(id, db, fields)

@router.patch('/{id}', description='', response_model=schemas.Role, name='Role')
async def update(id:int, payload:schemas.UpdateRole, db:Session=Depends(get_db)):
    # print(payload.copy(exclude={'in_perm','ex_perm'}))
    return await crud.role.update(id, payload.copy(exclude={'in_perm','ex_perm'}), db)

@router.delete('/{id}', description='', name='Role')
async def delete(id:int, db:Session=Depends(get_db)):
    return await crud.role.delete(id, db)