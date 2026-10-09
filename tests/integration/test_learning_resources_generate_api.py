"""Integration tests for one-shot ingest -> generate -> persist learning resources."""

from fastapi.testclient import TestClient


def _profile(client: TestClient) -> int:
    response = client.post(
        "/api/v1/onboarding", json={"username": "Amara", "interests": ["Biology"], "age": 21}
    )
    assert response.status_code == 201
    return int(response.json()["id"])


def test_generate_resource_from_topic_and_notes(client: TestClient) -> None:
    onboarding_id = _profile(client)
    response = client.post(
        "/api/v1/learning-resources/generate",
        data={
            "onboarding_id": str(onboarding_id),
            "topic": "Cell division",
            "notes": (
                "Mitosis produces two genetically identical daughter cells. "
                "Metaphase aligns chromosomes at the cell equator."
            ),
            "resource_types": ["summary", "flashcards", "practice_quiz"],
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()

    assert body["resource"]["title"] == "Cell division"
    assert body["resource"]["onboarding_id"] == onboarding_id
    assert body["version"]["version_number"] == 1
    assert body["version"]["resource_types"] == ["summary", "flashcards", "practice_quiz"]
    assert body["version"]["content"]["topic"] == "Cell division"
    assert len(body["version"]["content"]["flashcards"]) > 0
    assert "genetically identical" in body["version"]["summary"]
    assert body["generation"]["is_ollama_online"] is False
    assert any("offline" in warning.lower() for warning in body["generation"]["warnings"])

    listed = client.get("/api/v1/learning-resources", params={"onboarding_id": onboarding_id})
    assert [item["id"] for item in listed.json()] == [body["resource"]["id"]]


def test_generate_resource_from_uploaded_file(client: TestClient) -> None:
    onboarding_id = _profile(client)
    body = b"DNA replication copies the genome before cell division."
    files = [("files", ("dna.txt", body, "text/plain"))]
    response = client.post(
        "/api/v1/learning-resources/generate",
        data={"onboarding_id": str(onboarding_id), "topic": "DNA"},
        files=files,
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["resource"]["source_label"] == "dna.txt"
    assert body["version"]["content"]["topic"] == "DNA"


def test_generate_resource_requires_material(client: TestClient) -> None:
    onboarding_id = _profile(client)
    response = client.post(
        "/api/v1/learning-resources/generate",
        data={"onboarding_id": str(onboarding_id), "topic": "Empty"},
    )
    assert response.status_code == 422


def test_generate_resource_unknown_learner_returns_404(client: TestClient) -> None:
    response = client.post(
        "/api/v1/learning-resources/generate",
        data={"onboarding_id": "9999", "topic": "Cell division", "notes": "Some notes here."},
    )
    assert response.status_code == 404
