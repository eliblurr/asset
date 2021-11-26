from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from dependencies import get_db
from . import crud, schemas
from typing import List

router = APIRouter()

@router.post('/{level}/aggregator')
async def create(schema:schemas.ResponseSchema, level:schemas.Level, db:Session=Depends(get_db)):
    res = {}
    try:
        dbs = [db]
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

            print(
                res[schema.resource],
                sep="\n"
            )

            return res

    except Exception as e:
        print(e)

    

# @router.post('/reports/{resource}', description='', status_code=200, name='Generate Report')
# async def create(level:schemas.Level, resource:schemas.AResource, db:Session=Depends(get_db)):
#     return 

# @router.post('/dashboard', description='', status_code=200, name='Analytics')
# async def create(level:schemas.Level, keys_or_ids:list=Body(...), db:Session=Depends(get_db)):
#     if level==schemas.Level.db:
#         return await crud.db_aggregator(keys_or_ids, db)
#     if level==schemas.Level.tenant:
#         return await crud.tenant_aggregator(keys_or_ids, db)