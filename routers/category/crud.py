from typing import Optional, List
from . import models, schemas
from cls import CRUD

category = CRUD(models.Category)
schema = {
    schemas.Resource.assets: (CRUD(models.CategoryAsset), schemas.CategoryAsset),
    schemas.Resource.vendors: (CRUD(models.CategoryVendor), schemas.CategoryVendor)
}

async def add_to_category(id:int, ids:List[int], child:schemas.Resource, db):
    schema = schema.get(child)
    payload = [schema[1](c_id=c_id, category_id=id) for c_id in ids]
    return await schema[0].bk_create(payload, db)

async def rem_from_category(id:int, ids:List[int], child:schemas.Resource, db):
    schema = schema.get(child)
    payload = [schema[1](c_id=c_id, category_id=id) for c_id in ids]
    for obj in payload:
        await schema[0].bk_delete_2(db, obj)
    return "success"