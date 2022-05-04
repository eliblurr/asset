from sqlalchemy import func, union_all, select, and_, or_, extract
from sqlalchemy.types import Date, DateTime, DATE, DATETIME
from sqlalchemy.dialects.postgresql import array
from database import MetaData, session as db
from . import schemas, models
from typing import List

class Aggregate:
    '''
        reading accross multiple schema 
        union field for respective model accross all schemas
        aggr result for final result

        REFERENCE EXAMPLE:
            from database import MetaData, session
            from routers.asset.models import Asset
            from sqlalchemy import func, union_all, select

            asset1 = Asset.__table__.tometadata(metadata=MetaData(schema='5e0cfddf87da708f62c1312cd20cebdb'))
            subq1 = select(asset1.c.id) 

            asset2 = Asset.__table__.tometadata(metadata=MetaData(schema='6ece118caa5d398ae551f68b784b75dc'))
            subq2 = select(asset2.c.id)

            union = union_all(subq1, subq2).subquery()

            q = select(func.sum(union.c.id).label('sum'), union.c.id).group_by(union.c.id)

            res = session.execute(q)

            print(subq1, subq2, union, q, res.mappings().all(), sep='\n\n')
    '''

    def __init__(self, model):
        self.table = model.__table__

    async def aggregate(self, field_aggr:List[schemas.FieldAggr], sources:schemas.Source, epochs:schemas.Epoch=None, group_by:List[str]=[], return_query:bool=False, and_f:dict={}, or_f:dict={}, **kwargs):
        'This function performs aggregation'

        filters = list(and_f.keys())+list(or_f.keys())+list(kwargs.keys())
        if epochs: filters.append(epochs.field)
        fields = set([dict(field)['field'] for field in field_aggr]+group_by)
        
        for field in filters: await self._is_attribute(field, loc=['filters', 'epochs'])
        for field in fields: await self._is_attribute(field, loc=['fields', 'group_by'])
        for source in sources: await self._verify_source(sources)
        
        queryset, grouping = await self._get_queryset(fields=fields, sources=sources, epochs=epochs), []
        args = [getattr(func, aggr.op)(queryset.c[aggr.field]).label(aggr.op+'__'+aggr.field) for aggr in field_aggr]
        
        if group_by:
            grouping.extend([queryset.c[field] for field in group_by])

        if epochs:
            if epochs.months:grouping.append(queryset.c.month)
            if epochs.years: grouping.append(queryset.c.year)
        
        args.extend(grouping)
        q = select(*args).group_by(*grouping)
        res = db.execute(q)
        
        return res if return_query else res.mappings().all()

    async def _get_queryset(self, fields, sources, epochs, and_f:dict={}, or_f:dict={}, **kwargs):
        'This function constructs subqueries'

        tenants, queries, fields, epoch_fltrs = [dict(source)['tenant'] for source in sources], [], list(fields), []

        if epochs:
            epoch_fltrs = await self._process_epochs(epochs)

        for tenant in tenants:
            # do joins with branches[might be different for each resource]
            tbl = self.table.tometadata(metadata=MetaData(schema=tenant))

            if epochs:
                months = extract('month', getattr(tbl.c, epochs.field)).label('month')
                years = extract('year', getattr(tbl.c, epochs.field)).label('year')
                fields.extend([months, years, epochs.field])
            
            stmt = select([tbl.c[field].label(field) if type(field)==str else field for field in fields]).where(and_(**and_f)).where(or_(**or_f)).where(and_(**kwargs)).where(epoch_fltrs)
            queries.append(stmt)

        return union_all(*queries).subquery()

    async def _process_epochs(self, epochs):
        'This fuction processes and verifies epoch and returns filters'

        await self._is_date(epochs.field)

        months = extract('month', getattr(self.table.c, epochs.field)).label('month')
        years = extract('year', getattr(self.table.c, epochs.field)).label('year')
        days = extract('day', getattr(self.table.c, epochs.field)).label('day')

        filters = and_(
            or_(*[months==int(month) for month in epochs.months]),
            or_(*[years==int(years) for year in epochs.years]),
            or_(*[days==int(day) for day in epochs.days]),
        )
        
        return filters

    async def _is_attribute(self, field, loc=None):
        'This function checks if a field ia an attribute of model'
        try: getattr(self.table.c, field)
        except: raise KeyError(f'{field} in not a valid attribute. {"loc: "+str(loc) if loc else ""}')

    async def _verify_source(self, sources):
        'This function verifies tenants and their branches'
        'check if list of branches for a given tenant is a valid subset of that tenants branches'

        for source in sources:
            tbl = self.table.tometadata(metadata=MetaData(schema=source.tenant))

            source_branches = array(source.branches)
            tenant_branches = func.array(db.query(tbl.c.id).as_scalar())

            is_valid = db.query(source_branches.contained_by(tenant_branches)).scalar()

            if not is_valid:
                raise ValueError(f'some branches provided are not valid tenant branches')
        
    async def _is_date(self, field):
        if not isinstance(self.table.c[field].type, (DATETIME, DATE, Date, DateTime)):
            raise KeyError(f'{field} in not a valid date type.')


# check if list of branches for a given tenant is valid or subset of that tenants branches

# tbl = models.Asset.__table__
# tbl = tbl.tometadata(metadata=MetaData(schema='6ece118caa5d398ae551f68b784b75dc'))
# ids = array([1, 4])
# ls = func.array(
#     db.query(tbl.c.id).as_scalar()
# )
# valid = db.query(
#     ids.contained_by(ls)
# ).scalar()
# print(valid)

# payload = {
#     "sources": [
#         {
#             "tenant": "6ece118caa5d398ae551f68b784b75dc",
#             "branches": [ ]
#         },
#         {
#             "tenant": "5e0cfddf87da708f62c1312cd20cebdb",
#             "branches": [ ]
#         }
#     ],
#     "params": {
#         "resource": "assets",
#         "fields": [
#             {
#                 "field": "id",
#                 "op": "count"
#             },
#             {
#                 "field": "price",
#                 "op": "sum"
#             }
#         ],
#         "group_by": [
#             "id"
#         ]
#     }
# }

# test = Aggregate(models.Asset)
# test.aggregate(
#     payload['params']['fields'],
#     payload['sources'], 
#     group_by=payload['params']['group_by']
# )