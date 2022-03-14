from fastapi import APIRouter, Depends, Request
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List
from . import crud, schemas
from utils import r_fields
import re

router = APIRouter()

@router.post('/', response_model=schemas.Catalogue, status_code=201, name='Catalogues')
async def create(payload:schemas.CreateCatalogue, db:Session=Depends(get_db)):
    return await crud.catalogue.create(payload, db)

@router.get('/', response_model=schemas.CatalogueList, name='Catalogues')
@ContentQueryChecker(crud.catalogue.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.catalogue.read(params, db)

@router.get('/{id}', response_model=Union[schemas.Catalogue, dict], name='Catalogues')
async def read_by_id(id:int, fields:List[str]=r_fields(crud.catalogue.model), db:Session=Depends(get_db)):
    return await crud.catalogue.read_by_id(id, db, fields)

@router.patch('/{id}', response_model=schemas.Catalogue, name='Catalogues')
async def update(id:int, payload:schemas.UpdateCatalogue, db:Session=Depends(get_db)):
    return await crud.catalogue.update(id, payload, db)

@router.delete('/{id}', name='Catalogues')
async def delete(id:int, db:Session=Depends(get_db)):
    await crud.catalogue.delete(id, db)

@router.delete('/', name='Catalogues')
async def delete(ids:int, db:Session=Depends(get_db)):
    return await crud.catalogue.bk_delete(ids, db)

@router.put('/{resource_id}/remove-asset', name='Catalogues')
@router.put('/{resource_id}/append-asset', name='Catalogues')
async def update(request:Request, resource_id:int, related_resource_ids:List[int], db:Session=Depends(get_db)):
    if re.search(r'(remove-asset)', request.url.path):
        return await crud.rem_from_catalogue(resource_id, related_resource_ids, db)
    return await crud.add_to_catalogue(resource_id, related_resource_ids, db)

from routers.asset.crud import asset

@router.get('/{resource_id}/assets', name='Catalogue assets')
@ContentQueryChecker(asset.model.c(), None)
async def read(resource_id:int, db:Session=Depends(get_db), **params):
    return await crud.catalogue.read(params, db, use_related_name='assets', resource_id=resource_id)
