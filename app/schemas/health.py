"""Health-check response schema."""

from typing import Literal

from pydantic import BaseModel


class HealthRead(BaseModel):
    """Service liveness and database connectivity status."""

    status: Literal["ok", "degraded"]
    app: str
    version: str
    environment: str
    database: Literal["connected", "disconnected"]
