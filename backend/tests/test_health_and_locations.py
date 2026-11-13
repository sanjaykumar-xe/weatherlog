import httpx
import pytest

from tests.fake_provider import GEOCODING_HOST


def test_health_returns_ok_without_calling_provider(client, provider):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"data": {"status": "ok"}}
    assert provider.requests == []


@pytest.mark.parametrize("query", ["", "   "])
def test_empty_search_is_rejected(client, provider, query):
    response = client.get("/api/locations/search", params={"q": query})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "empty_query"
    assert provider.requests == []


def test_missing_search_query_is_rejected(client, provider):
    response = client.get("/api/locations/search")
    assert response.status_code == 422


def test_overlong_search_query_is_rejected(client, provider):
    response = client.get("/api/locations/search", params={"q": "x" * 101})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_valid_search_returns_normalized_matches(client, provider):
    response = client.get("/api/locations/search", params={"q": "  Chennai "})
    assert response.status_code == 200
    results = response.json()["data"]
    assert len(results) == 2  # the incomplete third result is dropped
    assert results[0] == {
        "name": "Chennai", "admin_area": "Tamil Nadu", "country": "India",
        "latitude": 13.0878, "longitude": 80.2785, "timezone": "Asia/Kolkata",
    }
    params = provider.requests_to(GEOCODING_HOST)[0].url.params
    assert params["name"] == "Chennai"
    assert params["count"] == "10"


def test_search_without_matches_returns_empty_list(client, provider):
    response = client.get("/api/locations/search", params={"q": "Atlantis"})
    assert response.status_code == 200
    assert response.json()["data"] == []


def test_search_provider_failure_returns_502(client, provider):
    provider.overrides[GEOCODING_HOST] = lambda request: httpx.Response(500)
    response = client.get("/api/locations/search", params={"q": "Chennai"})
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "provider_error"
