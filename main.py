from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database import SessionLocal, engine
from cls import SocketConnectionManager
from fastapi import FastAPI, Request
from datetime import time, datetime
from config import *
import logging, os

logging.logFile,logging.atTime = os.path.join(LOG_ROOT, f'logs'), time()

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

socket = SocketConnectionManager()
logging.config.fileConfig('logging.conf')
templates = Jinja2Templates(directory="static/html")
app.mount(MEDIA_URL, StaticFiles(directory=MEDIA_ROOT), name="media")
app.mount(STATIC_URL, StaticFiles(directory=STATIC_ROOT), name="static")
app.mount(DOCUMENT_URL, StaticFiles(directory=DOCUMENT_ROOT), name="documents")

@app.middleware("http")
async def tenant_session(request:Request, call_next):
    db = SessionLocal()
    if request.headers.get('tenant_key', None):
        db = SessionLocal(bind=engine.execution_options(schema_translate_map={None: request.headers.get('tenant_key')}))
    request.state.db = db
    response = await call_next(request)
    return response

from urls import *

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



# locale = Locale('en', 'US') # en, US specifies language, territory respectives

# for k,v in locale.territories.items():
#     print(f'{k} : {v}')

# for k,v in locale.currencies.items():
#     print(f'{k} : {v}')

# from babel.numbers import format_currency

# print( format_currency(45678987654.98, 'GHS', locale='en_GH') )

# print(
#     dir(Locale.currencies),
#     locale.currencies['GHS'],
#     sep='\n\n'
# )