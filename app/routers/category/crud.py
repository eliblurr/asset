from . import models, schemas
from typing import List
from cls import CRUD

category = CRUD(models.Category)

schema = {
    schemas.RelatedResource.vendors: (CRUD(models.CategoryVendor), schemas.CategoryVendor, 'vendor_id'),
    schemas.RelatedResource.consumables: (CRUD(models.CategoryConsumable), schemas.CategoryConsumable, 'consumable_id'),
    schemas.RelatedResource.assets: (CRUD(models.CategoryAsset), schemas.CategoryAsset, 'asset_id')
}

async def add_resource_to_category(resource_id: int, related_resource_id: List[int], child:schemas.RelatedResource, db):
    obj = schema.get(child)
    payload = [obj[1](category_id=resource_id, c_id=id)for id in related_resource_id]
    return await obj[0].bk_create(payload, db)

async def rem_resource_from_category(resource_id: int, related_resource_id: List[int], child:schemas.RelatedResource, db):
    obj = schema.get(child)
    return await obj[0].bk_delete(related_resource_id, db, use_field=obj[2], category_id=resource_id)