from fastapi.responses import FileResponse
from fastapi import APIRouter
from config import LOG_ROOT
from pathlib import Path
from typing import List
import os

router = APIRouter()
# , response_class=FileResponse

@router.get('/files', description='Read logs')
async def read_sd(file:str=None, ):
    files = [FileResponse(file) for file in Path(LOG_ROOT).iterdir() if file.is_file()]
    # print('sd')
    print(files)
    return files
    
    # f = []
    # for file in files:
    #     if file.is_file():
    #         f.append(file)

    # print(f)
    # return f
 
@router.delete('/', description='Delete logs')
async def delete(file:str):
    pass

# file = Path(LOG_ROOT).iterdir()

# files = Path(LOG_ROOT).iterdir()

# for file in files:
#     if file.is_file():
#         print(file.name)

# print(dir(os.listdir(LOG_ROOT)[1]))

    # print(filename.split('.')[-1])
# filter all filename that correspond to date

# 1. serve log static files
# 1. serve filter by date
# for file in os.scandir(LOG_ROOT):
# print(dir(os.scandir(LOG_ROOT)[2]))

# print(files)
# for file in files.iterdir():
#     print(file.name)
# print(dir(files.iterdir()[4]))



# from fastapi import FastAPI, File, UploadFile


# List all files in a directory using os.listdir
# basepath = 'my_directory/'
# for entry in os.listdir(basepath):
#     if os.path.isfile(os.path.join(basepath, entry)):
#         print(entry)

# # List all files in a directory using scandir()
# basepath = 'my_directory/'
# with os.scandir(basepath) as entries:
#     for entry in entries:
#         if entry.is_file():
#             print(entry.name)

# from pathlib import Path

# basepath = Path('my_directory/')
# files_in_basepath = basepath.iterdir()
# for item in files_in_basepath:
#     if item.is_file():
#         print(item.name)