from pydantic import BaseModel, constr, conint, validator
from typing import List, Union, Optional
import datetime, enum
from . import models

op = enum.Enum('op', {v:v for v in ["sum","min","max","avg","count"]})
resource = enum.Enum('resource', {v:v for v in models.objects.keys()})

class Epoch(BaseModel):
    years: List[constr(regex=r'(\d\d\d\d)$')]=[]
    months: List[conint(gt=0, lt=13)]=[]
    days: List[conint(gt=0, lt=32)]=[]
    field: str

class FieldAggr(BaseModel):
    field: str
    op: op

    class Config:  
        use_enum_values = True

class Payload(BaseModel):
    resource: resource
    fields: List[FieldAggr]
    group_by: Optional[List[str]]
    kwargs: Optional[dict] = {}
    and_ : Optional[dict] = {}
    or_ : Optional[dict] = {}
    epochs: Optional[Epoch]

class Source(BaseModel):
    tenant: str
    branches: List[int] = [] # if branches is empty use all branches

class Schema(BaseModel):
    sources: List[Source]
    params: Payload
        
    @validator('sources')
    def verify_tenant_unique(cls, v):
        tenants = [source.tenant for source in v]
        if tenants.__len__()!=set(tenants).__len__():
            raise ValueError('repeating tenant keys, must be unique')
        return v