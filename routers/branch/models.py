from sqlalchemy import Column, String, Integer, ForeignKey, event
from sqlalchemy.orm import relationship, validates
from constants import EMAIL, PHONE, URL
from mixins import BaseMixin
from database import Base
import re

class Branch(BaseMixin, Base):
    '''Branch Model'''
    __tablename__ = 'branches'

    url = Column(String, nullable=True)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    metatitle = Column(String, nullable=True)
    description = Column(String, nullable=True)
    postal_address = Column(String, nullable=True)
    street_address = Column(String, nullable=True)
    digital_address = Column(String, nullable=True)
    title = Column(String, nullable=False, unique=True)
    
    staff = relationship("User", back_populates="branch")
    departments = relationship("Department", back_populates="branch")

    @validates('email')
    def validate_email(self, key, address):
        assert re.search(EMAIL, address), 'invalid email format'
        return address

    @validates('contact')
    def validate_phone(self, key, address):
        assert re.search(PHONE, address), 'invalid phone format'
        return address

    @validates('url')
    def validate_url(self, key, address):
        assert re.search(URL, address), 'invalid url format'
        return address

@event.listens_for(Branch, 'after_delete')
def remove_file(mapper, connection, target):
    from routers.upload.models import Upload
    with connection.begin():
        connection.execute(Upload.__table__.delete().where(Upload.object==target))

# class BranchDepartment(Base):
#     '''Branch Department Model'''
#     __tablename__ = 'branch_departments'

#     branch_id = Column(Integer, ForeignKey('branches.id'), primary_key=True)
#     department_id = Column(Integer, ForeignKey('departments.id'), primary_key=True)

#     # ...Make Association Table
#     # inventories

# from sqlalchemy.orm import column_property
# from sqlalchemy import select, text

# departments = relationship("Department", secondary=BranchDepartment.__table__, back_populates="branches") 

# inventories = column_property(
#     select()
# )

# inventories = relationship(
#     "Inventory",
#     secondary="Inventory.departments",
#     primaryjoin="Branch.id==Inventory.branch_id",
#     secondaryjoin="Inventory.department_id==Department.id"
# )

# inventories = column_property(
#     select(text('Inventory')).join(
#        text(' Branch, Branch.departments')
#     ).where(
#         text(
#             "or_("
#             "Inventory.branch_id==Branch.id"
#             "and_(Inventory.department_id==BranchDepartment.department_id, Branch.id==BranchDepartment.branch_id)"
#             ")"
#         )
#     ).scalar_subquery() 
# )

# inventories = column_property(
#     select(text('Inventory')).where(text('Inventory.branch_id==Branch.id')).scalar_subquery()   
# )

# select(
    #     text('Inventory'))
    # ).where(text('Inventory.branch_id==Branch.id')
    # select(text('Department')).where(text('Inventory.department_id==Department.id')).scalar_subquery()

# inventories = relationship('Inventory', cascade="all, delete", lazy='dynamic', back_populates="branch")

#     secondary="join(Branch, Inventory, Branch.departments)",
# #     # "join(Branch, BranchDepartment, Branch.id==BranchDepartment.branch_id).join(Inventory, BranchDepartment.department_id==Inventory.department_id )",
#     primaryjoin=
# #     # secondaryjoin="and_(Branch.id==BranchDepartment.branch_id, BranchDepartment.department_id==Inventory.department_id)",

#     "or_(Branch.id==Inventory.branch_id,"
#     "and_(Branch.id==BranchDepartment.branch_id, Inventory.department_id==BranchDepartment.department_id))"
#     # "and_(Branch.id==BranchDepartment.branch_id,Inventory.department_id==BranchDepartment.department_id))"


# db.query(Inventoties).join()

# inventories = relationship('Inventory', back_populates="branch", cascade="all, delete", lazy='dynamic') # include join through departements
# primaryjoin="and_(User.id==Address.user_id, "
#                     "Address.city=='Boston')"
# assets = relationship('Asset', back_populates="branch", cascade="all, delete", lazy='dynamic') # custom join
