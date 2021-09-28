from pydantic import BaseSettings
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent

ALLOWED_ORIGINS = ["*"]
ALLOWED_HEADERS = ["*"]
ALLOWED_METHODS = ["*"]

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')


class Settings(BaseSettings):
    DATABASE_URL: str
    APP_NAME: str = "e-Asset api service"
    ADMIN_EMAIL: str

    class Config:
        env_file = ".env"


settings = Settings()


# print(BASE_DIR)

# APP_ROOT = Path(__file__).resolve().parent


# PROJECT_APP_PATH = os.path.dirname(os.path.abspath(__file__))


# PROJECT_APP = os.path.basename(PROJECT_APP_PATH)

# PROJECT_ROOT = BASE_DIR = os.path.dirname(PROJECT_APP_PATH)

# BASE_DIR = Path(__file__).resolve().parent.parent


# print(PROJECT_APP_PATH, PROJECT_APP, PROJECT_ROOT, BASE_DIR, APP_ROOT, sep='\n\n')
