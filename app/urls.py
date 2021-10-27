from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from fastapi import FastAPI, Request, WebSocket
from fastapi.openapi.utils import get_openapi
from database import Base, TenantBase, engine
from fastapi.responses import HTMLResponse
from main import app, templates, socket
from config import settings
import os

@app.get("/jinja2/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("test.html", {"request": request, "id": id})

@app.post("/init")
def init():  
    Base.metadata.create_all(bind=engine)

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


from services.email import email, Mail

id={'id':11}

mail = Mail(
    subject='Some Sub',
    recipients=['a@a.com', 'b@b.com'],
    template_name="emailtest.html",
    body=id, 
)

@app.post('/email') 
async def send_email():
    try:
        await email(mail)
    except Exception as e:
        print(e)

'''/////////////////////'''


from sqlalchemy import Column, String, Integer, CheckConstraint
from dependencies import get_db
from mixins import BaseMixin
from fastapi import Depends
from database import Base
from cls import FileField

class TestDB(BaseMixin, Base):
    '''TestDB Model'''
    __tablename__ = "test_db"
    
    file = FileField(upload_to='/some_path')

print(
    # dir(TestDB),
    # [(c.name, c.type.python_type) for c in TestDB.__table__.columns],
    # TestDB.__table__.columns,
    # TestDB.__mapper__.c['file'],
    sep='\n'
)
# return [(c.name, c.type.python_type) if c.name!='__ts_vector__' else (c.name, None) for c in cls.__table__.columns]
# TableB.__mapper__.c['common_column'].excel_column_name

Base.metadata.create_all(bind=engine)

# TestDB.file()

# obj = TestDB(file=TestDB.file())
# obj()
# print(dir(obj))

@app.post('/custom-field')
def custom_field(db=Depends(get_db)):
    obj = TestDB(file='sdsds')
    db.add(obj)
    db.commit()
    pass