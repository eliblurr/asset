from config import settings, Settings
from fastapi import APIRouter
from utils import logger
from . import schemas
import dotenv

from importlib import reload
import config as cfg

router = APIRouter()

@router.get('/', description='Read Settings')
async def read(safe:bool=True):
    if safe:
        return {k:v for k,v in settings.dict().items() if k not in schemas.UNSAFE_KEYS}
    return settings.dict()

@router.patch('/', description='Update Settings')
async def update(payload:schemas.UpdateSettings):
    try:
        file = dotenv.find_dotenv()
        if dotenv.load_dotenv(file):
            [dotenv.set_key(file, k, str(v)) for k,v in payload.dict(exclude_unset=True).items()]  
    except Exception as e:
        logger(__name__, e, 'critical')
        return 'failure', {"info":".env file could not be updated"}
    else:
        pass
        # cfg.settings = cfg.Settings() reset settings here
    return 'success', {"info":".env file successfully updated"}