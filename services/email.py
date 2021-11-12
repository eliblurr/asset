from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr, BaseModel, validator
from typing import List, Optional, Union
from config import settings, BASE_DIR
import os

fm = FastMail(
    ConnectionConfig(
        MAIL_USERNAME = settings.MAIL_USERNAME,
        MAIL_PASSWORD = settings.MAIL_PASSWORD,
        MAIL_FROM = settings.MAIL_FROM,
        MAIL_PORT = settings.MAIL_PORT,
        MAIL_SERVER = settings.MAIL_SERVER,
        MAIL_FROM_NAME = settings.MAIL_FROM_NAME,
        MAIL_TLS = settings.MAIL_TLS,
        MAIL_SSL = settings.MAIL_SSL,
        USE_CREDENTIALS = settings.USE_CREDENTIALS,
        VALIDATE_CERTS = settings.VALIDATE_CERTS,
        TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'static/html')
    )
)

class Mail(BaseModel):
    subject: Optional[str] = settings.DEFAULT_MAIL_SUBJECT
    template_name:Optional[str]
    recipients: List[EmailStr]
    body: Union[str, dict]

    @validator('body')
    def verify_template_name(cls, v, values):
        if isinstance(v, dict) and not values["template_name"]:
            raise ValueError('body should be of type dict')
        return v
        
async def email(mail:Union[Mail, dict], *args, **kwargs):
    mail = Mail.parse_obj(mail) if isinstance(mail, dict) else mail
    message = MessageSchema(
        subject=mail.subject,
        recipients=mail.recipients, 
        attachments=kwargs.get('attachments', []),
    )
    if mail.template_name:
        message.template_body = mail.dict().get("body")
    else:
        message.body, message.subtype  = mail.body, "html"
    await fm.send_message(message, template_name=mail.template_name)