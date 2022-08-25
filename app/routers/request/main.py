from exceptions import NotFound, OperationNotAllowed, BadRequestError
from fastapi import APIRouter, Depends, HTTPException, Request
from .utils import notify, notify_reminder, messages
from dependencies import get_db, validate_bearer
from utils import r_fields, logger, raise_exc
from psycopg2.errors import UndefinedTable
from sqlalchemy.exc import DBAPIError
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from scheduler import scheduler
from datetime import timedelta
from typing import Union, List
from . import crud, schemas
from utils import gen_code
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
        payload, item, meta, tmp_kw = payload['payload'], payload['item'], {}, {}              
        recipient, kw = await crud.validate_author(payload.author_id, db) # if recipient send request to inventory manager for operation
        await crud.validate_priority(payload.priority_id, db)        
        
        if item=='consumables':
            manager, meta, tmp_kw = await crud.validate_consumable(payload.obj.consumable_id, payload.obj.quantity, db)
            tmp_kw.update({'tag':'consumable'})

        if item=='assets':
            manager, meta, tmp_kw = await crud.validate_asset(payload.obj.asset_id, db)
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

    req = await crud.request.create(payload.copy(exclude={'obj'}), db, **kw) # activities here
        
    if req: 
        meta = meta.update({'id':req.id})
        recipient = recipient if not recipient else manager

        try:
            _messages = messages()
            notify(push_id=recipient.push_id, message = {'key':'request', 'message': _messages['request']['department'],'meta':meta})
            notify_reminder(id=req.id, date=payload.obj.start_date-timedelta(days=1), name='expiry-notify-reminder', push_id=recipient.push_id, message={'key':'request', 'message': _messages['request']['expires'], 'meta':meta.update({'datetime':payload.obj.start_date})})
            scheduler.add_job( 
                crud.expire,
                id=f'{req.id}_ID{gen_code(10)}',
                name='expire-request', 
                run_date=payload.start_date, 
                trigger='date',
                kwargs={'id':req.id}
            )
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

from routers.activity.crud import add_activity

@router.patch('/{id}/transfer', name='Transfer') # , response_model=schemas.Request
async def transfer_(id:int, payload:Union[schemas.AssetTransfer, schemas.ConsumableTransfer], db:Session=Depends(get_db)):
    activity = [{'func': add_activity, 'args': ('asset.transfer', {'holder':['holder.first_name', 'holder.last_name'], 'datetime':'updated'})}]
    return await crud.transfer(id, payload, db)

@router.patch('/{id}/swap-holder', name='Change current holder')
async def swap_holder(id:int, payload:schemas.SwapHolder, db:Session=Depends(get_db)):
    activity = [{'func': add_activity, 'args': ('asset.swap', {'holder':['holder.first_name', 'holder.last_name'], 'datetime':'updated'})}]
    return await crud.request.update_2(request_id, payload, db, activity=activity)

@router.patch('/{id}', response_model=schemas.Request, name='Request')
async def update_request(id:int, payload:schemas.UpdateRequest, db:Session=Depends(get_db)):
    activity = []
    if payload.status:
        if payload.status.value=='accepted':activity.append({'func': add_activity, 'args':('request.accept', {'datetime':'updated'})})
        elif payload.status.value=='declined':activity.append({'func': add_activity, 'args':('request.decline', {'datetime':'updated'})})
    return await crud.request.update_2(id, payload, db, activity=activity)

@router.delete('/{id}', name='Request', status_code=204)
async def delete(id:int, db:Session=Depends(get_db)):
    await crud.request.delete(id, db)
    crud.remove_scheduled_jobs(id)