from sqlalchemy import Column, String, Integer, event, func, select, or_
from sqlalchemy.orm import relationship, validates
from sqlalchemy.exc import IntegrityError
from constants import EMAIL, PHONE, URL
from rds.tasks import async_remove_file
from mixins import BaseMixin
from utils import today_str
from database import Base
from ctypes import File
import re

class Manufacturer(BaseMixin, Base):
    '''Manufacturer Model'''
    __tablename__ = "manufacturers"
    __table_args__ = ({'schema':'public'},)

    url = Column(String, nullable=True)
    email = Column(String, nullable=True)
    scheme = Column(String, nullable=True)
    title = Column(String, nullable=False)
    contact = Column(String, nullable=True)
    metatitle = Column(String, nullable=True)
    description = Column(String, nullable=True)
    logo = Column(File(upload_to=f'{today_str()}', size=(100,100)))
    
    @validates('email')
    def validate_email(self, key, address):
        assert re.search(EMAIL, address), 'invalid email format'
        return address

    @validates('contact')
    def validate_phone(self, key, address):
        assert re.search(PHONE, address), 'invalid phone format'
        return address

    @validates('url')
    def validate_website(self, key, address):
        assert re.search(URL, address), 'invalid url format'
        return address

@event.listens_for(Manufacturer.logo, 'set', propagate=True)
def receive_set(target, value, oldvalue, initiator):
    if oldvalue:async_remove_file(oldvalue)

@event.listens_for(Manufacturer, 'before_insert')
@event.listens_for(Manufacturer, 'before_update')
def check_integrity(mapper, connection, target):
    with connection.begin():
        table = Manufacturer.__table__
        res = connection.execute(select(func.count()).select_from(table).where(func.lower(table.c.title)==target.title.lower(), or_(table.c.scheme==target.scheme, table.c.scheme==None))).scalar()
        connection.execute(table.update().where(func.lower(table.c.title)==target.title.lower(), table.c.scheme!=None), {"status": False})
        if target.id:
            res = connection.execute(select(func.count()).select_from(table).where(func.lower(table.c.title)==target.title.lower(), or_(table.c.scheme==target.scheme, table.c.scheme==None), table.c.id!=target.id)).scalar()
        if res:raise IntegrityError('Unacceptable Operation', '[title, scheme]', 'title and scheme must be unique together')