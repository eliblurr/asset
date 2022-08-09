from routers.branch.crud import branch
from routers.asset.crud import asset
from exceptions import NotFound
from . import models, schemas
from enum import Enum
from cls import CRUD

upld = CRUD(models.Upload)

objects = {'asset': asset, 'branch': branch}
resources = Enum('Object', {v:v for v in objects.keys()})

async def create(resource, resource_id, uploads, db):
    if resource and resource_id:
        obj = await objects[resource.value].read_by_id(resource_id, db)
        if obj is None:
            raise NotFound(f"resource with id:{resource_id} not found")
        db.add_all([
            models.Upload(
                url=upload[0],
                upload_type=upload[1],
                object= obj,
                filename= upload[3],
                extension= upload[2],
            )
            for upload in uploads
        ])
    else: db.add_all([
            models.Upload(url=upload[0],upload_type=upload[1]) for upload in uploads
        ])
    db.commit()
    return "upload successful"

async def read(resource, resource_id, params, offset, limit, db):
    obj = await objects[resource.value].read_by_id(resource_id, db)
    if obj is None:raise NotFound(f"resource with id:{resource_id} not found")    
    base = db.query(models.Upload).filter_by(object=obj, **params)
    data = base.offset(offset).limit(limit).all()
    return {'bk_size':base.count(), 'pg_size':data.__len__(), 'data':data}

async def update(id, resource, resource_id, db):
    upload = db.query(models.Upload).get(id)
    if upload is None:raise NotFound(f"upload with id:{id} not found")
    obj = objects[resource.value].read_by_id(resource_id, db)
    if obj is None:raise NotFound(f"resource with id:{resource_id} not found")
    upload.object = obj
    db.commit()
    return True

async def delete(ids, db):
    for id in ids:
        obj = db.query(models.Upload).filter_by(id=id).first()
        if obj:db.delete(obj)
    db.commit()
    return True
