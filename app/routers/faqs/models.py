from sqlalchemy import Column, String, Integer, CheckConstraint
from mixins import BaseMixin
from database import Base

class FAQ(BaseMixin, Base):
    '''FAQ Model'''
    __tablename__ = "faqs"

    title = Column(String, nullable=False)
    metatitle = Column(String, nullable=True)
    description = Column(String, nullable=False)
    index = Column(Integer, CheckConstraint('index>0'), autoincrement=True, nullable=False, unique=True, index=True)