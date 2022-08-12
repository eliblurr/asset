from routers.user.account.models import User, Administrator
from datetime import timedelta, datetime
from sqlalchemy.orm import Session
from database import SessionLocal
from fastapi import HTTPException
from scheduler import scheduler
from . import models, schemas
from utils import raise_exc
from typing import Union

async def verify_user(payload:schemas.Login, account:str, db:Session):

    model = User if account=="users" else Administrator        
    user = db.query(model).filter_by(email=payload.email).first()

    if not user:
        raise HTTPException(status_code=404, detail=raise_exc("email", "user not found", "NotFound"))
    if user.verify_hash(payload.password, user.password):
        return user
    raise HTTPException(status_code=401, detail=raise_exc("password", "wrong credentials", "Unauthorized"))
    
    # except Exception as e:
    #     print(e)

def read_by_id(id:str, account:schemas.Account, db:Session):
    model = User if account=="users" else Administrator
    return db.query(model).get(id)

async def read_by_email(email:str, account:str, db:Session):
    model = User if account=="users" else Administrator
    return db.query(model).filter_by(email=email).first()

async def is_token_blacklisted(token:str, db:Session):
    return db.query(models.RevokedToken.id).filter_by(jti=token).first() is not None

async def add_email_verification_code(email, account:schemas.Account, db:Session):
    model = User if account=="users" else Administrator
    user = db.query(model).filter_by(email=email)
    if not user:
        raise HTTPException(status_code=404, detail=raise_exc("email", "user not found", "NotFound"))
    obj = models.EmailVerificationCode(email=email)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

async def revoke_token(payload:Union[schemas.Logout, str], db:Session):
    try:
        if isinstance(payload, str):
            db.add(models.RevokedToken(jti=payload))
        else:
            db.add_all([models.RevokedToken(jti=token) for token in payload.dict().values()])
        db.commit()
        return 'success', 'token(s) successfully blacklisted'
    except Exception as e: 
        print(e)

def del_code(email, db:Session=SessionLocal()):
    obj = db.query(models.EmailVerificationCode).filter_by(email=email).delete()
    # User.query.filter(User.id == 123).delete()
    # .get(email)
    # 
    # if obj:
    #     db.delete(obj)
    db.commit()
    return True

def schedule_del_code(email):
    from config import settings
    return scheduler.add_job(
        del_code,
        trigger='date',
        kwargs={'email':email},
        id=f'ID-{email}',
        replace_existing=True,
        run_date=datetime.utcnow() + timedelta(minutes=settings.EMAIL_CODE_DURATION_IN_MINUTES)
    )