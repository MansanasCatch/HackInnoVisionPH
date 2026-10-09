"""Unit tests for LocalAIService logic and active model resolution."""

import pytest

from app.models.device import DeviceSpecs
from app.repositories.device_repository import AbstractDeviceRepository
from app.schemas.ai import AIGenerateRequest
from app.services.local_ai_service import LocalAIService


class FakeDeviceRepository(AbstractDeviceRepository):
    def __init__(self) -> None:
        self._device = DeviceSpecs(
            id=1,
            onboarding_id=10,
            ram_gb=16.0,
            gpu_name="RTX 3060",
            vram_gb=6.0,
            cpu_cores=8,
            storage_free_gb=100.0,
            os_name="Windows 11",
            selected_model="gemma2:2b",
            pull_status="completed",
        )

    def add(self, device: DeviceSpecs) -> DeviceSpecs:
        return device

    def get(self, device_id: int) -> DeviceSpecs | None:
        return self._device

    def get_by_onboarding_id(self, onboarding_id: int) -> DeviceSpecs | None:
        if onboarding_id == 10:
            return self._device
        return None

    def update(self, device: DeviceSpecs) -> DeviceSpecs:
        return device

    def get_latest_active_model(self) -> str:
        return "llama3.2:1b"


@pytest.fixture
def ai_service() -> LocalAIService:
    return LocalAIService(FakeDeviceRepository())


def test_active_model_resolution_from_device_specs(ai_service: LocalAIService) -> None:
    # Uses selected model for onboarding_id=10
    model = ai_service.get_active_model_for_account(onboarding_id=10)
    assert model == "gemma2:2b"

    # Override takes precedence
    model_override = ai_service.get_active_model_for_account(
        onboarding_id=10, model_override="mistral:7b"
    )
    assert model_override == "mistral:7b"

    # Default model for unknown account
    default_model = ai_service.get_active_model_for_account(onboarding_id=99)
    assert default_model == "llama3.2:1b"


def test_generate_with_attached_file_context(ai_service: LocalAIService) -> None:
    req = AIGenerateRequest(
        prompt="Summarize the key notes from my attached file.",
        onboarding_id=10,
    )
    uploaded = [
        ("lecture1.txt", b"Photosynthesis transforms light into chemical energy.", "text/plain")
    ]
    res = ai_service.generate(request=req, uploaded_files=uploaded)

    assert res.model_used == "gemma2:2b"
    assert res.attached_files_count == 1
    assert res.ingested_files[0].filename == "lecture1.txt"
    assert "Photosynthesis" in res.ingested_files[0].extracted_text
