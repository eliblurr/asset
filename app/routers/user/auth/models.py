from sqlalchemy import Column, String, event
from mixins import GenCodeMixin, BaseMixin
from sqlalchemy.orm import validates 
from ..account.models import *
from constants import EMAIL
from database import Base
import re

class EmailVerificationCode(GenCodeMixin, Base):
    '''Email Verification model'''
    __tablename__ = 'email_verication_codes'
    __table_args__ = ({'schema':'public'},)

    email = Column(String, unique=True, primary_key=True)
    
    @validates('email')
    def validate_email(self, key, value):
        assert re.search(EMAIL, value), 'invalid email format'
        return value

class RevokedToken(BaseMixin, Base):
    __tablename__ = 'revoked_tokens'
    __table_args__ = ({'schema':'public'},)

    jti = Column(String)

@event.listens_for(EmailVerificationCode, 'before_insert')
def delete_existing_value(mapper, connection, target):
    with connection.begin():
        # connection.execute("""DELETE FROM email_verication_codes WHERE email=:email""",{'email':target.email})

        # d = addresses_table.delete().where(addresses_table.c.retired == 1)
# d.execute()

        connection.execute(
            EmailVerificationCode.__table__.delete().where(EmailVerificationCode.__table__.c.email == target.email)
        )