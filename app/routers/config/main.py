from fastapi import APIRouter
from config import settings
from . import schemas
import dotenv

router = APIRouter()

@router.get('/', description='Read Settings')
async def read():
    return settings.dict()
    
@router.patch('/', description='Update Settings')
async def update(payload:schemas.UpdateSettings):
    file = dotenv.find_dotenv()
    if dotenv.load_dotenv(file):
        [dotenv.set_key(file, k, v) for k,v in payload.dict(exclude_unset=True).items()]
    return 'success', {"info":".env file successfully updated"}