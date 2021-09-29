from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request
from database import Base, engine
from main import app, templates

@app.get("/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("test.html", {"request": request, "id": id})

@app.post("/init")
def init():  
    Base.metadata.create_all(bind=engine, tables=[table for table in Base.metadata.sorted_tables if table.schema=='public'])

from routers.priority.main import router as priority
from routers.tenant.main import router as tenant
from routers.policy.main import router as policy
from routers.faqs.main import router as faqs

app.include_router(faqs, tags=['Frequently Asked Questions'], prefix='/frequently-asked-questions')
app.include_router(tenant, tags=['Tenants/Organizations'], prefix='/tenants')
app.include_router(priority, tags=['Priorities'], prefix='/priorities')
app.include_router(policy, tags=['Policies'], prefix='/policies')