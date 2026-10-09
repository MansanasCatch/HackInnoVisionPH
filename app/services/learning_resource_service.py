"""Use cases for versioned learning resource records."""

from app.core.exceptions import NotFoundError
from app.models.learning_resource import LearningResource, LearningResourceVersion
from app.repositories.learning_resource_repository import AbstractLearningResourceRepository
from app.repositories.onboarding_repository import AbstractOnboardingRepository
from app.schemas.learning_resource import (
    LearningResourceCreate,
    LearningResourceRead,
    LearningResourceVersionCreate,
    LearningResourceVersionRead,
    VersionProgressRead,
)


class LearningResourceService:
    """Orchestrates learning resource records, versions, and progress lookup."""

    def __init__(
        self,
        repository: AbstractLearningResourceRepository,
        onboarding_repository: AbstractOnboardingRepository,
    ) -> None:
        self._repository = repository
        self._onboarding_repository = onboarding_repository

    def create_resource(self, payload: LearningResourceCreate) -> LearningResourceRead:
        """Create a learning resource record for an onboarding account."""
        self._ensure_onboarding_exists(payload.onboarding_id)
        resource = LearningResource(
            onboarding_id=payload.onboarding_id,
            title=payload.title,
            subject=payload.subject,
            source_label=payload.source_label,
        )
        saved = self._repository.add_resource(resource)
        return LearningResourceRead.model_validate(saved)

    def list_resources(
        self, *, onboarding_id: int, limit: int = 50, offset: int = 0
    ) -> list[LearningResourceRead]:
        """List learning resource records for an onboarding account."""
        self._ensure_onboarding_exists(onboarding_id)
        resources = self._repository.list_resources(
            onboarding_id=onboarding_id, limit=limit, offset=offset
        )
        return [LearningResourceRead.model_validate(resource) for resource in resources]

    def get_resource(self, resource_id: int) -> LearningResourceRead:
        """Fetch a learning resource record by ID."""
        return LearningResourceRead.model_validate(self._get_resource_or_raise(resource_id))

    def create_version(
        self, resource_id: int, payload: LearningResourceVersionCreate
    ) -> LearningResourceVersionRead:
        """Create the next version for a learning resource record."""
        resource = self._get_resource_or_raise(resource_id)
        version_number = self._repository.next_version_number(resource_id)
        title = payload.title or f"{resource.title} v{version_number}"
        version = LearningResourceVersion(
            learning_resource_id=resource_id,
            version_number=version_number,
            title=title,
            summary=payload.summary,
            content=payload.content,
            resource_types=[resource_type.value for resource_type in payload.resource_types],
            topics=payload.topics,
            is_current=True,
        )
        saved = self._repository.create_version(version)
        return LearningResourceVersionRead.model_validate(saved)

    def list_versions(
        self, *, resource_id: int, limit: int = 3
    ) -> list[LearningResourceVersionRead]:
        """List latest selectable versions for a learning resource record."""
        self._get_resource_or_raise(resource_id)
        versions = self._repository.list_versions(resource_id=resource_id, limit=limit)
        return [LearningResourceVersionRead.model_validate(version) for version in versions]

    def get_version(self, *, resource_id: int, version_id: int) -> LearningResourceVersionRead:
        """Fetch one version under a resource."""
        version = self._get_version_or_raise(version_id)
        if version.learning_resource_id != resource_id:
            raise NotFoundError(
                f"Version {version_id} was not found under learning resource {resource_id}."
            )
        return LearningResourceVersionRead.model_validate(version)

    def get_progress(
        self, *, resource_id: int, version_id: int, onboarding_id: int
    ) -> VersionProgressRead:
        """Return progress for a learner on one exact resource version."""
        self._ensure_onboarding_exists(onboarding_id)
        version = self._get_version_or_raise(version_id)
        if version.learning_resource_id != resource_id:
            raise NotFoundError(
                f"Version {version_id} was not found under learning resource {resource_id}."
            )

        progress = self._repository.get_progress(
            onboarding_id=onboarding_id, resource_version_id=version_id
        )
        if progress is None:
            return VersionProgressRead(
                onboarding_id=onboarding_id,
                resource_version_id=version_id,
                first_time_for_version=True,
                attempts_count=0,
            )

        return VersionProgressRead(
            onboarding_id=onboarding_id,
            resource_version_id=version_id,
            first_time_for_version=progress.attempts_count == 0,
            attempts_count=progress.attempts_count,
            latest_score=progress.latest_score,
            best_score=progress.best_score,
            latest_accuracy=progress.latest_accuracy,
            mastery_state=progress.mastery_state,
            first_started_at=progress.first_started_at,
            last_studied_at=progress.last_studied_at,
        )

    def _ensure_onboarding_exists(self, onboarding_id: int) -> None:
        if self._onboarding_repository.get(onboarding_id) is None:
            raise NotFoundError(f"Onboarding account with ID {onboarding_id} not found.")

    def _get_resource_or_raise(self, resource_id: int) -> LearningResource:
        resource = self._repository.get_resource(resource_id)
        if resource is None:
            raise NotFoundError(f"Learning resource with ID {resource_id} was not found.")
        return resource

    def _get_version_or_raise(self, version_id: int) -> LearningResourceVersion:
        version = self._repository.get_version(version_id)
        if version is None:
            raise NotFoundError(f"Learning resource version with ID {version_id} was not found.")
        return version
