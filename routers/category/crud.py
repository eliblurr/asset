from . import models, schemas
from cls import CRUD

category = CRUD(models.Category)
category_asset = CRUD(models.CategoryAsset)
category_vendor = CRUD(models.CategoryVendor)