from fastapi import APIRouter
from config import LOG_ROOT
import os

router = APIRouter()

@router.get('/', description='read logs')
async def read(file:str=None, ):
    for filename in os.listdir(LOG_ROOT):
        print(filename.split('.')[-1])
    # filter all filename that correspond to date

# 1. serve log static files
# 1. serve filter by date
@router.delete('/', description='delete logs')
async def delete(file:str):
    print(file)