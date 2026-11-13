from fastapi import APIRouter, Query

from app.errors import AppError
from app.services.geocoding import search_locations

router = APIRouter(prefix="/api/locations", tags=["locations"])


@router.get("/search")
async def search(q: str = Query("", max_length=100)):
    query = q.strip()
    if not query:
        raise AppError(422, "empty_query", "Enter a city, town or postal code to search.")
    return {"data": await search_locations(query)}
