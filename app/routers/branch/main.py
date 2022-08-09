from dependencies import get_db, validate_bearer
from fastapi import APIRouter, Depends, Request
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from typing import Union, List
from . import crud, schemas
from utils import r_fields

router = APIRouter()

@router.post('/', response_model=schemas.Branch, status_code=201, name='Branch')
async def create(payload:schemas.CreateBranch, db:Session=Depends(get_db)):
    return await crud.branch.create(payload, db)

@router.get('/', response_model=schemas.BranchList, name='Branch')
@ContentQueryChecker(crud.branch.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.branch.read(params, db)

@router.get('/{id}', response_model=Union[schemas.Branch, dict], name='Branch')
async def read_by_id(id:int, fields:List[str]=r_fields(crud.branch.model), db:Session=Depends(get_db)):
    return await crud.branch.read_by_id(id, db, fields)

@router.patch('/{id}', response_model=schemas.Branch, name='Branch')
async def update(id:int, payload:schemas.UpdateBranch, db:Session=Depends(get_db)):
    return await crud.branch.update(id, payload, db)

@router.delete('/{id}', name='Branch', status_code=204)
async def delete(id:int, db:Session=Depends(get_db)):
    await crud.branch.delete(id, db)


from routers.asset.crud import asset
from routers.inventory.crud import inventory
from routers.department.crud import department

@router.get('/{b_id}/inventories', name='read branch inventories')
@ContentQueryChecker(inventory.model.c(), None)
async def read(b_id:int, db:Session=Depends(get_db), **params):
    joins = {'filters':{}, 'joins':[{'target':department.model, 'filters':{'branch_id':b_id}}]}
    return await inventory.read(params, db, joins=joins)

@router.get('/{b_id}/assets', name='read branch assets')
@ContentQueryChecker(asset.model.c(), None)
async def read(b_id:int, db:Session=Depends(get_db), **params):
    joins = {'filters':{}, 'joins':[{'target':inventory.model, 'filters':{}}, {'target':department.model, 'filters':{'branch_id':b_id}}]}
    return await asset.read(params, db, joins=joins)

@router.get('/{resource_id}/departments', name='Branch')
@ContentQueryChecker(department.model.c(), None)
async def read(resource_id:int, db:Session=Depends(get_db), **params):
    return await crud.branch.read(params, db, use_related_name='departments', resource_id=resource_id)

# proposals
# department
# inventory
# asset
# analytics
# catalogue
# 