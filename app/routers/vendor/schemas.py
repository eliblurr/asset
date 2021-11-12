from typing import Optional, List, Union
from constants import URL, EMAIL, PHONE
from pydantic import BaseModel, constr
import routers.vendor.models as m
import datetime

class VendorBase(BaseModel):
    title: str
    email: Optional[constr(regex=EMAIL)]
    website: Optional[constr(regex=URL)]
    contact: Optional[constr(regex=PHONE)]

    class Config:
        orm_mode = True

    class Meta:
        model = m.Vendor

class CreateVendor(VendorBase):
    status: Optional[bool]

class UpdateVendor(BaseModel):
    title: Optional[str]
    email: Optional[constr(regex=EMAIL)]
    website: Optional[constr(regex=URL)]
    contact: Optional[constr(regex=EMAIL)]

class Vendor(VendorBase):
    id: int
    status: bool
    created: datetime.datetime
    updated: datetime.datetime

class VendorList(BaseModel):
    bk_size: int
    pg_size: int
    data: Union[List[Vendor], list]