"""Pydantic schemas for device hardware specs detection and local AI model selection."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class DeviceSpecsDetect(BaseModel):
    """Auto-detected hardware specs from host machine."""

    ram_gb: float = Field(description="Total RAM in GB")
    gpu_name: str | None = Field(default=None, description="Detected GPU model name")
    vram_gb: float = Field(default=0.0, description="Dedicated GPU VRAM in GB")
    cpu_cores: int = Field(description="Total CPU logical cores")
    storage_free_gb: float = Field(description="Free disk storage in GB")
    os_name: str = Field(description="Operating System")


class DeviceSpecsCreate(BaseModel):
    """Payload to save hardware specs setup linked to an onboarding account."""

    onboarding_id: int = Field(description="ID of the onboarding account")
    ram_gb: float = Field(ge=0.5, description="RAM in GB")
    gpu_name: str | None = Field(default=None, description="GPU model name")
    vram_gb: float = Field(default=0.0, ge=0, description="GPU VRAM in GB")
    cpu_cores: int = Field(ge=1, description="CPU logical cores")
    storage_free_gb: float = Field(ge=0, description="Free disk storage in GB")
    os_name: str = Field(default="Windows", description="Operating system")
    selected_model: str | None = Field(
        default=None, description="Initial local AI model selection (auto-recommended if omitted)"
    )


class DeviceSpecsUpdate(BaseModel):
    """Payload to update device hardware specs."""

    ram_gb: float | None = Field(default=None, ge=0.5)
    gpu_name: str | None = Field(default=None)
    vram_gb: float | None = Field(default=None, ge=0)
    cpu_cores: int | None = Field(default=None, ge=1)
    storage_free_gb: float | None = Field(default=None, ge=0)
    os_name: str | None = Field(default=None)
    selected_model: str | None = Field(default=None)


class ModelOption(BaseModel):
    """Local AI model details and recommendation reasoning based on device specs."""

    model_name: str = Field(description="Ollama model tag, e.g. llama3.2:1b")
    display_name: str = Field(description="Human readable name")
    size_gb: float = Field(description="Approximate VRAM/RAM memory requirement in GB")
    min_ram_gb: float = Field(description="Minimum recommended system RAM in GB")
    min_vram_gb: float = Field(description="Minimum recommended dedicated VRAM in GB")
    tier: str = Field(description="Hardware tier requirement: Low, Medium, or High")
    is_recommended: bool = Field(description="Whether this model is recommended for the given hardware")
    reason: str = Field(description="Detailed reason explaining why this model is or isn't applicable for the device specs")


class ModelSuggestionsResponse(BaseModel):
    """Response returned when fetching AI model recommendations."""

    recommended_model: str = Field(description="Top recommended model tag for the device")
    device_summary: str = Field(description="Hardware summary line")
    models: list[ModelOption] = Field(description="List of available local AI model choices with reasons")


class ModelSelectPayload(BaseModel):
    """Payload to set/switch active local AI model at runtime."""

    onboarding_id: int = Field(description="ID of the onboarding account")
    selected_model: str = Field(description="Target Ollama model tag, e.g. llama3.2:1b")
    auto_pull: bool = Field(default=True, description="Whether to trigger an auto-pull from Ollama server")


class ActiveModelResponse(BaseModel):
    """Response returning the active model to be used by AI operations."""

    onboarding_id: int | None = Field(default=None, description="Associated onboarding account ID")
    active_model: str = Field(description="Currently active local AI model tag")
    pull_status: str = Field(description="Status of model pull (e.g. completed, pulling, pending, not_pulled)")
    is_ollama_online: bool = Field(description="Whether local Ollama service is reachable")


class DeviceSpecsRead(BaseModel):
    """Schema returned by device endpoints."""

    id: int
    onboarding_id: int
    ram_gb: float
    gpu_name: str | None
    vram_gb: float
    cpu_cores: int
    storage_free_gb: float
    os_name: str
    selected_model: str
    pull_status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
