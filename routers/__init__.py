import routers.activity.models
import routers.asset.models
import routers.catalogue.models
import routers.currency.models
import routers.user.account.models 
import routers.user.role.models
import routers.department.models 
import routers.inventory.models
import routers.proposal.models
import routers.priority.models 
import routers.request.models
import routers.policy.models 
import routers.vendor.models
import routers.branch.models 
import routers.faqs.models 
import routers.manufacturer.models 
import routers.category.models
import routers.tenant.models

from database import Base

__all__=[
    Base
]

# print(
#     Base.metadata.sorted_tables
#     # [table for table in Base.metadata.sorted_tables if table.schema=='public']
# )

'''
    Do this to order the the way each model interacts with Base from database.py
    Tenant Model is called last so Base will have all metadata from all the 
    other models[for use in create_tenant_schema]
'''