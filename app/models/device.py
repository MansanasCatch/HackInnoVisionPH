"""ORM model for device specs setup and local AI model selection."""

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class DeviceSpecs(Base, TimestampMixin):
    """Hardware specifications and active local AI model choice for an onboarding account."""

    __tablename__ = "device_specs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    onboarding_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("onboardings.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    ram_gb: Mapped[float] = mapped_column(Float, nullable=False)
    gpu_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    vram_gb: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    cpu_cores: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_free_gb: Mapped[float] = mapped_column(Float, nullable=False)
    os_name: Mapped[str] = mapped_column(String(50), nullable=False)
    selected_model: Mapped[str] = mapped_column(String(100), default="llama3.2:1b", nullable=False)
    pull_status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)

    onboarding: Mapped["OnboardingProfile"] = relationship("OnboardingProfile", back_populates="device_specs")

    def __repr__(self) -> str:
        return f"<DeviceSpecs id={self.id} onboarding_id={self.onboarding_id} ram={self.ram_gb}GB model={self.selected_model!r}>"
