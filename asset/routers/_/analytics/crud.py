from dependencies import session_generator
from routers.tenant.crud import tenant
from sqlalchemy.orm import Session
from . import models, schemas
from cls import Aggregator

# base = db.query(models.Department).join(Location).filter(Location.id==loc_id) if loc_id else db.query(models.Department)

async def get_all_tenants(db:Session):
    params = {"fields":["key"], "sort":[], "q":None, "offset":None, "limit":None}
    obj = await tenant.read(params, db)
    return [item for sublist in obj.get('data') for item in sublist] 

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


from .schemas import Source
# from pydantic.dataclasses import dataclass
from pydantic import ValidationError, validator
from constants import MONTHS
from typing import Union
from sqlalchemy import literal
from database import SessionLocal, engine

# class YearFilter(BaseModel):

async def get_all_tenants(db:Session):
    params = {"fields":["key"], "sort":[], "q":None, "offset":None, "limit":None}
    obj = await tenant.read(params, db)
    return [item for sublist in obj.get('data') for item in sublist] 
    
class DateFilter(BaseModel):
    field:str = 'created'
    months:List[
        Union[
            conint(gt=0, lt=13), 
            constr(
                regex=f"^({'|'.join(set(MONTHS.keys()))})$", 
                strip_whitespace=True, 
                to_lower=True
            )
        ]
    ] = [1,2,3,4,5,6,7,8,9,10,11,12]
    year:constr(regex=r'(\d\d\d\d)$')

    @validator('months', each_item=True)
    def month_str_to_int(cls, v):
        if isinstance(v, str):
            v = MONTHS.get(v, None)
        return v

def verify_tenant(keys):
    prev_key = None
    for key in keys:
        yield key

