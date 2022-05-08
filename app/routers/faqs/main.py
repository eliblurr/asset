from dependencies import get_db, validate_bearer
from fastapi import APIRouter, Depends
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from typing import Union, List
from . import crud, schemas
from utils import r_fields

router = APIRouter()

@router.post('/', response_model=schemas.FAQ, status_code=201, name='FAQ') # is authenticated, is system admin
async def create(payload:schemas.CreateFAQ, db:Session=Depends(get_db)): # , is_validated=Depends(validate_bearer)
    return await crud.faq.create(payload, db)

@router.get('/', response_model=schemas.FAQList, name='FAQ')
@ContentQueryChecker(crud.faq.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.faq.read(params, db)

@router.get('/{id}', response_model=Union[schemas.FAQ, dict], name='FAQ')
async def read_by_id(id:int, fields:List[str]=r_fields(crud.faq.model), db:Session=Depends(get_db)):
    return await crud.faq.read_by_id(id, db, fields)

@router.patch('/{id}', response_model=schemas.FAQ, name='FAQ') # is authenticated, is system admin
async def update(id:int, payload:schemas.UpdateFAQ, db:Session=Depends(get_db)):# , is_validated=Depends(validate_bearer)
    return await crud.faq.update(id, payload, db)

@router.delete('/{id}', name='FAQ', status_code=204) # is authenticated, is system admin
async def delete(id:int, db:Session=Depends(get_db)): # , is_validated=Depends(validate_bearer)
    await crud.faq.delete(id, db)