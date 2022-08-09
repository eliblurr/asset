from pydantic import BaseModel
from typing import Optional

class Message(BaseModel):
    push_id: str
    message: dict
    web_push_subscription: Optional[str]