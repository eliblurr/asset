from starlette.concurrency import run_until_first_complete
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import close_all_sessions
from fastapi.staticfiles import StaticFiles
from services.broadcaster import broadcast
from database import SessionLocal, engine
from fastapi import FastAPI, Request
from scheduler import scheduler
import config as cfg

app = FastAPI(
    docs_url=None, 
    redoc_url=None,
    title=cfg.settings.NAME,
    version=cfg.settings.VERSION,
    openapi_url='/openapi.json'
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials = True,
    allow_origins = cfg.ORIGINS,
    allow_methods = cfg.METHODS,
    allow_headers = cfg.HEADERS,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
app.mount(cfg.STATIC_URL, StaticFiles(directory=cfg.STATIC_ROOT), name="static")
app.mount(cfg.UPLOAD_URL, StaticFiles(directory=cfg.UPLOAD_ROOT), name="upload")

@app.on_event("startup")
async def startup_event():
    print('service started')
    scheduler.start()
    await broadcast.connect()

@app.on_event("shutdown")
async def shutdown_event():
    close_all_sessions()
    scheduler.shutdown(wait=False)
    await broadcast.disconnect()

@app.middleware("http")
async def tenant_session(request:Request, call_next):
    db = SessionLocal(bind=engine.execution_options(schema_translate_map={None: request.headers.get('tenant_key'), 'global': request.headers.get('tenant_key')})) if request.headers.get('tenant_key', None) else SessionLocal()
    request.state.db = db
    response = await call_next(request)
    return response

from urls import *

# 
# on_startup=[broadcast.connect], on_shutdown=[broadcast.disconnect]
# # from sockets import broadcast, chatroom_ws_receiver, chatroom_ws_sender

# 
# from starlette.templating import Jinja2Templates
# from fastapi import FastAPI, WebSocket, Request
# from fastapi.responses import HTMLResponse
# from pydantic import BaseModel
# import json

# class Publish(BaseModel):
#     channel: str = "chatroom"
#     message: str

# app = FastAPI(on_startup=[broadcast.connect], on_shutdown=[broadcast.disconnect])
# templates = Jinja2Templates("templates")

# @app.get("/", response_class=HTMLResponse, name='chatroom_ws')
# async def homepage(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})



# @app.post("/push")
# async def send_message(publish: Publish):
#     print(broadcast._subscribers['chatroom']) # if does not exist persist message # replace chatroom with tenant_id@user_id or replace numerical ids with UUIDs/ or send messages to email / or generate a socket_client_id for each user 
#     await broadcast.publish(publish.channel, json.dumps([publish.message]))
#     return publish
