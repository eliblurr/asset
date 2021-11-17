from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from dependencies import get_db
from . import crud, schemas
from typing import List

router = APIRouter()

@router.post('/', description='', status_code=201, name='Generate Report')
async def create(payload:int, db:Session=Depends(get_db)):
    return 

@router.get('/', description='', status_code=201, name='Analytics')
async def create(dashboard:bool=False, db:Session=Depends(get_db)):
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