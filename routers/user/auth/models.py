from sqlalchemy import Column, String, event
from mixins import BaseMixin
from database import Base
from passlib import pwd

# class PasswordResetCode(BaseMixin, Base):
#     __tablename__ = 'password_reset_codes'

#     code = Column(String, unique=True)
#     user_id = Column(Integer, unique=True)

#     @staticmethod
#     def generate_code():
#         return gen_code(9)

class RevokedToken(BaseMixin, Base):
    __tablename__ = 'revoked_tokens'

    token = Column(String)

class PasswordResetCode(Base):
    __tablename__ = 'password_reset_codes'

    email = Column(String, unique=True, primary_key=True)
    code = Column(String, default=pwd.genword)

@event.listens_for(PasswordResetCode, 'before_insert')
def delete_existing_value(mapper, connection, target):
    connection.execute("""DELETE FROM :table WHERE email=:email;""",{'table':PasswordResetCode.__tablename__, 'email':target.email})