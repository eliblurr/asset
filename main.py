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