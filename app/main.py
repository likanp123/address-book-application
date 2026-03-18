from __future__ import annotations

from fastapi import FastAPI

from app.api.routes.addresses import router as addresses_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logger import RequestLoggingMiddleware, get_logger, setup_logging


def create_app() -> FastAPI:
    """Application factory for consistent startup behavior."""

    setup_logging(settings.log_level)
    app_logger = get_logger("address_book")

    app = FastAPI(
        title="Address Book API",
        version="1.0.0",
        debug=settings.app_env.lower() == "development",
    )

    app.add_middleware(RequestLoggingMiddleware, logger=app_logger)
    register_exception_handlers(app)

    app.include_router(addresses_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "env": settings.app_env}

    return app


app = create_app()

