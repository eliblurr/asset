from fastapi import APIRouter, Depends, Query
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List
from . import crud, schemas

router = APIRouter()

@router.post('/', description='', response_model=schemas.FAQ, status_code=201, name='FAQ')
async def create(payload:schemas.CreateFAQ, db:Session=Depends(get_db)):
    return await crud.faq.create(payload, db)

@router.get('/', description='', response_model=schemas.FAQList, name='FAQ')
@ContentQueryChecker(crud.faq.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.faq.read(params, db)

@router.get('/{id}', description='', response_model=Union[schemas.FAQ, dict], name='FAQ')
async def read_by_id(id:str, fields:List[str]=Query(None, regex=f'^({"|".join([x[0] for x in crud.faq.model.c()])})$'), db:Session=Depends(get_db)):
    return await crud.faq.read_by_id(id, db)

@router.patch('/{id}', description='', response_model=schemas.FAQ, name='FAQ')
async def update(id:str, payload:schemas.UpdateFAQ, db:Session=Depends(get_db)):
    return await crud.faq.update(id, payload, db)

@router.delete('/{id}', description='', name='FAQ')
async def delete(id:str, db:Session=Depends(get_db)):
    return await crud.faq.delete(id, db)