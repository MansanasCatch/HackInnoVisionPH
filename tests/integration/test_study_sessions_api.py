"""Integration tests for version-aware study sessions."""

from fastapi.testclient import TestClient


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


def test_list_study_sessions_returns_completed_sessions_newest_first(client: TestClient) -> None:
    onboarding_id = _create_profile(client)
    resource_id = _create_resource(client, onboarding_id)
    version_id = _create_version(client, resource_id, "Version 1")

    for score in (1, 2):
        session_id = client.post(
            "/api/v1/study-sessions",
            json={"onboarding_id": onboarding_id, "resource_version_id": version_id},
        ).json()["id"]
        client.post(
            f"/api/v1/study-sessions/{session_id}/complete",
            json={"score": score, "total_items": 2},
        )
    # an unfinished session must not appear in reports
    client.post(
        "/api/v1/study-sessions",
        json={"onboarding_id": onboarding_id, "resource_version_id": version_id},
    )

    response = client.get("/api/v1/study-sessions", params={"onboarding_id": onboarding_id})
    assert response.status_code == 200
    sessions = response.json()
    assert [session["score"] for session in sessions] == [2, 1]
    assert all(session["completed_at"] is not None for session in sessions)


def test_list_study_sessions_unknown_learner_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/study-sessions", params={"onboarding_id": 9999})
    assert response.status_code == 404
