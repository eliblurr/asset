from typing import Optional, List
from .models import UploadType
from pydantic import BaseModel
import datetime

class UpdateUpload(BaseModel):
    pass

class UploadBase(BaseModel):
    url: str
    upload_type: UploadType

class Upload(UploadBase):
    id: int
    created: datetime.datetime
    updated: datetime.datetime

class UploadList(BaseModel):
    bk_size: int
    pg_size: int
    data: List[Upload]