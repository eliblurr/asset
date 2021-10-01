from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from fastapi import FastAPI, Request, WebSocket
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
from main import app, templates, socket
from database import Base, engine
from config import settings
import os

@app.get("/jinja2/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("test.html", {"request": request, "id": id})

@app.post("/init")
def init():  
    Base.metadata.create_all(bind=engine, tables=[table for table in Base.metadata.sorted_tables if table.schema=='public'])

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket:WebSocket, client_id:int):
    await socket.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
    except:
        socket.disconnect(websocket)

from routers.priority.main import router as priority
from routers.tenant.main import router as tenant
from routers.policy.main import router as policy
from routers.faqs.main import router as faqs

app.include_router(faqs, tags=['Frequently Asked Questions'], prefix='/frequently-asked-questions')
app.include_router(tenant, tags=['Tenants/Organizations'], prefix='/tenants')
app.include_router(priority, tags=['Priorities'], prefix='/priorities')
app.include_router(policy, tags=['Policies'], prefix='/policies')

def custom_openapi():
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description=settings.APP_DOC_DESC if os.getenv('DOC')=='docs' else settings.APP_REDOC_DESC if os.getenv('DOC')=='redoc' else settings.APP_DESCRIPTION,
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "/static/images/logo.png"
    }
    app.openapi_schema = openapi_schema
    return openapi_schema

app.openapi = custom_openapi

@app.get("/", include_in_schema=False, name='redoc')
async def redoc_html():
    os.environ['DOC']='redoc'
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=settings.APP_NAME + " - Docs",
        redoc_js_url="/static/js/redoc.standalone.js",
        redoc_favicon_url="/static/images/logo.png",
        with_google_fonts=True
    )

@app.get("/docs", include_in_schema=False, name='docs')
async def custom_swagger_ui_html():
    os.environ['DOC']='docs'
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=settings.APP_NAME + " - Swagger UI",
        swagger_js_url="/static/js/swagger-ui-bundle.js",
        swagger_css_url="/static/css/swagger-ui.css",
        swagger_favicon_url="/static/images/logo.png",
    )