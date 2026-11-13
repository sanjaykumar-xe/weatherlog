import httpx
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.database import create_tables, get_session, make_engine
from app.main import app
from app.services import client as provider_client
from tests.fake_provider import FakeProvider

RECORD_PAYLOAD = {
    "location_name": "Chennai",
    "admin_area": "Tamil Nadu",
    "country": "India",
    "latitude": 13.0878,
    "longitude": 80.2785,
    "start_date": "2024-01-01",
    "end_date": "2024-01-03",
}


@pytest.fixture
def provider():
    fake = FakeProvider()
    provider_client.transport = httpx.MockTransport(fake.handle)
    yield fake
    provider_client.transport = None


@pytest.fixture
def engine(tmp_path):
    db_engine = make_engine(f"sqlite:///{tmp_path / 'test.db'}")
    create_tables(db_engine)
    yield db_engine
    db_engine.dispose()


@pytest.fixture
def client(engine):
    def override_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def record_payload():
    return dict(RECORD_PAYLOAD)
