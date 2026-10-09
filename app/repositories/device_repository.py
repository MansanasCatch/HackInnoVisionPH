"""Data-access repository for device specs and model selection."""

from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.device import DeviceSpecs


class AbstractDeviceRepository(Protocol):
    """Interface defining operations for device hardware specs persistence."""

    def add(self, device: DeviceSpecs) -> DeviceSpecs:
        """Add new device specs setup."""
        ...

    def get(self, device_id: int) -> DeviceSpecs | None:
        """Fetch device specs by ID."""
        ...

    def get_by_onboarding_id(self, onboarding_id: int) -> DeviceSpecs | None:
        """Fetch device specs linked to an onboarding account."""
        ...

    def update(self, device: DeviceSpecs) -> DeviceSpecs:
        """Persist changes to device specs or model selection."""
        ...

    def get_latest_active_model(self) -> str:
        """Fetch the active selected model for AI tasks."""
        ...


class SqlAlchemyDeviceRepository(AbstractDeviceRepository):
    """Production repository implementation backed by SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, device: DeviceSpecs) -> DeviceSpecs:
        self._session.add(device)
        self._session.commit()
        self._session.refresh(device)
        return device

    def get(self, device_id: int) -> DeviceSpecs | None:
        return self._session.get(DeviceSpecs, device_id)

    def get_by_onboarding_id(self, onboarding_id: int) -> DeviceSpecs | None:
        statement = select(DeviceSpecs).where(DeviceSpecs.onboarding_id == onboarding_id)
        return self._session.scalars(statement).first()

    def update(self, device: DeviceSpecs) -> DeviceSpecs:
        self._session.add(device)
        self._session.commit()
        self._session.refresh(device)
        return device

    def get_latest_active_model(self) -> str:
        statement = (
            select(DeviceSpecs.selected_model).order_by(DeviceSpecs.updated_at.desc()).limit(1)
        )
        res = self._session.scalars(statement).first()
        return res if res else "llama3.2:1b"
