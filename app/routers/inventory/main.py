from dependencies import get_db, validate_bearer
from routers.activity.crud import add_activity
from fastapi import APIRouter, Depends
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from typing import Union, List
from . import crud, schemas
from utils import r_fields

router = APIRouter()

@router.post('/', response_model=schemas.Inventory, status_code=201, name='Inventory') # is authenticated, if role in []
async def create(payload:schemas.CreateInventory, db:Session=Depends(get_db)):
    return await crud.inventory.create(payload, db)

@router.get('/', response_model=schemas.InventoryList, name='Inventory') # is authenticated
@ContentQueryChecker(crud.inventory.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.inventory.read(params, db)

@router.get('/{id}', response_model=Union[schemas.Inventory, dict], name='Inventory') # is authenticated
async def read_by_id(id:int, fields:List[str]=r_fields(crud.inventory.model), db:Session=Depends(get_db)):
    return await crud.inventory.read_by_id(id, db, fields)

@router.patch('/{id}', response_model=schemas.Inventory, name='Inventory') # is authenticated, if role in []
async def update(id:int, payload:schemas.UpdateInventory, db:Session=Depends(get_db)):
    activity = []
    if payload.manager_id:
        activity.append({'func': add_activity, 'args':('inventory.update_manager', {'manager':['manager.first_name', 'manager.last_name'], 'datetime':'updated', 'manager_id':'manager.id',})})
    return await crud.inventory.update_2(id, payload, db, activity=activity)

@router.delete('/{id}', name='Inventory', status_code=204) # is authenticated, if role in []
async def delete(id:int, db:Session=Depends(get_db)):
    await crud.inventory.delete(id, db)

from routers.proposal.crud import proposal
from routers.request.crud import request
from routers.asset.crud import asset

@router.get('/{r_id}/proposals', name='Inventory') # is authenticated
@ContentQueryChecker(proposal.model.c(), None)
async def read(r_id:int, db:Session=Depends(get_db), **params):
    return await crud.inventory.read(params, db, use_related_name='proposals', resource_id=r_id)

@router.get('/{r_id}/requests', name='Inventory') # is authenticated
@ContentQueryChecker(request.model.c(), None)
async def read(r_id:int, db:Session=Depends(get_db), **params):
    return await crud.inventory.read(params, db, use_related_name='requests', resource_id=r_id)

@router.get('/{r_id}/assets', name='Inventory') # is authenticated
@ContentQueryChecker(asset.model.c(), None)
async def read(r_id:int, db:Session=Depends(get_db), **params):
    return await crud.inventory.read(params, db, use_related_name='assets', resource_id=r_id)