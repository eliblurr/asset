import routers.manufacturer.models as m, datetime
from typing import Optional, List, Union
from constants import URL, EMAIL, PHONE
from pydantic import BaseModel, constr
from utils import as_form

class ManufacturerBase(BaseModel):
    title: str
    scheme: Optional[str]
    metatitle: Optional[str]
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

@as_form
class UpdateManufacturer(ManufacturerBase):
    title: Optional[str]
    status: Optional[bool]

class Manufacturer(ManufacturerBase):
    id: int
    status: bool
    logo: Optional[str]
    created: datetime.datetime
    updated: datetime.datetime

class ManufacturerList(BaseModel):
    bk_size: int
    pg_size: int
    data: Union[List[Manufacturer], list]