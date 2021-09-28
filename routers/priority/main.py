from fastapi import APIRouter, Depends
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from . import crud, schemas

router = APIRouter()

@router.post('/', description='', response_model=schemas.Priority, status_code=201, name='Priority')
async def create(payload:schemas.CreatePriority, db:Session=Depends(get_db)):
    return await crud.priority.create(payload, db)

@router.get('/', description='', response_model=schemas.PriorityList, name='Priority')
@ContentQueryChecker(crud.priority.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.priority.read(params, db)

@router.get('/{id}', description='', response_model=schemas.Priority, name='Priority')
async def read_by_id(id:str, db:Session=Depends(get_db)):
    return await crud.priority.read_by_id(id, db)

@router.patch('/{id}', description='', response_model=schemas.Priority, name='Priority')
async def update(id:str, payload:schemas.UpdatePriority, db:Session=Depends(get_db)):
    return await crud.priority.update(id, payload, db)

@router.delete('/{id}', description='', name='Priority')
async def delete(id:str, db:Session=Depends(get_db)):
    return await crud.priority.delete(id, db)