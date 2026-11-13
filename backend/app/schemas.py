from datetime import date, datetime
from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, PlainSerializer

from app.models import WeatherRecord

LATITUDE_RULES = {"ge": -90, "le": 90, "allow_inf_nan": False}
LONGITUDE_RULES = {"ge": -180, "le": 180, "allow_inf_nan": False}

Latitude = Annotated[float, Query(**LATITUDE_RULES)]
Longitude = Annotated[float, Query(**LONGITUDE_RULES)]
def serialize_utc(value: datetime) -> str:
    if value.tzinfo is not None:
        return value.isoformat().replace("+00:00", "Z")
    return value.isoformat() + "Z"


UtcDatetime = Annotated[datetime, PlainSerializer(serialize_utc, return_type=str)]


class RecordInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    location_name: str = Field(min_length=1, max_length=200)
    admin_area: str | None = Field(default=None, max_length=200)
    country: str | None = Field(default=None, max_length=200)
    latitude: float = Field(**LATITUDE_RULES)
    longitude: float = Field(**LONGITUDE_RULES)
    start_date: date
    end_date: date


class ObservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    observation_date: date
    temperature_min: float | None
    temperature_max: float | None
    temperature_mean: float | None
    precipitation_sum: float | None
    wind_speed_max: float | None
    weather_code: int | None


class RecordSummary(BaseModel):
    id: int
    location_name: str
    admin_area: str | None
    country: str | None
    latitude: float
    longitude: float
    start_date: date
    end_date: date
    timezone: str | None
    provider: str
    dataset: str
    created_at: UtcDatetime
    updated_at: UtcDatetime
    observation_count: int


class RecordDetail(RecordSummary):
    observations: list[ObservationRead]


def record_summary(record: WeatherRecord, observation_count: int) -> RecordSummary:
    return RecordSummary(**record.model_dump(), observation_count=observation_count)


def record_detail(record: WeatherRecord) -> RecordDetail:
    observations = [ObservationRead.model_validate(row) for row in record.observations]
    return RecordDetail(**record.model_dump(), observation_count=len(observations), observations=observations)
