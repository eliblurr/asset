from routers.currency import *
from routers.priority import *
from routers.manufacturer import *
from routers.policy import *
from routers.config import *
from routers.branch import *
from routers.faqs import *
from routers.user import *
from routers.catalogue import *
from routers.category import *
from routers.vendor import *
from routers.consumable import *
from routers.department import *
from routers.inventory import *
from routers.subscription import *
from routers.activity import *
from routers.log import *
from routers.proposal import *
from routers.upload import *
from routers.asset import *
from routers.request import *
from routers.tenant import *

from database import Base, Model

__all__=[
    'Base',
    'permission',
    'currency',
    'priority',
    'policy',
    'config',
    'account',
    'auth',
    'role',
    'faqs',
    'vendor',
    'tenant',
    'category',
    'manufacturer',
    'branch',
    'department', 
    'inventory',
    'upload',
    'activity',
    'consumable',
    'subscription',
    'logs', 
    'proposal', 
    'asset',
    'request',
    'catalogue'
]

from database import engine

tables=[table for table in Base.metadata.sorted_tables if table.schema=='public' or table.schema=='global']
Base.metadata.create_all(bind=engine, tables=tables)
Model.metadata.create_all(bind=engine)

'''
    Do this to order the the way each model interacts with Base from database.py
    Tenant Model is called last so Base will have all metadata from all the 
    other models[for use in create_tenant_schema]
'''