"""Contract-bound fakes of neighbour services (plan.md §3.3: neighbours are mocked from contracts).

A :class:`ContractFake` is an ASGI app built on one ``contracts/openapi/<api>.v1.yaml``:

* a request to an operation that is not in the contract, a missing required header or query
  parameter, or a body that does not match the request schema is a *violation* (and 4xx);
* each response the fake produces is validated against the documented status and schema;
  a mismatch is a violation too.

Tests assert ``violations == []`` so the assistant is checked against the neighbours' contracts
while the fakes keep just enough state to play the scenario. The assistant itself is never faked.
"""

from __future__ import annotations

import json
import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import Receive, Scope, Send

from jane_kit.contracts import ContractViolation, OpenAPISpec

__all__ = ["ContractFake", "FakeRequest", "Reply", "load_spec", "problem"]

_SPECS: dict[Path, OpenAPISpec] = {}


def load_spec(path: Path) -> OpenAPISpec:
    """Specs are parsed once per test session (YAML parsing dominates the fakes' start-up)."""
    key = path.resolve()
    if key not in _SPECS:
        _SPECS[key] = OpenAPISpec.load(key)
    return _SPECS[key]


@dataclass
class FakeRequest:
    method: str
    path: str
    path_params: dict[str, str]
    query: dict[str, str]
    headers: dict[str, str]
    json: Any


@dataclass
class Reply:
    status: int
    body: Any = None
    headers: dict[str, str] = field(default_factory=dict)
    media_type: str = "application/json"
    raw: bytes | None = None


def problem(status: int, code: str, title: str | None = None, **extra: Any) -> Reply:
    body = {
        "type": f"urn:jane:problem:{code}",
        "title": title or code.replace("_", " ").capitalize(),
        "status": status,
        "code": code,
        **extra,
    }
    return Reply(status, body, media_type="application/problem+json")


Handler = Callable[[FakeRequest], Awaitable[Reply] | Reply]


class ContractFake:
    def __init__(self, spec_path: Path, name: str) -> None:
        self.spec = load_spec(spec_path)
        self.name = name
        self.handlers: dict[str, Handler] = {}
        self.calls: list[tuple[str, FakeRequest, int]] = []
        self.violations: list[str] = []
        self.idempotency: dict[str, tuple[str, Reply]] = {}

    def on(self, operation_id: str) -> Callable[[Handler], Handler]:
        self.spec.by_id(operation_id)  # the operation must exist in the contract

        def deco(fn: Handler) -> Handler:
            self.handlers[operation_id] = fn
            return fn

        return deco

    def called(self, operation_id: str) -> list[FakeRequest]:
        return [r for op, r, _ in self.calls if op == operation_id]

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope, receive)
        response = await self._handle(request)
        await response(scope, receive, send)

    async def _handle(self, request: Request) -> Response:
        method, path = request.method, request.url.path
        try:
            op = self.spec.operation(method, path)
        except ContractViolation as exc:
            self.violations.append(str(exc))
            return JSONResponse({"error": str(exc)}, status_code=404)
        names = re.findall(r"\{([^}/]+)\}", op.path)
        pattern = re.sub(r"\{[^}/]+\}", "([^/]+)", re.escape(op.path).replace(r"\{", "{").replace(r"\}", "}"))
        m = re.match(f"^{pattern}$", path)
        path_params = dict(zip(names, m.groups() if m else (), strict=False))
        query = dict(parse_qsl(request.url.query))
        headers = {k.lower(): v for k, v in request.headers.items()}
        for p in op.parameters:
            where, pname = p.get("in"), str(p.get("name"))
            if not p.get("required"):
                continue
            if where == "header" and pname.lower() not in headers:
                self.violations.append(f"{self.name} {op.operation_id}: missing required header {pname}")
                return self._reply(op, problem(422, "validation_failed", detail=f"missing header {pname}"))
            if where == "query" and pname not in query:
                self.violations.append(f"{self.name} {op.operation_id}: missing required query {pname}")
                return self._reply(op, problem(422, "validation_failed", detail=f"missing query {pname}"))
        raw = await request.body()
        payload: Any = None
        if op.spec.get("requestBody") is not None:
            ctype = headers.get("content-type", "application/json").split(";")[0].strip()
            try:
                payload = json.loads(raw) if raw else None
                self.spec.validate_request(method, path, payload, ctype)
            except (ValueError, ContractViolation) as exc:
                self.violations.append(f"{self.name} {op.operation_id}: {exc}")
                return self._reply(op, problem(422, "validation_failed", detail=str(exc)[:500]))
        req = FakeRequest(method, path, path_params, query, headers, payload)
        key = headers.get("idempotency-key")
        fp = json.dumps([method, path, payload], sort_keys=True)
        if key and key in self.idempotency:
            old_fp, old = self.idempotency[key]
            if old_fp != fp:
                self.violations.append(
                    f"{self.name} {op.operation_id}: Idempotency-Key reused with another body"
                )
                return self._reply(op, problem(422, "idempotency_key_reused"))
            self.calls.append((str(op.operation_id), req, old.status))
            return self._reply(op, old, replayed=True)
        handler = self.handlers.get(str(op.operation_id))
        if handler is None:
            self.violations.append(f"{self.name}: no fake for {op.operation_id} (unexpected call)")
            return self._reply(op, problem(501, "not_implemented"))
        result = handler(req)
        reply = await result if isinstance(result, Awaitable) else result
        if key and reply.status < 500:
            self.idempotency[key] = (fp, reply)
        self.calls.append((str(op.operation_id), req, reply.status))
        return self._reply(op, reply)

    def _reply(self, op: Any, reply: Reply, replayed: bool = False) -> Response:
        if reply.raw is None:
            try:
                self.spec.validate_response(op.method, op.path, reply.status, reply.body, reply.media_type)
            except ContractViolation as exc:
                self.violations.append(f"{self.name} response {op.operation_id}: {exc}")
        headers = dict(reply.headers)
        if replayed:
            headers["Idempotency-Replayed"] = "true"
        if reply.raw is not None:
            return Response(reply.raw, status_code=reply.status, headers=headers, media_type=reply.media_type)
        if reply.body is None:
            return Response(status_code=reply.status, headers=headers)
        return JSONResponse(
            reply.body, status_code=reply.status, headers=headers, media_type=reply.media_type
        )
