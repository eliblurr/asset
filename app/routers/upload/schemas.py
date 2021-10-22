from typing import List, Optional, Set

from pydantic import BaseModel, HttpUrl

class Upload(BaseModel):
    url: HttpUrl
    name: str

# class CretaeUpload(BaseModel):
#     pass

# from typing import Optional, List
# from pydantic import BaseModel
# from utils import as_form
# from enum import Enum
# import datetime

# @as_form
# class CreateImage(BaseModel):
#     meal_id: Optional[int]
#     menu_id: Optional[int]
#     category_id: Optional[int]
#     restaurant_id: Optional[int]

# class Image(ImageBase):
#     id: int
#     created: datetime.datetime
#     updated: datetime.datetime