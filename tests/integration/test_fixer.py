import asyncio
import os
import re

import pytest

from fx.rates import ClientException, FixerApi, RatesApi

ENABLE = "FX_ENABLE_INTEGRATION_TESTS" in os.environ


# We need to override pytest-asyncio default event_loop fixture, else it closes the loop too early
@pytest.fixture
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture
def api() -> RatesApi:
    token = os.environ.get("FX_FIXER_TOKEN")
    if token is not None:
        return FixerApi(token)
    pytest.skip("FX_FIXER_TOKEN is empty")


@pytest.mark.skipif(
    not ENABLE, reason="FX_ENABLE_INTEGRATION_TESTS",
)
class TestFixerApi:
    @staticmethod
    @pytest.mark.asyncio
    async def test_get_symbols(api: RatesApi):
        symbols = await api.get_symbols()
        assert all(re.match(r"^[A-Z]{3}$", s) for s in symbols)

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_rate(api: RatesApi):
        r1 = await api.get_rate("BRL", "USD")
        r2 = await api.get_rate("USD", "BRL")
        assert pytest.approx(r1, 1.0 / r2)

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_rate_invalid_symbols(api: RatesApi):
        with pytest.raises(ClientException):
            await api.get_rate("foo", "bar")
        with pytest.raises(ClientException):
            await api.get_rate("foo", "USD")
        with pytest.raises(ClientException):
            await api.get_rate("USD", "foo")
