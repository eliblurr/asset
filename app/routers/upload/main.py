from fastapi import APIRouter, File, UploadFile, Depends
from dependencies import get_db, validate_bearer
from utils import raise_exc, file_ext
from config import UPLOAD_EXTENSIONS
from sqlalchemy.orm import Session
from exceptions import NotFound
from . import schemas, crud
from typing import List

router = APIRouter()

def verify_upload(files:List[UploadFile]=File(...)):
    try:
        uploads = []
        for file in files:
            ext = file_ext(file.filename)
            media = [k for k,v in UPLOAD_EXTENSIONS.items() if ext in v]
            assert media, f"unsupported format for {file.filename}"
            uploads.append([file, media[0], ext, file.filename])
        return uploads
    except AssertionError as e:
        raise HTTPException(status_code=400, detail=raise_exc(msg=f"{e}", type=e.__class__.__name__))

@router.post('/', status_code=201, name='Upload')
@router.post('/{resource}/{resource_id}', status_code=201, name='Upload') # perm is authenticated
async def create(resource:crud.resources=None, resource_id:int=None, uploads=Depends(verify_upload), db:Session=Depends(get_db)):
    try:return await crud.create(resource, resource_id, uploads, db)
    except Exception as e:
        status_code=404 if isinstance(e, NotFound) else 500
        raise HTTPException(status_code=status_code, detail=raise_exc(msg=e._message(), type=e.__class__.__name__))

@router.get('/', response_model=schemas.UploadList, name='Upload') # perm is authenticated 
async def read(media:schemas.m.UploadType=None, offset:int=0, limit:int=100 , db:Session=Depends(get_db)):
    params = schemas.params
    params.update({'offset': offset, 'limit': limit,})
    if media:params.update({"upload_type":media.value})
    return await crud.upld.read(params, db)

@router.get('/{id}', response_model=schemas.Upload, name='Upload') # perm is authenticated
async def read(id:int, db:Session=Depends(get_db)):
    return await crud.upld.read_by_id(id, db)

@router.get('/{resource}/{resource_id}', response_model=schemas.UploadList, name='Upload') # perm is authenticated
async def read(resource:crud.resources, resource_id:int, media:schemas.m.UploadType=None, offset:int=0, limit:int=100, db:Session=Depends(get_db)):
    try: 
        params = {"upload_type":media.value} if media else {}
        return await crud.read(resource, resource_id, params, offset, limit, db)
    except Exception as e:
        status_code=404 if isinstance(e, NotFound) else 500
        raise HTTPException(status_code=status_code, detail=raise_exc(msg=e._message(), type=e.__class__.__name__))
    
@router.patch('/{id}/{resource}/{resource_id}', status_code=202, name='Upload') # perm is authenticated, is tenant user and has role in [admin]
async def update(id:int, resource:crud.resources, resource_id:int, db:Session=Depends(get_db)):
    try:return await crud.update(id, resource, resource_id, db)
    except Exception as e:
        status_code=404 if isinstance(e, NotFound) else 500
        raise HTTPException(status_code=status_code, detail=raise_exc(msg=e._message(), type=e.__class__.__name__))
    
@router.delete('/', name='Upload') # perm is authenticated, is tenant user and has role in [admin]
@router.delete('/{id}', name='Upload') # perm is authenticated, is tenant user and has role in [admin]
async def update(id:int=None, ids:List[int]=[], db:Session=Depends(get_db)):
    if id:ids.append(id)
    return await crud.delete(ids, db)