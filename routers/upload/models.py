from sqlalchemy import Column, Enum, Unicode, Integer, event
from sqlalchemy_utils import generic_relationship
from rds.tasks import async_remove_file
from config import UPLOAD_EXTENSIONS
from mixins import BaseMixin
from utils import today_str
from database import Base
from ctypes import File
import enum
# from ..asset.crud import asset

UploadType = enum.Enum('UploadType', {v:v for v in UPLOAD_EXTENSIONS.keys()})
    
class Upload(BaseMixin, Base):
    '''Upload Model'''
    __tablename__ = "uploads"

    url = Column(File(upload_to=f'uploads/{today_str()}'), nullable=False)
    upload_type = Column(Enum(UploadType), nullable=False)

    object_type = Column(Unicode(255))
    object_id = Column(Integer, nullable=True)
    object = generic_relationship('object_type', 'object_id')

@event.listens_for(Upload, 'after_delete')
def remove_file(mapper, connection, target):
    if target.url:async_remove_file(target.url)

class UploadProxy:
    
    def _base_(self, db, type_:str, offset:int=0, limit:int=100):
        return db.query(
            Upload.url
        ).filter(
            Upload.object==self,
            Upload.upload_type==type_
        ).order_by(
            desc(Upload.created)
        ).offset(offset).limit(limit).all()
    
    def documents(self, db, offset:int=0, limit:int=100):
        return self._base_(self, db, 'document', offset, limit)

    def videos(self, db, offset:int=0, limit:int=100):
        return self._base_(self, db, 'video', offset, limit)

    def audio(self, db, offset:int=0, limit:int=100):
        return self._base_(self, db, 'audio', offset, limit)

    def images(self, db, offset:int=0, limit:int=100):
        return self._base_(self, db, 'image', offset, limit)