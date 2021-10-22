from sqlalchemy import Column, String, Boolean, Integer, event, CheckConstraint
from sqlalchemy.orm import validates
from constants import COLOR_HEX
from database import TenantBase
from mixins import BaseMixin
import re

class Priority(BaseMixin, TenantBase):
    '''Priority Model'''
    __tablename__ = "priorities"
    
    color_hex = Column(String, nullable=False)
    title = Column(String, nullable=False, unique=True)
    default = Column(Boolean, nullable=False, default=False)
    index = Column(Integer, CheckConstraint('index>0'), autoincrement=True, nullable=False, unique=True, index=True)

    @validates('color_hex')
    def validate_hex(self, key, value):
        assert re.search(COLOR_HEX, value), 'invalid color hex format for color_hex'
        return value

def after_create(target, connection, **kw):
    connection.execute(
        Priority.__table__.insert(), 
        [
            {"title":'low', "index":1, "color_hex":'#d63031', "default":False}, 
            {"title":'medium', "index":2, "color_hex":'#fdcb6e', "default":True}, 
            {"title":'high', "index":3, "color_hex":'#00b894', "default":False}, 
        ]
    )
event.listen(Priority.__table__, "after_create", after_create)

@event.listens_for(Priority, 'before_insert')
@event.listens_for(Priority, 'before_update')
def check_default_table(mapper, connection, target):
    connection.execute(
        Priority.__table__.update().where(Priority.__table__.c.default==True).values(default=False)
    )
    # from sqlalchemy import bindparam
    # connection.execute(
    #     Priority.__table__.update().where(Priority.__table__.c.default==bindparam('_search')).values({
    #         'default': bindparam('default'),
    #     }),
    #     [
    #         {'_search': True, 'default': False},
    #     ]
    # )
