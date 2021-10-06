from fastapi.responses import FileResponse
from fastapi import APIRouter, Request
from datetime import datetime
from config import LOG_ROOT
from pathlib import Path
from typing import List
import os

router = APIRouter()
path = Path(LOG_ROOT)

def get_entries(file):
    DEBUG, INFO, WARNING, ERROR, CRITICAL = 0, 0, 0, 0, 0
    with open(file, 'r', encoding = 'utf-8') as f:
        for line in f.readlines():
            if ' - DEBUG - ' in line:
                DEBUG+=1
            if ' - INFO - ' in line:
                INFO+=1
            if ' - WARNING - ' in line:
                WARNING+=1
            if ' - ERROR - ' in line:
                ERROR+=1
            if ' - CRITICAL - ' in line:
                CRITICAL+=1
    return {
        "DEBUG":DEBUG,
        "INFO":INFO,
        "WARNING":WARNING,
        "ERROR":ERROR,
        "CRITICAL":CRITICAL,
    }

@router.get('/', description='Read logs')
@router.get('/download', description='Read logs')
async def read(request: Request,file:str=None, offset:int=0, limit:int=20):
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
    
@router.delete('/', description='Delete logs')
async def delete(files:List[str]):
    for file in files:
        file_path = os.path.join(path, file)
        if os.path.exists(file_path):
            os.remove(file_path)
    return "success", {"info":f"File(s) no longer exists"}