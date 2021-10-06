from constants import URL, EMAIL, PHONE
from pydantic import BaseModel, constr
from typing import Optional

class UpdateSettings(BaseModel):
    BASE_URL: Optional[constr(regex=URL)]
    ADMIN_EMAIL: Optional[constr(regex=EMAIL)]
    DATABASE_URL: Optional[str]
    VERSION: Optional[str]
    MEDIA_FILE_BUCKET: Optional[constr(regex=URL)]
    APP_NAME: Optional[str]
    TWILIO_PHONE_NUMBER: Optional[constr(regex=PHONE)]
    TWILIO_AUTH_TOKEN: Optional[str]
    TWILIO_ACCOUNT_SID: Optional[str]
    SECRET: Optional[str]
    APP_DESCRIPTION: Optional[str]