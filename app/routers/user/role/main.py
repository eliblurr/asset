from dependencies import get_db, validate_bearer
from ..permission.crud import permission
from fastapi import APIRouter, Depends
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from pydantic import parse_obj_as
from typing import Union, List
from . import crud, schemas
from utils import r_fields

router = APIRouter()

@router.post('/', response_model=schemas.Role, status_code=201, name='Role')
async def create(payload:schemas.CreateRole, db:Session=Depends(get_db)):
    return await crud.role.create(payload, db)

@router.get('/', response_model=schemas.RoleList, name='Role')
@ContentQueryChecker(crud.role.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.role.read(params, db)

@router.get('/{id}', response_model=Union[schemas.Role, dict], name='Role')
async def read_by_id(id:int, fields:List[str]=r_fields(crud.role.model), db:Session=Depends(get_db)):
    return await crud.role.read_by_id(id, db, fields)

@router.patch('/{id}', response_model=schemas.Role, name='Role')
async def update(id:int, payload:schemas.UpdateRole, db:Session=Depends(get_db)):
    return await crud.role.update_2(id, payload, db)

@router.patch('/{id}/add-permissions', name='Role', response_model=schemas.RoleWithPerm)
async def update(id:int, payload:List[int], db:Session=Depends(get_db)):
    role = await crud.role.read_by_id(id, db)
    if role:role.add_perm(payload, db)
    db.refresh(role)
    return role

@router.patch('/{id}/remove-permissions', response_model=schemas.RoleWithPerm, name='Role')
async def update(id:int, payload:List[int], db:Session=Depends(get_db)):
    role = await crud.role.read_by_id(id, db)
    if role:role.remove_perm(payload, db)
    db.refresh(role)
    return role

@router.delete('/{id}', description='', name='Role')
async def delete(id:int, db:Session=Depends(get_db)):
    return await crud.role.delete(id, db)

from routers.user.permission.schemas import PermissionSummaryList

@router.get('/{resource_id}/permissions', name='Role Permissions')
@ContentQueryChecker(permission.model.c(), None)
async def read(resource_id:int, db:Session=Depends(get_db), **params):
    return parse_obj_as(PermissionSummaryList, await crud.role.read(params, db, use_related_name='permissions', resource_id=resource_id))
