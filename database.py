from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from utils import db_url

engine = create_engine(db_url()) #, connect_args={"check_same_thread": False}
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base(metadata=MetaData(schema=None))

# Base_1 = declarative_base(metadata=MetaData(schema=1))
# Base_2 = declarative_base(metadata=MetaData(schema=2))

# def merge_metadata(*original_metadata) -> MetaData:
#     merged = MetaData()
#     for original_metadatum in original_metadata:
#         for table in original_metadatum.tables.values():
#             table.to_metadata(merged)
#     return merged

# Base = declarative_base(metadata=merge_metadata(Base_1.metadata, Base_2.metadata))