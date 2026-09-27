"""Error model: RFC 9457 Problem Details (``application/problem+json``) per WP-00 contract.

Wire format: ``contracts/schemas/common/problem.schema.json``; code catalogue with HTTP statuses and
``retryable``: ``contracts/docs/errors.md``. This module is the single place that maps exceptions to
that schema — services raise :class:`JaneError` subclasses (or ``JaneError(code=...)``).
"""

from __future__ import annotations

import logging
from typing import Any, ClassVar

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from starlette.exceptions import HTTPException as StarletteHTTPException

from jane_kit.logs import current_context

__all__ = [
    "KNOWN_CODES",
    "PROBLEM_CONTENT_TYPE",
    "PROBLEM_TYPE_BASE",
    "BadRequest",
    "Conflict",
    "FieldError",
    "Forbidden",
    "JaneError",
    "LimitExceeded",
    "NotFound",
    "Problem",
    "RateLimited",
    "ServiceUnavailable",
    "Timeout",
    "Unauthenticated",
    "UpstreamUnavailable",
    "ValidationFailed",
    "install_error_handlers",
    "problem_response",
]

PROBLEM_CONTENT_TYPE = "application/problem+json"
PROBLEM_TYPE_BASE = "urn:jane:problem:"

# code -> (HTTP status, retryable) from contracts/docs/errors.md (WP-00 draft).
KNOWN_CODES: dict[str, tuple[int, bool]] = {
    "bad_request": (400, False),
    "validation_failed": (422, False),
    "unauthenticated": (401, False),
    "forbidden": (403, False),
    "not_found": (404, False),
    "method_not_allowed": (405, False),
    "conflict": (409, False),
    "version_exists": (409, False),
    "idempotency_in_progress": (409, True),
    "job_not_cancellable": (409, False),
    "upstream_conflict": (409, False),
    "precondition_failed": (412, False),
    "precondition_required": (428, False),
    "idempotency_key_reused": (422, False),
    "payload_too_large": (413, False),
    "unsupported_media_type": (415, False),
    "limit_exceeded": (422, False),
    "rate_limited": (429, True),
    "budget_exhausted": (429, False),
    "secret_detected": (422, False),
    "dependency_not_allowed": (422, False),
    "digest_mismatch": (422, False),
    "schema_mismatch": (422, False),
    "out_of_scope": (422, False),
    "access_denied_by_policy": (403, False),
    "source_unavailable": (502, True),
    "upstream_unavailable": (502, True),
    "internal_error": (500, True),
    "not_implemented": (501, False),
    "service_unavailable": (503, True),
    "timeout": (504, True),
}

log = logging.getLogger(__name__)


class FieldError(BaseModel):
    model_config = ConfigDict(extra="allow")

    pointer: str | None = None
    """JSON Pointer into the request body, e.g. ``/stages/2/handler/version``."""
    parameter: str | None = None
    """Name of a query/path/header parameter."""
    code: str | None = None
    message: str


