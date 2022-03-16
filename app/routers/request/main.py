from exceptions import NotFound, OperationNotAllowed, BadRequestError
from fastapi import APIRouter, Depends, HTTPException
from utils import r_fields, logger, raise_exc
from psycopg2.errors import UndefinedTable
from sqlalchemy.exc import DBAPIError
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List
from . import crud, schemas

router = APIRouter()

def verify_payload(payload:schemas.CreateRequest, item:schemas.Items):
    if not payload:raise HTTPException(status_code=422, detail="payload cannot be empty")
    case1 = item.value=='consumables' and isinstance(payload.obj, schemas.CreateConsumableRequest)
    case2 = item.value=='assets' and isinstance(payload.obj, schemas.CreateAssetRequest)
    # case3 = item.value=='catalogues' and isinstance(payload.obj, schemas.CreateCatalogueRequest)

    if not any((case1, case2)):raise HTTPException(status_code=422, detail="payload mismatch with item type")
    return {'payload':payload, 'item':item.value}

@router.post('/{item}', response_model=Union[schemas.ConsumableRequest, schemas.AssetRequest], status_code=201, name='Request')
async def create(payload=Depends(verify_payload), db:Session=Depends(get_db)):
    try:

        payload, item, data = payload['payload'], payload['item'], {}
        
        await crud.validate_author(payload.author_id, db)
        await crud.validate_priority(payload.priority_id, db)        
        
        if item=='consumables':
            managers, data = await crud.validate_consumable(payload.obj.consumable_id, payload.obj.quantity, db)

        if item=='assets':
            managers, data = await crud.validate_asset(payload.obj.asset_id, db)

        "if payload['item']=='catalogues':"
        "managers, data = crud.validate_catalogue(payload.obj.catalogue_id, db)"
        " kwargs = {'catalogues':payload.obj}"

        req = await crud.request.create(payload.copy(exclude={'obj'}), db)
        
        # if req: 
        #     data = data.update({'key':'request', 'id':req.id})
        #     'send notifications here'
        
        # return req
    
    except Exception as e:
        status_code, msg, class_name = 500, f'{e}' , f"{e.__class__.__name__}"
        if isinstance(e, DBAPIError):
            status_code = 400
            msg=f'(UndefinedTable) This may be due to missing or invalid tenant_key in request header' if isinstance(e.orig, UndefinedTable) else f'{e.orig}'
        else:
            status_code = 400 if isinstance(e, BadRequestError) else 404 if isinstance(e, NotFound) else status_code
            msg = f"{e._message()}" if isinstance(e, (BadRequestError, NotFound,)) else msg   
        logger(__name__, e, 'critical')
        raise HTTPException(status_code=status_code, detail=raise_exc(msg=msg, type=class_name))

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