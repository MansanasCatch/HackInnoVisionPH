"""Unit tests for DeviceService and model recommendation engine."""

from collections.abc import Sequence

import pytest

from app.core.exceptions import NotFoundError
from app.db.base import utc_now
from app.models.device import DeviceSpecs
from app.models.onboarding import OnboardingProfile
from app.repositories.device_repository import AbstractDeviceRepository
from app.repositories.onboarding_repository import AbstractOnboardingRepository
from app.schemas.device import DeviceSpecsCreate, ModelSelectPayload
from app.services.device_service import DeviceService
from app.services.model_recommendation import recommend_models_for_hardware


class FakeDeviceRepository(AbstractDeviceRepository):
    def __init__(self) -> None:
        self._items: dict[int, DeviceSpecs] = {}
        self._next_id = 1

    def add(self, device: DeviceSpecs) -> DeviceSpecs:
        now = utc_now()
        device.id = self._next_id
        self._next_id += 1
        device.created_at = now
        device.updated_at = now
        self._items[device.id] = device
        return device

    def get(self, device_id: int) -> DeviceSpecs | None:
        return self._items.get(device_id)

    def get_by_onboarding_id(self, onboarding_id: int) -> DeviceSpecs | None:
        for d in self._items.values():
            if d.onboarding_id == onboarding_id:
                return d
        return None

    def update(self, device: DeviceSpecs) -> DeviceSpecs:
        device.updated_at = utc_now()
        self._items[device.id] = device
        return device

    def get_latest_active_model(self) -> str:
        if not self._items:
            return "llama3.2:1b"
        latest = max(self._items.values(), key=lambda d: d.updated_at)
        return latest.selected_model


class FakeOnboardingRepository(AbstractOnboardingRepository):
    def __init__(self) -> None:
        self._items: dict[int, OnboardingProfile] = {
            1: OnboardingProfile(id=1, username="Amara Mensah", interests=["Biology"], age=20)
        }

    def add(self, profile: OnboardingProfile) -> OnboardingProfile:
        self._items[profile.id] = profile
        return profile

    def get(self, profile_id: int) -> OnboardingProfile | None:
        return self._items.get(profile_id)

    def get_by_username(self, username: str) -> OnboardingProfile | None:
        return None

    def list(self, *, limit: int = 50, offset: int = 0) -> Sequence[OnboardingProfile]:
        return list(self._items.values())

    def update(self, profile: OnboardingProfile) -> OnboardingProfile:
        return profile


@pytest.fixture
def device_service() -> DeviceService:
    return DeviceService(FakeDeviceRepository(), FakeOnboardingRepository())


def test_model_recommendations_reasons() -> None:
    # Test low spec hardware
    res_low = recommend_models_for_hardware(ram_gb=4.0, vram_gb=0.0)
    assert res_low.recommended_model == "qwen2.5:0.5b"
    assert any("Fits" in m.reason for m in res_low.models if m.model_name == "qwen2.5:0.5b")

    # Test high spec hardware
    res_high = recommend_models_for_hardware(ram_gb=16.0, vram_gb=6.0, gpu_name="RTX 3060")
    assert res_high.recommended_model == "llama3.2:3b"
    assert any("Fits in dedicated VRAM" in m.reason for m in res_high.models if m.is_recommended)


def test_create_device_specs_setup(device_service: DeviceService) -> None:
    payload = DeviceSpecsCreate(
        onboarding_id=1,
        ram_gb=16.0,
        gpu_name="NVIDIA RTX 3060",
        vram_gb=6.0,
        cpu_cores=8,
        storage_free_gb=100.0,
        os_name="Windows 11",
    )
    res = device_service.create_or_update_device_specs(payload)
    assert res.onboarding_id == 1
    assert res.ram_gb == 16.0
    assert res.selected_model == "llama3.2:3b"


def test_runtime_switch_active_model(device_service: DeviceService) -> None:
    # Setup device
    device_service.create_or_update_device_specs(
        DeviceSpecsCreate(
            onboarding_id=1,
            ram_gb=8.0,
            cpu_cores=4,
            storage_free_gb=50.0,
            os_name="Windows 11",
        )
    )
    # Switch active model to mistral:7b
    switched = device_service.select_active_model(
        ModelSelectPayload(onboarding_id=1, selected_model="mistral:7b", auto_pull=False)
    )
    assert switched.selected_model == "mistral:7b"

    # Get active model
    active = device_service.get_active_model(onboarding_id=1)
    assert active.active_model == "mistral:7b"


def test_device_setup_nonexistent_account_raises_not_found(device_service: DeviceService) -> None:
    with pytest.raises(NotFoundError):
        device_service.create_or_update_device_specs(
            DeviceSpecsCreate(
                onboarding_id=999,
                ram_gb=8.0,
                cpu_cores=4,
                storage_free_gb=50.0,
            )
        )


def test_macos_apple_silicon_recommendation() -> None:
    res = recommend_models_for_hardware(ram_gb=16.0, vram_gb=12.0, gpu_name="Apple M2 Pro (Metal GPU)")
    assert res.recommended_model in ("llama3.2:3b", "mistral:7b")
    # Verify Apple Silicon Metal reasons are generated
    assert any("Apple Silicon" in m.reason for m in res.models if m.is_recommended)
    assert any("Metal" in m.reason for m in res.models if m.is_recommended)


def test_windows_nvidia_gpu_recommendation() -> None:
    res = recommend_models_for_hardware(ram_gb=16.0, vram_gb=8.0, gpu_name="NVIDIA GeForce RTX 4060")
    assert res.recommended_model == "llama3.2:3b"
    assert any("NVIDIA" in m.reason for m in res.models if m.is_recommended)
    assert any("Fits in dedicated VRAM" in m.reason for m in res.models if m.is_recommended)


def test_cross_platform_os_name_detection(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.services.device_detection import _detect_os_name

    # 1. Test macOS detection
    monkeypatch.setattr("platform.system", lambda: "Darwin")
    monkeypatch.setattr("platform.mac_ver", lambda: ("14.5", ("", "", ""), ""))
    assert _detect_os_name() == "macOS 14.5 (Sonoma)"

    # 2. Test macOS Sequoia detection
    monkeypatch.setattr("platform.mac_ver", lambda: ("15.1", ("", "", ""), ""))
    assert _detect_os_name() == "macOS 15.1 (Sequoia)"

    # 3. Test Windows detection
    monkeypatch.setattr("platform.system", lambda: "Windows")
    monkeypatch.setattr("platform.release", lambda: "11")
    assert _detect_os_name() == "Windows 11"
