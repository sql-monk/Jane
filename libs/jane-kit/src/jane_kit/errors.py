"""Error model: RFC 9457 Problem Details (``application/problem+json``) with a stable ``code``.

CONNECTION POINT (WP-00): the wire format of an error is defined by the error schema in
``contracts/``. This module is the single place that maps exceptions to that schema. When the
WP-00 contract changes, adjust :class:`Problem` (fields) and :data:`PROBLEM_TYPE_BASE` only;
services keep raising :class:`JaneError` subclasses.
"""

from __future__ import annotations

import logging
from typing import Any, ClassVar

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

from jane_kit.logs import current_context

__all__ = [
    "PROBLEM_CONTENT_TYPE",
    "PROBLEM_TYPE_BASE",
    "BadRequest",
    "Conflict",
    "Forbidden",
    "JaneError",
    "LimitExceeded",
    "NotFound",
    "Problem",
    "ProblemField",
    "Unauthorized",
    "Unavailable",
    "ValidationFailed",
    "install_error_handlers",
    "problem_response",
]

PROBLEM_CONTENT_TYPE = "application/problem+json"
PROBLEM_TYPE_BASE = "urn:jane:problem:"
"""``type`` URI prefix; the full type is ``PROBLEM_TYPE_BASE + code``."""

log = logging.getLogger(__name__)


class ProblemField(BaseModel):
    """One invalid input location (validation errors)."""

    model_config = ConfigDict(extra="allow")

    loc: list[str | int] = Field(default_factory=list)
    msg: str
    type: str | None = None


class Problem(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str = "about:blank"
    title: str
    status: int
    detail: str | None = None
    instance: str | None = None
    code: str
    """Stable machine-readable error code (snake_case)."""
    retryable: bool = False
    request_id: str | None = None
    errors: list[ProblemField] | None = None


class JaneError(Exception):
    """Base class for errors that map to a Problem response."""

    status: ClassVar[int] = 500
    code: ClassVar[str] = "internal_error"
    title: ClassVar[str] = "Internal error"
    retryable: ClassVar[bool] = False

    def __init__(
        self,
        detail: str | None = None,
        *,
        code: str | None = None,
        status: int | None = None,
        retryable: bool | None = None,
        errors: list[ProblemField] | None = None,
        headers: dict[str, str] | None = None,
        **extra: Any,
    ) -> None:
        super().__init__(detail or self.title)
        self.detail = detail
        self._code = code or type(self).code
        self._status = status or type(self).status
        self._retryable = type(self).retryable if retryable is None else retryable
        self.errors = errors
        self.headers = headers or {}
        self.extra = extra

    def to_problem(self, instance: str | None = None) -> Problem:
        return Problem(
            type=PROBLEM_TYPE_BASE + self._code,
            title=self.title,
            status=self._status,
            detail=self.detail,
            instance=instance,
            code=self._code,
            retryable=self._retryable,
            request_id=current_context().get("request_id"),
            errors=self.errors,
            **self.extra,
        )


class BadRequest(JaneError):
    status, code, title = 400, "bad_request", "Bad request"


class Unauthorized(JaneError):
    status, code, title = 401, "unauthorized", "Unauthorized"


class Forbidden(JaneError):
    status, code, title = 403, "forbidden", "Forbidden"


class NotFound(JaneError):
    status, code, title = 404, "not_found", "Not found"


class Conflict(JaneError):
    status, code, title = 409, "conflict", "Conflict"


class ValidationFailed(JaneError):
    status, code, title = 422, "validation_failed", "Validation failed"


class LimitExceeded(JaneError):
    status, code, title, retryable = 429, "limit_exceeded", "Limit exceeded", True


class Unavailable(JaneError):
    status, code, title, retryable = 503, "unavailable", "Service unavailable", True


def problem_response(problem: Problem, headers: dict[str, str] | None = None) -> JSONResponse:
    return JSONResponse(
        problem.model_dump(exclude_none=True, mode="json"),
        status_code=problem.status,
        media_type=PROBLEM_CONTENT_TYPE,
        headers=headers,
    )


_HTTP_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    406: "not_acceptable",
    409: "conflict",
    413: "payload_too_large",
    415: "unsupported_media_type",
    422: "validation_failed",
    429: "limit_exceeded",
}


def install_error_handlers(app: FastAPI) -> None:
    """Make every error of ``app`` a Problem response (including 404/405 and validation)."""

    async def jane_error(request: Request, exc: Exception) -> JSONResponse:
        assert isinstance(exc, JaneError)
        return problem_response(exc.to_problem(instance=request.url.path), exc.headers or None)

    async def http_error(request: Request, exc: Exception) -> JSONResponse:
        assert isinstance(exc, StarletteHTTPException)
        code = _HTTP_CODES.get(exc.status_code, "http_error")
        problem = Problem(
            type=PROBLEM_TYPE_BASE + code,
            title=code.replace("_", " ").capitalize(),
            status=exc.status_code,
            detail=exc.detail if isinstance(exc.detail, str) else None,
            instance=request.url.path,
            code=code,
            retryable=exc.status_code in (429, 503),
            request_id=current_context().get("request_id"),
        )
        return problem_response(problem, dict(exc.headers) if exc.headers else None)

    async def validation_error(request: Request, exc: Exception) -> JSONResponse:
        assert isinstance(exc, RequestValidationError)
        fields = [
            ProblemField(loc=list(e.get("loc", ())), msg=str(e.get("msg", "")), type=e.get("type"))
            for e in exc.errors()
        ]
        err = ValidationFailed("Request does not match the API contract", errors=fields)
        return problem_response(err.to_problem(instance=request.url.path))

    async def unhandled(request: Request, exc: Exception) -> JSONResponse:
        log.exception("unhandled error", extra={"path": request.url.path})
        return problem_response(JaneError().to_problem(instance=request.url.path))

    app.add_exception_handler(JaneError, jane_error)
    app.add_exception_handler(StarletteHTTPException, http_error)
    app.add_exception_handler(RequestValidationError, validation_error)
    app.add_exception_handler(Exception, unhandled)
