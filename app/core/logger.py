from __future__ import annotations

import json
import logging
import time
import uuid
from contextvars import ContextVar
from typing import Any, Callable, Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


request_id_ctx_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class JsonFormatter(logging.Formatter):
    """Simple structured JSON logger using standard library logging."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }

        request_id = request_id_ctx_var.get()
        if request_id:
            payload["request_id"] = request_id

        # Include extra fields if passed via `logger.info(..., extra={...})`.
        for key, value in record.__dict__.items():
            if key in {"levelname", "msg", "args", "name", "created", "msecs", "relativeCreated", "thread", "threadName", "processName", "process", "message"}:
                continue
            if key.startswith("_"):
                continue
            # Avoid overriding keys above.
            payload.setdefault(key, value)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=True)


def setup_logging(log_level: str = "INFO") -> None:
    """Configure structured logging for the app."""

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level.upper())

    # Avoid duplicate handlers in development reload.
    if root_logger.handlers:
        return

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger instance."""

    return logging.getLogger(name)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log each request with method/path/status and latency."""

    def __init__(self, app: Any, logger: logging.Logger) -> None:
        super().__init__(app)
        self._logger = logger

    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Response:
        request_id = str(uuid.uuid4())
        request_id_ctx_var.set(request_id)
        start = time.perf_counter()
        try:
            response: Response = await call_next(request)
            duration_ms = int((time.perf_counter() - start) * 1000)
            self._logger.info(
                "request completed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                },
            )
            return response
        except Exception:
            duration_ms = int((time.perf_counter() - start) * 1000)
            self._logger.exception(
                "request failed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                },
            )
            raise

