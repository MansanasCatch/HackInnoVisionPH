"""Domain exceptions and their HTTP translation.

Services raise these framework-agnostic exceptions; the API layer converts them
into consistent JSON error responses via :func:`register_exception_handlers`.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


class AppError(Exception):
    """Base class for all expected application errors."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    error_code: str = "bad_request"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""

    status_code = status.HTTP_404_NOT_FOUND
    error_code = "not_found"


class ConflictError(AppError):
    """Raised when an operation would violate a uniqueness rule."""

    status_code = status.HTTP_409_CONFLICT
    error_code = "conflict"


class UnprocessableError(AppError):
    """Raised when a request is well-formed but cannot be processed as given."""

    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    error_code = "unprocessable"


async def _app_error_handler(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, AppError)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.error_code, "message": exc.message}},
    )


async def _unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": {"code": "internal_error", "message": "Something went wrong."}},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach the application's exception handlers to ``app``."""
    app.add_exception_handler(AppError, _app_error_handler)
    app.add_exception_handler(Exception, _unhandled_error_handler)
