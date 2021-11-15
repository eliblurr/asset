from fastapi import APIRouter, Depends, Query
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List, Optional
from . import crud, schemas

router = APIRouter()

@router.post('/', description='', status_code=201, name='Currency')
async def create(payload:schemas.AddCurrency, db:Session=Depends(get_db)):
    return await crud.currency.create(payload, db)

@router.get('/', description='', response_model=schemas.CurrencyList, name='Currency')
@ContentQueryChecker(crud.currency.model.c(), None)
async def read(full_list:Optional[bool]=False, db:Session=Depends(get_db), **params):
    if full_list:
        data = schemas.m.CURRENCY[params["offset"]:params["offset"]+params["limit"]]
        return {'bk_size':schemas.m.CURRENCY.__len__(), 'pg_size':data.__len__(), 'data':data}
    return await crud.currency.read(params, db)

@router.get('/{id}', description='', response_model=dict, name='Currency')
async def read_by_id(id:int, fields:List[str]=Query(None, regex=f'({"|".join([x[0] for x in crud.currency.model.c()])})$'), db:Session=Depends(get_db)):
    return await crud.currency.read_by_id(id, db, fields)

@router.patch('/{id}', description='', name='Currency')
async def update(id:int, payload:schemas.UpdateCurrency, db:Session=Depends(get_db)):
    return await crud.currency.update(id, payload, db)

@router.delete('/{id}', description='', name='Currency')
async def delete(id:int, db:Session=Depends(get_db)):
    return await crud.currency.delete(id, db)