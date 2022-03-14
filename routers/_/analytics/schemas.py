from pydantic import BaseModel, constr, conint, validator
from typing import List, Union, Optional
import datetime, enum

Level = enum.Enum('Level', {v:v for v in ["branches","tenants"]})
Op = enum.Enum('Op', {v:v for v in ["sum","min","max","avg","count"]})
Resources = enum.Enum('Resources', {v:v for v in ["inventories","departments","proposals","requests","assets","policies"]})
    
class DateFilter(BaseModel):
    years:List[constr(regex=r'(\d\d\d\d)$')]=[]
    months: List[conint(gt=0, lt=13)]=[]
    field: str = 'created'

class Filter(BaseModel):
    and_ : Optional[dict] = {}
    or_ : Optional[dict] = {}
    kw: Optional[dict] = {}

class FieldOp(BaseModel):
    field: str
    op: Op

    class Config:  
        use_enum_values = True

class Schema(BaseModel):
    resource: Resources
    group_by: Optional[List[str]]
    d_filters: Optional[DateFilter]
    available_years_fields: Optional[List[str]]
    filters: Optional[Filter]
    aggr: List[FieldOp]

    class Config:  
        use_enum_values = True

class Source(BaseModel):
    tenant: str
    branches: Union[
        List[int],
        constr(regex=r'^(__all__)$')
    ]
    
class Schema(BaseModel):
    sources: Union[
        List[Source],
        constr(regex=r'^(__all__)$')
    ]
    schemas: List[Schema]

    @validator('sources')
    def tenant_is_unique(cls, v):
        if isinstance(v, list):
            keys = [source.tenant for source in v]
            if len(set(keys))!=len(keys):    
                raise ValueError('repeating tenant keys')
        return v