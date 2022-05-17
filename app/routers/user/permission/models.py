from sqlalchemy import Column, String, event, Integer, ForeignKey, select
from mixins import BaseMixin, BaseMethodMixin
from ..role.models import RolePermission
from sqlalchemy.orm import relationship
from database import Base
from constants import OPS

# https://github.com/holgi/fastapi-permissions -> ACL
# https://fastapi-contrib.readthedocs.io/en/latest/readme.html

class Permission(BaseMixin, Base):
    '''Permissions Model'''
    __tablename__ = "permissions"
    __table_args__ = ({'schema':'public'},)
    
    op = Column(String , nullable=False)
    name = Column(String , unique=True, nullable=False)
    code_name = Column(String , unique=True, nullable=False)
    description = Column(String, nullable=True)
    content_type_id = Column(Integer, ForeignKey('public.content_types.id'))
    content_type = relationship("ContentType", back_populates="permissions")
    roles = relationship('Role', secondary=RolePermission.__table__, back_populates="permissions")
    
class ContentType(BaseMethodMixin, Base):
    '''Content Types Model'''
    __tablename__ = "content_types"
    __table_args__ = ({'schema':'public'},)

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    model = Column(String, nullable=False)
    permissions = relationship("Permission", back_populates="content_type")

def after_create(target, connection, **kw):
    with connection.begin():
        connection.execute(
            ContentType.__table__.insert(), 
            [{"model":str(_map.mapped_table.name)} for _map in Base.registry.mappers]
        )

def after_create_permission(target, connection, **kw):
    with connection.begin():
        rows = connection.execute(ContentType.__table__.select()).all()
        connection.execute(
            Permission.__table__.insert(), [
                {
                    'name': f'Can {op} {" ".join(row[1].split("_"))}',
                    'code_name':f'can_{op}_{row[1]}',
                    'content_type_id':row[0],
                    'op':op
                } for op in OPS for row in rows
            ]
        )

event.listen(ContentType.__table__, "after_create", after_create)
event.listen(Permission.__table__, "after_create", after_create_permission)
