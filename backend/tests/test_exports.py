import csv
import io
import json

from app.exports import CSV_HEADER


def create(client, payload, **overrides):
    assert client.post("/api/records", json={**payload, **overrides}).status_code == 201


def read_csv(response):
    return list(csv.DictReader(io.StringIO(response.text.lstrip("\ufeff"))))


def test_csv_export_has_header_and_one_row_per_observation(client, provider, record_payload):
    create(client, record_payload, location_name="First")
    create(client, record_payload, location_name="Second", end_date="2024-01-05")
    response = client.get("/api/records/export", params={"format": "csv"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert 'filename="weatherlog-records.csv"' in response.headers["content-disposition"]
    assert response.headers["content-disposition"].startswith("attachment")

    rows = read_csv(response)
    assert list(rows[0].keys()) == CSV_HEADER
    assert len(rows) == 8  # 5 observations for the newest record, then 3
    assert rows[0]["location_name"] == "Second"
    assert rows[0]["record_id"] == "2"
    assert rows[0]["observation_date"] == "2024-01-01"
    assert rows[0]["temperature_min"] == "20.0"
    assert rows[-1]["location_name"] == "First"
    assert rows[-1]["observation_date"] == "2024-01-03"


def test_csv_export_neutralizes_spreadsheet_formulas(client, provider, record_payload):
    create(client, record_payload, location_name="=HYPERLINK(\"http://example.com\")")
    rows = read_csv(client.get("/api/records/export", params={"format": "csv"}))
    assert rows[0]["location_name"].startswith("'=")


def test_json_export_contains_metadata_and_observations(client, provider, record_payload):
    create(client, record_payload)
    response = client.get("/api/records/export", params={"format": "json"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert 'filename="weatherlog-records.json"' in response.headers["content-disposition"]

    payload = json.loads(response.text)
    assert payload["record_count"] == 1
    record = payload["records"][0]
    assert record["location_name"] == "Chennai"
    assert record["start_date"] == "2024-01-01"
    assert record["dataset"]
    assert len(record["observations"]) == 3
    assert record["observations"][0]["observation_date"] == "2024-01-01"


def test_export_with_no_records_returns_clear_error(client):
    for export_format in ("csv", "json"):
        response = client.get("/api/records/export", params={"format": export_format})
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "no_records"


def test_export_rejects_unsupported_or_missing_format(client, provider, record_payload):
    create(client, record_payload)
    assert client.get("/api/records/export", params={"format": "xml"}).status_code == 422
    assert client.get("/api/records/export").status_code == 422
