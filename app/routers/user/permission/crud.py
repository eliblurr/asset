from . import models, schemas
from cls import CRUD

permission = CRUD(models.Permission)
content_type = CRUD(models.ContentType)