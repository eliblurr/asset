from utils import schema_to_model
from exceptions import NotFound
from . import models, schemas
from cls import CRUD

package = CRUD(models.Package)
subscription = CRUD(models.Subscription)

async def update_subscription(asset_id, package_id, payload, db):
    obj = db.query(models.Subscription).filter_by(asset_id=asset_id, package_id=package_id).first()
    if not obj:
        raise NotFound('subscription could not be found')
    data = schema_to_model(payload, exclude_unset=True)
    [setattr(obj, k, v) for k, v in data.items()]
    db.commit()
    db.refresh(obj)
    return obj