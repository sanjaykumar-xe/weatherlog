"""Mocked Open-Meteo responses used only by the automated tests."""
from datetime import date, timedelta

import httpx

GEOCODING_HOST = "geocoding-api.open-meteo.com"
FORECAST_HOST = "api.open-meteo.com"
ARCHIVE_HOST = "archive-api.open-meteo.com"
AIR_QUALITY_HOST = "air-quality-api.open-meteo.com"


def geocoding_payload(params):
    name = params["name"]
    if name == "Atlantis":
        return {"generationtime_ms": 0.2}
    return {
        "results": [
            {"id": 1, "name": name, "latitude": 13.0878, "longitude": 80.2785, "country": "India",
             "admin1": "Tamil Nadu", "timezone": "Asia/Kolkata"},
            {"id": 2, "name": name, "latitude": 40.0, "longitude": -75.0, "country": "United States",
             "admin1": "Pennsylvania", "timezone": "America/New_York"},
            {"id": 3, "latitude": 1.0, "longitude": 1.0},  # no name: must be dropped
        ]
    }


def forecast_payload(params):
    payload = {"latitude": 13.08, "longitude": 80.27, "timezone": "Asia/Kolkata"}
    if "current" in params:
        payload["current"] = {
            "time": "2024-06-01T12:00", "interval": 900, "temperature_2m": 31.2,
            "relative_humidity_2m": 62, "apparent_temperature": 35.1, "is_day": 1,
            "precipitation": 0.4, "weather_code": 2, "cloud_cover": 40,
            "wind_speed_10m": 12.5, "wind_direction_10m": 210,
        }
    if "daily" in params:
        payload["daily"] = {
            "time": [(date(2024, 6, 1) + timedelta(days=i)).isoformat() for i in range(5)],
            "weather_code": [2, 3, 61, 95, 0],
            "temperature_2m_max": [34.0, 33.5, 31.0, 30.2, 35.1],
            "temperature_2m_min": [26.0, 26.5, 25.0, 24.8, 27.0],
            "precipitation_sum": [0.0, 0.2, 8.4, 12.0, 0.0],
            "precipitation_probability_max": [5, 20, 80, 90, 0],
            "wind_speed_10m_max": [18.0, 20.5, 25.1, 30.0, 15.2],
        }
    return payload


def air_quality_payload(params):
    return {
        "timezone": "Asia/Kolkata",
        "current": {"time": "2024-06-01T12:00", "interval": 3600, "pm10": 55.0, "pm2_5": 28.5, "us_aqi": 88},
    }


class FakeProvider:
    def __init__(self):
        self.requests = []
        # host -> callable(request) -> httpx.Response, for failures and special cases
        self.overrides = {}
        # archive days on or after this date come back as null (not yet published)
        self.unpublished_from = None

    def requests_to(self, host):
        return [request for request in self.requests if request.url.host == host]

    def archive_payload(self, params):
        start = date.fromisoformat(params["start_date"])
        end = date.fromisoformat(params["end_date"])
        days = [start + timedelta(days=i) for i in range((end - start).days + 1)]

        def hidden(day):
            return self.unpublished_from is not None and day >= self.unpublished_from

        def series(base):
            return [None if hidden(day) else base + index for index, day in enumerate(days)]

        return {
            "latitude": 13.08, "longitude": 80.27, "timezone": "Asia/Kolkata",
            "daily": {
                "time": [day.isoformat() for day in days],
                "temperature_2m_min": series(20.0),
                "temperature_2m_max": series(30.0),
                "temperature_2m_mean": series(25.0),
                "precipitation_sum": series(0.0),
                "wind_speed_10m_max": series(10.0),
                "weather_code": [None if hidden(day) else 3 for day in days],
            },
        }

    def handle(self, request):
        self.requests.append(request)
        override = self.overrides.get(request.url.host)
        if override:
            return override(request)
        params = dict(request.url.params)
        builders = {
            GEOCODING_HOST: geocoding_payload,
            FORECAST_HOST: forecast_payload,
            ARCHIVE_HOST: self.archive_payload,
            AIR_QUALITY_HOST: air_quality_payload,
        }
        return httpx.Response(200, json=builders[request.url.host](params))
