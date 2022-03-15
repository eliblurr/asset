from sqlalchemy import Column, String, event, Integer, ForeignKey
from exceptions import OperationNotAllowed
from sqlalchemy.orm import relationship
from mixins import BaseMixin
from database import Base

class RolePermission(Base):
    '''Role Permission Model'''
    __tablename__ = "role_permissions"

    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    permission_id = Column(Integer, ForeignKey('public.permissions.id'), primary_key=True)

class Role(BaseMixin, Base):
    '''Roles Model'''
    __tablename__ = "roles"

    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    users = relationship('User', back_populates="role")
    permissions = relationship('Permission', secondary=RolePermission.__table__, back_populates="roles")

    def has_perm(self, perm, db):
        return perm in self.permissions

    def add_perm(self, perm, db):
        if not self.has(perm):
            self.permissions.append(perm)
        db.commit()

    def remove_perm(self, perm, db):
        if self.has(perm):
            self.permissions.remove(perm)
        db.commit()
    
    def remove_all_perm(self, db):
        for perm in self.permissions:
            self.permissions.remove(perm)
        db.commit()

    def reset_perm(self, db):
        self.permissions.clear()
        db.commit() 

def after_create(target, connection, **kw):
    connection.execute(
        Role.__table__.insert(), 
        [   
            {"title":'Tenant Administrator', "permissions":[]},
            {"title":'Head of Department', "permissions":[]},
            {"title":'Facility Manager', "permissions":[]},
            {"title":'Head of Entity', "permissions":[]},
            {"title":'Store Manager', "permissions":[]},
            {"title":'Staff', "permissions":[]},
        ]   
    )

event.listen(Role.__table__, 'after_create', after_create)

@event.listens_for(Role.title, 'set', propagate=True)
def receive_set(target, value, oldvalue, initiator):
    if oldvalue=='Tenant Administrator' and value!=oldvalue:
        raise OperationNotAllowed('cannot update this property')