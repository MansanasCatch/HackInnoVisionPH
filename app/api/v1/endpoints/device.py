"""Endpoints for Device Hardware Specs Setup & Local AI Model Selection."""

from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import DeviceServiceDep
from app.schemas.device import (
    ActiveModelResponse,
    DeviceSpecsCreate,
    DeviceSpecsDetect,
    DeviceSpecsRead,
    ModelSelectPayload,
    ModelSuggestionsResponse,
)
from app.services.ollama_service import get_installed_ollama_models, is_ollama_reachable

router = APIRouter(prefix="/device", tags=["Device & AI Model Setup"])


@router.post(
    "/detect",
    response_model=DeviceSpecsDetect,
    summary="Auto-detect host hardware specs",
    description="Detect host machine RAM, GPU/VRAM, CPU cores, free disk storage, and OS.",
)
def detect_hardware_specs(service: DeviceServiceDep) -> DeviceSpecsDetect:
    """Auto-detect host hardware specifications."""
    return service.auto_detect_hardware()


@router.get(
    "/suggestions",
    response_model=ModelSuggestionsResponse,
    summary="Get AI model recommendations with reasons",
    description="Analyze hardware specs and return suggested local AI models with detailed applicability reasons.",
)
def get_model_suggestions(
    service: DeviceServiceDep,
    ram_gb: Annotated[float | None, Query(ge=0.5, description="System RAM in GB")] = None,
    vram_gb: Annotated[float, Query(ge=0, description="Dedicated GPU VRAM in GB")] = 0.0,
    gpu_name: Annotated[str | None, Query(description="GPU model name")] = None,
    onboarding_id: Annotated[int | None, Query(description="Onboarding account ID to pull saved specs from")] = None,
) -> ModelSuggestionsResponse:
    """Get dropdown selection options for local AI models with reasons."""
    return service.get_suggestions(
        ram_gb=ram_gb, vram_gb=vram_gb, gpu_name=gpu_name, onboarding_id=onboarding_id
    )


@router.post(
    "",
    response_model=DeviceSpecsRead,
    status_code=status.HTTP_201_CREATED,
    summary="Setup device specs for account",
    description="Save hardware specs setup linked to an onboarding account and set initial model.",
)
def create_device_specs_setup(
    payload: DeviceSpecsCreate,
    service: DeviceServiceDep,
) -> DeviceSpecsRead:
    """Create device specs setup for an onboarding account."""
    return service.create_or_update_device_specs(payload)


@router.get(
    "/account/{onboarding_id}",
    response_model=DeviceSpecsRead,
    summary="Get device specs for account",
    description="Fetch device specs and active model selection for a given onboarding account.",
)
def get_device_specs_by_account(
    onboarding_id: int,
    service: DeviceServiceDep,
) -> DeviceSpecsRead:
    """Get device specs for account."""
    return service.get_by_account(onboarding_id)


@router.post(
    "/select-model",
    response_model=DeviceSpecsRead,
    summary="Switch active local AI model at runtime",
    description="Switch active local model for an account and automatically pull model via Ollama.",
)
def switch_active_local_model(
    payload: ModelSelectPayload,
    service: DeviceServiceDep,
) -> DeviceSpecsRead:
    """Switch active local model at runtime."""
    return service.select_active_model(payload)


@router.get(
    "/active-model",
    response_model=ActiveModelResponse,
    summary="Get active local model for AI calls",
    description="Fetch the active local model configured for AI generation tasks.",
)
def get_active_model(
    service: DeviceServiceDep,
    onboarding_id: Annotated[int | None, Query(description="Onboarding account ID")] = None,
) -> ActiveModelResponse:
    """Fetch active local model for AI calls."""
    return service.get_active_model(onboarding_id=onboarding_id)


@router.get(
    "/ollama/models",
    summary="List local Ollama models",
    description="Check local Ollama service connection and list installed model tags.",
)
def list_ollama_models() -> dict[str, object]:
    """List installed models in local Ollama service."""
    online = is_ollama_reachable()
    installed = get_installed_ollama_models() if online else []
    return {
        "is_online": online,
        "installed_models": installed,
        "count": len(installed),
    }
