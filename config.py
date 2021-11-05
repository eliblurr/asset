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
    "IMAGE":[".jpeg", ".jpg", ".bmp", ".gif"],
    "VIDEO":[".mp4", ".avi", ".mpeg"],
    "AUDIO":[".mp3", ".aac", ".png", ".wav"],
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

    class Config:
        env_file = ".env"
        secrets_dir = BASE_DIR

settings = Settings()

if settings.USE_S3:
    pass
else:
    UPLOAD_URL = "/uploads/"
    UPLOAD_ROOT = os.path.join(BASE_DIR, 'uploads/')
    MEDIA_ROOT = os.path.join(UPLOAD_ROOT, 'media/')
    DOCUMENT_ROOT = os.path.join(UPLOAD_ROOT, 'documents/')
    
    if not os.path.isdir(UPLOAD_ROOT):
        os.mkdir(UPLOAD_ROOT)
        # os.makedirs(UPLOAD_ROOT, mode=0o777)

    LOG_ROOT = os.path.join(BASE_DIR, 'logs/')

    if not os.path.isdir(LOG_ROOT):
        os.mkdir(LOG_ROOT)
        # os.makedirs(name, mode=0o777, exist_ok=False)

locale = Locale('en', 'US')

'''
/uploads

/media/product/2021/10/20/no-logo.png

/uploads/media/audio/date_path/some_file
/uploads/media/images/date_path/some_file
/uploads/media/videos/date_path/some_file

/uploads/docs/date_path/some_file

'''

# MEDIA_URL = "/media/"
# DOCUMENT_URL = "/docs/"

# if not os.path.isdir(DOCUMENT_ROOT):
#     os.mkdir(DOCUMENT_ROOT)

# if not os.path.isdir(MEDIA_ROOT):
#     os.mkdir(MEDIA_ROOT)


# USE_S3 = os.getenv('USE_S3') == 'TRUE'

# if USE_S3:
#     # aws settings
#     AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
#     AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
#     AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME') asset-dev-1990
#     AWS_DEFAULT_ACL = None
#     AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
#     AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
#     # s3 static settings
#     STATIC_LOCATION = 'static'
#     STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/'
#     STATICFILES_STORAGE = 'hello_django.storage_backends.StaticStorage'
#     # s3 public media settings
#     PUBLIC_MEDIA_LOCATION = 'media'
#     MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
#     DEFAULT_FILE_STORAGE = 'hello_django.storage_backends.PublicMediaStorage'
#     # s3 private media settings
#     PRIVATE_MEDIA_LOCATION = 'private'
#     PRIVATE_FILE_STORAGE = 'hello_django.storage_backends.PrivateMediaStorage'
# else:
#     STATIC_URL = '/staticfiles/'
#     STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
#     MEDIA_URL = '/mediafiles/'
#     MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

# def image_upload(request):
#     if request.method == 'POST':
#         image_file = request.FILES['image_file']
#         image_type = request.POST['image_type']
#         if settings.USE_S3:
#             upload = Upload(file=image_file)
#             upload.save()
#             image_url = upload.file.url
#         else:
#             fs = FileSystemStorage()
#             filename = fs.save(image_file.name, image_file)
#             image_url = fs.url(filename)
#         return render(request, 'upload.html', {
#             'image_url': image_url
#         })
#     return render(request, 'upload.html')
