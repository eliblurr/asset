from routers.department.models import Department
from routers.inventory.models import Inventory
from routers.proposal.models import Proposal
from routers.request.models import Request
from routers.branch.models import Branch
from routers.tenant.models import Tenant
from routers.asset.models import Asset

objects = {
    'assets': Asset, 'requests':Request, 
    'proposals': Proposal,'inventories':Inventory, 
    'departments':Department
}