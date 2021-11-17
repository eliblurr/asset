from pydantic import BaseModel, constr, validator
from typing import Optional, List, Union
import routers.inventory.models as m
from constants import EMAIL, PHONE
import datetime

class InvManager(BaseModel):
    id: int
    branch_id: Optional[int]
    last_name: Optional[str]
    first_name: Optional[str]
    middle_name: Optional[str]
    email: constr(regex=EMAIL)
    phone: Optional[constr(regex=PHONE)]
    
    class Config:
        orm_mode = True

class InventoryBase(BaseModel):
    title: str
    metatitle: Optional[str]
    description: Optional[str]
    
    class Config:
        orm_mode = True

    class Meta:
        model = m.Inventory
      
class CreateInventory(InventoryBase):
    manager_id: int
    branch_id:Optional[int]
    department_id:Optional[int]

    @validator('department_id')
    def default_to_department(cls, v, values):
        if v and values['branch_id']:
            values['branch_id']=None
        return v
    
class UpdateInventory(BaseModel):
    title: Optional[str]
    metatitle: Optional[str]
    description: Optional[str]
    branch_id: Optional[int]
    manager_id: Optional[int]
    department_id:Optional[int]

    @validator('department_id')
    def default_to_department(cls, v, values):
        if v and values['branch_id']:
            values['branch_id']=None
        return v
    
class Inventory(InventoryBase):
    id: int
    manager: InvManager
    created: datetime.datetime
    updated: datetime.datetime

class InventoryList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[Inventory], list]
