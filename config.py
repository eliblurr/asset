from pydantic import BaseSettings
from pathlib import Path
from babel import Locale
import os

BASE_DIR = Path(__file__).resolve().parent

ALLOWED_ORIGINS = ["*"]
ALLOWED_HEADERS = ["*"]
ALLOWED_METHODS = ["*"]

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

os.environ['DOC'] = ''

JWT_ALGORITHM = 'HS256'

UPLOAD_EXTENSIONS = {
    "IMAGE":[".jpeg", ".jpg", ".bmp", ".gif", ".png", ".JPEG", ".JPG", ".BMP", ".GIF", ".PNG",],
    "VIDEO":[".mp4", ".avi", ".mpeg"],
    "AUDIO":[".mp3", ".aac", ".wav"],
    "DOCUMENT":[".pdf", ".csv", ".doc", ".docx", ".eot", ".txt", ".xls", ".xlsx"],
}

class Settings(BaseSettings):
    API_KEY: str
    BASE_URL: str
    ADMIN_EMAIL: str
    DATABASE_URL: str
    USE_S3: bool = False
    VERSION: str = '2.0.0'
    RESET_PASSWORD_PATH: str
    ACCOUNT_ACTIVATION_PATH: str
    APP_NAME: str = "e-Asset api service"
    TWILIO_PHONE_NUMBER: str = '+16196584362'
    TWILIO_AUTH_TOKEN: str = '7b6c506ee07337cc3d02536d5119c4b2'
    TWILIO_ACCOUNT_SID: str = 'AC959cbde01aced5669b0121ffea2df117'
    SECRET: str = "I2YsMiClydMj9lCGkIsnSuM7NP7Wm7ilwRlBGKPNOl5UBQtl7mIcka9MKgvf"
    APP_DESCRIPTION: str = """eAsset API Documentation developed by Eli for Some Organization"""
    APP_DOC_DESC: str = f"{APP_DESCRIPTION}\n\n <a href='/' style='color:hotpink;cursor:help'>see official API docs</a>"
    APP_REDOC_DESC: str = f"{APP_DESCRIPTION}\n\n <a href='/docs' style='color:hotpink;cursor:help'>Interactive Swagger docs</a>"
    ACCESS_TOKEN_DURATION_IN_MINUTES: float = 60
    REFRESH_TOKEN_DURATION_IN_MINUTES: float = 60
    DEFAULT_TOKEN_DURATION_IN_MINUTES: float = 15
    RESET_TOKEN_DURATION_IN_MINUTES: float = 15
    ACTIVATION_TOKEN_DURATION_IN_MINUTES: float = 15
    MAIL_USERNAME: str = "a9f521690f65a4"
    MAIL_PASSWORD: str = "11480b2eec8121"
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
    AWS_ACCESS_KEY_ID: str = "AKIAQFCNVCREKTZTA2V2"
    AWS_SECRET_ACCESS_KEY: str = "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"
    AWS_DEFAULT_ACL: str = "public-read"
    AWS_STORAGE_BUCKET_NAME: str = "asset-dev-1990"
    AWS_S3_OBJECT_CACHE_CONTROL: str = "max-age=86400"

    class Config:
        env_file = ".env"
        secrets_dir = BASE_DIR

settings = Settings()

AWS_S3_CUSTOM_DOMAIN = f'{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': settings.AWS_S3_OBJECT_CACHE_CONTROL}
UPLOAD_URL = "/uploads/"
UPLOAD_ROOT = os.path.join(BASE_DIR, 'uploads/')
MEDIA_ROOT = os.path.join(UPLOAD_ROOT, 'media/')
DOCUMENT_ROOT = os.path.join(UPLOAD_ROOT, 'documents/')

if not os.path.isdir(UPLOAD_ROOT):
    os.mkdir(UPLOAD_ROOT)

LOG_ROOT = os.path.join(BASE_DIR, 'logs/')

if not os.path.isdir(LOG_ROOT):
    os.mkdir(LOG_ROOT)

locale = Locale('en', 'US')