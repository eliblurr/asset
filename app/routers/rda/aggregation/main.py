from fastapi import APIRouter, HTTPException
from psycopg2.errors import UndefinedTable
from sqlalchemy.exc import IntegrityError
from dependencies import validate_bearer
from sqlalchemy.exc import DBAPIError
from . import crud, schemas, models
from exceptions import NotFound
from utils import raise_exc

router = APIRouter()

@router.post('/', name='aggregate')
async def aggregate(payload:schemas.Schema):
    try:
        obj = crud.Aggregate( models.objects[payload.params.resource.value] )

        return await obj.aggregate(
            field_aggr=payload.params.fields,
            sources=payload.sources,
            epochs=payload.params.epochs,
            group_by=payload.params.group_by,
            return_query=False,
            and_f=payload.params.and_,
            or_f=payload.params.or_,
        )

    except Exception as e:
        print(e)
        code, msg, clss = 500, f'{e}', f"{e.__class__.__name__}"

        if isinstance(e, DBAPIError):
            code = 409 if isinstance(e, IntegrityError) else 400 if isinstance(e.orig, UndefinedTable) else 500
            msg = f'(UndefinedTable) This may be due to missing or invalid tenant in payload source' if isinstance(e.orig, UndefinedTable) else f'{e.orig}'

        raise HTTPException(status_code=code, detail=raise_exc(msg=msg, type=clss))