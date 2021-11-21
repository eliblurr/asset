from fastapi import APIRouter, Depends, Query
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List
from . import crud, schemas

router = APIRouter()

@router.get('/', description='', response_model=schemas.ActivityList, name='Activity')
@ContentQueryChecker(crud.activity.model.c(), None, exclude=['meta'])
async def read(db:Session=Depends(get_db), **params):
    return await crud.activity.read(params, db)

@router.get('/{id}', description='', response_model=Union[schemas.Activity, dict], name='Activity')
async def read_by_id(id:int, fields:List[str]=Query(None, regex=f'({"|".join([x[0] for x in crud.activity.model.c()])})$'), db:Session=Depends(get_db)):
    return await crud.activity.read_by_id(id, db, fields)

@router.delete('/{id}', description='', name='Activity')
async def delete(id:int, db:Session=Depends(get_db)):
    return await crud.activity.delete(id, db)