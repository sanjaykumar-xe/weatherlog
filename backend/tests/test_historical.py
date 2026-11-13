from datetime import date, timedelta

import pytest

from app.config import MAX_RANGE_DAYS

URL = "/api/weather/historical"
BASE = {"latitude": 13.08, "longitude": 80.27, "start_date": "2024-01-01", "end_date": "2024-01-03"}


def get(client, **overrides):
    return client.get(URL, params={**BASE, **overrides})


def test_valid_range_returns_daily_rows(client, provider):
    response = get(client)
    assert response.status_code == 200
    data = response.json()["data"]
    assert [day["observation_date"] for day in data["days"]] == ["2024-01-01", "2024-01-02", "2024-01-03"]
    assert data["days"][1] == {
        "observation_date": "2024-01-02", "temperature_min": 21.0, "temperature_max": 31.0,
        "temperature_mean": 26.0, "precipitation_sum": 1.0, "wind_speed_max": 11.0, "weather_code": 3,
    }
    assert data["provider"] == "open-meteo"
    assert "reanalysis" in data["dataset"]
    assert data["timezone"] == "Asia/Kolkata"


@pytest.mark.parametrize("value", ["not-a-date", "2024-13-45", "2024-02-30", "01/02/2024"])
def test_invalid_date_format_is_rejected(client, provider, value):
    response = get(client, start_date=value)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert "start_date" in response.json()["error"]["message"]
    assert provider.requests == []


def test_missing_dates_are_rejected(client, provider):
    response = client.get(URL, params={"latitude": 1, "longitude": 1})
    assert response.status_code == 422


def test_start_after_end_is_rejected(client, provider):
    response = get(client, start_date="2024-01-05", end_date="2024-01-01")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_date_range"
    assert provider.requests == []


def test_future_dates_are_rejected(client, provider):
    future = (date.today() + timedelta(days=2)).isoformat()
    response = get(client, end_date=future)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "future_date"
    assert provider.requests == []


def test_dates_before_archive_start_are_rejected(client, provider):
    response = get(client, start_date="1939-12-31")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "date_too_early"


def test_maximum_range_is_enforced(client, provider):
    start = date(2024, 1, 1)
    allowed_end = start + timedelta(days=MAX_RANGE_DAYS - 1)
    assert get(client, end_date=allowed_end.isoformat()).status_code == 200

    too_long = get(client, end_date=(allowed_end + timedelta(days=1)).isoformat())
    assert too_long.status_code == 422
    assert too_long.json()["error"]["code"] == "range_too_long"


def test_unpublished_period_returns_useful_error(client, provider):
    provider.unpublished_from = date(2024, 1, 1)
    response = get(client)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "data_not_available"


def test_partially_published_period_keeps_gaps_as_null(client, provider):
    provider.unpublished_from = date(2024, 1, 3)
    response = get(client)
    assert response.status_code == 200
    days = response.json()["data"]["days"]
    assert days[1]["temperature_max"] == 31.0
    assert days[2]["temperature_max"] is None
    assert days[2]["weather_code"] is None
