from fastapi import APIRouter, Depends, Request
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List
from . import crud, schemas
from utils import r_fields
import re

router = APIRouter()

@router.post('/', response_model=schemas.Department, status_code=201, name='create department')
async def create(payload:schemas.CreateDepartment, db:Session=Depends(get_db)):
    return await crud.department.create(payload, db)

@router.get('/', response_model=schemas.DepartmentList, name='read departments')
@ContentQueryChecker(crud.department.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.department.read(params, db)

@router.get('-base/', response_model=schemas.BaseDepartmentList, name='read base-departments')
@ContentQueryChecker(crud.base_department.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.base_department.read(params, db)

@router.get('/{id}', response_model=Union[schemas.Department, dict], name='read department by id')
async def read_by_id(id:int, fields:List[str]=r_fields(crud.department.model), db:Session=Depends(get_db)):
    return await crud.department.read_by_id(id, db, fields)

@router.get('-base/{id}', response_model=Union[schemas.BaseDepartment, dict], name='read base-department by id')
async def read_by_id(id:int, fields:List[str]=r_fields(crud.base_department.model), db:Session=Depends(get_db)):
    return await crud.base_department.read_by_id(id, db, fields)

@router.put('/', response_model=schemas.Department, status_code=201, name='create branch department')
async def create(payload:schemas.CreateDepartment2, db:Session=Depends(get_db)):
    return await crud.department.create(payload, db)

@router.patch('/{id}', response_model=schemas.Department, name='update department')
async def update(request:Request, id:int, payload:schemas.UpdateDepartment, db:Session=Depends(get_db)):
    return await crud.department.update(id, payload, db)

@router.patch('-base/{id}', response_model=schemas.BaseDepartment, name='update base-department')
async def update(id:int, payload:schemas.UpdateBaseDepartment, db:Session=Depends(get_db)):
    return await crud.base_department.update(id, payload, db)

@router.delete('/{id}', name='Delete Department')
@router.delete('-base/{id}', name='Delete Base Department')
@router.delete('/{id}/branches/{branch_id}', name='Delete Branch Department')
async def delete(request:Request, id:int, branch_id:int, db:Session=Depends(get_db)):
    if re.search(r'^(/departments-base)', request.url.path):
        return await crud.base_department.delete(id, db)
    if id and branch_id:
        return await crud.department.bk_delete_2(db, branch_id=branch_id, id=id)
    return await crud.department.delete(id, db)

from routers.asset.crud import asset
from routers.inventory.crud import inventory

@router.get('/{d_id}/assets', name='read departments assets')
@ContentQueryChecker(asset.model.c(), None)
async def read(d_id:int, db:Session=Depends(get_db), **params):
    joins = {'filters':{}, 'joins':[{'target':inventory.model, 'filters':{'department_id':d_id}}]}
    return await asset.read(params, db, joins=joins)