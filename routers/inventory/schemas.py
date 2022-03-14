from routers.user.account.schemas import UserSummary
from typing import Optional, List, Union
from pydantic import BaseModel
import datetime

class InventoryBase(BaseModel):
    title: str
    metatitle: Optional[str]
    description: Optional[str]

    class Config:
        orm_mode=True
      
class CreateInventory(InventoryBase):
    manager_id:int
    department_id:Optional[int]
    branch_id:Optional[int]
    
class UpdateInventory(InventoryBase):
    title: Optional[str]
    status: Optional[bool]
    
class Inventory(InventoryBase):
    id: int
    manager: Optional[UserSummary]
    created: datetime.datetime
    updated: datetime.datetime

class InventoryList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[Inventory], list]