import csv
import io
import json
from datetime import datetime, timezone

from fastapi import Response

from app.models import WeatherRecord
from app.schemas import record_detail

RECORD_FIELDS = [
    "id", "location_name", "admin_area", "country", "latitude", "longitude",
    "start_date", "end_date", "timezone", "provider", "dataset", "created_at", "updated_at",
]
OBSERVATION_FIELDS = [
    "observation_date", "temperature_min", "temperature_max", "temperature_mean",
    "precipitation_sum", "wind_speed_max", "weather_code",
]
CSV_HEADER = ["record_id"] + RECORD_FIELDS[1:] + OBSERVATION_FIELDS


def _csv_cell(value):
    if value is None:
        return ""
    # stop spreadsheet apps from running user-supplied text as a formula
    if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def build_csv(records: list[WeatherRecord]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(CSV_HEADER)
    for record in records:
        detail = record_detail(record).model_dump(mode="json")
        record_values = [_csv_cell(detail[field]) for field in RECORD_FIELDS]
        for observation in detail["observations"]:
            writer.writerow(record_values + [_csv_cell(observation[field]) for field in OBSERVATION_FIELDS])
    return buffer.getvalue()


def build_json(records: list[WeatherRecord]) -> str:
    payload = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "record_count": len(records),
        "records": [record_detail(record).model_dump(mode="json") for record in records],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def export_response(records: list[WeatherRecord], export_format: str) -> Response:
    if export_format == "csv":
        # the BOM lets Excel read non-ASCII place names correctly
        body = ("\ufeff" + build_csv(records)).encode("utf-8")
        media_type = "text/csv; charset=utf-8"
    else:
        body = build_json(records).encode("utf-8")
        media_type = "application/json"
    headers = {"Content-Disposition": f'attachment; filename="weatherlog-records.{export_format}"'}
    return Response(content=body, media_type=media_type, headers=headers)
