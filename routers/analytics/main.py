from fastapi import APIRouter, Depends, Body
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from dependencies import get_db
from . import crud, schemas
from typing import List

router = APIRouter()

# for tenant, for db

# from routers.currency.models import Currency

# from database import SessionLocal

# db = SessionLocal()

# # year = crud.dates_available('created', Currency, db)

# c = crud.Analytics(Currency)
# fields = [('id', 'sum_of_ids'),]
# # values
# r = c.avg( fields, db)
# print(r)

a = ['*', 'sdf']

print('*' in a )

@router.post('/', description='', status_code=201, name='Generate Report')
async def create(payload:int, db:Session=Depends(get_db)):
    return 

@router.post('/dashboard', description='', status_code=200, name='Analytics')
async def create(level:schemas.Level, payload:list=Body(...), db:Session=Depends(get_db)):
    if level==schemas.Level.db:
        # body contains list of tenant keys
        pass
    if level==schemas.Level.tenant:
        # body contains list of branch ids
        pass
    assets = {
        'years':0,
        'count':0,
        'count_by_status':{
            'decomissioned':0,
            'numerable':0,
            'consumable':0
        },
        'value':{
            'GHC':0,
            'USD':0
        },
        'value_by_status':{
            'decomissioned':0,
            'numerable':0,
            'consumable':0
        },
        'count_by_years':{
            '2001':{
                'count':0,
                'count_by_status':{
                    'decomissioned':0,
                    'numerable':0,
                    'consumable':0
                },
            }
        },
        'total':0,
        'total':0,
        'total':0,
        'total':0,
        'total':0,
        'total':0,
        'total':0, 
    }

    if dashboard:
        return 'dashboard data'
    return 

'''
    if file:
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            if request.url.path=='/logs/download':
                return FileResponse(file_path, media_type='text/plain', filename=f"{file}.log")
            return FileResponse(file_path, media_type='text/plain', stat_result=os.stat(file_path))
        else:
            return "error", {"info":f"File not found"}  
    files_gen_to_list = list(path.iterdir())
    files = [
        {
            "filename": file.name,
            "path": file.as_posix(),
            "entries": get_entries(file)
        }
        for file in files_gen_to_list[offset:offset+limit] if file.is_file()
    ]  
    return {
        "bk_size": files_gen_to_list.__len__(),
        "pg_size": files.__len__(),
        "data": files
    }
'''