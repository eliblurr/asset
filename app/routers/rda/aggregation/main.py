from fastapi import APIRouter

router = APIRouter()

@router.post('/', name='aggregate')
async def aggregate():
    pass

