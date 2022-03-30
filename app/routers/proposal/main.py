from routers.activity.crud import add_activity
from fastapi import APIRouter, Depends
from cls import ContentQueryChecker
from sqlalchemy.orm import Session
from utils import r_fields, logger
from dependencies import get_db
from typing import Union, List
from . import crud, schemas

router = APIRouter()

@router.post('/', response_model=schemas.Proposal, status_code=201, name='Proposal') # is authenticated
async def create(payload:schemas.CreateProposal, db:Session=Depends(get_db)):
    return await crud.proposal.create(payload, db, activity=[{'func': add_activity, 'args':('proposal.create', {'user':['author.first_name', 'author.last_name'], 'datetime':'created', 'user_id':'author.id',})}] )
    
@router.get('/', response_model=schemas.ProposalList, name='Proposal') # is authenticated
@ContentQueryChecker(crud.proposal.model.c(), None)
async def read(db:Session=Depends(get_db), **params):
    return await crud.proposal.read(params, db)

@router.get('/{id}', response_model=Union[schemas.Proposal, dict], name='Proposal') # is authenticated
async def read_by_id(id:int, fields:List[str]=r_fields(crud.proposal.model), db:Session=Depends(get_db)):
    return await crud.proposal.read_by_id(id, db, fields)

@router.patch('/{id}', response_model=schemas.Proposal, name='Proposal') # is authenticated
async def update(id:int, payload:schemas.UpdateProposal, db:Session=Depends(get_db)):
    activity = []
    if payload.status:
        if payload.status.value=='accepted':activity.append({'func': add_activity, 'args':('proposal.accept', {'user':['author.first_name', 'author.last_name'], 'datetime':'updated','user_id':'author.id',})})
        elif payload.status.value=='declined':activity.append({'func': add_activity, 'args':('proposal.decline', {'user':['author.first_name', 'author.last_name'], 'datetime':'updated','user_id':'author.id',})})
        elif payload.status.value=='procured':activity.append({'func': add_activity, 'args':('proposal.procured', {'inventory':'inventory.title', 'inventory_id':'inventory.id'})})
    return await crud.proposal.update_2(id, payload, db, activity=activity)

@router.delete('/{id}', name='Proposal', status_code=204) # is authenticated
async def delete(id:int, db:Session=Depends(get_db)):
    await crud.proposal.delete(id, db)