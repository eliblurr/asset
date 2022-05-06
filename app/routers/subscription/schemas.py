from typing import Optional, List, Union
from constants import PHONE, EMAIL, URL
import routers.subscription.models as m
from pydantic import BaseModel, constr
from utils import as_form
import datetime

# from routers.asset.schemas import AssetSummary

class AssetSummary(BaseModel):
    id: int
    make: str
    title: str
    model: str
    serial_number: str
    metatitle: Optional[str]
    description: Optional[str]

    class Config:
        orm_mode = True

class PackageBase(BaseModel):
    title: str
    metatitle: Optional[str]
    description: Optional[str]
    service_owner_url: Optional[constr(regex=URL)]
    service_owner_email: Optional[constr(regex=EMAIL)]
    service_owner_phone: Optional[constr(regex=PHONE)]
     
    class Config:
        orm_mode = True

    class Meta:
        model = m.Package

@as_form
class CreatePackage(PackageBase):
    pass
    
class UpdatePackage(PackageBase):
    title: Optional[str]
    status: Optional[bool]
    
class Package(PackageBase):
    id: int
    logo: Optional[str]
    created: datetime.datetime
    updated: datetime.datetime

class PackageList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[Package], list]

class SubscriptionBase(BaseModel):
    asset_id: int
    package_id: int
    price: Optional[float]

    class Config:
        orm_mode = True

    class Meta:
        model = m.Subscription

class CreateSubscription(SubscriptionBase):
    pass

class UpdateSubscription(BaseModel):
    price: Optional[float]
    status: Optional[bool]

class Subscription(BaseModel):
    asset_id: int
    package: Package
    asset: AssetSummary
    price: Optional[float]

    class Config:
        orm_mode = True

class SubscriptionList(BaseModel):
    bk_size: int
    pg_size: int
    data:  Union[List[Subscription], list]
