from fastapi import Request, Header, HTTPException
from config import settings

def get_db(request:Request):
    try:
        yield request.state.db
    finally:
        request.state.db.close()

# Global Dependency
# app = FastAPI(dependencies=[Depends(verify_token), Depends(verify_key)])
async def verify_key(x_key: str = Header(...)):
    if x_key != settings.API_KEY:
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key