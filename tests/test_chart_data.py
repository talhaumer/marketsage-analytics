"""Tests for GET /chart-data endpoint."""
import pytest
import pandas as pd
from fastapi.testclient import TestClient
from unittest.mock import patch


@pytest.fixture
def client():
    from api.main import app
    return TestClient(app)


def _mock_hist():
    idx = pd.DatetimeIndex([pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-03")])
    return pd.DataFrame(
        {
            "Close": [185.2, 186.0],
            "Volume": [82000000, 75000000],
            "High": [187.0, 187.5],
            "Low": [184.0, 185.5],
            "Open": [184.5, 185.8],
        },
        index=idx,
    )


def test_chart_data_returns_ohlcv_shape(client):
    with patch("api.main.get_price_history", return_value=_mock_hist()):
        response = client.get("/chart-data?symbols=AAPL&timeframe=1y")
    assert response.status_code == 200
    data = response.json()
    assert "AAPL" in data
    assert len(data["AAPL"]) == 2
    row = data["AAPL"][0]
    for field in ("date", "close", "volume", "high", "low", "open"):
        assert field in row


def test_chart_data_multiple_symbols(client):
    with patch("api.main.get_price_history", return_value=_mock_hist()):
        response = client.get("/chart-data?symbols=AAPL,MSFT&timeframe=1y")
    assert response.status_code == 200
    data = response.json()
    assert "AAPL" in data and "MSFT" in data


def test_chart_data_rejects_invalid_symbol(client):
    response = client.get("/chart-data?symbols=BAD!SYM&timeframe=1y")
    assert response.status_code == 422


def test_chart_data_empty_symbols_returns_400(client):
    response = client.get("/chart-data?symbols=&timeframe=1y")
    assert response.status_code == 400


def test_chart_data_empty_hist_returns_empty_list(client):
    with patch("api.main.get_price_history", return_value=pd.DataFrame()):
        response = client.get("/chart-data?symbols=FAKE&timeframe=1y")
    assert response.status_code == 200
    assert response.json()["FAKE"] == []
