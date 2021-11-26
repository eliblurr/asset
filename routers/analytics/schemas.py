from pydantic import BaseModel, constr, conint
from typing import List, Union, Optional
import datetime, enum

Level = enum.Enum('Level', {v:v for v in ["db","tenant"]})
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
    d_filters: Optional[DateFilter]
    available_years_fields: Optional[List[str]]
    group_by: Optional[List[str]]
    filters: Optional[Filter]
    aggr: List[FieldOp]

    class Config:  
        use_enum_values = True
    
class ResponseSchema(BaseModel):
    keys_or_ids: Union[List[int], List[str]] = []
    schemas: List[Schema]