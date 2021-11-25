from fastapi import APIRouter, Depends, Body, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from dependencies import get_db
from . import crud, schemas
from constants import DT_Z
from typing import List

router = APIRouter()

@router.post('/test')
async def create(db:Session=Depends(get_db)):
    return 

# # years:List[str]=Query(None, regex=DT_Z),
# @router.post('/reports/{resource}', description='', status_code=200, name='Generate Report')
# async def create(level:schemas.Level, resource:schemas.AResource, db:Session=Depends(get_db)):
#     return 

# @router.post('/dashboard', description='', status_code=200, name='Analytics')
# async def create(level:schemas.Level, keys_or_ids:list=Body(...), db:Session=Depends(get_db)):
#     if level==schemas.Level.db:
#         return await crud.db_aggregator(keys_or_ids, db)
#     if level==schemas.Level.tenant:
#         return await crud.tenant_aggregator(keys_or_ids, db)