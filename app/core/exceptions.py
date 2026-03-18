from __future__ import annotations

from typing import Any

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError


def _error_payload(code: str, message: str, details: Any | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"code": code, "detail": message}
    if details is not None:
        payload["details"] = details
    return payload


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(code="http_error", message=str(exc.detail)),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=_error_payload(
            code="validation_error",
            message="Request validation failed",
            details=exc.errors(),
        ),
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    # Avoid returning raw SQL error details to clients.
    return JSONResponse(
        status_code=500,
        content=_error_payload(code="database_error", message="Database operation failed"),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=_error_payload(code="internal_error", message="An unexpected error occurred"),
    )


def register_exception_handlers(app: Any) -> None:
    """Register global exception handlers for consistent API errors."""

    from fastapi import FastAPI

    if not isinstance(app, FastAPI):
        # Keep it generic while still being safe.
        raise TypeError("app must be a FastAPI instance")

    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

