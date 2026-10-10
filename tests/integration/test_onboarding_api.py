"""Integration tests for Onboarding API endpoints."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


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

    # Delete profile
    response = client.delete(f"/api/v1/onboarding/{profile_id}")
    assert response.status_code == 204

    # Verify deleted
    response = client.get(f"/api/v1/onboarding/{profile_id}")
    assert response.status_code == 404


def test_delete_profile_clears_all_child_data(client: TestClient, db_session: Session) -> None:
    """Verify that deleting an onboarding profile deletes all child records in every related table."""
    from app.models.device import DeviceSpecs
    from app.models.learning_resource import LearningResource, LearningResourceVersion
    from app.models.study import (
        ArchivedVersionAnalytics,
        StudyAnswer,
        StudySession,
        UserVersionProgress,
    )

    # 1. Create onboarding profile
    res = client.post("/api/v1/onboarding", json={"username": "ChildCleanupUser", "interests": ["Math"], "age": 20})
    assert res.status_code == 201
    profile_id = res.json()["id"]

    # 2. Add DeviceSpecs
    device = DeviceSpecs(
        onboarding_id=profile_id,
        ram_gb=16.0,
        gpu_name="RTX 4060",
        vram_gb=8.0,
        cpu_cores=8,
        storage_free_gb=120.0,
        os_name="Windows 11",
        selected_model="qwen2.5:1.5b",
    )
    db_session.add(device)

    # 3. Add LearningResource & Version
    resource = LearningResource(
        onboarding_id=profile_id,
        title="Linear Algebra",
        subject="Math",
        source_label="Textbook",
    )
    db_session.add(resource)
    db_session.flush()

    version = LearningResourceVersion(
        learning_resource_id=resource.id,
        version_number=1,
        title="Linear Algebra v1",
        summary="Summary of vectors",
        content={"key_notes": ["Note 1"]},
        resource_types=["notes"],
        topics=["Vectors"],
        is_current=True,
    )
    db_session.add(version)
    db_session.flush()

    # 4. Add StudySession & StudyAnswer
    session = StudySession(
        onboarding_id=profile_id,
        resource_version_id=version.id,
        mode="quiz",
        source="quiz",
        score=10,
        total_items=10,
        correct_items=10,
        accuracy=1.0,
        first_time_for_version=True,
    )
    db_session.add(session)
    db_session.flush()

    answer = StudyAnswer(
        study_session_id=session.id,
        question_id="q1",
        concept_id="c1",
        concept_name="Vectors",
        student_answer="A quantity with magnitude and direction",
        correct_answer="A quantity with magnitude and direction",
        is_correct=True,
    )
    db_session.add(answer)

    # 5. Add UserVersionProgress
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    progress = UserVersionProgress(
        onboarding_id=profile_id,
        resource_version_id=version.id,
        first_started_at=now,
        last_studied_at=now,
        attempts_count=1,
        best_score=10,
        latest_score=10,
        latest_accuracy=1.0,
        mastery_state="mastered",
    )
    db_session.add(progress)

    # 6. Add ArchivedVersionAnalytics
    analytics = ArchivedVersionAnalytics(
        learning_resource_id=resource.id,
        onboarding_id=profile_id,
        version_number=1,
        attempts_count=1,
        total_items=10,
        correct_items=10,
        total_time_seconds=300,
        best_score=10,
        latest_score=10,
        concept_stats=[],
    )
    db_session.add(analytics)
    db_session.commit()

    # Verify all records exist prior to deletion
    assert db_session.query(DeviceSpecs).filter(DeviceSpecs.onboarding_id == profile_id).count() == 1
    assert db_session.query(LearningResource).filter(LearningResource.onboarding_id == profile_id).count() == 1
    assert db_session.query(LearningResourceVersion).filter(LearningResourceVersion.learning_resource_id == resource.id).count() == 1
    assert db_session.query(StudySession).filter(StudySession.onboarding_id == profile_id).count() == 1
    assert db_session.query(StudyAnswer).filter(StudyAnswer.study_session_id == session.id).count() == 1
    assert db_session.query(UserVersionProgress).filter(UserVersionProgress.onboarding_id == profile_id).count() == 1
    assert db_session.query(ArchivedVersionAnalytics).filter(ArchivedVersionAnalytics.onboarding_id == profile_id).count() == 1

    # Call API to delete profile
    del_res = client.delete(f"/api/v1/onboarding/{profile_id}")
    assert del_res.status_code == 204

    # Verify that profile and ALL child data are completely cleared
    assert client.get(f"/api/v1/onboarding/{profile_id}").status_code == 404
    assert db_session.query(DeviceSpecs).filter(DeviceSpecs.onboarding_id == profile_id).count() == 0
    assert db_session.query(LearningResource).filter(LearningResource.onboarding_id == profile_id).count() == 0
    assert db_session.query(LearningResourceVersion).filter(LearningResourceVersion.learning_resource_id == resource.id).count() == 0
    assert db_session.query(StudySession).filter(StudySession.onboarding_id == profile_id).count() == 0
    assert db_session.query(StudyAnswer).filter(StudyAnswer.study_session_id == session.id).count() == 0
    assert db_session.query(UserVersionProgress).filter(UserVersionProgress.onboarding_id == profile_id).count() == 0
    assert db_session.query(ArchivedVersionAnalytics).filter(ArchivedVersionAnalytics.onboarding_id == profile_id).count() == 0

