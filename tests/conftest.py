from typing import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fx import app
from fx.database import Base, get_db
from fx.rates import DummyRatesApi, get_rates


@pytest.yield_fixture()
def test_client() -> Iterator[TestClient]:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    with TestClient(app) as client:
        app.dependency_overrides[get_db] = lambda: db
        app.dependency_overrides[get_rates] = lambda: DummyRatesApi()
        yield client  # type: ignore
        db.close()
        app.dependency_overrides = {}
    Base.metadata.drop_all(bind=engine)
