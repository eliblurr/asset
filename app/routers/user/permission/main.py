from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_db, validate_bearer
from psycopg2.errors import UndefinedTable
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from pydantic import parse_obj_as
from typing import Union, List
from . import crud, schemas
from utils import r_fields

router = APIRouter()

@router.post('/', response_model=schemas.Permission, status_code=201, name='Permission')
async def create(payload:schemas.CreatePermission, db:Session=Depends(get_db)):
    return await crud.permission.create(payload, db)

@router.get('/', response_model=schemas.PermissionList, name='Permission')
@ContentQueryChecker(crud.permission.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.permission.read(params, db)

@router.get('/{id}', response_model=Union[schemas.Permission, dict], name='Permission')
async def read_by_id(id:int, fields:List[str]=r_fields(crud.permission.model), db:Session=Depends(get_db)):
    return await crud.permission.read_by_id(id, db, fields)

@router.delete('/{id}', name='Permission')
async def delete(id:int, db:Session=Depends(get_db)):
    return await crud.permission.delete_2(id, db)

ct_router = APIRouter()

from routers.user.role.models import Role
from .models import Permission

@ct_router.get('/', name='Content Type')
@ContentQueryChecker(crud.content_type.model.c(), None)
async def read(role:int=0, include_permissions:bool=False, db:Session=Depends(get_db), **params):
    if role:
        try:
            schemas.PermissionSummaryWithHasPerm.__config__.permissions = list(*zip(*db.query(Permission.id).join(Role, Permission.roles).filter(Role.id==role).all()))
            return parse_obj_as(schemas.ContentTypeWithHasPermList, await crud.content_type.read(params, db))
        except Exception as e:
            if isinstance(e.orig, UndefinedTable):
                raise HTTPException(status_code=400, detail=f'(UndefinedTable) This may be due to missing or invalid tenant_key in request header')
            raise HTTPException(status_code=500, detail=f'{e}')
    if include_permissions:
        return parse_obj_as(schemas.ContentTypeList, await crud.content_type.read(params, db))
    return await crud.content_type.read(params, db)

@ct_router.get('/{id}', name='Content Type')
async def read_by_id(id:int, role:int, include_permissions:bool=False, fields:List[str]=r_fields(crud.content_type.model), db:Session=Depends(get_db)):
    if role:
        try:
            schemas.PermissionSummaryWithHasPerm.__config__.permissions = list(*zip(*db.query(Permission.id).join(Role, Permission.roles).filter(Role.id==role).all()))
            return parse_obj_as(schemas.ContentTypeWithHasPerm, await crud.content_type.read_by_id(id, db, fields))
        except Exception as e:
            if isinstance(e.orig, UndefinedTable):
                raise HTTPException(status_code=400, detail=f'(UndefinedTable) This may be due to missing or invalid tenant_key in request header')
            raise HTTPException(status_code=500, detail=f'{e}')
    if include_permissions: 
        return parse_obj_as(schemas.ContentType, await crud.content_type.read_by_id(id, db, fields)) 
    return parse_obj_as(schemas.ContentTypeBase, await crud.content_type.read_by_id(id, db, fields))

@ct_router.get('/{resource_id}/permissions', response_model=Union[schemas.PermissionSummaryList, list], name='Content Type')
@ContentQueryChecker(crud.permission.model.c(), None)
async def read(resource_id:int, db:Session=Depends(get_db), **params):
    return await crud.content_type.read(params, db, use_related_name='permissions', resource_id=resource_id)


@router.get('dummy/{id}', response_model=Union[schemas.Casl, dict], name='Permission')
async def read_by_id(id:int, fields:List[str]=r_fields(crud.permission.model), db:Session=Depends(get_db)):
    return await crud.permission.read_by_id(id, db, fields)