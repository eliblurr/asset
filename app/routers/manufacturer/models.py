from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint, event, func, CheckConstraint
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from constants import EMAIL, PHONE, URL
from sqlalchemy.orm import validates
from mixins import BaseMixin
from utils import today_str
from database import Base
from ctypes import File
import re

class Manufacturer(BaseMixin, Base):
    '''Manufacturer Model'''
    __tablename__ = "manufacturers"
    __table_args__ = (
        UniqueConstraint('title', 'tenant_key', name='uix_tnt_key_man'),
        {'schema':'public'},
    )

    email = Column(String, nullable=True)
    title = Column(String, nullable=False)
    contact = Column(String, nullable=True)
    website = Column(String, nullable=True)
    metatitle = Column(String, nullable=True)
    tenant_key = Column(String, nullable=True)
    description = Column(String, nullable=False)
    logo = Column(File(upload_to=f'manufaturers/{today_str()}/images/logo/', size=(100,100)))

    @validates('email')
    def validate_email(self, key, address):
        assert re.search(EMAIL, address), 'invalid email format'
        return address
    
    @validates('contact')
    def validate_phone(self, key, address):
        assert re.search(PHONE, address), 'invalid phone format'
        return address

    @validates('website')
    def validate_website(self, key, address):
        assert re.search(URL, address), 'invalid url format'
        return address

@event.listens_for(Manufacturer, 'before_insert')
@event.listens_for(Manufacturer, 'before_update')
def check_integrity(mapper, connection, target):
    res = connection.execute(
        Manufacturer.__table__.select().where(func.lower(Manufacturer.__table__.c.title) == target.title.lower(), Manufacturer.__table__.c.tenant_key==None)
    ).rowcount
    if res: raise IntegrityError('Unacceptable Operation', 'title', 'IntegrityError')