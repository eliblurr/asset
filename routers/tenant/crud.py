from . import models, schemas
from cls import CRUD

tenant = CRUD(models.Tenant)

async def delete(id, db):
    '''Delete approach that works with mapper event after delete'''
    obj, cnt = await tenant.read_by_id(id, db), 0
    if obj:
        db.delete(obj)
        cnt += 1
        db.commit()        
    return "success", {"info":f"{cnt} row(s) deleted"}

async def update():
    '''Update approach that works with mapper event after delete'''
    pass

tenant.delete = delete