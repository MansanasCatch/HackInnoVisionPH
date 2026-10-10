"""Engine and session factory plus the FastAPI ``get_db`` dependency."""

from collections.abc import Iterator
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

_settings = get_settings()

_connect_args: dict[str, Any] = {"check_same_thread": False} if _settings.is_sqlite else {}

engine = create_engine(
    _settings.database_url,
    echo=_settings.database_echo,
    pool_pre_ping=True,
    connect_args=_connect_args,
)

if _settings.is_sqlite:
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """Yield a database session and guarantee it is closed afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
