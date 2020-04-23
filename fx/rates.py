"""Module declaring the API for exchange rates.

By default the application uses dummy fixed values for exchange rates. The fixer.io API can be used
by setting the environment variable FX_FIXER_TOKEN to your API key (see
https://fixer.io/documentation).
"""

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


class ApiException(Exception):
    """The remote API responded with an error the application doesn't handle. Ultimately this will
    result in a 500 error to the client.
    """


class ClientException(Exception):
    """The API responded with an error due to a bad request we forwarded from the client. This is
    forwarded as a 400 error to the client.
    """


FIXER_TOKEN = os.environ.get("FX_FIXER_TOKEN")
if FIXER_TOKEN is None:
    logger.warning(
        "FX_FIXER_TOKEN environment variable not set, defaulting to dummy API."
    )


def get_rates() -> Iterator["RatesApi"]:
    """Function for dependency injection with :class:`fastapi.Dependency`.
    """
    # We check for FIXER_TOKEN here instead of at the toplevel because then mypy undertands that
    # FIXER_TOKEN can't be None when we instantiate FixerApi
    if FIXER_TOKEN is None:
        yield DummyRatesApi()
    else:
        yield FixerApi(FIXER_TOKEN)


class RatesApi(ABC):
    """Declares functionality which rates APIs should implement.
    """

    @abstractmethod
    async def get_symbols(self) -> List[str]:
        """Returns a list of all available symbols.
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_rate(self, from_symbol: str, to_symbol: str) -> float:
        """Returns the current exchange rate from `from_symbol` to `to_symbol`.

        Raises
        ------
        ClientException
            When `from_symbol` or `to_symbol` is invalid.
        """
        raise NotImplementedError()


class DummyRatesApi(RatesApi):
    """Dummy API with fixed rates defined in `DummyRatesApi.RATES`.
    """

    RATES = {
        "GBP": 1.23,
        "BRL": 0.19,
        "USD": 1.00,
    }

    async def get_symbols(self) -> List[str]:
        return list(self.RATES)

    async def get_rate(self, from_symbol: str, to_symbol: str) -> float:
        return self.sync_get_rate(from_symbol, to_symbol)

    @classmethod
    def sync_get_rate(cls, from_symbol: str, to_symbol: str) -> float:
        """Can be used instead of `get_rate` to ease unit testing.
        """
        if from_symbol not in cls.RATES:
            raise ClientException(f"Unknown symbol {from_symbol!r}")
        if to_symbol not in cls.RATES:
            raise ClientException(f"Unknown symbol {to_symbol!r}")
        from_rate = cls.RATES[from_symbol]
        to_rate = cls.RATES[to_symbol]
        return from_rate / to_rate


@dataclass
class _CachedResponse:
    """Cached HTTP responses for fixer.io
    """

    resp: Dict[str, Any]
    etag: str
    date: str


class FixerApi(RatesApi):
    """Implementation of :class:`RatesApi` using the fixer.io API.
    """

    BASE_URL = "http://data.fixer.io/api/"
    _session: Optional[aiohttp.ClientSession] = None

    def __init__(self, access_key: str) -> None:
        self._key = access_key
        self._cached_responses: Dict[str, _CachedResponse] = {}

    @classmethod
    def _cached_session(cls) -> aiohttp.ClientSession:
        if cls._session is None:
            cls._session = aiohttp.ClientSession()
        return cls._session

    async def get_symbols(self) -> List[str]:
        data = await self._get("symbols")
        return list(data["symbols"].keys())

    async def get_rate(self, from_symbol: str, to_symbol: str) -> float:
        data = await self._get("latest")
        rates = data["rates"]
        if from_symbol not in rates:
            raise ClientException(f"Unknown symbol {from_symbol!r}")
        if to_symbol not in rates:
            raise ClientException(f"Unknown symbol {to_symbol!r}")
        return rates[to_symbol] / rates[from_symbol]

    async def _get(self, endpoint: str) -> Dict[str, Any]:
        headers = {}
        cached = self._cached_responses.get(endpoint)
        if cached:
            headers["If-None-Match"] = cached.etag
            headers["If-Modified-Since"] = cached.date
        async with self._cached_session().get(
            f"{self.BASE_URL}{endpoint}",
            params={"access_key": self._key},
            headers=headers,
        ) as resp:
            # If the content wasn't modified since the lest fetched etag, just resend it
            if resp.status == 304:
                assert cached
                return cached.resp

            data = await resp.json()
            if data["success"]:
                if "ETag" in resp.headers and "Date" in resp.headers:
                    self._cached_responses[endpoint] = _CachedResponse(
                        resp=data, etag=resp.headers["ETag"], date=resp.headers["Date"],
                    )
                return data
            if data["error"]["code"] == 202:
                # 202 is the error code for invalid symbols
                # See https://fixer.io/documentation
                raise ClientException("You have provided invalid symbols")
            raise ApiException(data["error"])