class Av2:
    query_type = enum.Enum('QueryType', {v:v for v in ["res","subq","query"]})

    def __init__(self, model, tenant_model, branch_model):
        self.model = model
        self.branch_model = branch_model
        self.tenant_model = tenant_model

    async def op(self, aggr, sources, db:Session, date_filters:DateFilter=None, q_type:query_type='res', group_by:List[str]=[], and_filters:dict={}, or_filters:dict={}, **kw):
        
        fields, ops = zip(*[(dict(field)["field"], dict(field)["op"]) for field in aggr])

        queryset, d_fields = await self.get_queryset(fields, sources, db, date_filters, group_by, and_filters, or_filters, **kw), [] 

        queryset, db = queryset
        # print(dir(queryset), queryset.schema)

        print('ds')

        # return

        obj = [getattr(func, op)(queryset.c[field]).label(op) for op in set(ops) for field in set(fields)]

        print('ds')
        
        if date_filters:
            if date.months:
                d_fields.append(queryset.c.month)
            if date.years:
                d_fields.append(queryset.c.year)
            obj.extend(d_fields)

        if group_by:
            group_by = [queryset.c[group_by] for group_by in group_by]
            obj.extend(group_by)
            d_fields.extend(group_by)

        base = db.query(*obj).group_by(*d_fields)
        return base if q_type=='query' else base.subquery() if q_type=='subq' else base.all()


        j = queryset[0].subquery()

        q = db.query(j.c.id).select_entity_from(j)

        print(q.all())



        # p = queryset[0].subquery()

        # q = db.query(func.sum(p.c.id).label('ids'), p.c.status).group_by(p.c.status)

        # print(queryset[0].session.connection().get_execution_options())

        # [queryset.subquery() for queryset in queryset]


        # q = db.query(func.sum(p.c.id).label('ids'), p.c.status).group_by(p.c.status)

        # with engine.connect() as connection:
        #     result = connection.execute(p)
        #     for row in result:
        #         print(row)

        

        return  

        obj = [getattr(func, op)(queryset.c[field]).label(op) for op in set(ops) for field in set(fields)]

        base = db.query(*obj).select_entity_from(queryset)

        # print(dir(queryset), queryset.schema)

        # select_entity_from(select_stmt.subquery()) 
        # print({"res": base.all()})

        

        
        

        obj = [getattr(func, op)(queryset.c[field]).label(op) for op in set(ops) for field in set(fields)]

        base = db.query(*obj)
        
        # if date_filters:
        #     if date.months:
        #         d_fields.append(queryset.c.month)
        #     if date.years:
        #         d_fields.append(queryset.c.year)
        #     obj.extend(d_fields)

        # if group_by:
        #     group_by = [queryset.c[group_by] for group_by in group_by]
        #     obj.extend(group_by)
        #     d_fields.extend(group_by)

        base = db.query(*obj)

        print(base)
        # .group_by(*d_fields)
        return base if q_type=='query' else base.subquery() if q_type=='subq' else base.all()

    async def get_queryset(self, fields, sources:Union[List[Source], str], db:Session, date_filters:List[DateFilter]=[], group_by:List[str]=[], and_filters:dict={}, or_filters:dict={}, **kw):
        
        fields = [getattr(self.model, field).label(field) for field in set(fields)]
        
        if group_by:
            fields += [getattr(self.model, group_by).label(group_by) for group_by in group_by]
        
        d_fields, d_filters = [], []

        if date_filters:
            d_fields, d_filters = await self.date_filter(date_filters)
            fields.extend(d_fields)  
        
        if sources=='__all__':
            sources = [Source(tenant=tenant.key, branches='__all__') for tenant in await self.get_all_tenants(db)]
        else:
            # sources = [schemas.Source(tenant=source[0], branches=source[1]) for source in set([(source.tenant, source.branches) for source in sources])]
            pass
            # remove duplicate from sources and update sources
            # keys = set([source.tenant for source in sources])
            # res = list(zip(keys, list(map(self.verify_key, keys, [db for key in keys]))))
            # failed = [pair[0] for pair in list(filter(lambda x:x[1]==None, res))]
            # if failed:
            #     raise ValueError(f'unrecognized tenant key @ {failed}')

        querysets = list(self.query_generator(sources, fields, or_filters, and_filters, d_filters))

        # querysets = [queryset.subquery() for queryset in list(querysets)]

        # res = zip(*[(dict(field)["field"], dict(field)["op"]) for field in aggr])

        res = list(zip(*querysets))
        

        # i = union_all(*querysets).subquery()

        print(
            # dir(i),
            # querysets,
            res,
            res[1][0],
            # i.schema,
            sep='\n'
        )

        return union_all(*res[0]).subquery(), res[1][0]
        # , res[1][0]
        # union_all(*[queryset.subquery() for queryset in list(querysets)])

    async def date_filter(self, payload:List[DateFilter]):
        # res = map(self.year_filter, payload)
        return list(zip(*map(self.year_filter, payload)))

    async def year_filter(self, payload:DateFilter):
        if not await self.is_date(payload.field):
            raise ValueError(f'{payload.field} not a date field')

        fields, filters, year, months = [], [], None, None

        if payload.months:
            months = extract('month', getattr(self.model, payload.field)).label('month')
            filters.append(or_(*[months==int(month) for month in payload.months])) 
        
        if payload.years:
            year = extract('year', getattr(self.model, payload.field)).label('year')
            filters.append(or_(*[year==int(year) for year in payload.years])) 
        
        fields.extend([year, months])
        return fields, filters

    async def years_available(self, db:Session, field='created'):
        if not await self.is_date(field):
            raise ValueError(f'{field} not a date field')
        return [date[0].year for date in db.query(getattr(self.model, field).cast(Date)).distinct().all()]

    async def is_date(self, field):
        return isinstance(self.model.__table__.c[field].type, (DATETIME, DATE, Date, DateTime))

    def query_generator(self, sources:List[Source], fields, or_filters=[], and_filters={}, d_filters=None, **kwargs):
        '''query generator for multischema operations'''

        for source in sources:
            
            session = SessionLocal(
                bind=engine.execution_options(
                    schema_translate_map = {
                        None: source.tenant
                    }
                )
            )

            base = session.query(*fields)

            # print(dir(base))

            q = base.filter(or_(**or_filters), and_(**and_filters), *d_filters)
            # print(dir(q))
            yield q, session

            # try:
            #     base.join(self.branch_model)
            #     if source.branches=='__all__':
            #         yield base.filter(or_(**or_filters), and_(**and_filters), *d_filters)
            #     else:
            #         yield base.filter(self.branch_model.id.in_(source.branches), or_(**or_filters), and_(**and_filters), *d_filters)
            # except:
            #     yield base.filter(or_(**or_filters), and_(**and_filters), *d_filters)

    async def get_all_tenants(self, db:Session):
        return db.query(self.tenant_model.key).all()

    def verify_key(self, key, db:Session):
        q = db.query(self.tenant_model).filter(self.tenant_model.key==key)
        return db.query(literal(True)).filter(q.exists()).scalar()

