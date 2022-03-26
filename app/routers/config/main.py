from fastapi import APIRouter, HTTPException
from config import get_settings
import dotenv, os, config
from utils import logger
from . import schemas

router = APIRouter()

@router.get('/', description='Read Settings')
async def read(safe:bool=True):
    if safe:
        return {k:v for k,v in config.settings.dict().items() if k not in schemas.UNSAFE_KEYS}
    return settings.dict()

@router.patch('/', description='Update Settings')
async def update(payload:schemas.UpdateSettings):
    try:        
        file = dotenv.find_dotenv(config.settings.__config__.env_file)
        if dotenv.load_dotenv(file):
            [dotenv.set_key(file, k, str(v)) for k,v in payload.dict(exclude_unset=True).items()]  
            for k,v in dotenv.dotenv_values(file).items():os.environ[k]=v
            config.settings = get_settings()
    except Exception as e:
        logger(__name__, e, 'critical')
        raise HTTPException(status_code=417, detail=['failure', {"info":f"{e}"}])
        return 'failure', {"info":".env file could not be updated"}
    return 'success', {"info":".env file successfully updated"}