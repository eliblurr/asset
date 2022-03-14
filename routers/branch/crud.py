from . import models, schemas
from cls import CRUD

branch = CRUD(models.Branch)

# assets -> asset.join(inv).join(dep).filter(dep.bid=bid)
# inventories -> inv.join(dep).filter(dep.bid=bid)
# departments -> use related name

# from routers.asset.crud import asset
# from routers.inventory.crud import inventory
# from routers.department.crud import department

# from database import SessionLocal

# db = SessionLocal()

# base = db.query(inventory.model)
# bas

# print(base)

# async def read_inventory(d_id:int, params, db):
#     return await inventory.read()

# # branch_departments = CRUD(models.BranchDepartment)

# async def add_department(resource_id, related_resource_ids, resource, db):
#     payload = [schemas.BranchDepartment(branch_id=resource_id, department_id=id)for id in related_resource_id]
#     return await branch_departments.bk_create(payload, db)

# async def remove_department(resource_id, related_resource_ids, resource, db):
#     return await branch_departments.bk_delete(related_resource_id, db, use_field=department_id, branch_id=resource_id)