from constants import URL, EMAIL, PHONE
from pydantic import BaseModel, constr
from typing import Optional

class UpdateSettings(BaseModel):
    BASE_URL: Optional[str]
    ADMIN_EMAIL: Optional[str]
    VERIFICATION_PATH: Optional[str]

    EMAIL_CODE_DURATION_IN_MINUTES: Optional[float]
    ACCESS_TOKEN_DURATION_IN_MINUTES: Optional[float]
    REFRESH_TOKEN_DURATION_IN_MINUTES: Optional[float]
    PASSWORD_RESET_TOKEN_DURATION_IN_MINUTES: Optional[float]
    ACCOUNT_VERIFICATION_TOKEN_DURATION_IN_MINUTES: Optional[float]

    TWILIO_PHONE_NUMBER: Optional[str]
    TWILIO_AUTH_TOKEN: Optional[str]
    TWILIO_ACCOUNT_SID: Optional[str]

    MAIL_USERNAME: Optional[str]
    MAIL_PASSWORD: Optional[str]
    MAIL_FROM: Optional[str]
    MAIL_PORT: Optional[int]
    MAIL_SERVER: Optional[str]
    MAIL_FROM_NAME: Optional[str]
    MAIL_TLS: Optional[bool]
    MAIL_SSL: Optional[bool]
    USE_CREDENTIALS: Optional[bool]
    VALIDATE_CERTS: Optional[bool]
    DEFAULT_MAIL_SUBJECT: Optional[str]

    REDIS_HOST: Optional[str]
    REDIS_PORT: Optional[str]
    REDIS_PASSWORD: Optional[str]
    REDIS_USER: Optional[str]
    REDIS_NODE: Optional[str]
    REDIS_MAX_RETRIES: Optional[int]
    REDIS_RETRY_INTERVAL: Optional[int]

    USE_S3: Optional[bool]
    AWS_ACCESS_KEY_ID: Optional[str]
    AWS_SECRET_ACCESS_KEY: Optional[str]
    AWS_DEFAULT_ACL: Optional[str]
    AWS_STORAGE_BUCKET_NAME: Optional[str]
    AWS_S3_OBJECT_CACHE_CONTROL: Optional[str]

    APS_COALESCE: Optional[bool]
    APS_MAX_INSTANCES: Optional[int]
    APS_MISFIRE_GRACE_TIME: Optional[int]
    APS_THREAD_POOL_MAX_WORKERS: Optional[int]
    APS_PROCESS_POOL_MAX_WORKERS: Optional[int]

UNSAFE_KEYS = ['SECRET', 'APIKEY', 'DATABASE_URL']