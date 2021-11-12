from . import models, schemas
from cls import CRUD

tenant = CRUD(models.Tenant)

async def delete(id, db):
    '''Delete approach that works with mapper event after delete'''
    obj, cnt = db.query(models.Tenant).get(id), 0
    if obj:
        db.delete(obj)
        db.commit()
        cnt += 1
    return "success", {"info":f"{cnt} tenant(s) deleted"}

async def update_password(id, password, db):
    '''Update approach that works with mapper event after delete'''
    obj = await tenant.read_by_id(id, db)
    obj.password = password

tenant.delete = delete