from typing import Optional, List, Union
from constants import URL, EMAIL, PHONE
from pydantic import BaseModel, constr
import routers.vendor.models as m
import datetime

class VendorBase(BaseModel):
    title: str
    metatitle: Optional[str]
    description: Optional[str]
    url: Optional[constr(regex=URL)]
    email: Optional[constr(regex=EMAIL)]
    contact: Optional[constr(regex=PHONE)]

    class Config:
        orm_mode = True

    class Meta:
        model = m.Vendor

class CreateVendor(VendorBase):
    pass
    
class UpdateVendor(VendorBase):
    title: Optional[str]
    status: Optional[bool]

class Vendor(VendorBase):
    id: int
    status: bool
    created: datetime.datetime
    updated: datetime.datetime

class VendorList(BaseModel):
    bk_size: int
    pg_size: int
    data: Union[List[Vendor], list]