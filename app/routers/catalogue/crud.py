from typing import Optional, List
from . import models, schemas
from cls import CRUD

catalogue = CRUD(models.Catalogue)
catalogue_asset = CRUD(models.CatalogueAsset)

async def add_to_catalogue(id:int, ids:List[int], db):
    payload = [schemas.CatalogueAsset(asset_id=a_id, catalogue_id=id) for a_id in ids]
    return await catalogue_asset.bk_create(payload, db)

async def rem_from_catalogue(id:int, ids:List[int], db):
    # payload = [schemas.CatalogueAsset(asset_id=a_id, catalogue_id=id) for a_id in ids]
    # for obj in payload:
    #     await catalogue_asset.bk_delete_2(db, obj)
    # return 

    return await catalogue_asset.bk_delete_2(ids, db, use_field='asset_id', catalogue_id=id)