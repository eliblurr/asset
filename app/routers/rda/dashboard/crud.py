from . import models, schemas
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, Date
from sqlalchemy.types import Date, DateTime, DATE, DATETIME
from sqlalchemy import func, distinct, and_, or_, extract
from typing import List

class Analytics:
    def __init__(self, model):
        self.model = model

    async def sum(self, fields:list, db:Session, group_by=None, order_by=None, subq=False, **kw):
        sums = [
            func.sum(
                getattr(self.model, field[0])
            ).label(
                field[1]
            ) for field in fields
        ]
        base = db.query(*sums).filter_by(**kw)
        if group_by:
            attr = getattr(self.model, group_by)
            base = db.query(*sums, attr).filter_by(**kw).group_by(attr)
        return base.subquery() if subq else base.all()

    async def count(self, fields:list, db:Session, group_by=None, order_by=None, subq=False, **kw):
        cnts = [
            func.count(
                getattr(self.model, field[0])
            ).label(
                field[1]
            ) for field in fields
        ]
        base = db.query(*cnts).filter_by(**kw)
        if group_by:
            attr = getattr(self.model, group_by)
            base = db.query(*cnts, attr).filter_by(**kw).group_by(attr)
        return base.subquery() if subq else base.all()

    async def min(self, fields:list, db:Session, group_by=None, order_by=None, subq=False, **kw):
        mins = [
            func.min(
                getattr(self.model, field[0])
            ).label(
                field[1]
            ) for field in fields
        ]
        base = db.query(*mins).filter_by(**kw)
        if group_by:
            attr = getattr(self.model, group_by)
            base = db.query(*mins, attr).filter_by(**kw).group_by(attr)
        return base.subquery() if subq else base.all()
    
    async def max(self, fields:list, db:Session, group_by=None, order_by=None, subq=False, **kw):
        maxs = [
            func.max(
                getattr(self.model, field[0])
            ).label(
                field[1]
            ) for field in fields
        ]
        base = db.query(*maxs).filter_by(**kw)
        if group_by:
            attr = getattr(self.model, group_by)
            base = db.query(*maxs, attr).filter_by(**kw).group_by(attr)
        return base.subquery() if subq else base.all()

    async def avg(self, fields:list, db:Session, group_by=None, order_by=None, subq=False,**kw):
        avgs = [
            func.avg(
                getattr(self.model, field[0])
            ).label(
                field[1]
            ) for field in fields
        ]
        base = db.query(*avgs).filter_by(**kw)
        if group_by:
            attr = getattr(self.model, group_by)
            base = db.query(*avgs, attr).filter_by(**kw).group_by(attr)
        return base.subquery() if subq else base.all()

    async def years_available(self, field, db:Session):
        dates = db.query(getattr(self.model, field).cast(Date)).distinct().all()
        return [date[0].year for date in dates]

class Aggregator:
    
    def __init__(self, model):
        self.model = model

    async def op(self, aggr, db:Session, date:schemas.DateFilter=None, group_by:List[str]=[], and_filters:dict={}, or_filters:dict={}, **kw):
        fields, ops = zip(*[(dict(field)["field"], dict(field)["op"]) for field in aggr])
        queryset, d_fields = await self.get_queryset(fields, db, date, group_by, and_filters, or_filters, **kw), []      

        obj = [getattr(func, op)(queryset.c[field]).label(op) for op in set(ops) for field in set(fields)]

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

        base = db.query(*obj).group_by(*d_fields).all()

        return [row._asdict() for row in base]
   
    async def get_queryset(self, fields:list, db:Session, date:schemas.DateFilter=None, group_by:List[str]=[], and_filters:dict={}, or_filters:dict={}, **kw):
        fields = [getattr(self.model, field).label(field) for field in set(fields)]
        if group_by:
            fields += [getattr(self.model, group_by).label(group_by) for group_by in group_by]
        d_fields,d_filters = [],[]

        if date:
            d_fields,d_filters = await self.year_filter(date)
            fields.extend(d_fields)   

        fields = [field for field in fields if field is not None]

        or_filters = [getattr(self.model, k)==v for k,v in or_filters.items()]

        # querysets = db.query(*fields).filter(or_(**or_filters)).filter(and_(**and_filters)).filter(**kw).filter(*d_filters)

        querysets = db.query(*fields).filter_by(
            **kw, **and_filters
        ).filter(*d_filters, *or_filters)

        return querysets.subquery()

    async def year_filter(self, obj:schemas.DateFilter):
        if not await self.is_date(obj.field):
            raise ValueError(f'{obj.field} not valid yyyy/mm')
        fields,filters,yObj,mObj = [],[],None,None
        if obj.months:
            mObj = extract('month', getattr(self.model, obj.field)).label('month')
            filters.append(or_(*[mObj==int(month) for month in obj.months])) 
        if obj.years:
            yObj = extract('year', getattr(self.model, obj.field)).label('year')
            filters.append(or_(*[yObj==int(year) for year in obj.years])) 
        fields.extend([yObj, mObj])
        return fields, filters

    async def years(self, db:Session, field='created_at'):
        if not await self.is_date(field):
            raise ValueError(f'{field} not date_type')
        return [date[0].year for date in db.query(getattr(self.model, field).cast(Date)).distinct().all()]

    async def is_date(self, field):
        return isinstance(self.model.__table__.c[field].type, (DATETIME, DATE, Date, DateTime))

asset = Analytics(models.Asset)
request = Analytics(models.Request)
proposal = Analytics(models.Proposal)
inventory = Analytics(models.Inventory)

switcher = {
    "department":Aggregator(models.Department),
    "inventory":Aggregator(models.Inventory),
    "proposal":Aggregator(models.Proposal),
    "request":Aggregator(models.Request),
    "asset": Aggregator(models.Asset), 
}