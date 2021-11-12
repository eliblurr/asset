from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from config import settings

if settings.DATABASE_URL.split(':', 1)[0] == 'postgres':
    DATABASE_URL = 'postgresql:' + settings.DATABASE_URL.split(':', 1)[1]
else:
    DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
TenantBase = declarative_base(metadata=MetaData(schema=None))
Base = declarative_base(metadata=MetaData(schema=None))
metadata = MetaData()

def merge_metadata(*original_metadata) -> MetaData:
    merged = MetaData()
    for original_metadatum in original_metadata:
        for table in original_metadatum.tables.values():
            table.to_metadata(merged)
    return merged

GlobalBase = declarative_base(metadata=merge_metadata(Base.metadata, TenantBase.metadata))
# merge_metadata(metadata)



# Base1 = declarative_base()
# Base2 = declarative_base()
# print(merge_metadata(Base.metadata, TenantBase.metadata).tables)

# tenant_metadata = MetaData(schema=None)


# metadata2 = MetaData(schema='public')
# Base2 = declarative_base(metadata=metadata2)