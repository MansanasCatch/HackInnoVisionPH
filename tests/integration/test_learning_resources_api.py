"""Integration tests for learning resource version APIs."""

from fastapi.testclient import TestClient


def _create_profile(client: TestClient) -> int:
    response = client.post(
        "/api/v1/onboarding",
        json={"username": "Cheryl", "interests": ["Biology"], "age": 21},
    )
    assert response.status_code == 201
    return int(response.json()["id"])


def _create_resource(client: TestClient, onboarding_id: int) -> int:
    response = client.post(
        "/api/v1/learning-resources",
        json={
            "onboarding_id": onboarding_id,
            "title": "Cell division & mitosis",
            "subject": "Biology",
            "source_label": "Biology lesson notes",
        },
    )
    assert response.status_code == 201
    return int(response.json()["id"])


def test_learning_resource_versions_keep_latest_three(client: TestClient) -> None:
    onboarding_id = _create_profile(client)
    resource_id = _create_resource(client, onboarding_id)

    for index in range(1, 5):
        response = client.post(
            f"/api/v1/learning-resources/{resource_id}/versions",
            json={
                "title": f"Cell division version {index}",
                "summary": f"Version {index} summary",
                "content": {"summary": f"Condensed lesson {index}"},
                "resource_types": [
                    "summary",
                    "reviewer",
                    "flashcards",
                    "practice_quiz",
                    "mock_exam",
                    "qa_reviewer",
                ],
                "topics": ["Mitosis", "Interphase"],
            },
        )
        assert response.status_code == 201
        assert response.json()["version_number"] == index

    response = client.get(f"/api/v1/learning-resources/{resource_id}/versions")
    assert response.status_code == 200
    versions = response.json()
    assert [version["version_number"] for version in versions] == [4, 3, 2]
    assert len(versions) == 3

    latest = versions[0]
    assert latest["is_current"] is True
    assert latest["resource_types"] == [
        "summary",
        "reviewer",
        "flashcards",
        "practice_quiz",
        "mock_exam",
        "qa_reviewer",
    ]

    progress = client.get(
        f"/api/v1/learning-resources/{resource_id}/versions/{latest['id']}/progress",
        params={"onboarding_id": onboarding_id},
    )
    assert progress.status_code == 200
    assert progress.json()["first_time_for_version"] is True
    assert progress.json()["attempts_count"] == 0
