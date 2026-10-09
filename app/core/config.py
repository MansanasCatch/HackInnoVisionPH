"""Application settings loaded from environment variables and the optional ``.env`` file."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = BASE_DIR / "frontend"


class Settings(BaseSettings):
    """Strongly-typed application configuration.

    Every field can be overridden with an environment variable of the same name
    (case-insensitive), e.g. ``PORT=9000`` or ``DATABASE_URL=postgresql+psycopg://...``.
    """

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "InnoVisionPH Hackathon API"
    app_version: str = "1.0.0"
    environment: Literal["development", "staging", "production", "test"] = "development"
    debug: bool = True

    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1, le=65535)

    database_url: str = f"sqlite:///{(BASE_DIR / 'innovision.db').as_posix()}"
    database_echo: bool = False

    cors_origins: list[str] = ["http://127.0.0.1:8000", "http://localhost:8000"]
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    api_v1_prefix: str = "/api/v1"

    @property
    def is_sqlite(self) -> bool:
        """Return ``True`` when the configured database is SQLite."""
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance (one per process)."""
    return Settings()
