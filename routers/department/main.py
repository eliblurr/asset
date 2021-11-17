from fastapi import APIRouter, Depends, Query, Body
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List
from . import crud, schemas

router = APIRouter()

@router.post('/', description='', response_model=schemas.Department, status_code=201, name='Department')
async def create(payload:schemas.CreateDepartment, db:Session=Depends(get_db)):
    return await crud.department.create(payload, db)

@router.get('/', description='', response_model=schemas.DepartmentList, name='Department')
@ContentQueryChecker(crud.department.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.department.read(params, db)

@router.get('/{id}', description='', response_model=Union[schemas.Department, dict], name='Department')
async def read_by_id(id:int, fields:List[str]=Query(None, regex=f'({"|".join([x[0] for x in crud.department.model.c()])})$'), db:Session=Depends(get_db)):
    return await crud.department.read_by_id(id, db, fields)

@router.patch('/{id}', description='', response_model=schemas.Department, name='Department')
async def update(id:int, payload:schemas.UpdateDepartment, db:Session=Depends(get_db)):
    return await crud.department.update(id, payload, db)

@router.delete('/{id}', description='', name='Department')
async def delete(id:int, db:Session=Depends(get_db)):
    return await crud.department.delete(id, db)

@router.post('/{id}/{resource}', description='', status_code=202, name='Department Assets/Staff/Inventories/Proposals/Requests')
async def add_to_category(id:int, resource:schemas.DResource, ids:List[int] = Body(...), db:Session=Depends(get_db)):
    return await crud.add_to_department(id, ids, resource, db)

@router.delete('/{id}/{resource}', description='', status_code=204, name='Department Assets/Staff/Inventories/Proposals/Requests')
async def rem_from_category(id:int, resource:schemas.DResource, ids:List[int] = Body(...), db:Session=Depends(get_db)):
    return await crud.rem_from_department(id, ids, resource, db)