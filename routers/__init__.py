import routers.manufacturer.models 
import routers.priority.models 
import routers.policy.models 
import routers.vendor.models
import routers.faqs.models 
import routers.tenant.models

'''
    Do this to order the the way each model interacts with Base from database.py
    Tenant Model is called last so Base will have all metadata from all the 
    other models[for use in create_tenant_schema]
'''