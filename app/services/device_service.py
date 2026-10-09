"""Use cases for Device Specs Setup and Local AI Model management."""

from app.core.exceptions import NotFoundError
from app.models.device import DeviceSpecs
from app.repositories.device_repository import AbstractDeviceRepository
from app.repositories.onboarding_repository import AbstractOnboardingRepository
from app.schemas.device import (
    ActiveModelResponse,
    DeviceSpecsCreate,
    DeviceSpecsDetect,
    DeviceSpecsRead,
    DeviceSpecsUpdate,
    ModelSelectPayload,
    ModelSuggestionsResponse,
)
from app.services.device_detection import detect_system_hardware
from app.services.model_recommendation import recommend_models_for_hardware
from app.services.ollama_service import (
    get_installed_ollama_models,
    is_ollama_reachable,
    trigger_ollama_pull_background,
)


class DeviceService:
    """Business logic orchestrator for device hardware specs and local AI model selection."""

    def __init__(
        self,
        device_repository: AbstractDeviceRepository,
        onboarding_repository: AbstractOnboardingRepository | None = None,
    ) -> None:
        self._device_repo = device_repository
        self._onboarding_repo = onboarding_repository

    def auto_detect_hardware(self) -> DeviceSpecsDetect:
        """Auto-detect host machine RAM, GPU, CPU, storage, and OS."""
        return detect_system_hardware()

    def get_suggestions(
        self,
        ram_gb: float | None = None,
        vram_gb: float = 0.0,
        gpu_name: str | None = None,
        onboarding_id: int | None = None,
    ) -> ModelSuggestionsResponse:
        """Get model options with specific hardware applicability reasons."""
        if onboarding_id is not None:
            saved = self._device_repo.get_by_onboarding_id(onboarding_id)
            if saved is not None:
                ram_gb = saved.ram_gb
                vram_gb = saved.vram_gb
                gpu_name = saved.gpu_name

        if ram_gb is None:
            detected = detect_system_hardware()
            ram_gb = detected.ram_gb
            vram_gb = detected.vram_gb
            gpu_name = detected.gpu_name

        return recommend_models_for_hardware(ram_gb=ram_gb, vram_gb=vram_gb, gpu_name=gpu_name)

    def create_or_update_device_specs(self, payload: DeviceSpecsCreate) -> DeviceSpecsRead:
        """Create or update device specs setup linked to an onboarding account."""
        if self._onboarding_repo is not None:
            account = self._onboarding_repo.get(payload.onboarding_id)
            if account is None:
                raise NotFoundError(f"Onboarding account with ID {payload.onboarding_id} not found.")

        # Determine model selection
        selected_model = payload.selected_model
        if not selected_model:
            suggestions = recommend_models_for_hardware(
                ram_gb=payload.ram_gb, vram_gb=payload.vram_gb, gpu_name=payload.gpu_name
            )
            selected_model = suggestions.recommended_model

        existing = self._device_repo.get_by_onboarding_id(payload.onboarding_id)
        if existing is not None:
            existing.ram_gb = payload.ram_gb
            existing.gpu_name = payload.gpu_name
            existing.vram_gb = payload.vram_gb
            existing.cpu_cores = payload.cpu_cores
            existing.storage_free_gb = payload.storage_free_gb
            existing.os_name = payload.os_name
            existing.selected_model = selected_model
            existing.pull_status = "pulling"
            saved = self._device_repo.update(existing)
        else:
            device = DeviceSpecs(
                onboarding_id=payload.onboarding_id,
                ram_gb=payload.ram_gb,
                gpu_name=payload.gpu_name,
                vram_gb=payload.vram_gb,
                cpu_cores=payload.cpu_cores,
                storage_free_gb=payload.storage_free_gb,
                os_name=payload.os_name,
                selected_model=selected_model,
                pull_status="pulling",
            )
            saved = self._device_repo.add(device)

        # Trigger auto pull in background
        trigger_ollama_pull_background(selected_model)

        return DeviceSpecsRead.model_validate(saved)

    def get_by_account(self, onboarding_id: int) -> DeviceSpecsRead:
        """Get device specs and selected model for an account."""
        device = self._device_repo.get_by_onboarding_id(onboarding_id)
        if device is None:
            raise NotFoundError(f"Device specs for onboarding account {onboarding_id} not found.")
        return DeviceSpecsRead.model_validate(device)

    def select_active_model(self, payload: ModelSelectPayload) -> DeviceSpecsRead:
        """Runtime switch of the active local AI model for an account."""
        device = self._device_repo.get_by_onboarding_id(payload.onboarding_id)
        if device is None:
            raise NotFoundError(f"Device specs for onboarding account {payload.onboarding_id} not found.")

        device.selected_model = payload.selected_model
        device.pull_status = "pulling" if payload.auto_pull else "pending"
        saved = self._device_repo.update(device)

        if payload.auto_pull:
            trigger_ollama_pull_background(payload.selected_model)

        return DeviceSpecsRead.model_validate(saved)

    def get_active_model(self, onboarding_id: int | None = None) -> ActiveModelResponse:
        """Fetch current active local model to be used by Local AI execution engine."""
        active_model = "llama3.2:1b"
        pull_status = "completed"
        ollama_online = is_ollama_reachable()

        if onboarding_id is not None:
            device = self._device_repo.get_by_onboarding_id(onboarding_id)
            if device is not None:
                active_model = device.selected_model
                pull_status = device.pull_status
        else:
            active_model = self._device_repo.get_latest_active_model()

        if ollama_online:
            installed = get_installed_ollama_models()
            if active_model in installed:
                pull_status = "completed"

        return ActiveModelResponse(
            onboarding_id=onboarding_id,
            active_model=active_model,
            pull_status=pull_status,
            is_ollama_online=ollama_online,
        )
