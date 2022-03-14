from fastapi import APIRouter, Depends
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List
from . import crud, schemas
from utils import r_fields

router = APIRouter()

@router.post('/', response_model=Union[schemas.RequestForConsumable, schemas.RequestForAsset], status_code=201, name='Request')
async def create(payload:Union[schemas.CreateRequestForAsset, schemas.CreateRequestForConsumable], db:Session=Depends(get_db)):
    res = await crud.request.create(payload, db, exclude_unset=True)
    if res:pass
        # manager_id = author.u_department.manager_id if author.u_department else asset.inventory.department.manager_id if asset.inventory.department else asset.department.manager_id if asset.department else asset.inventory.manager_id
        # if not manager_id:
        #     raise HTTPException(status_code=400, detail='could not direct your request to anyone')
        # activity, scheduling
    return res

@router.get('/', response_model=schemas.RequestList, name='Request')
@ContentQueryChecker(crud.request.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.request.read(params, db)

@router.get('/{id}', response_model=Union[schemas.RequestForAsset, schemas.RequestForConsumable, dict], name='Request')
async def read_by_id(id:int, fields:List[str]=r_fields(crud.request.model), db:Session=Depends(get_db)):
    return await crud.request.read_by_id(id, db, fields)

# @router.patch('/{id}', response_model=schemas.FAQ, name='FAQ')
# async def update(id:int, payload:schemas.UpdateFAQ, db:Session=Depends(get_db)):
#     return await crud.faq.update(id, payload, db)

# @router.patch('/{id}', response_model=schemas.FAQ, name='FAQ')
# async def update(id:int, payload:schemas.UpdateFAQ, db:Session=Depends(get_db)):
#     return await crud.faq.update(id, payload, db)

@router.delete('/{id}', name='Request')
async def delete(id:int, db:Session=Depends(get_db)):
    res = await crud.request.delete(id, db)
    crud.remove_scheduled_jobs(id)
    return res