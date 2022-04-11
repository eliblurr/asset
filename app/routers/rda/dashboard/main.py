from exceptions import NotFound, OperationNotAllowed, BadRequestError
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session
from dependencies import get_db
from . import crud, schemas
from typing import List

router = APIRouter()

@router.get('/', description='read dashboard')
async def read(db:Session=Depends(get_db)):
    try:
        return {
            "asset":{
                "total": await crud.asset.count([("id", "total_count")], db),
                "assigned": await crud.asset.count([("id", "total_count")], db, available=True),
                "decomissioned": await crud.asset.count([("id", "total_count")], db, decommission=True)
            },
            "inventory":{
                "total":await crud.inventory.count([("id", "total_count")], db),
                "active":await crud.inventory.count([("id", "total_count")], db, status=True),
                "inactive":await crud.inventory.count([("id", "total_count")], db, status=False)
            },
            "request":{
                "total":await crud.request.count([("id", "total_count")], db),
                "pending":await crud.request.count([("id", "total_count")], db, status='active'),
                "approved":await crud.request.count([("id", "total_count")], db, status='accepted')
            },
            "proposal":{
                "total":await crud.proposal.count([("id", "total_count")], db),
                "pending":await crud.proposal.count([("id", "total_count")], db, status='active'),
                "approved":await crud.proposal.count([("id", "total_count")], db, status='accepted')
            },
        }
    except Exception as e:
        print(e)
        status_code, msg, class_name = 500, f'{e}' , f"{e.__class__.__name__}"
        if isinstance(e, DBAPIError):
            status_code = 400
            msg=f'(UndefinedTable) This may be due to missing or invalid tenant_key in request header' if isinstance(e.orig, UndefinedTable) else f'{e.orig}'
        else:
            status_code = 400 if isinstance(e, BadRequestError) else 404 if isinstance(e, NotFound) else status_code
            msg = f"{e._message()}" if isinstance(e, (BadRequestError, NotFound,)) else msg  
        raise HTTPException(status_code=status_code, detail=raise_exc(msg=msg, type=class_name))