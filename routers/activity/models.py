from sqlalchemy import Column, String, Integer, CheckConstraint
from mixins import BaseMixin
from database import Base

class Activity(BaseMixin, Base):
    '''FAQ Model'''
    __tablename__ = "activities"

    title = Column(String, nullable=False)
    metatitle = Column(String, nullable=True)
    description = Column(String, nullable=False)
