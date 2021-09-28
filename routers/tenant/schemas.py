from pydantic import BaseModel, constr
from constants import PHONE, EMAIL
import routers.tenant.models as m
from typing import Optional, List
from datetime import datetime
from utils import as_form

class TenantBase(BaseModel):
    title: str
    sub_domain_id: str
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
    id: Optional[int]

class UpdateTenant(BaseModel):
    title: Optional[str]
    metatitle: Optional[str]
    description: Optional[str]
    sub_domain_id: Optional[str]
    street_address: Optional[str]
    postal_address: Optional[str]
    digital_address: Optional[str]
    email: Optional[constr(regex=EMAIL)]
    phone: Optional[constr(regex=PHONE)]

class Tenant(TenantBase):
    id: str
    created: datetime
    updated: datetime

class TenantList(BaseModel):
    bk_size: int
    pg_size: int
    data: List[Tenant]