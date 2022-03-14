from babel.numbers import list_currencies
from typing import Union, List, Optional
from fastapi import APIRouter, Depends
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from . import crud, schemas
from utils import r_fields

router = APIRouter()

@router.post('/', response_model=schemas.Currency, status_code=201, name='Currency')
async def create(payload:schemas.m.CurrencyChoice, db:Session=Depends(get_db)):
    payload = schemas.AddCurrency(currency=payload.name)
    return await crud.currency.create(payload, db)

@router.get('/', response_model=schemas.CurrencyList, name='Currency')
@ContentQueryChecker(crud.currency.model.c(), None)
async def read(moderate:Optional[bool]=False, db:Session=Depends(get_db), **params):
    currencies = await crud.currency.read(params, db)
    if moderate:
        names = [c.name for c in currencies['data']]
        data = [(c, c in names) for c in list_currencies()]
        pg = data[params["offset"]:params["offset"]+params["limit"]]
        return {'bk_size':data.__len__(), 'pg_size':pg.__len__(), 'data':pg}
    return currencies

@router.get('/{id}', response_model=Union[schemas.Currency, dict], name='Currency')
async def read_by_id(id:int, fields:List[str]=r_fields(crud.currency.model), db:Session=Depends(get_db)):
    return await crud.currency.read_by_id(id, db, fields)

@router.patch('/{id}', response_model=schemas.Currency, name='Currency')
async def update(id:int, payload:schemas.UpdateCurrency, db:Session=Depends(get_db)):
    return await crud.currency.update(id, payload, db)

@router.delete('/{id}', name='Currency', status_code=204)
async def delete(id:int, db:Session=Depends(get_db)):
    await crud.currency.delete(id, db)