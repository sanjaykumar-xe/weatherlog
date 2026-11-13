from app.services.client import get_json, invalid_response

AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


async def fetch_air_quality(latitude: float, longitude: float) -> dict:
    data = await get_json(
        AIR_QUALITY_URL,
        {"latitude": latitude, "longitude": longitude, "current": "pm2_5,pm10,us_aqi", "timezone": "auto"},
    )
    current = data.get("current")
    if not isinstance(current, dict):
        raise invalid_response()
    return {
        "time": current.get("time"),
        "timezone": data.get("timezone"),
        "pm2_5": current.get("pm2_5"),
        "pm10": current.get("pm10"),
        "us_aqi": current.get("us_aqi"),
        "units": {"pm2_5": "µg/m³", "pm10": "µg/m³", "us_aqi": "US AQI"},
    }
