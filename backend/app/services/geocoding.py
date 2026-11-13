from app.services.client import get_json, invalid_response

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
MAX_RESULTS = 10


def _normalize(result) -> dict | None:
    try:
        name = result["name"]
        latitude = float(result["latitude"])
        longitude = float(result["longitude"])
    except (KeyError, TypeError, ValueError):
        return None
    if not name or not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return None
    return {
        "name": name,
        "admin_area": result.get("admin1"),
        "country": result.get("country"),
        "latitude": latitude,
        "longitude": longitude,
        "timezone": result.get("timezone"),
    }


async def search_locations(query: str) -> list[dict]:
    data = await get_json(
        GEOCODING_URL,
        {"name": query, "count": MAX_RESULTS, "language": "en", "format": "json"},
    )
    results = data.get("results") or []
    if not isinstance(results, list):
        raise invalid_response()
    locations = (_normalize(result) for result in results)
    return [location for location in locations if location]
