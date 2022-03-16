from babel.numbers import list_currencies, get_currency_symbol, format_currency
from sqlalchemy import Column, Enum, event
from mixins import BaseMixin
from database import Base
import enum

CurrencyChoice = enum.Enum('CurrencyChoice', {v:v for v in list_currencies()})

class Currency(BaseMixin, Base):
    '''Currency Model'''
    __tablename__ = "currencies"

    currency = Column(Enum(CurrencyChoice), nullable=False, unique=True, default=True)

    def get_currency_symbol(self):
        return get_currency_symbol(self.currency.value)

    def format_currency(self, value:float):
        return format_currency(value, self.currency.value)

def after_create(target, connection, **kw):
    with connection.begin():
        connection.execute(
            Currency.__table__.insert(), 
            [
                {"currency":'USD'}, {"currency":'GHS'}, 
                {"currency":'EUR'}, {"currency":'GBP'}, 
            ]
        )

event.listen(Currency.__table__, "after_create", after_create)
