from typing import Optional, List, Union
import routers.proposal.models as m
from pydantic import BaseModel, validator, conint
import datetime, enum

class ProposalStatus(str, enum.Enum):
    active = 'active'
    accepted = 'accepted'
    declined = 'declined'
    delivered = 'delivered'

# inventory = relationship("Inventory", back_populates="proposals")
# department = relationship("Department", back_populates="proposals")
# inventory_id = Column(Integer, ForeignKey('inventories.id'), nullable=True)
# department_id = Column(Integer, ForeignKey('departments.id'), nullable=False)
# status = Column(Enum(ProposalStatus), default=ProposalStatus.active, nullable=False)

class ProposalBase(BaseModel):
    title: str
    justification: str
    author_id: conint(gt=0)
    metatitle: Optional[str]
    priority_id: conint(gt=0)
    description: Optional[str]
    department_id: conint(gt=0)
    inventory_id: Optional[conint(gt=0)]
    
    class Config:
        orm_mode = True

    class Meta:
        model = m.Proposal

class CreateProposal(ProposalBase):
    status: Optional[ProposalStatus]

    @validator('status')
    def _xor_(cls, v, values):
        if v==ProposalStatus.accepted:
            if not values['inventory_id']:
                raise ValueError('inventory id required')
        return v

class UpdateProposal(BaseModel):
    title: Optional[str]
    metatitle: Optional[str]
    description: Optional[str]
    justification: Optional[str]
    author_id: Optional[conint(gt=0)]
    priority_id: Optional[conint(gt=0)]
    inventory_id: Optional[conint(gt=0)]
    department_id: Optional[conint(gt=0)]

class Proposal(ProposalBase):
    id: int
    status: enum.Enum
    created: datetime.datetime
    updated: datetime.datetime

class ProposalList(BaseModel):
    bk_size: int
    pg_size: int
    data: Union[List[Proposal], list]