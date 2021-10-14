from sqlalchemy import Column, String, Integer
from mixins import BaseMixin
from utils import gen_code
from database import Base

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