from typing import Optional, List, Union
from constants import URL, EMAIL, PHONE
import routers.manufacturer.models as m
from pydantic import BaseModel, constr
from utils import as_form
import datetime

class ManufacturerBase(BaseModel):
    title: str
    metatitle: Optional[str]
    tenant_key: Optional[str]
    description: Optional[str]
    email: Optional[constr(regex=EMAIL)]
    website: Optional[constr(regex=URL)]
    contact: Optional[constr(regex=PHONE)]

    class Config:
        orm_mode = True

    class Meta:
        model = m.Manufacturer

@as_form
class CreateManufacturer(ManufacturerBase):
    status: Optional[bool]

class UpdateManufacturer(BaseModel):
    title: Optional[str]
    status: Optional[bool]
    metatitle: Optional[str]
    tenant_key: Optional[str]
    description: Optional[str]
    email: Optional[constr(regex=EMAIL)]
    website: Optional[constr(regex=URL)]
    contact: Optional[constr(regex=PHONE)]

class Manufacturer(ManufacturerBase):
    id: int
    status: bool
    created: datetime.datetime
    updated: datetime.datetime

class ManufacturerList(BaseModel):
    bk_size: int
    pg_size: int
    data: Union[List[Manufacturer], list]