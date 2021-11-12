from fastapi import APIRouter, Depends, Query
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from dependencies import get_db
from typing import Union, List
from . import crud, schemas

router = APIRouter()

@router.post('/', description='', response_model=schemas.Proposal, status_code=201, name='Proposal')
async def create(payload:schemas.CreateProposal, db:Session=Depends(get_db)):
    return await crud.proposal.create(payload, db)

@router.get('/', description='', response_model=schemas.ProposalList, name='Proposal')
@ContentQueryChecker(crud.proposal.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.proposal.read(params, db)

@router.get('/{id}', description='', response_model=Union[schemas.Proposal, dict], name='Proposal')
async def read_by_id(id:int, fields:List[str]=Query(None, regex=f'({"|".join([x[0] for x in crud.proposal.model.c()])})$'), db:Session=Depends(get_db)):
    return await crud.proposal.read_by_id(id, db, fields)

@router.patch('/{id}', description='', response_model=schemas.Proposal, name='Proposal')
async def update(id:int, payload:schemas.UpdateProposal, db:Session=Depends(get_db)):
    return await crud.proposal.update(id, payload, db)

@router.delete('/{id}', description='', name='Proposal')
async def delete(id:int, db:Session=Depends(get_db)):
    return await crud.proposal.delete(id, db)