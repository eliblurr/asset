import routers.upload.models as m, datetime
from typing import Optional, List, Union
from pydantic import BaseModel

class UpdateUpload(BaseModel):
    pass

class UploadBase(BaseModel):
    url: str
    upload_type: m.UploadType

    class Config:
        orm_mode = True

    class Meta:
        model = m.Upload

class Upload(UploadBase):
    id: int
    object_type: str
    created: datetime.datetime
    updated: datetime.datetime

class UploadList(BaseModel):
    bk_size: int
    pg_size: int
    data: Union[List[Upload], list]

params = {'offset': 0, 'limit': 100, 'fields': None, 'q': None, 'sort': ['created']}