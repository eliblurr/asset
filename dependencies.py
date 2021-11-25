from fastapi import Request, Header, HTTPException, Depends
from routers.user.auth.crud import is_token_blacklisted
from utils import http_exception_detail, decode_jwt
from jwt.exceptions import ExpiredSignatureError
from database import SessionLocal, engine
from exceptions import BlacklistedToken
from main import oauth2_scheme
from config import settings

def get_db(request:Request):
    try:
        yield request.state.db
    finally:
        request.state.db.close()

def session_generator(schemas):
    prev_schema = None
    for schema in schemas:
        yield SessionLocal(bind=engine.execution_options(schema_translate_map={prev_schema: str(schema)}))
        prev_schema = schema

# Global Dependency
# app = FastAPI(dependencies=[Depends(verify_token), Depends(verify_key)])
async def verify_key(x_key: str = Header(...)):
    if x_key != settings.API_KEY:
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key

async def validate_bearer(token:str=Depends(oauth2_scheme), db=Depends(get_db)):
    try:
        # if await is_token_blacklisted(token, db):
        #     raise BlacklistedToken('token blacklisted')  
        return token, decode_jwt(token)
    except Exception as e:
        raise HTTPException(
            status_code=401 if isinstance(e, ExpiredSignatureError) else 500, 
            detail=http_exception_detail(loc="Bearer <token>", msg=f"{e}", type=f"{e.__class__}"), 
            headers={"WWW-Authenticate": "Bearer"}
        )
