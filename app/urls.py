from fastapi.openapi.docs import (
    get_redoc_html, 
    get_swagger_ui_html, 
    get_swagger_ui_oauth2_redirect_html)
from services.broadcaster import chatroom_ws_receiver, chatroom_ws_sender
from fastapi.concurrency import run_until_first_complete
from fastapi.openapi.utils import get_openapi
from dependencies import validate_bearer
from fastapi import WebSocket, Depends
from config import STATIC_URL
from routers import *
from main import app
import config as cfg

app.include_router(faqs, tags=['Frequently Asked Questions'], prefix='/frequently-asked-questions')
app.include_router(config, tags=['Environment Configuration'], prefix='/configurations', dependencies=[Depends(validate_bearer)])
app.include_router(account, tags=['User & Adminstrator Accounts'], prefix='/accounts')
app.include_router(subscription, tags=['Subscriptions'], prefix='/subscriptions', dependencies=[Depends(validate_bearer)])
app.include_router(manufacturer, tags=['Manufacturers'], prefix='/manufacturers', dependencies=[Depends(validate_bearer)])
app.include_router(content_type, tags=['Content Types'], prefix='/content-types', dependencies=[Depends(validate_bearer)])
app.include_router(tenant, tags=['Tenants/Organizations'], prefix='/tenants')
app.include_router(permission, tags=['Permissions'], prefix='/permissions', dependencies=[Depends(validate_bearer)])
app.include_router(department, tags=['Departments'], prefix='/departments', dependencies=[Depends(validate_bearer)])
app.include_router(consumable, tags=['Consumables'], prefix='/consumables', dependencies=[Depends(validate_bearer)])
app.include_router(inventory, tags=['Inventories'], prefix='/inventories', dependencies=[Depends(validate_bearer)])
app.include_router(upload, tags=['File-Uploads'], prefix='/file-uploads')
app.include_router(catalogue, tags=['Catalogues'], prefix='/catalogues', dependencies=[Depends(validate_bearer)])
app.include_router(category, tags=['Categories'], prefix='/categories', dependencies=[Depends(validate_bearer)])
app.include_router(currency, tags=['Currencies'], prefix='/currencies', dependencies=[Depends(validate_bearer)])
app.include_router(priority, tags=['Priorities'], prefix='/priorities', dependencies=[Depends(validate_bearer)])
app.include_router(aggregation, tags=['Analytics'], prefix='/aggregate', dependencies=[Depends(validate_bearer)])
app.include_router(activity, tags=['Activities'], prefix='/activities', dependencies=[Depends(validate_bearer)])
app.include_router(dashboard, tags=['Analytics'], prefix='/dashboard', dependencies=[Depends(validate_bearer)])
app.include_router(proposal, tags=['Proposals'], prefix='/proposals', dependencies=[Depends(validate_bearer)])
app.include_router(report, tags=['Analytics'], prefix='/reports', dependencies=[Depends(validate_bearer)])
app.include_router(branch, tags=['Branches'], prefix='/branches', dependencies=[Depends(validate_bearer)])
app.include_router(policy, tags=['Policies'], prefix='/policies', dependencies=[Depends(validate_bearer)])
app.include_router(request, tags=['Requests'], prefix='/request') # , dependencies=[Depends(validate_bearer)]
app.include_router(logs, tags=['Logs'], prefix='/system-logs', dependencies=[Depends(validate_bearer)])
app.include_router(vendor, tags=['Vendor'], prefix='/vendors', dependencies=[Depends(validate_bearer)])
app.include_router(asset, tags=['Asset'], prefix='/assets', dependencies=[Depends(validate_bearer)])
app.include_router(role, tags=['Roles'], prefix='/roles', dependencies=[Depends(validate_bearer)])
app.include_router(auth, tags=['Authentication'])

def get_openapi_schema(path='/redoc'):
    description = f""" {cfg.settings.DESCRIPTION} \n\n {
    "<a href='/docs' style='color:#c0392b;cursor:help'>Interactive Swagger docs</a>" if path=="/redoc" else 
    "<a href='/'>Official API docs</a>"}"""
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=description,
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": f"{STATIC_URL}/images/logo.ico"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    def custom_openapi():
        return get_openapi_schema(path='/docs')
    app.openapi = custom_openapi
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_favicon_url=f"{STATIC_URL}images/logo.ico",
        swagger_js_url=f"{STATIC_URL}js/swagger-ui-bundle.js",
        swagger_css_url=f"{STATIC_URL}css/swagger-ui.css",
    )

@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()

@app.get('/', name='Home', include_in_schema=False)
async def redoc_html():
    def custom_openapi():
        return get_openapi_schema(path='/redoc')
    app.openapi = custom_openapi
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url=f"{STATIC_URL}js/redoc.standalone.js",
        redoc_favicon_url=f"{STATIC_URL}images/logo.ico",
        with_google_fonts=True
    )

@app.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel:str):
    await websocket.accept()
    await run_until_first_complete(
        (chatroom_ws_receiver, {"websocket": websocket, 'channel':channel}),
        (chatroom_ws_sender, {"websocket": websocket, 'channel':channel}),
    )