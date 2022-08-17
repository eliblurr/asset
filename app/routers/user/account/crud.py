from utils import raise_exc, decode_jwt, schema_to_model, create_jwt
from ..auth.crud import is_token_blacklisted, revoke_token
from ..auth.models import EmailVerificationCode
from  fastapi import HTTPException, Depends
from exceptions import BlacklistedToken
from sqlalchemy.orm import Session
from ..auth.schemas import Logout
from dependencies import get_db
from . import models, schemas
from config import settings
from cls import CRUD

user = CRUD(models.User)
administrator = CRUD(models.Administrator)

async def decode_token(token:str, db:Session=Depends(get_db)):
    try:
        if await is_token_blacklisted(token, db):
            raise BlacklistedToken('token blacklisted')  
        obj = decode_jwt(token)
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=raise_exc(loc="<token>", msg=f"{e}", type=f"{e.__class__}"), 
            headers={"WWW-Authenticate": "token"})
    else:
        if obj.get('revoke_after', False):
            await revoke_token(token, db)
    return obj

async def update_password_with_code(id, account:schemas.Account, payload:schemas.UpdatePassword, db:Session):

    obj = administrator if account.value == "administrators" else user

    user = await obj.read_by_id(id, db)
    code = db.query(EmailVerificationCode).get(user.email)
    
    if not code:
        raise HTTPException(status_code=403, detail="verification code invalid or expired")    
        
    user.password = payload.password

    db.commit()

async def email_exist(email, db:Session):
    db.query()
    return True

async def gen_token(id, account:str=None, **kwargs):
    data = {"id":id, "account":account}
    data.update(kwargs)  
    return create_jwt(data, exp=settings.ACCOUNT_VERIFICATION_TOKEN_DURATION_IN_MINUTES)

async def bk_create(account:schemas.Account, payload:list, db):
    model = models.Administrator if account.value=="administrators" else models.User
    obj = [model(**schema_to_model(payload)) for payload in payload]
    db.add_all(obj)
    db.commit()
    [db.refresh(obj) for obj in obj]
    return obj