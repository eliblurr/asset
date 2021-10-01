from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from cls import SocketConnectionManager
from fastapi import FastAPI, Request
from datetime import time, datetime
from database import SessionLocal
from config import *
import logging, os

logging.logFile,logging.atTime = os.path.join(LOG_ROOT, f'logs.log'), time()

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
    try:
        db = SessionLocal()
        if request.headers.get('tenant_id', None):
            db.connection(execution_options={"schema_translate_map": {None: request.headers.get('tenant_id')}})
        request.state.db = db
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response

from urls import *

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

# from babel import Locale

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