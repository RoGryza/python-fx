import json
from math import floor

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from fx.model import BaseModel, Currency


class TestCurrency:
    @staticmethod
    @given(st.integers(min_value=0))
    def test_init_ok(i: int) -> None:
        assert i == Currency(i).value

    @staticmethod
    @given(st.integers(max_value=-1))
    def test_init_negative(i: int) -> None:
        with pytest.raises(ValueError):
            Currency(i)

    @staticmethod
    @given(st.integers(min_value=0))
    def test_validation_ok(i: int) -> None:
        class Model(BaseModel):
            c: Currency

        assert Model(c=i).c == Currency(i)
        assert Model(c=Currency(i)).c == Currency(i)

    @staticmethod
    @given(st.integers(max_value=-1))
    def test_validation_negative(i: int) -> None:
        class Model(BaseModel):
            c: Currency

        with pytest.raises(ValidationError) as e:
            Model(c=i)
        assert e.value.errors() == [
            {
                "loc": ("c",),
                "type": "value_error",
                "msg": f"Currency can't be negative, got {i!r}",
            }
        ]

    @staticmethod
    @given(st.floats() | st.text())
    def test_validation_wrong_type(x) -> None:
        class Model(BaseModel):
            c: Currency

        with pytest.raises(ValidationError) as e:
            Model(c=x)
        assert e.value.errors() == [
            {"loc": ("c",), "type": "type_error", "msg": "must be an integer",}
        ]

    @staticmethod
    @given(
        st.integers(min_value=0), st.integers(min_value=1),
    )
    def test_multiplication_integers(n: int, m: int) -> None:
        assert Currency(n) * m == Currency(n * m)

    @staticmethod
    @given(
        st.integers(min_value=0),
        st.floats(
            min_value=0.0,
            max_value=1_000_000_000,
            allow_nan=False,
            allow_infinity=False,
        ),
    )
    def test_multiplication_floats(n: int, s: float) -> None:
        assert Currency(n) * s == Currency(floor(n * s))

    @staticmethod
    @given(
        st.integers(min_value=0),
        st.floats(
            min_value=0, max_value=1_000_000_000, allow_nan=False, allow_infinity=False
        ),
    )
    def test_multiplication_commutative(n: int, s: float) -> None:
        assert Currency(n) * s == s * Currency(n)

    @staticmethod
    @given(st.integers(min_value=0), st.integers(min_value=0, max_value=99))
    def test_str(i: int, frac: int) -> None:
        assert str(Currency(100 * i + frac)) == f"{i}.{frac:02d}"


class TestBaseModel:
    @staticmethod
    @given(st.integers(min_value=0))
    def test_json_roundtrip(i: int) -> None:
        class Model(BaseModel):
            c: Currency

        model = Model(c=Currency(i))
        serialized = json.loads(model.json())
        assert model == Model(**serialized)
