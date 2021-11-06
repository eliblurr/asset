from . import models, schemas
from cls import CRUD

asset = CRUD(models.Asset)
image = CRUD(models.AssetImage)
document = CRUD(models.AssetDocument)