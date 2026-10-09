"""Integration tests for the per-concept knowledge map."""

from fastapi.testclient import TestClient


def _setup(client: TestClient) -> tuple[int, int]:
    onboarding_id = client.post(
        "/api/v1/onboarding", json={"username": "Amara", "interests": [], "age": 20}
    ).json()["id"]
    resource_id = client.post(
        "/api/v1/learning-resources",
        json={"onboarding_id": onboarding_id, "title": "Mitosis", "subject": "Biology"},
    ).json()["id"]
    version_id = client.post(
        f"/api/v1/learning-resources/{resource_id}/versions",
        json={"summary": "s", "content": {}, "resource_types": ["practice_quiz"], "topics": []},
    ).json()["id"]
    return onboarding_id, version_id


def _run_session(
    client: TestClient, onboarding_id: int, version_id: int, results: dict[str, bool]
) -> None:
    session_id = client.post(
        "/api/v1/study-sessions",
        json={"onboarding_id": onboarding_id, "resource_version_id": version_id},
    ).json()["id"]
    for concept, correct in results.items():
        response = client.post(
            f"/api/v1/study-sessions/{session_id}/answers",
            json={
                "question_id": f"q-{concept}",
                "concept_id": concept,
                "concept_name": concept.title(),
                "is_correct": correct,
            },
        )
        assert response.status_code == 201
    done = client.post(
        f"/api/v1/study-sessions/{session_id}/complete",
        json={"score": sum(results.values()), "total_items": len(results)},
    )
    assert done.status_code == 200


def test_knowledge_map_is_empty_without_evidence(client: TestClient) -> None:
    onboarding_id, _ = _setup(client)
    response = client.get("/api/v1/knowledge-map", params={"onboarding_id": onboarding_id})
    assert response.status_code == 200
    assert response.json() == {"onboarding_id": onboarding_id, "items": []}


def test_knowledge_map_classifies_concepts_by_accuracy(client: TestClient) -> None:
    onboarding_id, version_id = _setup(client)
    _run_session(client, onboarding_id, version_id, {"metaphase": True, "interphase": False})

    response = client.get("/api/v1/knowledge-map", params={"onboarding_id": onboarding_id})
    assert response.status_code == 200
    items = {item["concept_id"]: item for item in response.json()["items"]}
    assert items["metaphase"]["state"] == "strong"
    assert items["metaphase"]["accuracy"] == 100.0
    assert items["interphase"]["state"] == "needs_practice"
    assert items["interphase"]["accuracy"] == 0.0
    # needs_practice concepts are listed first so the UI can lead with gaps
    assert response.json()["items"][0]["concept_id"] == "interphase"


def test_knowledge_map_uses_only_latest_three_sessions(client: TestClient) -> None:
    onboarding_id, version_id = _setup(client)
    for outcome in (False, False, True, True, True):
        _run_session(client, onboarding_id, version_id, {"anaphase": outcome})

    items = client.get("/api/v1/knowledge-map", params={"onboarding_id": onboarding_id}).json()[
        "items"
    ]
    anaphase = next(item for item in items if item["concept_id"] == "anaphase")
    assert anaphase["sessions"] == 3
    assert anaphase["answers"] == 3
    assert anaphase["accuracy"] == 100.0
    assert anaphase["state"] == "strong"


def test_knowledge_map_unknown_learner_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/knowledge-map", params={"onboarding_id": 9999})
    assert response.status_code == 404
