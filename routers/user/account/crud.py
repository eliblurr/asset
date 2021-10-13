from . import models, schemas
from cls import CRUD

user = CRUD(models.User)

async def update_password(id, password, db):
    '''Update approach that works with mapper event after delete'''
    obj = await user.read_by_id(id, db)
    obj.password = password