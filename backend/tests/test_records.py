import httpx
from sqlalchemy import text
from sqlmodel import Session, select

from app.database import make_engine
from app.models import WeatherObservation, WeatherRecord
from tests.fake_provider import ARCHIVE_HOST


def create(client, payload, **overrides):
    return client.post("/api/records", json={**payload, **overrides})


def observation_count(engine):
    with Session(engine) as session:
        return len(session.exec(select(WeatherObservation)).all())


def test_create_saves_record_and_observations(client, provider, engine, record_payload):
    response = create(client, record_payload)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["id"] == 1
    assert data["location_name"] == "Chennai"
    assert data["timezone"] == "Asia/Kolkata"
    assert data["provider"] == "open-meteo"
    assert "reanalysis" in data["dataset"]
    assert data["observation_count"] == 3
    assert [row["observation_date"] for row in data["observations"]] == ["2024-01-01", "2024-01-02", "2024-01-03"]
    assert data["created_at"].endswith("Z")
    assert observation_count(engine) == 3


def test_saved_record_survives_restart(client, provider, engine, record_payload):
    create(client, record_payload)
    engine.dispose()
    restarted = make_engine(str(engine.url))
    with Session(restarted) as session:
        record = session.get(WeatherRecord, 1)
        assert record.location_name == "Chennai"
        assert len(record.observations) == 3
    restarted.dispose()


def test_invalid_input_is_rejected_and_not_saved(client, provider, engine, record_payload):
    bad_payloads = [
        {"latitude": 95},
        {"longitude": -200},
        {"latitude": "abc"},
        {"location_name": "   "},
        {"start_date": "nope"},
        {"start_date": "2024-02-01", "end_date": "2024-01-01"},
    ]
    for overrides in bad_payloads:
        assert create(client, record_payload, **overrides).status_code == 422
    assert provider.requests == []
    assert client.get("/api/records").json()["meta"]["total"] == 0


def test_provider_failure_saves_nothing(client, provider, engine, record_payload):
    provider.overrides[ARCHIVE_HOST] = lambda request: httpx.Response(500)
    response = create(client, record_payload)
    assert response.status_code == 502
    assert client.get("/api/records").json()["data"] == []
    assert observation_count(engine) == 0


def test_unpublished_data_saves_nothing(client, provider, engine, record_payload):
    from datetime import date

    provider.unpublished_from = date(2024, 1, 1)
    response = create(client, record_payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "data_not_available"
    assert observation_count(engine) == 0


def test_list_is_newest_first_with_counts_and_pagination(client, provider, record_payload):
    create(client, record_payload, location_name="First")
    create(client, record_payload, location_name="Second", end_date="2024-01-05")
    body = client.get("/api/records").json()
    assert [item["location_name"] for item in body["data"]] == ["Second", "First"]
    assert [item["observation_count"] for item in body["data"]] == [5, 3]
    assert "observations" not in body["data"][0]
    assert body["meta"] == {"total": 2, "limit": 50, "offset": 0}

    page = client.get("/api/records", params={"limit": 1, "offset": 1}).json()
    assert [item["location_name"] for item in page["data"]] == ["First"]
    assert page["meta"]["total"] == 2


def test_list_rejects_invalid_pagination(client):
    assert client.get("/api/records", params={"limit": 0}).status_code == 422
    assert client.get("/api/records", params={"limit": 101}).status_code == 422
    assert client.get("/api/records", params={"offset": -1}).status_code == 422


def test_get_returns_record_with_observations(client, provider, record_payload):
    create(client, record_payload)
    response = client.get("/api/records/1")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["location_name"] == "Chennai"
    assert len(data["observations"]) == 3
    assert data["observations"][0]["temperature_min"] == 20.0


def test_get_does_not_call_the_provider_again(client, provider, record_payload):
    create(client, record_payload)
    calls_after_create = len(provider.requests)
    client.get("/api/records/1")
    client.get("/api/records")
    assert len(provider.requests) == calls_after_create


def test_update_replaces_observations_and_keeps_identity(client, provider, engine, record_payload):
    created = create(client, record_payload).json()["data"]
    response = client.put(
        "/api/records/1",
        json={**record_payload, "location_name": "Chennai (updated)", "end_date": "2024-01-05"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == created["id"]
    assert data["created_at"] == created["created_at"]
    assert data["updated_at"] >= created["updated_at"]
    assert data["location_name"] == "Chennai (updated)"
    assert data["end_date"] == "2024-01-05"
    assert data["observation_count"] == 5
    assert observation_count(engine) == 5  # old rows were replaced, not kept


def test_failed_update_leaves_record_unchanged(client, provider, engine, record_payload):
    before = create(client, record_payload).json()["data"]
    provider.overrides[ARCHIVE_HOST] = lambda request: httpx.Response(500)
    response = client.put("/api/records/1", json={**record_payload, "location_name": "Changed", "end_date": "2024-01-05"})
    assert response.status_code == 502
    assert client.get("/api/records/1").json()["data"] == before
    assert observation_count(engine) == 3


def test_invalid_update_leaves_record_unchanged(client, provider, engine, record_payload):
    before = create(client, record_payload).json()["data"]
    response = client.put("/api/records/1", json={**record_payload, "start_date": "2024-02-01", "end_date": "2024-01-01"})
    assert response.status_code == 422
    assert client.get("/api/records/1").json()["data"] == before


def test_delete_removes_record_and_observations(client, provider, engine, record_payload):
    create(client, record_payload)
    response = client.delete("/api/records/1")
    assert response.status_code == 200
    assert response.json()["data"] == {"id": 1, "deleted": True}
    assert client.get("/api/records/1").status_code == 404
    assert observation_count(engine) == 0


def test_database_cascades_deletes_without_the_orm(client, provider, engine, record_payload):
    create(client, record_payload)
    with engine.begin() as connection:
        connection.execute(text("DELETE FROM weather_records"))
    assert observation_count(engine) == 0


def test_missing_record_returns_404(client, provider, record_payload):
    for response in (
        client.get("/api/records/999"),
        client.put("/api/records/999", json=record_payload),
        client.delete("/api/records/999"),
    ):
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "record_not_found"
    assert provider.requests == []


def test_non_integer_record_id_is_rejected(client):
    response = client.get("/api/records/abc")
    assert response.status_code == 422
