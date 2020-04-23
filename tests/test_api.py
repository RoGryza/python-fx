import itertools

from fastapi.testclient import TestClient

from fx import app
from fx.rates import DummyRatesApi


def test_get_symbols(test_client: TestClient) -> None:
    response = test_client.get("/symbols")
    assert response.status_code == 200
    expected_symbols = list(DummyRatesApi.RATES.keys())
    assert {"symbols": expected_symbols} == response.json()


def test_get_rate(test_client: TestClient) -> None:
    all_symbols = list(DummyRatesApi.RATES.keys())
    all_pairs = itertools.product(all_symbols, all_symbols)
    for a, b in all_pairs:
        response = test_client.get(f"/rate", params={"from_symbol": a, "to_symbol": b})
        assert response.status_code == 200
        assert {"rate": DummyRatesApi.sync_get_rate(a, b)} == response.json()


def test_get_rate_invalid_symbols(test_client: TestClient) -> None:
    response = test_client.get(
        f"/rate", params={"from_symbol": "USD", "to_symbol": "FOO"}
    )
    assert response.status_code == 400
    response = test_client.get(
        f"/rate", params={"from_symbol": "USD", "to_symbol": "invalid"}
    )
    assert response.status_code == 422
    response = test_client.get(
        f"/rate", params={"from_symbol": "FOO", "to_symbol": "USD"}
    )
    assert response.status_code == 400
    response = test_client.get(
        f"/rate", params={"from_symbol": "invalid", "to_symbol": "USD"}
    )
    assert response.status_code == 422


def test_api_trades(test_client: TestClient) -> None:
    response = test_client.get("/trades")
    assert response.status_code == 200
    assert {"trades": []} == response.json()

    requests = [
        {"sell_ccy": "BRL", "sell_amount": 100, "buy_ccy": "GBP", "rate": 1.0,},
        {"sell_ccy": "GBP", "sell_amount": 201, "buy_ccy": "USD", "rate": 2.3,},
        {"sell_ccy": "BRL", "sell_amount": 302, "buy_ccy": "GBP", "rate": 3.6,},
    ]
    trades: list = []
    for req in requests:
        response = test_client.post("/trades", json=req)
        trades.insert(0, response.json())

        response = test_client.get("/trades")
        assert response.status_code == 200
        assert {"trades": trades} == response.json()


def test_post_trade_same_symbol(test_client: TestClient) -> None:
    response = test_client.post(
        "/trades",
        json={"sell_ccy": "BRL", "sell_amount": 100, "buy_ccy": "BRL", "rate": 1.0,},
    )
    assert response.status_code == 422
