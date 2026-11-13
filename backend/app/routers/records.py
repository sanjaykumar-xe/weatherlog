from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import selectinload
from sqlmodel import Session, func, select

from app.database import get_session
from app.errors import AppError
from app.exports import export_response
from app.models import WeatherObservation, WeatherRecord, utc_now
from app.schemas import RecordInput, record_detail, record_summary
from app.services.weather import fetch_historical

router = APIRouter(prefix="/api/records", tags=["records"])


def get_record_or_404(session: Session, record_id: int) -> WeatherRecord:
    record = session.get(WeatherRecord, record_id)
    if record is None:
        raise AppError(404, "record_not_found", "That saved record does not exist.")
    return record


def apply_history(record: WeatherRecord, history: dict) -> None:
    record.timezone = history["timezone"]
    record.provider = history["provider"]
    record.dataset = history["dataset"]
    record.observations = [WeatherObservation(**day) for day in history["days"]]


# registered before "/{record_id}" so "export" is never parsed as an id
@router.get("/export")
def export_records(
    export_format: Literal["csv", "json"] = Query(alias="format"),
    session: Session = Depends(get_session),
):
    query = (
        select(WeatherRecord)
        .options(selectinload(WeatherRecord.observations))
        .order_by(WeatherRecord.created_at.desc(), WeatherRecord.id.desc())
    )
    records = session.exec(query).all()
    if not records:
        raise AppError(404, "no_records", "There are no saved records to export.")
    return export_response(records, export_format)


@router.get("")
def list_records(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
):
    total = session.exec(select(func.count(WeatherRecord.id))).one()
    query = (
        select(WeatherRecord, func.count(WeatherObservation.id))
        .join(WeatherObservation, isouter=True)
        .group_by(WeatherRecord.id)
        .order_by(WeatherRecord.created_at.desc(), WeatherRecord.id.desc())
        .offset(offset)
        .limit(limit)
    )
    rows = session.exec(query).all()
    return {
        "data": [record_summary(record, count) for record, count in rows],
        "meta": {"total": total, "limit": limit, "offset": offset},
    }


@router.post("", status_code=201)
async def create_record(payload: RecordInput, session: Session = Depends(get_session)):
    history = await fetch_historical(payload.latitude, payload.longitude, payload.start_date, payload.end_date)
    record = WeatherRecord(**payload.model_dump())
    apply_history(record, history)
    session.add(record)
    session.commit()
    session.refresh(record)
    return {"data": record_detail(record)}


@router.get("/{record_id}")
def get_record(record_id: int, session: Session = Depends(get_session)):
    return {"data": record_detail(get_record_or_404(session, record_id))}


@router.put("/{record_id}")
async def update_record(record_id: int, payload: RecordInput, session: Session = Depends(get_session)):
    record = get_record_or_404(session, record_id)
    # fetch first: nothing is modified unless the provider call succeeds
    history = await fetch_historical(payload.latitude, payload.longitude, payload.start_date, payload.end_date)
    for field, value in payload.model_dump().items():
        setattr(record, field, value)
    record.updated_at = utc_now()
    apply_history(record, history)
    session.add(record)
    session.commit()
    session.refresh(record)
    return {"data": record_detail(record)}


@router.delete("/{record_id}")
def delete_record(record_id: int, session: Session = Depends(get_session)):
    record = get_record_or_404(session, record_id)
    session.delete(record)
    session.commit()
    return {"data": {"id": record_id, "deleted": True}}