from sqlalchemy import select

session = SessionLocal()
# models.Proposal.__table_args__ = ({None:'87a96fa3aed8fd4d80d423e1d07cb954'},)

statement = select(models.Policy)

# result = session.execute(statement).all()

# print(res/ult)

# models.Proposal.__table_args__ = ({'schema':'87a96fa3aed8fd4d80d423e1d07cb954'},)

# print(dir(models.Proposal), models.Proposal.__table_args__)
# print(models.Proposal.__table_args__, db.query(models.Proposal))

# from database import Base

# new_model = models.Proposal

# def table_factory (name, tablename, schemaname):
#     table_class = type(
#         name,
#         (Base,),
#         dict (
#             __tablename__ = tablename,
#             __table_args__ = {'schema': schemaname}
#             )
#         )
#     return table_class

# prop1 = table_factory (name = "dummy",
#                          tablename = "proposals",
#                          schemaname = 'a')

# prop2 = table_factory (name = "dummy2",
#                          tablename = "proposals",
#                          schemaname = 'b')



# def table_factory (model, schema):

#     table_class = type(
#         name,
#         (Base,),
#         dict (
#             __tablename__ = model.__tablename__,
#             __table_args__ = {None: schema}
#             )
#         )
#     return table_class

# from dependencies import session_generator

# keys = ["public", "asdasdasd", "asdasdas"]

# sessions = session_generator(keys)
# paths = [session.connection().get_execution_options() for session in session_generator(keys)]

# print(paths)

# A simple Aggregator class
# fields = ['id']
# q_type = QueryType.res -> [
#     res = "res" -> return actual results
#     subq = "subq" -> returns subquery
#     query = "query" -> returns query
# ]
# group_by = 'status'
# op = 'sum' -> [
#     count = 'count' -> for sql COUNT function
#     sum = 'sum' -> for sql SUM function
#     min = 'min' -> for sql MIN function
#     max = 'max' -> for sql MAX function
#     avg = 'avg' -> for sql AVG function
# ]
# res = zx.op(
#     fields, list(sessions), op, q_type, group_by
# )

# 1. verify sources
# 2. query generator



def get_tenant_keys(db:Session):
    return db.query(models.Tenant.key).all()

def verify_key(key, db:Session):
    q = db.query(models.Tenant).filter(models.Tenant.key==key)
    return db.query(literal(True)).filter(q.exists()).scalar()



def query_generator(sources:List[Source], fields, or_filters=[], and_filters={}, d_filters=None, **kwargs):
    '''query generator for multischema operations'''

    prev_schema = None

    for source in sources:
        session = SessionLocal(bind=engine.execution_options(schema_translate_map={prev_schema: source.tenant}))

        try:
            if source.branches=='__all__':
                yield session.query(*fields).join(models.Branch).filter(or_(**or_filters), and_(**and_filters), *d_filters)
            else:
                yield session.query(*fields).join(models.Branch).filter(models.Branch.id.in_(source.branches) ,or_(**or_filters), \
                    and_(**and_filters), *d_filters)
        except:
            yield session.query(*fields).filter(or_(**or_filters), and_(**and_filters), *d_filters)

        prev_schema = source.tenant


    # set session execution option to None if necessary

# schema_translate_map={
#         None: "user_schema_one",     # no schema name -> "user_schema_one"
#         "special": "special_schema", # schema="special" becomes "special_schema"
#         "public": None               # Table objects with schema="public" will render with no schema
#     }

def gen(ls):
    print('first line')
    for j in ls:
        print(j)
        yield j
    print('last line')

# p = gen([1,2,3])

# for i in range(3):
# print(all(p))
'''
for key, branches in source:
    if not key is valid:
        raise ValidationError(f"unrecognized key {key}")

    change key metadata to point schema to key

    q = db.query(fields).join(Branch).filter(Branch.in_(branches)).filter(**kw)
'''


# m = verify_tenant([True, True, True, True])
# j = all(m)
# print(dir(j))
   


# ls
# for i in 
# .count()