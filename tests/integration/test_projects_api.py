"""End-to-end API tests through FastAPI's TestClient."""

from fastapi import status
from fastapi.testclient import TestClient

API = "/api/v1"


def _create(client: TestClient, name: str = "SmartBayanihan", **extra: str) -> dict[str, object]:
    response = client.post(f"{API}/projects", json={"name": name, "team_name": "Kalinga", **extra})
    assert response.status_code == status.HTTP_201_CREATED, response.text
    body: dict[str, object] = response.json()
    return body


def test_health_reports_database_connected(client: TestClient) -> None:
    response = client.get(f"{API}/health")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["database"] == "connected"


def test_welcome_page_is_served(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]


def test_static_assets_are_served(client: TestClient) -> None:
    assert client.get("/static/css/styles.css").status_code == status.HTTP_200_OK
    assert client.get("/static/js/app.js").status_code == status.HTTP_200_OK


def test_favicon_is_served(client: TestClient) -> None:
    response = client.get("/favicon.ico")
    assert response.status_code == status.HTTP_200_OK


def test_project_api_flow(client: TestClient) -> None:
    created = _create(client, tech_stack="FastAPI")
    project_id = created["id"]

    listed = client.get(f"{API}/projects").json()
    assert [p["id"] for p in listed] == [project_id]

    fetched = client.get(f"{API}/projects/{project_id}")
    assert fetched.status_code == status.HTTP_200_OK
    assert fetched.json()["name"] == "SmartBayanihan"

    stats = client.get(f"{API}/projects/stats").json()
    assert stats == {"total": 1, "by_status": {"idea": 1, "building": 0, "submitted": 0}}


def test_duplicate_name_returns_conflict(client: TestClient) -> None:
    _create(client, "JeepRoute")

    response = client.post(f"{API}/projects", json={"name": "JeepRoute", "team_name": "Biyahe"})

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["error"]["code"] == "conflict"


def test_invalid_payload_returns_422(client: TestClient) -> None:
    response = client.post(f"{API}/projects", json={"name": "x", "team_name": ""})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
