from pydantic import BaseModel, constr, conint
from typing import List, Optional
import enum

Op = enum.Enum('Op', {v:v for v in ["sum","min","max","avg","count"]})
Resources = enum.Enum('Resources', {v:v for v in ["inventory","department","proposal","request","asset"]})
    
class DateFilter(BaseModel):
    years:List[constr(regex=r'(\d\d\d\d)$')]=[]
    months: List[conint(gt=0, lt=13)]=[]
    field: str = 'created_at'

class ExtraFilter(BaseModel):
    and_ : Optional[dict] = {}
    or_ : Optional[dict] = {}
    kw: Optional[dict] = {}

class AggregationField(BaseModel):
    field: str
    op: Op

    class Config:  
        use_enum_values = True

class Schema(BaseModel):
    resource: Resources
    group_by: Optional[List[str]]
    date_filters: Optional[DateFilter]
    years_available_fields:Optional[List[str]]
    filters: Optional[ExtraFilter]
    aggr: List[AggregationField]

    class Config:  
        use_enum_values = True