class Problem(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str
    title: str
    status: int
    detail: str | None = None
    instance: str | None = None
    code: str
    retryable: bool | None = None
    retry_after_seconds: int | None = None
    errors: list[FieldError] | None = None
    trace_id: str | None = None
    details: dict[str, Any] | None = None


def _title(code: str) -> str:
    return code.replace("_", " ").capitalize()


class JaneError(Exception):
    """Base class for errors that map to a Problem response. Status/retryable default from the catalogue."""

    code: ClassVar[str] = "internal_error"

    def __init__(
        self,
        detail: str | None = None,
        *,
        code: str | None = None,
        status: int | None = None,
        retryable: bool | None = None,
        title: str | None = None,
        errors: list[FieldError] | None = None,
        details: dict[str, Any] | None = None,
        retry_after_seconds: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.error_code = code or type(self).code
        default_status, default_retryable = KNOWN_CODES.get(self.error_code, (500, False))
        self.status = status or default_status
        self.retryable = default_retryable if retryable is None else retryable
        self.title = title or _title(self.error_code)
        self.detail = detail
        self.errors = errors
        self.details = details
        self.retry_after_seconds = retry_after_seconds
        self.headers = dict(headers or {})
        if retry_after_seconds is not None:
            self.headers.setdefault("Retry-After", str(retry_after_seconds))
        super().__init__(detail or self.title)

    def to_problem(self, instance: str | None = None) -> Problem:
        return Problem(
            type=PROBLEM_TYPE_BASE + self.error_code,
            title=self.title,
            status=self.status,
            detail=self.detail,
            instance=instance,
            code=self.error_code,
            retryable=self.retryable,
            retry_after_seconds=self.retry_after_seconds,
            errors=self.errors,
            trace_id=current_context().get("trace_id"),
            details=self.details,
        )


class BadRequest(JaneError):
    code = "bad_request"


class ValidationFailed(JaneError):
    code = "validation_failed"


class Unauthenticated(JaneError):
    code = "unauthenticated"


class Forbidden(JaneError):
    code = "forbidden"


class NotFound(JaneError):
    code = "not_found"


class Conflict(JaneError):
    code = "conflict"


class LimitExceeded(JaneError):
    """A request asks for more than the effective limit or hard cap (422, not retryable)."""

    code = "limit_exceeded"


class RateLimited(JaneError):
    code = "rate_limited"


class ServiceUnavailable(JaneError):
    code = "service_unavailable"


class UpstreamUnavailable(JaneError):
    code = "upstream_unavailable"


class Timeout(JaneError):
    code = "timeout"


def problem_response(problem: Problem, headers: dict[str, str] | None = None) -> JSONResponse:
    return JSONResponse(
        problem.model_dump(exclude_none=True, mode="json"),
        status_code=problem.status,
        media_type=PROBLEM_CONTENT_TYPE,
        headers=headers,
    )


_HTTP_CODES = {
    400: "bad_request",
    401: "unauthenticated",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    409: "conflict",
    412: "precondition_failed",
    413: "payload_too_large",
    415: "unsupported_media_type",
    422: "validation_failed",
    428: "precondition_required",
    429: "rate_limited",
    501: "not_implemented",
    503: "service_unavailable",
    504: "timeout",
}


def _field_error(err: dict[str, Any]) -> FieldError:
    loc = [str(p) for p in err.get("loc", ())]
    message = str(err.get("msg", ""))
    code = err.get("type")
    if loc[:1] == ["body"]:
        return FieldError(
            pointer="/" + "/".join(p.replace("~", "~0").replace("/", "~1") for p in loc[1:]),
            code=code,
            message=message,
        )
    if loc and loc[0] in {"query", "path", "header", "cookie"}:
        return FieldError(parameter=".".join(loc[1:]), code=code, message=message)
    return FieldError(code=code, message=message)


def install_error_handlers(app: FastAPI) -> None:
    """Make every error of ``app`` a Problem response (including 404/405 and validation)."""

    async def jane_error(request: Request, exc: Exception) -> JSONResponse:
        assert isinstance(exc, JaneError)
        return problem_response(exc.to_problem(instance=request.url.path), exc.headers or None)

    async def http_error(request: Request, exc: Exception) -> JSONResponse:
        assert isinstance(exc, StarletteHTTPException)
        code = _HTTP_CODES.get(exc.status_code, "internal_error" if exc.status_code >= 500 else "bad_request")
        err = JaneError(
            exc.detail if isinstance(exc.detail, str) else None, code=code, status=exc.status_code
        )
        return problem_response(
            err.to_problem(instance=request.url.path), dict(exc.headers) if exc.headers else None
        )

    async def validation_error(request: Request, exc: Exception) -> JSONResponse:
        assert isinstance(exc, RequestValidationError)
        errors = [_field_error(dict(e)) for e in exc.errors()]
        if any(e.get("type") == "json_invalid" for e in exc.errors()):
            err: JaneError = BadRequest("request body is not valid JSON", errors=errors)
        else:
            err = ValidationFailed("request does not match the API contract", errors=errors)
        return problem_response(err.to_problem(instance=request.url.path))

    async def unhandled(request: Request, exc: Exception) -> JSONResponse:
        log.exception("unhandled error", extra={"path": request.url.path})
        return problem_response(JaneError().to_problem(instance=request.url.path))

    app.add_exception_handler(JaneError, jane_error)
    app.add_exception_handler(StarletteHTTPException, http_error)
    app.add_exception_handler(RequestValidationError, validation_error)
    app.add_exception_handler(Exception, unhandled)
