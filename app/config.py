from fastapi.templating import Jinja2Templates
from pydantic import BaseSettings
from datetime import time, date
from functools import lru_cache
import logging, os, config
from pathlib import Path
from babel import Locale

BASE_DIR = Path(__file__).resolve().parent

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

UPLOAD_URL = "/uploads"
UPLOAD_ROOT = os.path.join(BASE_DIR, 'uploads/')

LOG_ROOT = os.path.join(BASE_DIR, 'logs/')
KEY_ROOT = os.path.join(BASE_DIR, 'x64js/')

AUDIO_ROOT = os.path.join(UPLOAD_ROOT, 'media/audio/')
VIDEO_ROOT = os.path.join(UPLOAD_ROOT, 'media/videos/')
IMAGE_ROOT = os.path.join(UPLOAD_ROOT, 'media/images/')
DOCUMENT_ROOT = os.path.join(UPLOAD_ROOT, 'documents/')

IMAGE_URL = os.path.relpath(IMAGE_ROOT, UPLOAD_ROOT)
VIDEO_URL = os.path.relpath(VIDEO_ROOT, UPLOAD_ROOT)
AUDIO_URL = os.path.relpath(AUDIO_ROOT, UPLOAD_ROOT)
DOCUMENT_URL = os.path.relpath(DOCUMENT_ROOT, UPLOAD_ROOT)

SMALL = (400,400)
LISTQUAD = (250,250)
THUMBNAIL = (128, 128)

UPLOAD_EXTENSIONS = {
    "IMAGE":[".jpeg", ".jpg", ".bmp", ".gif", ".png", ".JPEG", ".JPG", ".BMP", ".GIF", ".PNG",],
    "VIDEO":[".mp4", ".avi", ".mpeg"],
    "AUDIO":[".mp3", ".aac", ".wav"],
    "DOCUMENT":[".pdf", ".csv", ".doc", ".docx", ".eot", ".txt", ".xls", ".xlsx"],
}

ORIGINS = ["*"]
HEADERS = ["*"]
METHODS = ["*"]

JWT_ALGORITHM = 'HS256'

LANGUAGE = "en"

locale = Locale(LANGUAGE)

TEMPLATES = Jinja2Templates(directory=os.path.join(STATIC_ROOT, f'html'))

class Settings(BaseSettings):
    DATABASE_URL: str
    VERSION: str = '2.0.0'
    BASE_URL: str = 'http://localhost'
    ADMIN_EMAIL: str = 'admin@admin.com'
    NAME: str = "e-Asset Management API Service"
    DESCRIPTION: str = "API documentation for eAsset Management API service"
    APIKEY: str = '_7f$2uF9CArFq7LtmQqBNuQdTa@KLt@*Y%M24Ry=eUd%R6QsXW3=Z-g!!Rvu#srJ5*#PhbV'
    SECRET: str = "khgdcvgbh"
        
    VERIFICATION_PATH: str = "accounts/activate-account/" 
    PASSWORD_RESET: str = "reset-password/" 
    TENANT_ACTIVATION_PATH: str = "tenants/activate-tenant/"

    EMAIL_CODE_DURATION_IN_MINUTES: int = 15
    ACCESS_TOKEN_DURATION_IN_MINUTES: int = 60
    REFRESH_TOKEN_DURATION_IN_MINUTES: int = 600
    PASSWORD_RESET_TOKEN_DURATION_IN_MINUTES: int = 15
    ACCOUNT_VERIFICATION_TOKEN_DURATION_IN_MINUTES: int = 15

    TWILIO_PHONE_NUMBER: str = '+16196584362'
    TWILIO_AUTH_TOKEN: str = '7b6c506ee07337cc3d02536d5119c4b2'
    TWILIO_ACCOUNT_SID: str = 'AC959cbde01aced5669b0121ffea2df117'

    MAIL_USERNAME: str = "829e507086a9d9" # "a9f521690f65a4"
    MAIL_PASSWORD: str = "e6e1d4fe2a31d3" # "11480b2eec8121"
    MAIL_FROM: str = "elisegb-49cabc@inbox.mailtrap.io"
    MAIL_PORT: int = 2525
    MAIL_SERVER: str = "smtp.mailtrap.io"
    MAIL_FROM_NAME: str = "eAsset"
    MAIL_TLS: bool = False
    MAIL_SSL: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    DEFAULT_MAIL_SUBJECT: str = "SOME DEFAULT SUBJECT HERE"

    APS_COALESCE: bool = False
    APS_MAX_INSTANCES: int = 20
    APS_MISFIRE_GRACE_TIME: int = 4
    APS_THREAD_POOL_MAX_WORKERS: int = 20
    APS_PROCESS_POOL_MAX_WORKERS: int = 5

    USE_S3: bool = False
    AWS_ACCESS_KEY_ID: str = "AKIAQFCNVCREKTZTA2V2"
    AWS_SECRET_ACCESS_KEY: str = "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"
    AWS_DEFAULT_ACL: str = "public-read"
    AWS_STORAGE_BUCKET_NAME: str = "asset-dev-1990"
    AWS_S3_OBJECT_CACHE_CONTROL: str = "max-age=86400"

    REDIS_HOST:str="127.0.0.1"
    REDIS_PORT:str='6379'
    REDIS_PASSWORD:str=''
    REDIS_USER:str=''
    REDIS_NODE:str=0
    REDIS_MAX_RETRIES:int = 3
    REDIS_RETRY_INTERVAL:int=10

    class Config:
        env_file = '.env'
        secrets_dir = KEY_ROOT

