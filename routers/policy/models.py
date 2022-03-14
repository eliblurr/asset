from sqlalchemy import Column, String, Integer, CheckConstraint
from mixins import BaseMixin
from database import Base

class Policy(BaseMixin, Base):
    '''Policy Model'''
    __tablename__ = "policies"
    __table_args__ = ({'schema':'public'},)
    CheckConstraint('index > 0', name='check2')
    
    title = Column(String, nullable=False)
    metatitle = Column(String, nullable=True)
    description = Column(String, nullable=False)
    index = Column(Integer, autoincrement=True, nullable=False, unique=True, index=True) #, CheckConstraint('index>0'),