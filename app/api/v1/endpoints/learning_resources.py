"""Endpoints for learning resource records and version history."""

from typing import Annotated

from fastapi import APIRouter, File, Form, Query, UploadFile, status

from app.api.deps import LearningResourceServiceDep, ResourceGenerationServiceDep
from app.api.uploads import read_uploads
from app.schemas.learning_resource import (
    ArchivedVersionAnalyticsRead,
    GeneratedLearningResource,
    LearningResourceCreate,
    LearningResourceRead,
    LearningResourceVersionCreate,
    LearningResourceVersionRead,
    StudyResourceType,
    VersionProgressRead,
)

router = APIRouter(prefix="/learning-resources", tags=["Learning Resources"])


@router.post(
    "/generate",
    response_model=GeneratedLearningResource,
    status_code=status.HTTP_201_CREATED,
    summary="Generate study materials from a topic, notes and files and save them",
)
async def generate_learning_resource(
    service: ResourceGenerationServiceDep,
    onboarding_id: Annotated[int, Form(ge=1)],
    topic: Annotated[str, Form()],
    notes: Annotated[str, Form()] = "",
    item_count: Annotated[int, Form(ge=10, le=50)] = 10,
    resource_types: Annotated[list[StudyResourceType] | None, Form()] = None,
    files: Annotated[list[UploadFile] | None, File()] = None,
) -> GeneratedLearningResource:
    """Generate study materials and persist them as a learning resource version."""
    uploaded = await read_uploads(files)
    return service.generate(
        onboarding_id=onboarding_id,
        topic=topic,
        notes=notes,
        resource_types=resource_types,
        uploaded_files=uploaded,
        item_count=item_count,
    )


@router.post(
    "",
    response_model=LearningResourceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a learning resource record",
)
def create_learning_resource(
    payload: LearningResourceCreate,
    service: LearningResourceServiceDep,
) -> LearningResourceRead:
    """Create a learning resource record for an onboarding account."""
    return service.create_resource(payload)


@router.get("", response_model=list[LearningResourceRead], summary="List learning resources")
def list_learning_resources(
    service: LearningResourceServiceDep,
    onboarding_id: Annotated[int, Query(ge=1)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[LearningResourceRead]:
    """List learning resource records for an onboarding account."""
    return service.list_resources(onboarding_id=onboarding_id, limit=limit, offset=offset)


@router.get(
    "/{resource_id}",
    response_model=LearningResourceRead,
    summary="Get a learning resource record",
)
def get_learning_resource(
    resource_id: int,
    service: LearningResourceServiceDep,
) -> LearningResourceRead:
    """Fetch one learning resource record."""
    return service.get_resource(resource_id)


@router.post(
    "/{resource_id}/versions",
    response_model=LearningResourceVersionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a learning resource version",
)
def create_learning_resource_version(
    resource_id: int,
    payload: LearningResourceVersionCreate,
    service: LearningResourceServiceDep,
) -> LearningResourceVersionRead:
    """Create the next version under a learning resource record."""
    return service.create_version(resource_id, payload)


@router.get(
    "/{resource_id}/versions",
    response_model=list[LearningResourceVersionRead],
    summary="List latest learning resource versions",
)
def list_learning_resource_versions(
    resource_id: int,
    service: LearningResourceServiceDep,
    limit: Annotated[int, Query(ge=1, le=3)] = 3,
) -> list[LearningResourceVersionRead]:
    """Return the latest selectable versions, limited to 3 by default."""
    return service.list_versions(resource_id=resource_id, limit=limit)


@router.get(
    "/{resource_id}/analytics/archived",
    response_model=list[ArchivedVersionAnalyticsRead],
    summary="List archived version analytics",
)
def list_archived_version_analytics(
    resource_id: int, service: LearningResourceServiceDep
) -> list[ArchivedVersionAnalyticsRead]:
    """Return compact study metrics for removed resource versions."""
    return service.list_archived_analytics(resource_id)


@router.get(
    "/{resource_id}/versions/{version_id}",
    response_model=LearningResourceVersionRead,
    summary="Get a learning resource version",
)
def get_learning_resource_version(
    resource_id: int,
    version_id: int,
    service: LearningResourceServiceDep,
) -> LearningResourceVersionRead:
    """Fetch a specific version under a learning resource record."""
    return service.get_version(resource_id=resource_id, version_id=version_id)


@router.get(
    "/{resource_id}/versions/{version_id}/progress",
    response_model=VersionProgressRead,
    summary="Get learner progress for a version",
)
def get_learning_resource_version_progress(
    resource_id: int,
    version_id: int,
    service: LearningResourceServiceDep,
    onboarding_id: Annotated[int, Query(ge=1)],
) -> VersionProgressRead:
    """Check whether a learner has studied this exact version before."""
    return service.get_progress(
        resource_id=resource_id,
        version_id=version_id,
        onboarding_id=onboarding_id,
    )
