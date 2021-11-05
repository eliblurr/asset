from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from fastapi import FastAPI, Request, WebSocket
from fastapi.openapi.utils import get_openapi
from database import Base, TenantBase, engine
from fastapi.responses import HTMLResponse
from main import app, templates, socket
from config import settings
import os, logging

logger = logging.getLogger("eAsset.main")

@app.get("/jinja2/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("test.html", {"request": request, "id": id})

@app.post("/init")
def init():  
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.critical(f"{e.__class__}: {e}") 

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket:WebSocket, client_id:int):
    await socket.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
    except:
        socket.disconnect(websocket)

from routers.manufacturer.main import router as manufacturer
from routers.user.account.main import router as user
from routers.priority.main import router as priority
from routers.user.role.main import router as role
from routers.user.auth.main import router as auth
from routers.branch.main import router as branch
from routers.tenant.main import router as tenant
from routers.policy.main import router as policy
from routers.vendor.main import router as vendor
from routers.config.main import router as config
from routers.faqs.main import router as faqs
from routers.log.main import router as log

app.include_router(faqs, tags=['Frequently Asked Questions'], prefix='/frequently-asked-questions')
app.include_router(branch, tags=['Tenant/Organization Branch'], prefix='/branches')
app.include_router(config, tags=['Environment Configuration'], prefix='/settings')
app.include_router(manufacturer, tags=['Manufacturers'], prefix='/manufacturers')
app.include_router(tenant, tags=['Tenants/Organizations'], prefix='/tenants')
app.include_router(priority, tags=['Priorities'], prefix='/priorities')
app.include_router(policy, tags=['Policies'], prefix='/policies')
app.include_router(user, tags=['User Accounts'], prefix='/users')
app.include_router(vendor, tags=['Vendor'], prefix='/vendors')
app.include_router(role, tags=['Roles'], prefix='/roles')
app.include_router(log, tags=['Logs'], prefix='/logs')
app.include_router(auth, tags=['Authentication'])

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

from ctypes import File
from sqlalchemy import Column
from fastapi import Depends, File as F, UploadFile
from database import Base, SessionLocal
from dependencies import get_db
from mixins import BaseMixin
from datetime import date
from services.aws import s3_upload
today = date.today()

class TestDB(BaseMixin, Base):
    '''TestDB Model'''
    __tablename__ = "test_db"

    file = Column(File(upload_to=f'{today.strftime("%Y/%m/%d")}/images/'))

Base.metadata.create_all(bind=engine)

@app.post('/custom-file')
def fi(file:UploadFile=F(None), db=Depends(get_db)):
    try:
        s3_upload(file)
        # obj = TestDB(file=file)
        # db.add(obj)
        # db.commit()
    except Exception as e:
        print(e)

# obj = TestDB(some_str=24)

# print(obj.some_str)

# db = SessionLocal()

# db.add(obj)
# db.commit()

# res = [res.file for res in db.query(TestDB).all()]

# print(res)

# from fastapi import File, UploadFile
# from cls import FileReader
# from constants import SUPPORTED_EXT
# from exceptions import FileNotSupported
 
# f_reader = FileReader([".csv", ".CSV", ".xlsx", ".xlsm", ".xls", ".xml", ".xla"])

# @app.post("/file-op")
# async def create_upload_file(file: UploadFile = File(...)):
#     try:
#         a = await f_reader.read(file, ["Gender", "Last Name", "First Name",], to_dict=True)
#         print(a)
#         # return {"filename": file.content_type}
#     except Exception as e:
#         print("%s: %s", e.__class__, e)


# @api.websocket("/ws/{client_id}")
# async def websocket_endpoint(websocket:WebSocket, client_id:int):
#     await manager.connect(websocket, client_id)
#     try:
#         while True:
#             data = await websocket.receive_text()
#     except:
#         manager.disconnect(websocket)
# from typing import List

# from fastapi import FastAPI, WebSocket
# from fastapi.responses import HTMLResponse

# # app = FastAPI()

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
#             var ws = new WebSocket("ws://localhost:8000/ws");
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

# send_email

# from services.email import email, Mail

# id={'id':234243423}

# mail = Mail(
#     subject='Some Sub',
#     recipients=['a@a.com', 'b@b.com'],
#     template_name="email.html",
#     body=id, 
# )

# @app.post('/email') 
# async def send_email():
#     try:
#         await email(mail.dict())
#     except Exception as e:
#         print(e)

# from clry import add, email

# print(mail.json())

# add.delay()
# try:
#     email.delay(mail.dict())
# except Exception as e:
#     print(e)

# logger = logging.getLogger("eAsset.main")

# '''/////////////////////'''

# from sqlalchemy import Column, String, Integer, CheckConstraint
# from fastapi import Depends, File as F, UploadFile
# from database import Base, SessionLocal
# from dependencies import get_db
# from mixins import BaseMixin
# from cls import File 

    
#     file = FileField(upload_to='/some_path')

# print(
#     # dir(TestDB),
#     # [(c.name, c.type.python_type) for c in TestDB.__table__.columns],
#     # TestDB.__table__.columns,
#     # TestDB.__mapper__.c['file'],
#     sep='\n'
# )
# # return [(c.name, c.type.python_type) if c.name!='__ts_vector__' else (c.name, None) for c in cls.__table__.columns]
# # TableB.__mapper__.c['common_column'].excel_column_name

# Base.metadata.create_all(bind=engine)

# # TestDB.file()

# # obj = TestDB(file=TestDB.file())
# # obj()
# # print(dir(obj))

# @app.post('/custom-field')
# def custom_field(db=Depends(get_db)):
#     obj = TestDB(file='sdsds')
    # db.add(obj)
    # db.commit()
#     pass