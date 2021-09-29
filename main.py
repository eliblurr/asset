from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from cls import SocketConnectionManager
from fastapi import FastAPI, Request
from database import SessionLocal
from config import *

app = FastAPI()
socket = SocketConnectionManager()
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