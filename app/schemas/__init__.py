from app.schemas.ai import (
    AIGenerateRequest,
    AIGenerateResponse,
    ExtractedFileContent,
)
from app.schemas.device import (
    ActiveModelResponse,
    DeviceSpecsCreate,
    DeviceSpecsDetect,
    DeviceSpecsRead,
    DeviceSpecsUpdate,
    ModelOption,
    ModelSelectPayload,
    ModelSuggestionsResponse,
)
from app.schemas.health import HealthRead
from app.schemas.learning_resource import (
    LearningResourceCreate,
    LearningResourceRead,
    LearningResourceVersionCreate,
    LearningResourceVersionRead,
    StudyResourceType,
    VersionProgressRead,
)
from app.schemas.onboarding import (
    OnboardingCreate,
    OnboardingRead,
    OnboardingUpdate,
)
from app.schemas.study import (
    StudyAnswerCreate,
    StudyAnswerRead,
    StudyMode,
    StudySessionComplete,
    StudySessionCompleteResponse,
    StudySessionRead,
    StudySessionStart,
    StudySource,
)

__all__ = [
    "AIGenerateRequest",
    "AIGenerateResponse",
    "ActiveModelResponse",
    "DeviceSpecsCreate",
    "DeviceSpecsDetect",
    "DeviceSpecsRead",
    "DeviceSpecsUpdate",
    "ExtractedFileContent",
    "HealthRead",
    "LearningResourceCreate",
    "LearningResourceRead",
    "LearningResourceVersionCreate",
    "LearningResourceVersionRead",
    "ModelOption",
    "ModelSelectPayload",
    "ModelSuggestionsResponse",
    "OnboardingCreate",
    "OnboardingRead",
    "OnboardingUpdate",
    "StudyAnswerCreate",
    "StudyAnswerRead",
    "StudyMode",
    "StudyResourceType",
    "StudySessionComplete",
    "StudySessionCompleteResponse",
    "StudySessionRead",
    "StudySessionStart",
    "StudySource",
    "VersionProgressRead",
]
