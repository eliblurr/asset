from fastapi import APIRouter

router = APIRouter()

@router.post('/', name='generate report')
async def generate_report():
    pass
