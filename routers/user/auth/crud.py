from routers.user.account.models import User
from routers.user.account.crud import user
from routers.tenant.models import Tenant
from routers.tenant.crud import tenant
from utils import http_exception_detail
from fastapi import HTTPException
from . import models, schemas
from cls import CRUD

# password_reset_code = CRUD(models.PasswordResetCode)

async def read_user_by_id(id, _type, db):
    return await user.read_by_id(id, db) if _type=='users' else await tenant.read_by_id(id, db)

async def read_user(payload, userType, db):
    model = User if userType=='users' else Tenant
    return db.query(model).filter_by(**payload.dict()).first()

async def verify_user(payload, _type, db):
    model = User if _type=='users' else Tenant
    user = db.query(model).filter_by(email=payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail=http_exception_detail(loc="email", msg="user not found", type="NotFound"))
    if not user.verify_hash(payload.password, user.password):
        raise HTTPException(status_code=401, detail=http_exception_detail(loc="password", msg="could not verify password", type="Unauthorized"))
    return user

async def activate_user(id, _type, password, db):
    model = User if _type=='users' else Tenant
    db.query(model).filter_by(id=id).update({"is_active":True, "password":password})
    db.commit()
    return "success", {"info":"account successfully activated"}

async def revoke_token(payload:schemas.Logout, db):
    db.add_all([models.RevokedToken(token=token) for token in payload.dict().values()])
    db.commit()
    return 'success', {"info":"tokens successfully blacklisted"}

async def is_token_blacklisted(token:str, db):
    return db.query(models.RevokedToken).filter_by(token=token).first() is not None