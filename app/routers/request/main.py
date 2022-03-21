from exceptions import NotFound, OperationNotAllowed, BadRequestError
from fastapi import APIRouter, Depends, HTTPException, Request
from utils import r_fields, logger, raise_exc
from psycopg2.errors import UndefinedTable
from sqlalchemy.exc import DBAPIError
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List
from . import crud, schemas
from re import search

router = APIRouter()

def verify_payload(payload:schemas.CreateRequest, item:schemas.Items):
    if not payload:raise HTTPException(status_code=422, detail="payload cannot be empty")
    case1 = item.value=='consumables' and isinstance(payload.obj, schemas.CreateConsumableRequest)
    case2 = item.value=='assets' and isinstance(payload.obj, schemas.CreateAssetRequest)

    if not any((case1, case2)):raise HTTPException(status_code=422, detail="payload mismatch with item type")
    return {'payload':payload, 'item':item.value}

@router.post('/{item}', response_model=schemas.Request, status_code=201, name='Request')
async def create(payload=Depends(verify_payload), db:Session=Depends(get_db)):
    try:
        payload, item, msg, tmp_kw = payload['payload'], payload['item'], {}, {}              
        recipient, kw = await crud.validate_author(payload.author_id, db) # if recipient send request to inventory manager for operation
        await crud.validate_priority(payload.priority_id, db)        
        
        if item=='consumables':
            manager, msg, tmp_kw = await crud.validate_consumable(payload.obj.consumable_id, payload.obj.quantity, db)
            tmp_kw.update({'tag':'consumable'})

        if item=='assets':
            manager, msg, tmp_kw = await crud.validate_asset(payload.obj.asset_id, db)
            tmp_kw.update({'tag':'asset'})
      
        kw.update(tmp_kw)
    
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

    req = await crud.request.create(payload.copy(exclude={'obj'}), db, **kw)
        
    if req: 
        msg = msg.update({'key':'request', 'id':req.id})
        try:
            'send notifications here [webpush[B] to manager if not author-> reciepient]'
            'set jobs and reminders [set expire[send notification in here] to start_date if start_date, set reminder about request expiration for manager ]'
        except Exception as e:
            logger(__name__, e, 'critical')
            
    return req

@router.get('/', response_model=schemas.RequestList, name='Request')
@ContentQueryChecker(crud.request.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.request.read(params, db)

@router.get('/{id}', response_model=schemas.Request, name='Request')
async def read_by_id(id:int, fields:List[str]=r_fields(crud.request.model), db:Session=Depends(get_db)):
    return await crud.request.read_by_id(id, db, fields)

@router.patch('/{id}', response_model=schemas.Request, name='Request')
async def update_request(id:int, payload:schemas.UpdateRequest, db:Session=Depends(get_db)):
    return await crud.update_request(id, payload, db)

@router.delete('/{id}', name='Request', status_code=204)
async def delete(id:int, db:Session=Depends(get_db)):
    await crud.request.delete(id, db)
    crud.remove_scheduled_jobs(id)