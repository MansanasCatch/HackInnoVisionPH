"""Health-check endpoint."""

from fastapi import APIRouter

from app.api.deps import HealthServiceDep
from app.schemas.health import HealthRead

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthRead, summary="API and database health")
def read_health(service: HealthServiceDep) -> HealthRead:
    """Return API liveness and database connectivity."""
    return service.check()
