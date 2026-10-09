"""Service that reports application and database health."""

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.logging import get_logger
from app.schemas.health import HealthRead

logger = get_logger(__name__)


class HealthService:
    """Checks that the API is alive and the database is reachable."""

    def __init__(self, session: Session, settings: Settings) -> None:
        self._session = session
        self._settings = settings

    def check(self) -> HealthRead:
        database_ok = self._ping_database()
        return HealthRead(
            status="ok" if database_ok else "degraded",
            app=self._settings.app_name,
            version=self._settings.app_version,
            environment=self._settings.environment,
            database="connected" if database_ok else "disconnected",
        )

    def _ping_database(self) -> bool:
        try:
            self._session.execute(text("SELECT 1"))
        except SQLAlchemyError:
            logger.exception("Database health check failed")
            return False
        return True
