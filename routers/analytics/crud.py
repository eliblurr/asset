from dependencies import session_generator
from sqlalchemy.orm import Session
from . import models, schemas
from cls import Aggregator

from sqlalchemy import func, distinct, union_all, and_, or_, extract
from sqlalchemy.types import Date, DateTime, DATE, DATETIME
from pydantic import BaseModel, conint, constr
from typing import List
import enum

class D(BaseModel):
    field: str = 'created'
    months: List[conint(gt=0, lt=13)]=[]
    years:List[constr(regex=r'(\d\d\d\d)$')]=[]

class Aggregator:
    """
        A simple Aggregator class
        fields = ['id']
        q_type = QueryType.res -> [
            res = "res" -> return actual results
            subq = "subq" -> returns subquery
            query = "query" -> returns query
        ]
        group_by = 'status'
        op = 'sum' -> [
            count = 'count' -> for sql COUNT function
            sum = 'sum' -> for sql SUM function
            min = 'min' -> for sql MIN function
            max = 'max' -> for sql MAX function
            avg = 'avg' -> for sql AVG function
        ]
        res = zx.op(
            fields, list(sessions), op, q_type, group_by
        )
    """
    Op = enum.Enum('Op', {v:v for v in ["sum","min","max","avg","count"]})
    QueryType = enum.Enum('QueryType', {v:v for v in ["res","subq","query"]})
    
    def __init__(self, model):
        self.model = model

    async def op(self, aggr, dbs:List[Session], date:D=None, q_type:QueryType='res', group_by:List[str]=[], and_filters:dict={}, or_filters:dict={}, **kw):
        fields, ops = zip(*[(dict(field)["field"], dict(field)["op"]) for field in aggr])
        queryset, d_fields = await self.get_queryset(fields, dbs, date, group_by, and_filters, or_filters, **kw), []            
        obj = [getattr(func, op)(queryset.c[field]) for op in set(ops) for field in set(fields)]

        if date:
            if date.months:
                d_fields.append(queryset.c.month)
            if date.years:
                d_fields.append(queryset.c.year)
            obj.extend(d_fields)

        if group_by:
            group_by = [queryset.c[group_by] for group_by in group_by]
            obj.extend(group_by)
            d_fields.extend(group_by)

        base = dbs[0].query(*obj).group_by(*d_fields)
        return base if q_type=='query' else base.subquery() if q_type=='subq' else base.all()
   
    async def get_queryset(self, fields:list, dbs:List[Session], date:D=None, group_by:List[str]=[], and_filters:dict={}, or_filters:dict={}, **kw):
        fields = [getattr(self.model, field).label(field) for field in set(fields)]
        if group_by:
            fields += [getattr(self.model, group_by).label(group_by) for group_by in group_by]
        d_fields,d_filters = [],[]
        if date:
            d_fields,d_filters = await self.year_filter(date)
            fields.extend(d_fields)    
        querysets = [
            db.query(*fields).filter(or_(**or_filters)).filter(and_(**and_filters)).filter(**kw).filter(*d_filters)
            for db in dbs
        ]
        return union_all(*querysets).subquery()

    async def year_filter(self, obj:D):
        if not await self.is_date(obj.field):
            raise ValueError(f'{obj.field} not date_type')
        fields,filters,yObj,mObj = [],[],None,None
        if obj.months:
            mObj = extract('month', getattr(self.model, obj.field)).label('month')
            filters.append(or_(*[mObj==int(month) for month in obj.months])) 
        if obj.years:
            yObj = extract('year', getattr(self.model, obj.field)).label('year')
            filters.append(or_(*[yObj==int(year) for year in obj.years])) 
        fields.extend([yObj, mObj])
        return fields, filters

    async def years(self, db:Session, field='created'):
        if not await self.is_date(field):
            raise ValueError(f'{field} not date_type')
        return [date[0].year for date in db.query(getattr(self.model, field).cast(Date)).distinct().all()]

    async def is_date(self, field):
        return isinstance(self.model.__table__.c[field].type, (DATETIME, DATE, Date, DateTime))

switcher = {
    "inventories":Aggregator(models.Inventory),
    "departments":Aggregator(models.Department),
    "proposals":Aggregator(models.Proposal),
    "requests":Aggregator(models.Request),
    "policies": Aggregator(models.Policy),
    "assets": Aggregator(models.Asset), 
}

# Analytics & Report generation (DB level, Schema(s)/Tenant(s) level, Branch(es) level)
# Aggregations By some factor of some fields (DB level, Schema(s)/Tenant(s) level, Branch(es) level) .eg. group monetary value by currency
#               db
#             /    \
#       tenant      tenant
#        / \         | \
#       /   \        |  \
#      /     \       |   \
#   branch branch branch branch
# 
# ?level=db -> payload:tenants=[some tenant list, *] 
# ?level=tenant -> payload:branches=[some branch list, *]
# min, max, count, avg, sum
# order_by, group_by

# Assets
# - total count
# - total count by status
# - total count by numerable
# - total count by numerable
# - sum of prices by currency
# - total count by consumable
# - total value by consumable
# - total count by year [created]
# - total count by month [created]
# - total count of decomission assets
# - total asset value after depreciation

# Inventory
# - assets groupings in inventory
# - proposal count[grouping by status]
# - count of request[grouping by status]

# Department
# - assets groupings in inventory
# - proposal count[grouping by status]
# - count of request[grouping by status]

# Request
# - total requests
# - request count by status'
# - value of accepted[or other status'] request assets

# Proposal
# - total count by status' 
# - total count of proposals

# Finance
# total value by currency 