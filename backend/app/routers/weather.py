from datetime import date

from fastapi import APIRouter

from app.schemas import Latitude, Longitude
from app.services.air_quality import fetch_air_quality
from app.services.weather import fetch_current, fetch_forecast, fetch_historical

router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.get("/current")
async def current(latitude: Latitude, longitude: Longitude):
    return {"data": await fetch_current(latitude, longitude)}


@router.get("/forecast")
async def forecast(latitude: Latitude, longitude: Longitude):
    return {"data": await fetch_forecast(latitude, longitude)}


@router.get("/air-quality")
async def air_quality(latitude: Latitude, longitude: Longitude):
    return {"data": await fetch_air_quality(latitude, longitude)}


@router.get("/historical")
async def historical(latitude: Latitude, longitude: Longitude, start_date: date, end_date: date):
    return {"data": await fetch_historical(latitude, longitude, start_date, end_date)}
