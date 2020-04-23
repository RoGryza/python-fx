"""Common code for REST API models.
"""
from math import floor

import pydantic


class Currency:
    """Represents a currency amount.

    Stores values as integers interpred as fixed-point values with two decimal places to avoid
    issues with floating point precision (e.g. 1.05 is stored as the integer 105).

    Can be scaled by integer or floating point scalars, the result is always truncated to two
    decimal places.

    This class implements `__get_validators__`, which allows it to be used as fields in
    :mod:`pydantic` models.
    """

    __slots__ = ("value",)

    def __init__(self, value: int) -> None:
        if value < 0:
            raise ValueError(f"Currency can't be negative, got {value!r}")
        self.value = value

    @classmethod
    def __get_validators__(cls):
        yield cls._validate

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Currency):
            return NotImplemented
        return self.value == other.value

    @classmethod
    def _validate(cls, v) -> "Currency":
        if isinstance(v, Currency):
            return v
        if isinstance(v, int):
            return Currency(v)
        raise TypeError("must be an integer")

    def __mul__(self, other: object) -> "Currency":
        if not isinstance(other, (int, float)):
            return NotImplemented
        if other < 0:
            raise ValueError(
                f"Can't multiply currency with negative numbers, got {other!r}"
            )
        value = floor(self.value * other)
        return Currency(value)

    def __rmul__(self, other: object) -> "Currency":
        return self * other

    def __str__(self) -> str:
        if self.value == 0:
            return "0.00"
        int_, frac = divmod(self.value, 100)
        return f"{int_}.{frac:02d}"

    def __repr__(self) -> str:
        return f"Currency({self})"


class BaseModel(pydantic.BaseModel):
    """Use this base class instead of the default :class:`pydantic.BaseModel`, it configures common
    JSON encoders for the application's types.
    """

    class Config:
        json_encoders = {
            Currency: lambda c: c.value,
        }
