"""Shared pytest fixtures."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  (registers models on Base.metadata)
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app


@pytest.fixture
def engine() -> Iterator[Engine]:
    """Fresh in-memory SQLite engine per test."""
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(test_engine)
    yield test_engine
    Base.metadata.drop_all(test_engine)
    test_engine.dispose()


@pytest.fixture
def db_session(engine: Engine) -> Iterator[Session]:
    """Database session bound to the in-memory engine."""
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(autouse=True)
def offline_ollama(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep tests deterministic and fast: never call a real local Ollama server."""
    monkeypatch.setattr("app.services.local_ai_service.is_ollama_reachable", lambda: False)


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    """FastAPI test client using the in-memory database."""
    application = create_app()
    application.dependency_overrides[get_db] = lambda: db_session
    with TestClient(application) as test_client:
        yield test_client
