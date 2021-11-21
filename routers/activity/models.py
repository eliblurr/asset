from sqlalchemy import Column, String, Integer, CheckConstraint, JSON, ForeignKey
from sqlalchemy.orm import relationship
from mixins import BaseMixin
from database import Base

class Activity(BaseMixin, Base):
    '''Activity Model'''
    __tablename__ = "activities"

    meta = Column(JSON, nullable=False)
    msg = Column(String, nullable=False)
    
    asset_id = Column(Integer, ForeignKey('assets.id'))
    request_id = Column(Integer, ForeignKey('requests.id'))
    proposal_id = Column(Integer, ForeignKey('proposals.id'))

    __table_args__ = (
        CheckConstraint(
            """
                (
                    (asset_id IS NOT NULL AND COALESCE(request_id, proposal_id, restaurant_id) IS NULL) 
                OR  (request_id IS NOT NULL AND COALESCE(asset_id, proposal_id, restaurant_id) IS NULL) 
                OR  (proposal_id IS NOT NULL AND COALESCE(asset_id, request_id, restaurant_id) IS NULL) 
                ) 
                AND COALESCE(request_id, asset_id, proposal_id) IS NOT NULL
            """
        , name="single_fk_allowed"),
    )