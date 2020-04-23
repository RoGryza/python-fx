"""SQL database definitions.

The database uses the :mod:`databases` database URI from the environment variable FX_DATABASE. It
defaults to `sqlite:///./fx.db`.
"""
import os
from typing import Iterator

from databases import Database
from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


DB_URL = os.environ.get("FX_DATABSE", "sqlite:///./fx.db")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Iterator[Database]:
    """Function for dependency injection with :class:`fastapi.Dependency`.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Trade(Base):
    """Trades table.
    """

    __tablename__ = "trades"

    trade_id = Column(String, primary_key=True)
    sell_ccy = Column(String, nullable=False)
    sell_amount = Column(Integer, nullable=False)
    buy_ccy = Column(String, nullable=False)
    rate = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
