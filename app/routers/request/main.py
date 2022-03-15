from exceptions import NotFound, OperationNotAllowed, BadRequestError
from fastapi import APIRouter, Depends, HTTPException
from utils import r_fields, logger, raise_exc
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List
from . import crud, schemas

router = APIRouter()

def verify_payload(payload:schemas.CreateRequest, item:schemas.Items):
    if not payload:raise HTTPException(status_code=422, detail="payload cannot be empty")
    case1 = item.value=='assets' and isinstance(payload.obj, schemas.CreateConsumableRequest)
    case2 = item.value=='consumables' and isinstance(payload.obj, schemas.CreateAssetRequest)
    case3 = item.value=='catalogues' and isinstance(payload.obj, schemas.CreateCatalogueRequest)
    if not any((case1, case2, case3)):raise HTTPException(status_code=422, detail="payload mismatch with item type")
    return {'payload':payload, 'item':item.value}

@router.post('/{item}', response_model=Union[schemas.ConsumableRequest, schemas.AssetRequest], status_code=201, name='Request')
async def create(payload=Depends(verify_payload), db:Session=Depends(get_db)):
    try:
        
        await crud.validate_priority(payload.priority_id, db)

        if payload['item']=='consumables':
            manager = crud.validate_consumable(payload.obj.consumable_id, payload.obj.quantity, db)
            kwargs = {'consumables':payload.obj}

        if payload['item']=='assets':
            manager = crud.validate_asset(payload.obj.asset_id, db)
            kwargs = {'assets':payload.obj}

        # if payload['item']=='catalogues':
        #     obj = crud.validate_catalogue(payload.obj.id, db)
        #     kwargs = {'catalogues':payload.obj}

        return await request.create(payload.copy(exclude={'obj'}), db, **kwargs)
    
    except Exception as e:
        print(e)
        logger(__name__, e, 'critical')
        raise HTTPException(status_code=400, detail=raise_exc(msg=f"{e}", type=f"{e.__class__}"))

@router.get('/', response_model=schemas.RequestList, name='Request')
@ContentQueryChecker(crud.request.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.request.read(params, db)

@router.get('/{id}', response_model=Union[schemas.AssetRequest, schemas.ConsumableRequest, dict], name='Request')
async def read_by_id(id:int, fields:List[str]=r_fields(crud.request.model), db:Session=Depends(get_db)):
    return await crud.request.read_by_id(id, db, fields)

@router.delete('/{id}', name='Request', status_code=204)
async def delete(id:int, db:Session=Depends(get_db)):
    await crud.request.delete(id, db)
    crud.remove_scheduled_jobs(id)