from pydantic import BaseModel, constr, validator
import routers.tenant.models as m, datetime
from typing import Optional, List, Union
from constants import PHONE, EMAIL
from utils import as_form

class TenantBase(BaseModel):
    title: str
    sub_domain: str
    metatitle: Optional[str]
    description: Optional[str]
    phone: constr(regex=PHONE)
    email: constr(regex=EMAIL)
    street_address: Optional[str]
    postal_address: Optional[str]
    digital_address: Optional[str]

    class Config:
        orm_mode = True

    class Meta:
        model = m.Tenant

@as_form
class CreateTenant(TenantBase):
    @validator('sub_domain')
    def remove_all_spaces(cls, v):
        return v.replace(' ','')

@as_form
class UpdateTenant(TenantBase):
    title: Optional[str]
    is_active:Optional[bool]
    is_verified:Optional[bool]
    sub_domain: Optional[str]
    phone: Optional[constr(regex=PHONE)]
    email: Optional[constr(regex=EMAIL)]

class Tenant(TenantBase):
    id: int
    logo: str
    scheme: str
    bg_image: Optional[str]
    created: datetime.datetime
    updated: datetime.datetime

class TenantList(BaseModel):
    bk_size: int
    pg_size: int
    data: Union[List[Tenant], list]
