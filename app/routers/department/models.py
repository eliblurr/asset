from sqlalchemy import Column, String, ForeignKey, Integer, UniqueConstraint, func, event, select
from routers.user.account.models import User
from sqlalchemy.exc import IntegrityError
from rds.tasks import async_send_message
from sqlalchemy.orm import relationship
from utils import instance_changes
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

@event.listens_for(Department, "after_update")
@event.listens_for(Department, "after_insert")
def alert_department(mapper, connection, target):

    changes = instance_changes(target)
    head_of_department_id = changes.get('head_of_department_id', [None])    
    
    if head_of_department_id[0]:
        # stmt = select(User.push_id, User.first_name, User.last_name, Department.title, Department.updated, Department.id, Department.head_of_department_id).join(Department, Department.head_of_department_id==User.id).where(Department.id==target.id)

        stmt = select(User.push_id, User.first_name, User.last_name, BaseDepartment.title, Department.updated, Department.id, Department.head_of_department_id).join(Department, Department.head_of_department_id==User.id).join(BaseDepartment, BaseDepartment.id==Department.base_department_id).where(Department.id==target.id)

        with connection.begin():
            data = connection.execute(stmt)
            data = dict(data.mappings().first())

        if data:
            async_send_message(
                channel=data.get('push_id'),
                message={
                    'key':'department',
                    'message': "department assigned to {head_of_department} on {datetime}",
                    'meta': {
                        'id':data.get('id'), 
                        'title':data.get('title'),    
                        'datetime':data.get('updated'),               
                        'head_of_department_id':data.get('head_of_department_id'), 
                        'head_of_department':f'{data.get("first_name")} {data.get("last_name")}'
                    }
                }
            )