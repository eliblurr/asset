from sqlalchemy import Column, String, ForeignKey, Integer, UniqueConstraint, func, event, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from mixins import BaseMixin
from database import Base

class BaseDepartment(BaseMixin, Base):
    '''Base Department Model'''
    __tablename__ = 'base_departments'

    title = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)

class Department(BaseMixin, Base):
    '''Department Model'''
    __tablename__ = 'departments'
    __table_args__ = (UniqueConstraint('base_department_id', 'branch_id', name='_id_branch_id_'),)

    info = relationship("BaseDepartment", cascade="all, delete")
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=True)
    head_of_department_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    base_department_id = Column(Integer, ForeignKey('base_departments.id'), nullable=False) 
    head_of_department = relationship('User', foreign_keys="Department.head_of_department_id")
    staff = relationship('User', back_populates="department", foreign_keys="[User.department_id]")
    inventories = relationship('Inventory', back_populates="department")
    proposals = relationship('Proposal', back_populates="department")
    requests = relationship('Request', back_populates="departments")
    branch = relationship('Branch', back_populates="departments")

@event.listens_for(Department, 'before_insert')
@event.listens_for(Department, 'before_update')
def check_integrity(mapper, connection, target):
    table = Department.__table__
    args = [table.c.base_department_id==target.base_department_id, table.c.branch_id==target.branch_id]
    if target.id:args.append([table.c.id!=target.id])
    with connection.begin():
        res = connection.execute(select(func.count()).select_from(table).where(*args)).scalar()
        if res:raise IntegrityError('Unacceptable Operation', 'branch_id', 'branch_id and base_department_id must be unique together')