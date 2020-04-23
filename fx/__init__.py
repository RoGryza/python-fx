"""Main module for the fx application.

Instantiates a :class:`FastAPI` instance and declares the REST API.
"""
import os
import random
import string
from datetime import datetime
from typing import Iterator, List

from databases import Database
from fastapi import Depends, FastAPI, Query, Request
from fastapi.responses import JSONResponse
from pydantic import root_validator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from fx.database import Base, Trade, engine, get_db
from fx.model import BaseModel, Currency
from fx.rates import ClientException, RatesApi, get_rates

app = FastAPI(docs_url=None, redoc_url=None)
Base.metadata.create_all(bind=engine, checkfirst=True)


@app.exception_handler(ClientException)
async def _client_exception_handler(_request: Request, exc: ClientException):
    # Respond with 400 when a ClientException is raised.
    return JSONResponse(status_code=400, content={"message": str(exc)})


class TradeModel(BaseModel):
    """Response model for each trade sent in /trades.
    """

    id: str
    sell_ccy: str
    sell_amount: Currency
    buy_ccy: str
    buy_amount: Currency
    rate: float
    timestamp: datetime


class TradesResponse(BaseModel):
    """Response body for /trades.
    """

    trades: List[TradeModel]


@app.get("/trades", response_model=TradesResponse)
async def get_trades(db: Session = Depends(get_db)):
    """Returns a list of all trades, sorted in descending order by timetamps.
    """
    trade_rows = db.query(Trade).order_by(Trade.timestamp.desc())
    return TradesResponse(
        trades=[
            TradeModel(
                id=r.trade_id,
                sell_ccy=r.sell_ccy,
                sell_amount=Currency(r.sell_amount),
                buy_ccy=r.buy_ccy,
                buy_amount=Currency(r.sell_amount) * r.rate,
                rate=r.rate,
                timestamp=r.timestamp,
            )
            for r in trade_rows
        ]
    )


class NewTradeRequest(BaseModel):
    """Request body for POST /trade.
    """

    sell_ccy: str
    sell_amount: Currency
    buy_ccy: str
    rate: float

    @root_validator
    def _validate_currencies(cls, values):
        # pylint: disable=no-self-argument,no-self-use
        if "sell_ccy" in values and "buy_ccy" in values:
            if values["sell_ccy"] == values["buy_ccy"]:
                raise ValueError("buy_ccy and sell_ccy must not be the same symbol")
        return values


class NewTradeResponse(BaseModel):
    """Response body for POST /trades.
    """

    id: str
    sell_ccy: str
    sell_amount: Currency
    buy_ccy: str
    buy_amount: Currency
    rate: float
    timestamp: datetime


@app.post("/trades", response_model=NewTradeResponse)
async def post_trade(trade: NewTradeRequest, db: Session = Depends(get_db)):
    """Create a new trade.
    """

    new_id = "TR" + "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(7)
    )
    timestamp = datetime.utcnow()

    db.add(
        Trade(
            trade_id=new_id,
            sell_ccy=trade.sell_ccy,
            sell_amount=trade.sell_amount.value,
            buy_ccy=trade.buy_ccy,
            rate=trade.rate,
            timestamp=timestamp,
        )
    )
    db.commit()

    return NewTradeResponse(
        id=new_id,
        sell_ccy=trade.sell_ccy,
        sell_amount=trade.sell_amount,
        buy_ccy=trade.buy_ccy,
        buy_amount=trade.sell_amount * trade.rate,
        rate=trade.rate,
        timestamp=timestamp,
    )


class SymbolsResponse(BaseModel):
    """Response body for /symbols.
    """

    symbols: List[str]


@app.get("/symbols", response_model=SymbolsResponse)
async def get_symbols(rates: RatesApi = Depends(get_rates)):
    """Returns all available symbols.
    """
    return SymbolsResponse(symbols=await rates.get_symbols())


class RateResponse(BaseModel):
    """Response body for /rate.
    """

    rate: float


@app.get("/rate", response_model=RateResponse)
async def get_rate(
    from_symbol: str = Query(..., regex="^[A-Z]{3}$"),
    to_symbol: str = Query(..., regex="^[A-Z]{3}$"),
    rates: RatesApi = Depends(get_rates),
):
    """Returns the exchange rate for from `from_symbol` to `to_symbol`.
    """
    return RateResponse(rate=await rates.get_rate(from_symbol, to_symbol))
