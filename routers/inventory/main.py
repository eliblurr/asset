from fastapi import APIRouter, Depends
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List
from . import crud, schemas
from utils import r_fields

router = APIRouter()

@router.post('/', response_model=schemas.Inventory, status_code=201, name='Inventory')
async def create(payload:schemas.CreateInventory, db:Session=Depends(get_db)):
    return await crud.inventory.create(payload, db)

@router.get('/', response_model=schemas.InventoryList, name='Inventory')
@ContentQueryChecker(crud.inventory.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.inventory.read(params, db)

@router.get('/{id}', response_model=Union[schemas.Inventory, dict], name='Inventory')
async def read_by_id(id:int, fields:List[str]=r_fields(crud.inventory.model), db:Session=Depends(get_db)):
    return await crud.inventory.read_by_id(id, db, fields)

@router.patch('/{id}', response_model=schemas.Inventory, name='Inventory')
async def update(id:int, payload:schemas.UpdateInventory, db:Session=Depends(get_db)):
    return await crud.inventory.update(id, payload, db)

@router.delete('/{id}', name='Inventory')
async def delete(id:int, db:Session=Depends(get_db)):
    return await crud.inventory.delete(id, db)

from routers.proposal.crud import proposal
from routers.request.crud import request
from routers.asset.crud import asset

@router.get('/{r_id}/proposals', name='Inventory')
@ContentQueryChecker(proposal.model.c(), None)
async def read(r_id:int, db:Session=Depends(get_db), **params):
    return await crud.inventory.read(params, db, use_related_name='proposal', resource_id=r_id)

@router.get('/{r_id}/requests', name='Inventory')
@ContentQueryChecker(request.model.c(), None)
async def read(r_id:int, db:Session=Depends(get_db), **params):
    return await crud.inventory.read(params, db, use_related_name='request', resource_id=r_id)

@router.get('/{r_id}/assets', name='Inventory')
@ContentQueryChecker(asset.model.c(), None)
async def read(r_id:int, db:Session=Depends(get_db), **params):
    return await crud.inventory.read(params, db, use_related_name='asset', resource_id=r_id)