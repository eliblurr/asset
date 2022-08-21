from routers.consumable.models import Consumable
from exceptions import NotFound, BadRequestError
from routers.catalogue.models import Catalogue
from routers.priority.models import Priority
from routers.user.account.models import User
from rds.tasks import async_send_email
from sqlalchemy.orm import Session
from fastapi import HTTPException
from database import SessionLocal
from scheduler import scheduler
from . import models, schemas
from typing import Union
from cls import CRUD

request = CRUD(models.Request)

async def validate_author(id, db:Session):
    obj = db.query(User).filter_by(id=id).first()
    if not obj:raise NotFound(f'user with id:{id} not found')
    if obj.department:
        return obj.department.head_of_department, {"department_id":obj.department.id} 
    return None, {}

async def validate_priority(id, db:Session):
    obj = db.query(Priority).filter_by(id=id).first()
    if not obj:raise NotFound(f'priority with id:{id} not found')
    return True

async def validate_asset(id:int, db:Session):
    obj = db.query(models.Asset).filter_by(id=id).first()
    if not obj:raise NotFound(f'asset with id:{id} not found')
    if not obj.available:raise BadRequestError(f'asset with id:{id} not available')
    return obj.inventory.department.head_of_department if obj.inventory.department else obj.inventory.manager, {'title':obj.title, 'code':obj.code, 'asset_id':id, 'code':obj.code, 'type':'assets'}, {"inventory_id":obj.inventory.id}

async def validate_consumable(id, quantity, db:Session):
    obj = db.query(Consumable).filter_by(id=id).first()
    if not obj:raise NotFound(f'consumable with id:{id} not found')
    obj.validate_quantity(quantity, db)
    return obj.inventory.department.head_of_department if obj.inventory.department else obj.inventory.manager, {'title':obj.title, 'quantity':obj.quantity, 'consumable_id':id, 'code':obj.code, 'type':'consumables'}, {"inventory_id":obj.inventory.id}

def remove_scheduled_jobs(id:int):
    map(scheduler.remove_job, [job.id for job in scheduler.get_jobs() if job.split('_',1)[0]==str(id)])

def expire(id:int, db=SessionLocal()):
    request = db.query(models.Request).filter_by(id=id).first()
    if request: 
        request.status=schemas.RequestStatus.expired
        db.commit()
        remove_scheduled_jobs(id)

asset_request = CRUD(models.AssetRequest)
consumable_request = CRUD(models.ConsumableRequest)

async def transfer(request_id:int, payload:Union[schemas.AssetTransfer, schemas.ConsumableTransfer], db:Session, activity=[]):

    req = db.query(models.Request).filter_by(id=request_id).first()

    # add holder to payload
    payload.holder_id = req.author_id

    if payload.action=='ready' and req.status!='accepted':
        raise HTTPException(status_code=400, detail='transfer can only occur when request has been accepted')
    
    if req.tag.value=='asset':
        if not isinstance(payload, schemas.AssetTransfer):
            raise HTTPException(status_code=400, detail="payload mismatch with request tag")

        return await asset_request.update_2({'request_id':request_id}, payload, db, activity=activity)

    if req.tag.value=='consumable':
        if not isinstance(payload, schemas.ConsumableTransfer):
            raise HTTPException(status_code=400, detail="payload mismatch with request tag")
        
        return await consumable_request.update_2({'request_id':request_id}, payload, db, activity=activity)

async def swap_holder(request_id:int, payload:schemas.SwapHolder, db:Session):
    return await request.update_2(request_id, payload, db)