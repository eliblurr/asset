from . import models, schemas
from typing import List
from cls import CRUD

from routers.inventory.crud import inventory
from routers.proposal.crud import proposal
from routers.user.account.crud import user
from routers.request.crud import request
from routers.asset.crud import asset

department = CRUD(models.Department)

scheme = {
    schemas.DResource.staff: (user, getattr(models.Department, 'staff')),
    schemas.DResource.assets: (asset, getattr(models.Department, 'assets')),
    schemas.DResource.requests: (request, getattr(models.Department, 'requests')),
    schemas.DResource.proposals: (proposal, getattr(models.Department, 'proposals')),
    schemas.DResource.inventories: (inventory, getattr(models.Department, 'inventories'))
}

async def add_to_department(id:int, ids:List[int], child:schemas.DResource, db):
    scheme = scheme.get(child)
    dep = await department.read_by_id(id, db)
    if dep:
        obj = await scheme[0].read_by_id(id, db)
        if obj and (obj not in scheme[1]):
            scheme[1].append(obj)
        db.commit()
        db.refresh(dep)
        return dep

async def rem_from_department(id:int, ids:List[int], child:schemas.DResource, db):
    scheme = scheme.get(child)
    dep = await department.read_by_id(id, db)
    if dep:
        obj = await scheme[0].read_by_id(id, db)
        if obj and (obj in scheme[1]):
            scheme[1].remove(obj)
        db.commit()
        db.refresh(dep)
        return dep