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
from app.schemas.onboarding import (
    OnboardingCreate,
    OnboardingRead,
    OnboardingUpdate,
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
    "ModelOption",
    "ModelSelectPayload",
    "ModelSuggestionsResponse",
    "OnboardingCreate",
    "OnboardingRead",
    "OnboardingUpdate",
]
