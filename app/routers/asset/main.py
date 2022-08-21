from dependencies import get_db, validate_bearer
from fastapi import APIRouter, Depends
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from typing import Union, List
from . import crud, schemas
from utils import r_fields

router = APIRouter()

@router.post('/', response_model=Union[schemas.Asset, List[schemas.Asset]], status_code=201, name='Asset')
async def create(payload:Union[schemas.CreateAsset, List[schemas.CreateAsset]], db:Session=Depends(get_db)):
    if isinstance(payload, list):
        return await crud.asset.bk_create([payload.copy(exclude={'category_ids'}) for payload in payload], db)
    return await crud.asset.create(payload.copy(exclude={'category_ids'}), db)

@router.get('/', response_model=schemas.AssetList, name='Asset')
@ContentQueryChecker(crud.asset.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.asset.read(params, db)

@router.get('/{id}', response_model=Union[schemas.Asset, dict], name='Asset') #response_model=Union[schemas.Asset, dict], 
async def read_by_id(id:int, fields:List[str]=r_fields(crud.asset.model), db:Session=Depends(get_db)):
    return await crud.asset.read_by_id(id, db, fields)

@router.patch('/{id}', response_model=schemas.Asset, name='Asset')
async def update(id:int, payload:schemas.UpdateAsset, db:Session=Depends(get_db)):
    return await crud.asset.update_2(id, payload, db)

@router.delete('/{id}', name='Asset', status_code=204)
async def delete(id:int, db:Session=Depends(get_db)):
    await crud.asset.delete(id, db)
