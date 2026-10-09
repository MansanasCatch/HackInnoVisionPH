"""FastAPI application factory and ASGI entry point (``app.main:app``)."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import FRONTEND_DIR, get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.services.ollama_service import ensure_ollama_started

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Run start-up and shutdown hooks."""
    logger.info("%s v%s is starting", app.title, app.version)
    # Auto-start Ollama local AI server if available
    ensure_ollama_started()
    yield
    logger.info("%s is shutting down", app.title)


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="InnoVisionPH Hackathon.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    dist_dir = FRONTEND_DIR / "dist"
    frontend_target = dist_dir if (dist_dir / "index.html").exists() else FRONTEND_DIR

    if (frontend_target / "assets").exists():
        app.mount("/assets", StaticFiles(directory=frontend_target / "assets"), name="dist_assets")

    if (FRONTEND_DIR / "static").exists():
        app.mount("/static", StaticFiles(directory=FRONTEND_DIR / "static"), name="static")

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon() -> FileResponse:
        """Serve the favicon."""
        fav = frontend_target / "favicon.svg"
        if not fav.exists():
            fav = FRONTEND_DIR / "public" / "favicon.svg"
        return FileResponse(fav, media_type="image/svg+xml")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str) -> FileResponse:
        """Serve SPA static files or fallback to index.html."""
        if full_path:
            file_path = frontend_target / full_path
            if file_path.is_file():
                return FileResponse(file_path)
        return FileResponse(frontend_target / "index.html")

    return app


app = create_app()
