"""Integration tests for version-aware study sessions."""

import pytest
from fastapi.testclient import TestClient

from app.repositories.learning_resource_repository import SqlAlchemyLearningResourceRepository


def _create_profile(client: TestClient, username: str = "Amara") -> int:
    response = client.post(
        "/api/v1/onboarding",
        json={"username": username, "interests": ["Biology"], "age": 22},
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


def _create_version(client: TestClient, resource_id: int, title: str) -> int:
    response = client.post(
        f"/api/v1/learning-resources/{resource_id}/versions",
        json={
            "title": title,
            "summary": "Mitosis review material",
            "content": {"practice_quiz": [{"question_id": "q1"}]},
            "resource_types": ["practice_quiz"],
            "topics": ["Mitosis"],
        },
    )
    assert response.status_code == 201
    return int(response.json()["id"])


def test_study_session_tracks_first_time_answers_and_progress(
    client: TestClient,
) -> None:
    onboarding_id = _create_profile(client)
    resource_id = _create_resource(client, onboarding_id)
    version_one_id = _create_version(client, resource_id, "Version 1")
    version_two_id = _create_version(client, resource_id, "Version 2")

    response = client.post(
        "/api/v1/study-sessions",
        json={
            "onboarding_id": onboarding_id,
            "resource_version_id": version_two_id,
            "mode": "practice",
            "source": "practice_quiz",
        },
    )
    assert response.status_code == 201
    first_session = response.json()
    assert first_session["first_time_for_version"] is True
    session_id = first_session["id"]

    answer_payloads = [
        {
            "question_id": "q-001",
            "concept_id": "mitosis-metaphase",
            "concept_name": "Metaphase",
            "student_answer": "Chromosomes line up in the middle",
            "correct_answer": "Chromosomes align at the cell equator",
            "is_correct": True,
            "time_taken_seconds": 18,
            "confidence": 4,
            "hints_used": 0,
        },
        {
            "question_id": "q-002",
            "concept_id": "interphase",
            "concept_name": "Interphase",
            "student_answer": "The cytoplasm splits",
            "correct_answer": "DNA is copied",
            "is_correct": False,
            "time_taken_seconds": 22,
            "confidence": 2,
            "hints_used": 1,
        },
    ]
    for payload in answer_payloads:
        answer_response = client.post(f"/api/v1/study-sessions/{session_id}/answers", json=payload)
        assert answer_response.status_code == 201
        assert answer_response.json()["study_session_id"] == session_id

    completed = client.post(
        f"/api/v1/study-sessions/{session_id}/complete",
        json={
            "score": 1,
            "total_items": 2,
            "correct_items": 1,
            "time_spent_seconds": 740,
        },
    )
    assert completed.status_code == 200
    completed_data = completed.json()
    assert completed_data["session"]["accuracy"] == 50.0
    assert completed_data["progress"]["attempts_count"] == 1
    assert completed_data["progress"]["latest_score"] == 1
    assert completed_data["progress"]["best_score"] == 1
    assert completed_data["progress"]["latest_accuracy"] == 50.0
    assert completed_data["progress"]["mastery_state"] == "learning"

    progress = client.get(
        f"/api/v1/learning-resources/{resource_id}/versions/{version_two_id}/progress",
        params={"onboarding_id": onboarding_id},
    )
    assert progress.status_code == 200
    assert progress.json()["first_time_for_version"] is False

    second_session = client.post(
        "/api/v1/study-sessions",
        json={
            "onboarding_id": onboarding_id,
            "resource_version_id": version_two_id,
            "mode": "practice",
            "source": "practice_quiz",
        },
    )
    assert second_session.status_code == 201
    assert second_session.json()["first_time_for_version"] is False

    separate_version_session = client.post(
        "/api/v1/study-sessions",
        json={
            "onboarding_id": onboarding_id,
            "resource_version_id": version_one_id,
            "mode": "review",
            "source": "reviewer",
        },
    )
    assert separate_version_session.status_code == 201
    assert separate_version_session.json()["first_time_for_version"] is True


def test_only_current_version_advances_and_oldest_keeps_compact_analytics(
    client: TestClient,
) -> None:
    onboarding_id = _create_profile(client)
    resource_id = _create_resource(client, onboarding_id)
    versions = [_create_version(client, resource_id, f"Version {number}") for number in range(1, 4)]

    def start(version_id: int) -> int:
        response = client.post(
            "/api/v1/study-sessions",
            json={"onboarding_id": onboarding_id, "resource_version_id": version_id},
        )
        assert response.status_code == 201
        return response.json()["id"]

    first_id = start(versions[0])
    answer = {
        "question_id": "q-1", "concept_id": "mitosis", "concept_name": "Mitosis",
        "student_answer": "wrong", "correct_answer": "Cell division", "is_correct": False,
        "time_taken_seconds": 20, "confidence": 2, "hints_used": 1,
    }
    assert client.post(f"/api/v1/study-sessions/{first_id}/answers", json=answer).status_code == 201
    first_completion = client.post(
        f"/api/v1/study-sessions/{first_id}/complete",
        json={"score": 0, "time_spent_seconds": 30},
    )
    assert first_completion.status_code == 200
    assert first_completion.json()["new_version_id"] is None

    second_id = start(versions[1])
    second_completion = client.post(
        f"/api/v1/study-sessions/{second_id}/complete",
        json={"score": 5, "total_items": 1, "correct_items": 1},
    )
    assert second_completion.status_code == 200
    assert second_completion.json()["new_version_id"] is None

    third_id = start(versions[2])
    assert client.post(f"/api/v1/study-sessions/{third_id}/answers", json=answer).status_code == 201
    third_completion = client.post(
        f"/api/v1/study-sessions/{third_id}/complete",
        json={"score": 0, "time_spent_seconds": 40},
    )
    assert third_completion.status_code == 200
    completed = third_completion.json()
    assert completed["new_version_id"] is not None
    assert completed["archived_version_number"] == 1

    current = client.get(f"/api/v1/learning-resources/{resource_id}/versions")
    assert [version["version_number"] for version in current.json()] == [4, 3, 2]
    assert client.get(
        f"/api/v1/learning-resources/{resource_id}/versions/{versions[0]}"
    ).status_code == 404
    successor = current.json()[0]
    assert successor["id"] == completed["new_version_id"]
    assert (
        successor["content"]["adaptive_review"]["priority_concepts"][0]["concept_id"]
        == "mitosis"
    )
    assert successor["content"]["practice_quiz"] == [{"question_id": "q1"}]

    archived = client.get(f"/api/v1/learning-resources/{resource_id}/analytics/archived")
    assert archived.status_code == 200
    assert len(archived.json()) == 1
    assert archived.json()[0]["version_number"] == 1
    assert archived.json()[0]["attempts_count"] == 1
    assert archived.json()[0]["total_items"] == 1
    assert archived.json()[0]["concept_stats"][0]["hints_used"] == 1

    retried = client.post(
        f"/api/v1/study-sessions/{third_id}/complete", json={"score": 0}
    )
    assert retried.status_code == 200
    assert retried.json()["new_version_id"] == completed["new_version_id"]
    assert retried.json()["progress"]["attempts_count"] == 1
    assert client.post(f"/api/v1/study-sessions/{third_id}/answers", json=answer).status_code == 409

    older_retry = start(versions[2])
    older_completion = client.post(
        f"/api/v1/study-sessions/{older_retry}/complete", json={"score": 0}
    )
    assert older_completion.status_code == 200
    assert older_completion.json()["new_version_id"] is None
    assert [version["version_number"] for version in client.get(
        f"/api/v1/learning-resources/{resource_id}/versions"
    ).json()] == [4, 3, 2]

    fourth_id = start(successor["id"])
    fourth_completion = client.post(
        f"/api/v1/study-sessions/{fourth_id}/complete", json={"score": 0}
    )
    assert fourth_completion.status_code == 200
    assert fourth_completion.json()["archived_version_number"] == 2
    assert [version["version_number"] for version in client.get(
        f"/api/v1/learning-resources/{resource_id}/versions"
    ).json()] == [5, 4, 3]
    assert [record["version_number"] for record in client.get(
        f"/api/v1/learning-resources/{resource_id}/analytics/archived"
    ).json()] == [2, 1]


def test_failed_archive_rolls_back_completion(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    onboarding_id = _create_profile(client)
    resource_id = _create_resource(client, onboarding_id)
    for number in range(1, 4):
        version_id = _create_version(client, resource_id, f"Version {number}")
    session_response = client.post(
        "/api/v1/study-sessions",
        json={"onboarding_id": onboarding_id, "resource_version_id": version_id},
    )
    session_id = session_response.json()["id"]

    def fail_archive(self: SqlAlchemyLearningResourceRepository, resource_id: int) -> list[int]:
        raise RuntimeError("archive failed")

    with monkeypatch.context() as patcher:
        patcher.setattr(
            SqlAlchemyLearningResourceRepository, "_archive_excess_versions", fail_archive
        )
        with pytest.raises(RuntimeError, match="archive failed"):
            client.post(f"/api/v1/study-sessions/{session_id}/complete", json={"score": 0})

    session = client.get(f"/api/v1/study-sessions/{session_id}")
    assert session.status_code == 200
    assert session.json()["completed_at"] is None
    assert [version["version_number"] for version in client.get(
        f"/api/v1/learning-resources/{resource_id}/versions"
    ).json()] == [3, 2, 1]
