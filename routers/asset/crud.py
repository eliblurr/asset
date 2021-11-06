from utils import schema_to_model
from . import models, schemas
from cls import CRUD

asset = CRUD(models.Asset)
image = CRUD(models.AssetImage)
document = CRUD(models.AssetDocument)

async def bk_create(payload:list, db):
    obj = [models.Asset(**schema_to_model(payload)) for payload in payload]
    db.add_all(obj)
    db.commit()
    [db.refresh(obj) for obj in obj]
    return obj

async def update_warranty(id, warranty_deadline, db):
    '''Update approach that works with mapper event after delete'''
    obj = await asset.read_by_id(id, db)
    obj.warranty_deadline = warranty_deadline