from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends
from dependencies import get_db_2
from exceptions import NotFound
from config import STATIC_ROOT
from . import models, schemas
from utils import raise_exc
import json, os, enum
from cls import CRUD

activity = CRUD(models.Activity)

def get_message(ref): # ref eg. asset.return
    parent, child = ref.split('.')
    with open(os.path.join(STATIC_ROOT, 'json/messages.json')) as file:
        messages = json.load(file)  
        file.close()
    return messages[parent][child]

async def create(c, ref, meta:dict, resource, resource_id:int, db:Session):
    try:
        obj = c.read_by_id(resource_id, db)
        if obj is None:raise NotFound(f"resource with id:{resource_id} not found")
        payload = schemas.ActivityBase(message=get_message(ref), meta = meta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=raise_exc(msg=f"{e}", type= e.__class__.__name__))
    return await activity.create(payload, db, object=obj)

async def add_activity(object, ref, meta:dict, db:Session=Depends(get_db_2)):
    # db = next(get_db_2())
    payload = schemas.ActivityBase(message=get_message(ref), meta=meta)
    return await activity.create(payload, db, object=object)

from routers.asset.crud import asset
from routers.proposal.crud import proposal

objects = {
    'asset': asset,
    'proposal': proposal
}
resources = enum.Enum('Object', {v:v for v in objects.keys()})

async def read(resource, resource_id, offset, limit, db):
    obj = await objects[resource.value].read_by_id(resource_id, db)
    base = db.query(models.Activity).filter_by(object=obj).order_by('created')
    data = base.offset(offset).limit(limit).all()
    return {'bk_size':base.count(), 'pg_size':data.__len__(), 'data':data}
     