DER_BASE64_ENCODED_PRIVATE_KEY_FILE_PATH = os.path.join(KEY_ROOT, "private.txt")
DER_BASE64_ENCODED_PUBLIC_KEY_FILE_PATH = os.path.join(KEY_ROOT, "public.txt")

try:
    if not os.path.isdir(UPLOAD_ROOT):os.mkdir(UPLOAD_ROOT)
    if not os.path.isdir(LOG_ROOT):os.mkdir(LOG_ROOT)
    if not os.path.isdir(KEY_ROOT):os.mkdir(KEY_ROOT)
    if not settings.USE_S3:   
        if not os.path.isdir(AUDIO_ROOT):os.mkdir(AUDIO_ROOT)
        if not os.path.isdir(VIDEO_ROOT):os.mkdir(VIDEO_ROOT)
        if not os.path.isdir(IMAGE_ROOT):os.mkdir(IMAGE_ROOT)
        if not os.path.isdir(DOCUMENT_ROOT):os.mkdir(DOCUMENT_ROOT)
except:
    pass

if not (os.path.isfile(DER_BASE64_ENCODED_PRIVATE_KEY_FILE_PATH) and os.path.isfile(DER_BASE64_ENCODED_PUBLIC_KEY_FILE_PATH)):
    os.system(f'sh keys.sh -r {KEY_ROOT}')

# @lru_cache()
def get_settings():
    # if os.getenv('DOCKER') in ['True', 'true', 1, '1', True]:
    #     return Settings(_env_file="docker.env")
    # return Settings(_env_file=".env")

    if os.getenv('DOCKER') in ['True', 'true', 1, '1', True]:
        Settings.Config.env_file="docker.env"
    return Settings()

config.settings = get_settings()

VAPID_CLAIMS = {
    "sub": f"mailto:{config.settings.ADMIN_EMAIL}"
}

AWS_S3_CUSTOM_DOMAIN = f'https://{config.settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': config.settings.AWS_S3_OBJECT_CACHE_CONTROL}

logging.atTime = time()
logging.MAIL_FROM =  config.settings.MAIL_FROM
logging.ADMIN_EMAIL = config.settings.ADMIN_EMAIL
logging.logFile = os.path.join(LOG_ROOT, f"{date.today().strftime('%Y-%m-%d')}.log")
logging.MAIL_PORT = config.settings.MAIL_PORT
logging.MAIL_SERVER = config.settings.MAIL_SERVER
logging.MAIL_USERNAME = config.settings.MAIL_USERNAME
logging.MAIL_PASSWORD = config.settings.MAIL_PASSWORD
# logging.config.fileConfig(f'logging.conf')

import logging.config as loggingConfig
loggingConfig.fileConfig(f'logging.conf')

with open(DER_BASE64_ENCODED_PRIVATE_KEY_FILE_PATH, "r+") as private:
    VAPID_PRIVATE_KEY = private.readline().strip("\n")

with open(DER_BASE64_ENCODED_PUBLIC_KEY_FILE_PATH, "r+") as public:
    VAPID_PUBLIC_KEY = public.readline().strip("\n")

REDIS_URL:str=f"redis://{config.settings.REDIS_USER}:{config.settings.REDIS_PASSWORD}@{config.settings.REDIS_HOST}:{config.settings.REDIS_PORT}/{config.settings.REDIS_NODE}"