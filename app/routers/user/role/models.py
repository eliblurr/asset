from mixins import BaseMixin, PermissionMixin
from sqlalchemy import Column, String, event

from sqlalchemy.orm import relationship
from database import TenantBase, Base

class Role(BaseMixin, PermissionMixin, Base):
    '''Roles Model'''
    __tablename__ = "roles"
    # __table_args__ = ({'schema':None},)

    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    users = relationship('User', back_populates="role")
    # User - Role <-> Role - Permissions


def after_create(target, connection, **kw):
    connection.execute(
        Role.__table__.insert(), 
        [
            {"title":'Head of Department', "permissions":0},
            {"title":'Facility Manager', "permissions":0},
            {"title":'Head of Entity', "permissions":0},
            {"title":'Store Manager', "permissions":0},
            {"title":'Staff', "permissions":0},
        ]   
    )

event.listen(Role.__table__, 'after_create', after_create)