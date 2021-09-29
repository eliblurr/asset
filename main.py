from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from config import *

app = FastAPI()
templates = Jinja2Templates(directory="static/html")
app.mount(STATIC_URL, StaticFiles(directory=STATIC_ROOT), name="static")

from urls import *

from routers.tenant.models import Base
from database import engine

@app.post("/init")
def init():  
    Base.metadata.create_all(bind=engine)

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