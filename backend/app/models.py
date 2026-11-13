from datetime import date, datetime, timezone

from sqlmodel import Field, Relationship, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class WeatherRecord(SQLModel, table=True):
    __tablename__ = "weather_records"

    id: int | None = Field(default=None, primary_key=True)
    location_name: str
    admin_area: str | None = None
    country: str | None = None
    latitude: float
    longitude: float
    start_date: date
    end_date: date
    timezone: str | None = None
    provider: str
    dataset: str
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    observations: list["WeatherObservation"] = Relationship(
        back_populates="record",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "order_by": "WeatherObservation.observation_date",
        },
    )


class WeatherObservation(SQLModel, table=True):
    __tablename__ = "weather_observations"

    id: int | None = Field(default=None, primary_key=True)
    record_id: int = Field(foreign_key="weather_records.id", ondelete="CASCADE", index=True)
    observation_date: date
    temperature_min: float | None = None
    temperature_max: float | None = None
    temperature_mean: float | None = None
    precipitation_sum: float | None = None
    wind_speed_max: float | None = None
    weather_code: int | None = None

    record: WeatherRecord | None = Relationship(back_populates="observations")
