from datetime import date

from app.errors import AppError
from app.services.client import get_json, invalid_response
from app.validation import check_date_range

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

PROVIDER = "open-meteo"
HISTORICAL_DATASET = "Open-Meteo Historical Weather API (reanalysis, best-match model)"

# units are requested explicitly so the values below are always °C, km/h and mm
UNIT_PARAMS = {"temperature_unit": "celsius", "wind_speed_unit": "kmh", "precipitation_unit": "mm"}
UNITS = {
    "temperature": "°C",
    "humidity": "%",
    "precipitation": "mm",
    "cloud_cover": "%",
    "wind_speed": "km/h",
    "wind_direction": "°",
}

CURRENT_VARIABLES = [
    "temperature_2m", "relative_humidity_2m", "apparent_temperature", "is_day", "precipitation",
    "weather_code", "cloud_cover", "wind_speed_10m", "wind_direction_10m",
]
# output field -> provider variable
FORECAST_COLUMNS = {
    "weather_code": "weather_code",
    "temperature_max": "temperature_2m_max",
    "temperature_min": "temperature_2m_min",
    "precipitation_sum": "precipitation_sum",
    "precipitation_probability_max": "precipitation_probability_max",
    "wind_speed_max": "wind_speed_10m_max",
}
HISTORICAL_COLUMNS = {
    "temperature_min": "temperature_2m_min",
    "temperature_max": "temperature_2m_max",
    "temperature_mean": "temperature_2m_mean",
    "precipitation_sum": "precipitation_sum",
    "wind_speed_max": "wind_speed_10m_max",
    "weather_code": "weather_code",
}


def _value_at(daily: dict, variable: str, index: int):
    values = daily.get(variable)
    if isinstance(values, list) and index < len(values):
        return values[index]
    return None


def _daily_rows(data: dict, columns: dict[str, str]) -> list[dict]:
    daily = data.get("daily")
    days = daily.get("time") if isinstance(daily, dict) else None
    if not isinstance(days, list) or not days:
        raise invalid_response()
    return [
        {"date": day, **{field: _value_at(daily, variable, index) for field, variable in columns.items()}}
        for index, day in enumerate(days)
    ]


async def fetch_current(latitude: float, longitude: float) -> dict:
    data = await get_json(
        FORECAST_URL,
        {
            "latitude": latitude,
            "longitude": longitude,
            "current": ",".join(CURRENT_VARIABLES),
            "timezone": "auto",
            **UNIT_PARAMS,
        },
    )
    current = data.get("current")
    if not isinstance(current, dict):
        raise invalid_response()
    return {
        "time": current.get("time"),
        "timezone": data.get("timezone"),
        "weather_code": current.get("weather_code"),
        "is_day": current.get("is_day"),
        "temperature": current.get("temperature_2m"),
        "apparent_temperature": current.get("apparent_temperature"),
        "humidity": current.get("relative_humidity_2m"),
        "precipitation": current.get("precipitation"),
        "cloud_cover": current.get("cloud_cover"),
        "wind_speed": current.get("wind_speed_10m"),
        "wind_direction": current.get("wind_direction_10m"),
        "units": UNITS,
    }


async def fetch_forecast(latitude: float, longitude: float) -> dict:
    data = await get_json(
        FORECAST_URL,
        {
            "latitude": latitude,
            "longitude": longitude,
            "daily": ",".join(FORECAST_COLUMNS.values()),
            "forecast_days": 5,
            "timezone": "auto",
            **UNIT_PARAMS,
        },
    )
    return {"timezone": data.get("timezone"), "days": _daily_rows(data, FORECAST_COLUMNS), "units": UNITS}


def _to_observation(row: dict) -> dict:
    try:
        observation = {key: value for key, value in row.items() if key != "date"}
        observation["observation_date"] = date.fromisoformat(row["date"])
        if observation["weather_code"] is not None:
            observation["weather_code"] = int(observation["weather_code"])
    except (TypeError, ValueError):
        raise invalid_response()
    return observation


async def fetch_historical(latitude: float, longitude: float, start: date, end: date) -> dict:
    check_date_range(start, end)
    data = await get_json(
        ARCHIVE_URL,
        {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "daily": ",".join(HISTORICAL_COLUMNS.values()),
            "timezone": "auto",
            **UNIT_PARAMS,
        },
    )
    days = [_to_observation(row) for row in _daily_rows(data, HISTORICAL_COLUMNS)]
    if all(day[field] is None for day in days for field in HISTORICAL_COLUMNS):
        raise AppError(
            422,
            "data_not_available",
            "The provider has not published historical data for these dates yet. "
            "The archive usually lags a few days behind, so try an earlier end date.",
        )
    return {"timezone": data.get("timezone"), "provider": PROVIDER, "dataset": HISTORICAL_DATASET, "days": days}
