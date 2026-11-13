import httpx
import pytest

from tests.fake_provider import AIR_QUALITY_HOST, FORECAST_HOST

COORDS = {"latitude": 13.08, "longitude": 80.27}
HOST_BY_PATH = {"current": FORECAST_HOST, "forecast": FORECAST_HOST, "air-quality": AIR_QUALITY_HOST}


def raise_timeout(request):
    raise httpx.ReadTimeout("timed out", request=request)


def raise_connect_error(request):
    raise httpx.ConnectError("refused", request=request)


FAILURES = [
    (lambda request: httpx.Response(500, json={"error": True, "reason": "boom"}), 502, "provider_error"),
    (lambda request: httpx.Response(200, json={"error": True, "reason": "bad"}), 502, "provider_error"),
    (lambda request: httpx.Response(429, json={}), 503, "provider_rate_limited"),
    (raise_timeout, 504, "provider_timeout"),
    (raise_connect_error, 502, "provider_unreachable"),
    (lambda request: httpx.Response(200, content=b"not json"), 502, "provider_invalid_response"),
    (lambda request: httpx.Response(200, json={"unexpected": True}), 502, "provider_invalid_response"),
]


@pytest.mark.parametrize("path", HOST_BY_PATH)
@pytest.mark.parametrize(
    "params",
    [
        {"latitude": 91, "longitude": 0},
        {"latitude": -91, "longitude": 0},
        {"latitude": 0, "longitude": 181},
        {"latitude": 0, "longitude": -181},
        {"latitude": "abc", "longitude": 0},
        {"latitude": "nan", "longitude": 0},
        {"latitude": 0},
    ],
)
def test_invalid_coordinates_are_rejected(client, provider, path, params):
    response = client.get(f"/api/weather/{path}", params=params)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert provider.requests == []


@pytest.mark.parametrize("path", HOST_BY_PATH)
@pytest.mark.parametrize("failure,status,code", FAILURES)
def test_provider_failures_become_clean_errors(client, provider, path, failure, status, code):
    provider.overrides[HOST_BY_PATH[path]] = failure
    response = client.get(f"/api/weather/{path}", params=COORDS)
    assert response.status_code == status
    assert response.json()["error"]["code"] == code


def test_current_weather_is_normalized(client, provider):
    response = client.get("/api/weather/current", params=COORDS)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["temperature"] == 31.2
    assert data["apparent_temperature"] == 35.1
    assert data["humidity"] == 62
    assert data["wind_speed"] == 12.5
    assert data["wind_direction"] == 210
    assert data["weather_code"] == 2
    assert data["timezone"] == "Asia/Kolkata"
    assert data["units"]["temperature"] == "°C"
    params = provider.requests_to(FORECAST_HOST)[0].url.params
    assert params["temperature_unit"] == "celsius"
    assert params["wind_speed_unit"] == "kmh"
    assert params["timezone"] == "auto"


def test_forecast_returns_five_days(client, provider):
    response = client.get("/api/weather/forecast", params=COORDS)
    assert response.status_code == 200
    days = response.json()["data"]["days"]
    assert len(days) == 5
    assert days[0] == {
        "date": "2024-06-01", "weather_code": 2, "temperature_max": 34.0, "temperature_min": 26.0,
        "precipitation_sum": 0.0, "precipitation_probability_max": 5, "wind_speed_max": 18.0,
    }
    assert provider.requests_to(FORECAST_HOST)[0].url.params["forecast_days"] == "5"


def test_air_quality_is_normalized(client, provider):
    response = client.get("/api/weather/air-quality", params=COORDS)
    assert response.status_code == 200
    data = response.json()["data"]
    assert (data["pm2_5"], data["pm10"], data["us_aqi"]) == (28.5, 55.0, 88)
    assert data["units"]["pm2_5"] == "µg/m³"
    assert data["units"]["us_aqi"] == "US AQI"


def test_air_quality_tolerates_missing_variables(client, provider):
    payload = {"timezone": "GMT", "current": {"time": "2024-06-01T12:00", "pm10": 12.0}}
    provider.overrides[AIR_QUALITY_HOST] = lambda request: httpx.Response(200, json=payload)
    response = client.get("/api/weather/air-quality", params=COORDS)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["pm10"] == 12.0
    assert data["pm2_5"] is None
    assert data["us_aqi"] is None
