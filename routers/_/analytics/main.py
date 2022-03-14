from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.exc import ProgrammingError
from dependencies import session_generator
from utils import http_exception_detail
from sqlalchemy.orm import Session
from dependencies import get_db
from . import crud, schemas, models
from typing import List

router = APIRouter()

from database import SessionLocal, engine

session = SessionLocal(
    bind=engine.execution_options(
        schema_translate_map = {
            None: '87a96fa3aed8fd4d80d423e1d07cb954'
        }
    )
)

# q = session.query(models.Proposal).all()

# print(q)

# bind=engine.execution_options(schema_translate_map={None: source.tenant})

# async def a():
#     for i in range(5):yield i

# async def b():
#     return list(await a())

# print(b())

# def b():
#     pass
# print(next(a()))

sources = [
    schemas.Source(tenant='87a96fa3aed8fd4d80d423e1d07cb954', branches='__all__'),
    schemas.Source(tenant='87a96fa3aed8fd4d80d423e1d07cb954', branches='__all__'),
    # schemas.Source(tenant='key', branches='__all__'),
    # schemas.Source(tenant='james', branches='__all__'),
]
# '__all__'
# h = set([(source.tenant, source.branches) for source in sources])
# n = [schemas.Source(tenant=source[0], branches=source[1]) for source in h]
# print(n)

prop = crud.Av2(models.Proposal, tenant_model=models.Tenant, branch_model=models.Branch)
fields = ['id']
aggr = [schemas.FieldOp(field='id', op='min')]

@router.post('/test')
async def test(db:Session=Depends(get_db)):
    
    try:
        # keys = ["87a96fa3aed8fd4d80d423e1d07cb954"]
        # sessions = session_generator(keys)
        # paths = [session.connection().get_execution_options() for session in session_generator(keys)]

        # from .models import Proposal
        # from .schemas import FieldOp

        # zx = crud.Aggregator(Proposal)

        # op = 'count'
        # fields = ['id']
        # q_type = 'res'
        # group_by = 'status'
        # aggr = FieldOp(
        #     op='count',
        #     field='id'
        # )
        # date = crud.D(
        #     field = 'created',
        #     years = [2020, 2021, 2018],
        #     months = [11]
        # )

        # res = await zx.op(aggr=[aggr], dbs=list(sessions), date=date, q_type=q_type, group_by=[group_by])
        #  aggr, dbs:List[Session], date:D=None, q_type:QueryType='res', group_by:List[str]=[], and_filters:dict={}, or_filters:dict={}, **kw
        # print(res)
        res = await prop.op(aggr, sources, db, q_type='res', group_by=['status'])
        print(res)
    except Exception as e:
        print(e)
    # return db.query(literal(True)).filter(q.exists()).scalar()

# permission

"""@router.post('/')
async def analytics(payload:schemas.Schema, db:Session=Depends(get_db)):    

    print(payload)
    return
    # try:
    #     print(
    #         # dir(db.connection()),
    #         db.connection().get_execution_options().keys(),
    #         sep='\n\n'
    #     )
        
    #     return 

    # except Exception as e:
    #     print(e)
    #     sqlalchemy.exc.OperationalError

    # dbs = [db]
    # if not db.connection().get_execution_options().keys():
    #     if not schema.keys_or_ids:
    #         schema.keys_or_ids = await crud.get_all_tenants(db)
    #     dbs.extend(list(session_generator(schema.keys_or_ids)))
    # else:
    #     # perf op for branches here
    #     # or_filters
    #     # do op for tenants
    #     pass

    # print(dbs)
    # return
    res = {}
    try:
        # dbs = [db]
        for schema in schema.schemas:
            kw = schema.filters.kw if schema.filters else {}
            obj = crud.switcher.get(schema.resource)
            res.update(
                {
                    schema.resource: {
                        "aggr":await obj.op(
                            aggr = schema.aggr,
                            dbs = dbs,
                            date = schema.d_filters,
                            q_type = 'res',
                            group_by = schema.group_by,
                            and_filters = schema.filters.and_ if schema.filters else {},
                            or_filters = schema.filters.or_ if schema.filters else {},
                            **kw
                        )
                    }
                }
            )
            
            if schema.available_years_fields:
                res[schema.resource].update({"years_available":{}})
                for d_field in schema.available_years_fields:
                    res[schema.resource]["years_available"].update({d_field: await obj.years(dbs[0])})

            return res

    except Exception as e:
        print(e)
        status_code = 500
        detail = http_exception_detail(type=f"{e.__class__}", msg = f"{e}")
        raise HTTPException(status_code=500 if e.__class__ not in [AttributeError, ProgrammingError] else 400, detail=detail)"""