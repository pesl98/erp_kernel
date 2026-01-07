from typing import Any
from pydantic import BaseModel, Field

class ValueObject(BaseModel):
    """
    Base class for Value Objects. 
    Value Objects are immutable and defined by their attributes, not an identity.
    """
    class Config:
        frozen = True

class Money(ValueObject):
    amount: float
    currency: str = "USD"
    
    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError(f"Cannot add different currencies: {self.currency} vs {other.currency}")
        return Money(amount=self.amount + other.amount, currency=self.currency)

class Quantity(ValueObject):
    value: float
    unit: str = "PCE"
    
    def __add__(self, other: 'Quantity') -> 'Quantity':
        if self.unit != other.unit:
            raise ValueError(f"Cannot add different units: {self.unit} vs {other.unit}")
        return Quantity(value=self.value + other.value, unit=self.unit)
