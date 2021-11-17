from fastapi import APIRouter, Depends, Query
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List
from . import crud, schemas

router = APIRouter()

@router.post('/', description='some description here', response_model=schemas.Inventory, status_code=201, name='Inventory')
async def create(payload:schemas.CreateInventory, db:Session=Depends(get_db)):
    return await crud.inventory.create(payload, db)

@router.get('/', description='', response_model=schemas.InventoryList, name='Inventory')
@ContentQueryChecker(crud.inventory.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.inventory.read(params, db)

@router.get('/{id}', description='', response_model=Union[schemas.Inventory, dict], name='Inventory')
async def read_by_id(id:int, fields:List[str]=Query(None, regex=f'({"|".join([x[0] for x in crud.inventory.model.c()])})$'), db:Session=Depends(get_db)):
    return await crud.inventory.read_by_id(id, db, fields)

@router.patch('/{id}', description='', response_model=schemas.Inventory, name='Inventory')
async def update(id:int, payload:schemas.UpdateInventory, db:Session=Depends(get_db)):
    return await crud.inventory.update(id, payload, db)

@router.delete('/{id}', description='', name='Inventory')
async def delete(id:int, db:Session=Depends(get_db)):
    return await crud.inventory.delete(id, db)