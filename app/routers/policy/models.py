from sqlalchemy import Column, String, Integer, CheckConstraint
from mixins import BaseMixin
from database import Base

class Policy(BaseMixin, Base):
    '''Policy Model'''
    __tablename__ = "policies"
    
    title = Column(String, nullable=False)
    metatitle = Column(String, nullable=True)
    description = Column(String, nullable=False)
    index = Column(Integer, CheckConstraint('index>0'), autoincrement=True, nullable=False, unique=True, index=True)