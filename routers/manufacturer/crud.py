from . import models, schemas
from cls import CRUD


manufacturer = lambda tenant=True : CRUD(models.Manufacturer2, extra_models=[models.Manufacturer]) if tenant else CRUD(models.Manufacturer, extra_models=[models.Manufacturer2])

# manufacturer = CRUD(models.Manufacturer, extra_models=[models.Manufacturer2])
# manufacturer = CRUD(models.Manufacturer)