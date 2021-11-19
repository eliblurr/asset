import datetime, enum

class AResource(str, enum.Enum):
    assets = 'assets'
    requests = 'requests'
    proposals = 'proposals'
    inventories = 'inventories'
    departments = 'departments'

class Level(str, enum.Enum):
    db = 'db'
    tenant = 'tenant'
    branch = 'branch'