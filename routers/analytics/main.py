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

            return res

    except Exception as e:
        print(e.__class__)

# sqlalchemy.exc.ProgrammingError = 400