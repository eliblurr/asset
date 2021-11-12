from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database import SessionLocal, engine
from datetime import time, datetime
from cls import ConnectionManager
from scheduler import scheduler
from config import *
import logging, os

logging.logFile,logging.atTime, logging.MAIL_FROM, logging.ADMIN_EMAIL = os.path.join(LOG_ROOT, f'logs'), time(), settings.MAIL_FROM, settings.ADMIN_EMAIL
logging.MAIL_SERVER, logging.MAIL_PORT, logging.MAIL_USERNAME, logging.MAIL_PASSWORD = settings.MAIL_SERVER, settings.MAIL_PORT, settings.MAIL_USERNAME, settings.MAIL_PASSWORD

app = FastAPI(
    docs_url=None, 
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials = True,
    allow_origins = ALLOWED_ORIGINS,
    allow_methods = ALLOWED_METHODS,
    allow_headers = ALLOWED_HEADERS,
)

socket = ConnectionManager()
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('eAsset.main')
templates = Jinja2Templates(directory="static/html")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
app.mount(STATIC_URL, StaticFiles(directory=STATIC_ROOT), name="static")
app.mount(UPLOAD_URL, StaticFiles(directory=UPLOAD_ROOT), name="upload")

@app.middleware("http")
async def tenant_session(request:Request, call_next):
    db = SessionLocal(bind=engine.execution_options(schema_translate_map={None: request.headers.get('tenant_key')})) if request.headers.get('tenant_key', None) else SessionLocal()
    request.state.db = db
    response = await call_next(request)
    return response

@app.on_event("startup")
async def startup_event():
    print('startup', app.title)
    # try:
    #     scheduler.start()
    # except Exception as e:
    #     logger.critical(f"Scheduler could not start: {e.__class__}: {e}", exc_info=True) 
    
@app.on_event("shutdown")
def shutdown_event():
    pass
    # try:
    #     scheduler.shutdown(wait=False)
    # except Exception as e:
    #     logger.critical(f"Scheduler could not shutdown: {e.__class__}: {e}", exc_info=True) 

from urls import *

from clry import event
event.start_listener()

# @app.post("/evemt")
# def ass():
#     try:
#         event.emit("broadcast", "Custom message from event")
#         pass
#     except Exception as e:
#         print(e)

# from fastapi import Request
# from babel import Locale
# import babel

# from gettext import gettext as _

# string = _("This is a translatable string.")
# # print(string)

# local = Locale('en', 'US')

# print(dir(Locale))
# c = Locale.negotiate(['de_AT'], ['de', 'en'])
# a = babel.negotiate_locale(['en'], ['de', 'en', 'DE'])
# b = Locale.negotiate(['de'], ['de', 'en', 'DE'])
# # print(local)

# languages = list(local.languages.keys())
# territories = list(local.territories.keys())
# currencies = list(local.currencies.keys())

# s = babel.core.get_global('zone_territories')

# j = babel.core.get_global('territory_currencies')['GH']
# # print(s)

# @app.get('/babel')
# def local(request:Request):
#     # lang = request.headers['accept-language'] if request.headers.get('accept-language', None) else 'en-US'
#     # local = babel.core.negotiate(lang, )
#     return request.headers['accept-language'] if request.headers.get('accept-language', None) else 'en-US'

# from typing import Optional

# from fastapi import APIRouter, FastAPI
# from pydantic import BaseModel, HttpUrl

# # app = FastAPI()


# class Invoice(BaseModel):
#     id: str
#     title: Optional[str] = None
#     customer: str
#     total: float


# class InvoiceEvent(BaseModel):
#     description: str
#     paid: bool


# class InvoiceEventReceived(BaseModel):
#     ok: bool


# invoices_callback_router = APIRouter()


# @invoices_callback_router.post(
#     "{$callback_url}/invoices/{$request.body.id}", response_model=InvoiceEventReceived
# )
# def invoice_notification(body: InvoiceEvent):
#     print('sd')
#     pass


# @app.post("/invoices/", callbacks=invoices_callback_router.routes)
# def create_invoice(invoice: Invoice, callback_url: Optional[HttpUrl] = None):
#     """
#     Create an invoice.

#     This will (let's imagine) let the API user (some external developer) create an
#     invoice.

#     And this path operation will:

#     * Send the invoice to the client.
#     * Collect the money from the client.
#     * Send a notification back to the API user (the external developer), as a callback.
#         * At this point is that the API will somehow send a POST request to the
#             external API with the notification of the invoice event
#             (e.g. "payment successful").
#     """
#     # Send the invoice, collect the money, send the notification (the callback)
#     return {"msg": "Invoice received"}


# logger = logging.getLogger("eAsset.main")
# logger.critical("Program started") 
# print()
# print(dir(crud), crud.__name__)
# print(logger)

# print(dir(logging.handlers))

# @app.get('/test/logging')
# def a():
#     logger.debug("Program started", exc_info=True)   
#     logger.info("Program started", exc_info=True)
#     logger.warning("Program started") 
#     logger.error("Program started") 
#     logger.critical("Program started") 

# logging.basicConfig(filename="sample.log", level=logging.INFO)

# logging.debug("This is a debug message")
# logging.info("Informational message")
# logging.error("An error has happened!")
items = {}
items["foo"] = {"name": "Fighters"}
items["bar"] = {"name": "Tenders"}
@app.get("/items/{item_id}")
async def read_items(item_id: str):
    return items[item_id]