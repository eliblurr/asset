from fastapi.openapi.docs import (
    get_redoc_html, 
    get_swagger_ui_html, 
    get_swagger_ui_oauth2_redirect_html)
from services.broadcaster import chatroom_ws_receiver, chatroom_ws_sender
from fastapi.openapi.utils import get_openapi
from config import settings, STATIC_URL
from fastapi import WebSocket
from routers import *
from main import app

app.include_router(faqs, tags=['Frequently Asked Questions'], prefix='/frequently-asked-questions')
app.include_router(config, tags=['Environment Configuration'], prefix='/configurations')
app.include_router(account, tags=['User & Adminstrator Accounts'], prefix='/accounts')
app.include_router(subscription, tags=['Subscriptions'], prefix='/subscriptions')
app.include_router(manufacturer, tags=['Manufacturers'], prefix='/manufacturers')
app.include_router(tenant, tags=['Tenants/Organizations'], prefix='/tenants')
app.include_router(permission, tags=['Permissions'], prefix='/permissions')
app.include_router(department, tags=['Departments'], prefix='/departments')
app.include_router(consumable, tags=['Consumables'], prefix='/consumables')
app.include_router(inventory, tags=['Inventories'], prefix='/inventories')
app.include_router(upload, tags=['File-Uploads'], prefix='/file-uploads')
app.include_router(catalogue, tags=['Catalogues'], prefix='/catalogues')
app.include_router(category, tags=['Categories'], prefix='/categories')
app.include_router(currency, tags=['Currencies'], prefix='/currencies')
app.include_router(priority, tags=['Priorities'], prefix='/priorities')
app.include_router(activity, tags=['Activities'], prefix='/activities')
app.include_router(proposal, tags=['Proposals'], prefix='/proposals')
app.include_router(branch, tags=['Branches'], prefix='/branches')
app.include_router(policy, tags=['Policies'], prefix='/policies')
app.include_router(request, tags=['Requests'], prefix='/request')
app.include_router(vendor, tags=['Vendor'], prefix='/vendors')
app.include_router(asset, tags=['Asset'], prefix='/assets')
app.include_router(role, tags=['Roles'], prefix='/roles')
app.include_router(logs, tags=['Logs'], prefix='/logs')
app.include_router(auth, tags=['Authentication'])

def get_openapi_schema(path='/redoc'):
    description = f""" {settings.DESCRIPTION} \n\n {
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

@app.websocket("ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel:str):
    # channel = id_tenant
    await websocket.accept()
    # if user has persisting message ... send up here
    await run_until_first_complete(
        (chatroom_ws_receiver, {"websocket": websocket, 'channel':channel}),
        (chatroom_ws_sender, {"websocket": websocket, 'channel':channel}),
    )

'''
    1. broadcaster
    2. notification subscription [POST creates a subscription] [GET returns vapid public key which clients uses to send around push notification]
    3. asset + activities + relations
    4. [request] + activities
    5. category
    6. department + relations
    7. manufaturer
    8. branch + relations
    9. inventory + relations
'''

# from routers.analytics.main import router as analytics 
# app.include_router(analytics, tags=['Analytics'], prefix='/analytics')
