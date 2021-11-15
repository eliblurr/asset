from sqlalchemy import Column, String, Integer, Enum, CheckConstraint
from babel.numbers import list_currencies
from mixins import BaseMixin
from database import Base
import enum

CURRENCY=[(currency) for currency in list_currencies()]
CURRENCY_CHOICES = {v:v for v in CURRENCY}
CurrencyChoice = enum.Enum('CurrencyChoice', CURRENCY_CHOICES)

class Currency(BaseMixin, Base):
    '''Currency Model'''
    __tablename__ = "currencies"
    __table_args__ = ({'schema':'public'},)

    currency = Column(Enum(CurrencyChoice), nullable=False, unique=True)