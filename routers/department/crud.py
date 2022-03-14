from . import models, schemas
from typing import List
from cls import CRUD

department = CRUD(models.Department)
base_department = CRUD(models.BaseDepartment)

# from routers.asset.crud import asset

async def read_department_assets(id, params, db):
    pass

# asset.join(inv).filter(inv.did=did)

# try:
#         base = db.query(models.Item)
#         if loc_id:
#             q1, q2, q3 = base.join(Department).filter(Department.location_id==loc_id), \
#             base.join(Inventory).filter(Inventory.location_id==loc_id), base.join(Inventory).join(Department).filter(Department.location_id==loc_id)
#             base = q1.union(q2).union(q3)
#         bk_size = base.count()
#         if search and value:
#             try:
#                 if models.Item.__table__.c[search].type.python_type==bool or models.Item.__table__.c[search].type.python_type==int or models.Item.__table__.c[search].type.python_type==models.DepreciationAlgorithm:
#                     base = base.filter(models.Item.__table__.c[search]==value)
#                 else:
#                     base = base.filter(models.Item.__table__.c[search].like("%" + value + "%"))
#             except KeyError:
#                 pass
#         data = base.offset(skip).limit(limit).all()
#         return {'bk_size':bk_size, 'pg_size':data.__len__(), 'data':data}
#     except:
#         raise HTTPException(status_code=422, detail="{}: {}".format(sys.exc_info()[0], sys.exc_info()[1]))