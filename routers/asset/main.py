from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from cls import ContentQueryChecker, FileReader
from utils import http_exception_detail
from . import crud, schemas, models
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List
import json

router = APIRouter()

@router.post('/', description='', response_model=schemas.Asset, status_code=201, name='Asset')
async def create(payload:schemas.CreateAsset=Depends(schemas.CreateAsset.as_form), images:List[UploadFile]=File(None), file:UploadFile=File(None), documents:List[UploadFile]=File(None),db:Session=Depends(get_db)):
    try:
        if file:
            payload = [schemas.CreateAsset(**row) for row in  await FileReader(file, schemas.ASSET_HEADER).read(to_dict=True, replace_nan_with=None)] + [payload]
    except Exception as e:
        detail = json.loads(e.json())[0]
        raise HTTPException(status_code=422, detail=http_exception_detail(loc={'file':detail["loc"]}, msg=f'{detail["msg"]} - make sure required fields are not empty in file',  type=detail["type"]))
    if documents:
        documents = [models.AssetDocument(url=document) for document in documents]
    if images:
        images = [models.AssetImage(url=image) for image in images]
    return await crud.asset.bk_create(payload, db) if isinstance(payload, list) else await crud.asset.create(payload, db, images=images, documents=documents)

@router.get('/', description='', response_model=schemas.AssetList, name='Asset')
@ContentQueryChecker(crud.asset.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.asset.read(params, db)

@router.get('/{id}', description='', response_model=Union[schemas.Asset, dict], name='Asset')
async def read_by_id(id:int, fields:List[str]=Query(None, regex=f'({"|".join([x[0] for x in crud.asset.model.c()])})$'), db:Session=Depends(get_db)):
    return await crud.asset.read_by_id(id, db, fields)

@router.patch('/{id}', description='', response_model=schemas.Asset, name='Asset')
async def update(id:int, payload:schemas.UpdateAsset, db:Session=Depends(get_db)):
    return await crud.asset.update(id, payload, db)

@router.delete('/{id}', description='', name='Asset')
async def delete(id:int, db:Session=Depends(get_db)):
    return await crud.asset.delete(id, db)