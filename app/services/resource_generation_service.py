"""Generate study materials from user material and persist them as a learning resource."""

from app.core.exceptions import NotFoundError, UnprocessableError
from app.repositories.onboarding_repository import AbstractOnboardingRepository
from app.schemas.ai import AIGenerateRequest
from app.schemas.learning_resource import (
    GeneratedLearningResource,
    GenerationInfo,
    LearningResourceCreate,
    LearningResourceVersionCreate,
    StudyResourceType,
)
from app.services.learning_resource_service import LearningResourceService
from app.services.local_ai_service import LocalAIService


class ResourceGenerationService:
    """Compose AI generation with learning resource persistence."""

    def __init__(
        self,
        ai_service: LocalAIService,
        resource_service: LearningResourceService,
        onboarding_repository: AbstractOnboardingRepository,
    ) -> None:
        self._ai = ai_service
        self._resources = resource_service
        self._onboarding = onboarding_repository

    def generate(
        self,
        *,
        onboarding_id: int,
        topic: str,
        notes: str,
        resource_types: list[StudyResourceType] | None,
        uploaded_files: list[tuple[str, bytes, str | None]],
        item_count: int = 10,
    ) -> GeneratedLearningResource:
        """Generate materials, then store them as a resource with a first version."""
        if self._onboarding.get(onboarding_id) is None:
            raise NotFoundError(f"Onboarding account with ID {onboarding_id} not found.")

        topic = topic.strip()
        notes = notes.strip()
        if not topic or not (notes or uploaded_files):
            raise UnprocessableError("Provide a topic and either notes or at least one file.")

        response = self._ai.generate(
            AIGenerateRequest(
                prompt="",
                topic=topic,
                text_context=notes or None,
                onboarding_id=onboarding_id,
                item_count=item_count,
            ),
            uploaded_files,
        )
        materials = response.study_materials
        if materials is None:
            raise UnprocessableError("Study materials could not be generated from this material.")

        source_label = ", ".join(name for name, _, _ in uploaded_files) or "Typed notes"
        resource = self._resources.create_resource(
            LearningResourceCreate(
                onboarding_id=onboarding_id,
                title=(topic or materials.topic)[:160],
                subject=topic[:100],
                source_label=source_label[:255],
            )
        )

        topics: list[str] = []
        for name in [n.topic for n in materials.key_notes] + list(
            materials.source_coverage.covered_topics
        ):
            if name and name not in topics:
                topics.append(name)

        version = self._resources.create_version(
            resource.id,
            LearningResourceVersionCreate(
                summary=materials.summary.content,
                content=materials.model_dump(mode="json"),
                resource_types=resource_types
                or [
                    StudyResourceType.SUMMARY,
                    StudyResourceType.FLASHCARDS,
                    StudyResourceType.PRACTICE_QUIZ,
                ],
                topics=topics,
            ),
        )
        return GeneratedLearningResource(
            resource=resource,
            version=version,
            generation=GenerationInfo(
                model_used=response.model_used,
                is_ollama_online=response.is_ollama_online,
                execution_time_seconds=response.execution_time_seconds,
                warnings=response.warnings,
            ),
        )
