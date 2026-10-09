"""Integration tests for Onboarding API endpoints."""

from fastapi.testclient import TestClient


def test_create_and_get_onboarding_profile(client: TestClient) -> None:
    payload = {
        "username": "Amara Mensah",
        "interests": ["Biology", "English", "History"],
        "age": 22,
    }
    # Create profile
    response = client.post("/api/v1/onboarding", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "Amara Mensah"
    assert data["interests"] == ["Biology", "English", "History"]
    assert data["age"] == 22
    profile_id = data["id"]

    # Get by ID
    response = client.get(f"/api/v1/onboarding/{profile_id}")
    assert response.status_code == 200
    assert response.json()["username"] == "Amara Mensah"

    # Get by Username
    response = client.get("/api/v1/onboarding/user/Amara Mensah")
    assert response.status_code == 200
    assert response.json()["id"] == profile_id

    # List profiles
    response = client.get("/api/v1/onboarding")
    assert response.status_code == 200
    profiles = response.json()
    assert len(profiles) >= 1
    assert any(p["username"] == "Amara Mensah" for p in profiles)
