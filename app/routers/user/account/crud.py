from utils import schema_to_model
from . import models, schemas
from cls import CRUD

user = CRUD(models.User)

async def bk_create(payload:list, db):
    obj = [models.User(**schema_to_model(payload)) for payload in payload]
    db.add_all(obj)
    db.commit()
    [db.refresh(obj) for obj in obj]
    return obj

async def update_password(id, password, db):
    '''Update approach that works with mapper event after delete'''
    obj = await user.read_by_id(id, db)
    obj.password = password