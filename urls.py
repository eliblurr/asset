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


# from fastapi import UploadFile, File
# from PIL import Image
# from io import BytesIO
# from config import STATIC_ROOT
# import os

# # self.file.file.read()

# logo = os.path.join(STATIC_ROOT, 'images/logo.ico')
# # im_obj = Image.open(im)

# # print(im_obj)

# @app.post('/test')
# async def test(image:UploadFile=File(...)):
#     try:
#         with Image.open(BytesIO(image.file.read())) as im:
#             print(im)
#             image.file.close()
#         with Image.open(logo) as lg:
#             print(lg)
#     except Exception as e:
#         print(e)
#     finally:
#         print('image suss')



# from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
# from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
# from fastapi.openapi.utils import get_openapi
# from fastapi.responses import HTMLResponse
# from main import app, templates, socket
# from database import engine
# from config import settings
# from routers import Base
# import os, logging

# logger = logging.getLogger("eAsset.main")

# @app.get("/jinja2/{id}", response_class=HTMLResponse)
# async def read_item(request: Request, id: str):
#     return TEMPLATES.TemplateResponse("test.html", {"request": request, "id": id})

# @app.post("/init")
# def init():  
#     try:
#         Base.metadata.create_all(
#             bind=engine, 
#             tables=[table for table in Base.metadata.sorted_tables if table.schema=='public' or table.schema=='global']
#         )
#     except Exception as e:
#         print(e)
#         logger.critical(f"{e.__class__}: {e}") 

# @app.websocket("/ws/{client_id}")
# async def websocket_endpoint(websocket:WebSocket, client_id:int):
#     await socket.connect(websocket, client_id)
#     try:
#         while True:
#             data = await websocket.receive_text()
#     except WebSocketDisconnect:
#         socket.disconnect(websocket)

# from routers.user.permissions.main import router as permissions
# from routers.manufacturer.main import router as manufacturer
# from routers.department.main import router as department
# from routers.catalogue.main import router as catalogue
# from routers.analytics.main import router as analytics
# from routers.inventory.main import router as inventory
# from routers.category.main import router as category
# from routers.activity.main import router as activity
# from routers.proposal.main import router as proposal
# from routers.user.account.main import router as user
# from routers.priority.main import router as priority
# from routers.currency.main import router as currency
# from routers.request.main import router as request
# from routers.user.role.main import router as role
# from routers.user.auth.main import router as auth
# from routers.branch.main import router as branch
# from routers.tenant.main import router as tenant
# from routers.policy.main import router as policy
# from routers.vendor.main import router as vendor
# from routers.config.main import router as config
# from routers.asset.main import router as asset
# from routers.faqs.main import router as faqs
# from routers.log.main import router as log


# 
# app.include_router(catalogue, tags=['Request Catalogues'], prefix='/request-catalogues')
# app.include_router(permissions, tags=['User Permissions'], prefix='/user-permissions')
# 
# 
# 
# 
# 
# 
# 
# 
# 
# app.include_router(analytics, tags=['Analytics'], prefix='/analytics')
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 

# def custom_openapi():
#     openapi_schema = get_openapi(
#         title=settings.APP_NAME,
#         version=settings.VERSION,
#         description=settings.APP_DOC_DESC if os.getenv('DOC')=='docs' else settings.APP_REDOC_DESC if os.getenv('DOC')=='redoc' else settings.APP_DESCRIPTION,
#         routes=app.routes,
#     )
#     openapi_schema["info"]["x-logo"] = {
#         "url": "/static/images/logo.png"
#     }
#     app.openapi_schema = openapi_schema
#     return openapi_schema

# app.openapi = custom_openapi

# @app.get("/", include_in_schema=False, name='redoc')
# async def redoc_html():
#     os.environ['DOC']='redoc'
#     return get_redoc_html(
#         openapi_url=app.openapi_url,
#         title=settings.APP_NAME + " - Docs",
#         redoc_js_url="/static/js/redoc.standalone.js",
#         redoc_favicon_url="/static/images/logo.png",
#         with_google_fonts=True
#     )

# @app.get("/docs", include_in_schema=False, name='docs')
# async def custom_swagger_ui_html():
#     os.environ['DOC']='docs'
#     return get_swagger_ui_html(
#         openapi_url=app.openapi_url,
#         title=settings.APP_NAME + " - Swagger UI",
#         swagger_js_url="/static/js/swagger-ui-bundle.js",
#         swagger_css_url="/static/css/swagger-ui.css",
#         swagger_favicon_url="/static/images/logo.png",
#     )

# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: List[WebSocket] = []

#     async def connect(self, websocket: WebSocket):
#         print(websocket.path_params["client_id"])
#         await websocket.accept()
#         self.active_connections.append(websocket)

#     def disconnect(self, websocket: WebSocket):
#         self.active_connections.remove(websocket)

#     async def send_personal_message(self, message: str, websocket: WebSocket):
#         await websocket.send_text(message)

#     async def broadcast(self, message: str):
#         for connection in self.active_connections:
#             await connection.send_text(message)

# manager = ConnectionManager()   

# @app.websocket("/ws/{client_id}")
# async def websocket_endpoint(websocket:WebSocket, client_id:int):
#     await manager.connect(websocket)
#     try:
#         while True:
#             data = await websocket.receive_text()
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)
    
        
# # from typing import List

# # from fastapi import FastAPI, WebSocket
# # from fastapi.responses import HTMLResponse

# # # app = FastAPI()

# html = """
# <!DOCTYPE html>
# <html>
#     <head>
#         <title>Chat</title>
#     </head>
#     <body>
#         <h1>WebSocket Chat</h1>
#         <form action="" onsubmit="sendMessage(event)">
#             <input type="text" id="messageText" autocomplete="off"/>
#             <button>Send</button>
#         </form>
#         <ul id='messages'>
#         </ul>
#         <script>
#             var ws = new WebSocket("ws://localhost:8000/ws/2001");
#             ws.onmessage = function(event) {
#                 var messages = document.getElementById('messages')
#                 var message = document.createElement('li')
#                 var content = document.createTextNode(event.data)
#                 message.appendChild(content)
#                 messages.appendChild(message)
#             };
#             function sendMessage(event) {
#                 var input = document.getElementById("messageText")
#                 ws.send(input.value)
#                 input.value = ''
#                 event.preventDefault()
#             }
#         </script>
#     </body>
# </html>
# """

# @app.get("/socket")
# async def get():
#     return HTMLResponse(html)

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     # for message in websocket.iter_text():
#     #     print(message)
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_text()
#         await websocket.send_text(f"Message text was: {data}")