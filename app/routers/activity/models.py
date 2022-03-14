from sqlalchemy import Column, String, JSON, Unicode, Integer
from sqlalchemy_utils import generic_relationship
from mixins import BaseMixin
from database import Base

class Activity(BaseMixin, Base):
    '''Activity Model'''
    __tablename__ = "activities"

    meta = Column(JSON, nullable=False)
    message = Column(String, nullable=False)
    
    object_type = Column(Unicode(255))
    object_id = Column(Integer, nullable=False)
    object = generic_relationship('object_type', 'object_id')