"""Structured logging: one JSON object per line on stdout, with bound context.

Context (``request_id``, ``job_id``, ``source_id`` ...) is stored in a ``contextvars`` variable, so it
follows asyncio tasks. ``extra={...}`` fields of a log call are added to the record.
"""

from __future__ import annotations

import contextvars
import json
import logging
import sys
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any, Literal

__all__ = ["JsonFormatter", "bind_context", "configure_logging", "current_context", "get_logger"]

_context: contextvars.ContextVar[Mapping[str, Any]] = contextvars.ContextVar("jane_log_context", default={})  # noqa: B039

# Attributes every LogRecord has; anything else came from `extra=`.
_STANDARD = set(logging.LogRecord("", 0, "", 0, "", None, None).__dict__) | {
    "message",
    "asctime",
    "taskName",
    "color_message",
}  # uvicorn ANSI duplicate


def current_context() -> dict[str, Any]:
    return dict(_context.get())


@contextmanager
def bind_context(**values: Any) -> Iterator[None]:
    """Add fields to every log record emitted inside the block (and in tasks spawned from it)."""
    token = _context.set({**_context.get(), **{k: v for k, v in values.items() if v is not None}})
    try:
        yield
    finally:
        _context.reset(token)


class JsonFormatter(logging.Formatter):
    def __init__(self, service: str, instance: str | None = None) -> None:
        super().__init__()
        self.service = service
        self.instance = instance

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, UTC).isoformat(timespec="milliseconds"),
            "level": record.levelname.lower(),
            "logger": record.name,
            "msg": record.getMessage(),
            "service": self.service,
        }
        if self.instance:
            payload["instance"] = self.instance
        payload.update(_context.get())
        for key, value in record.__dict__.items():
            if key not in _STANDARD and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


class _ConsoleFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        ctx = {**_context.get(), **{k: v for k, v in record.__dict__.items() if k not in _STANDARD}}
        return f"{base} {json.dumps(ctx, ensure_ascii=False, default=str)}" if ctx else base


def configure_logging(
    service: str,
    level: str | int = "INFO",
    fmt: Literal["json", "console"] = "json",
    instance: str | None = None,
    stream: Any = None,
) -> None:
    """Configure the root logger once per process (idempotent; replaces previous handlers)."""
    handler = logging.StreamHandler(stream or sys.stdout)
    if fmt == "json":
        handler.setFormatter(JsonFormatter(service, instance))
    else:
        handler.setFormatter(_ConsoleFormatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s"))
    root = logging.getLogger()
    for old in list(root.handlers):
        root.removeHandler(old)
    root.addHandler(handler)
    root.setLevel(level if isinstance(level, int) else level.upper())
    # uvicorn installs its own handlers; route them through ours for uniform output.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        lg.handlers.clear()
        lg.propagate = True
    logging.getLogger("uvicorn.access").disabled = True  # replaced by jane_kit access log


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
