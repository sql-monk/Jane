"""Contract helpers over OpenAPI 3.1 documents in ``contracts/``.

* :class:`OpenAPISpec` - load a spec (YAML/JSON, local and cross-file ``$ref``), list operations,
  validate requests/responses (schemas are JSON Schema 2020-12).
* :class:`ContractClient` - wraps an httpx client (e.g. FastAPI ``TestClient``) and validates every
  response of the real service against the spec. Basis of ``@pytest.mark.contract`` tests.
* :func:`build_mock_app` - an ASGI mock of a neighbour service generated from its spec
  (examples from the spec, request validation, ``Prefer: code=...`` to pick a response).

CONNECTION POINT (WP-00): which files are specs and where they live is defined by ``contracts/``;
:func:`find_specs` discovers ``openapi*.yaml|yml|json`` files there.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

import httpx
import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

__all__ = [
    "ContractClient",
    "ContractViolation",
    "OpenAPISpec",
    "Operation",
    "build_mock_app",
    "example_from_schema",
    "find_specs",
]

HTTP_METHODS = ("get", "put", "post", "delete", "options", "head", "patch", "trace")


class ContractViolation(AssertionError):
    """The request or response does not match the contract."""


def _load_file(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    return json.loads(text) if path.suffix.lower() == ".json" else yaml.safe_load(text)


def _escape(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


@dataclass(frozen=True)
class Operation:
    method: str
    path: str
    operation_id: str | None
    spec: Mapping[str, Any]
    pointer: str  # JSON pointer of the operation object inside the root document

    @cached_property
    def regex(self) -> re.Pattern[str]:
        parts = re.split(r"(\{[^}/]+\})", self.path)
        pattern = "".join(
            f"(?P<{p[1:-1].replace('-', '_')}>[^/]+)" if p.startswith("{") else re.escape(p) for p in parts
        )
        return re.compile(f"^{pattern}$")

    @property
    def literal_weight(self) -> int:
        return len(re.sub(r"\{[^}]+\}", "", self.path))


class OpenAPISpec:
    def __init__(self, document: Mapping[str, Any], base_uri: str) -> None:
        if not str(document.get("openapi", "")).startswith("3.1"):
            raise ValueError(f"{base_uri}: only OpenAPI 3.1 is supported (JSON Schema 2020-12)")
        self.document = document
        self.base_uri = base_uri
        root: Resource[Any] = DRAFT202012.create_resource(document)
        registry: Registry[Any] = Registry(retrieve=self._retrieve)  # type: ignore[call-arg]
        self.registry = registry.with_resource(base_uri, root)

    @classmethod
    def load(cls, path: str | Path) -> OpenAPISpec:
        p = Path(path).resolve()
        return cls(_load_file(p), p.as_uri())

    @staticmethod
    def _retrieve(uri: str) -> Resource[Any]:
        parts = urlsplit(uri)
        if parts.scheme != "file":
            raise ValueError(f"only local $ref files are allowed in contracts, got {uri}")
        local = Path(unquote(parts.path.lstrip("/") if re.match(r"^/[A-Za-z]:", parts.path) else parts.path))
        resource: Resource[Any] = DRAFT202012.create_resource(_load_file(local))
        return resource

    # ------------------------------------------------------------------ navigation
    def resolve(self, node: Any) -> Any:
        """Follow a (non-schema) ``$ref`` such as ``#/components/responses/NotFound``."""
        seen = 0
        while isinstance(node, Mapping) and "$ref" in node:
            resolved = self.registry.resolver(self.base_uri).lookup(node["$ref"])
            node = resolved.contents
            seen += 1
            if seen > 32:
                raise ValueError("$ref cycle")
        return node

    @cached_property
    def operations(self) -> list[Operation]:
        ops = []
        for path, item in (self.document.get("paths") or {}).items():
            item = self.resolve(item)
            for method in HTTP_METHODS:
                if method in item:
                    op = item[method]
                    ops.append(
                        Operation(
                            method.upper(),
                            path,
                            op.get("operationId"),
                            op,
                            f"#/paths/{_escape(path)}/{method}",
                        )
                    )
        return ops

    def operation(self, method: str, path: str) -> Operation:
        """Find the operation for a concrete path (``/v1/jobs/abc``) or a template."""
        path = path.split("?", 1)[0]
        method = method.upper()
        server_prefix = self._server_prefix
        if server_prefix and path.startswith(server_prefix):
            path = path[len(server_prefix) :] or "/"
        candidates = [
            o for o in self.operations if o.method == method and (o.path == path or o.regex.match(path))
        ]
        if not candidates:
            raise ContractViolation(f"{method} {path} is not described in the contract {self.base_uri}")
        return max(candidates, key=lambda o: o.literal_weight)

    def by_id(self, operation_id: str) -> Operation:
        for op in self.operations:
            if op.operation_id == operation_id:
                return op
        raise KeyError(operation_id)

    @cached_property
    def _server_prefix(self) -> str:
        servers = self.document.get("servers") or []
        if servers:
            path = urlsplit(str(servers[0].get("url", ""))).path.rstrip("/")
            if path and "{" not in path:
                return path
        return ""

    # ------------------------------------------------------------------ validation
    def _validate(self, pointer: str, instance: Any, what: str) -> None:
        validator = Draft202012Validator({"$ref": self.base_uri + pointer}, registry=self.registry)
        errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
        if errors:
            lines = [f"- at /{'/'.join(map(str, e.absolute_path))}: {e.message}" for e in errors[:10]]
            raise ContractViolation(f"{what} does not match the contract:\n" + "\n".join(lines))

    def response_spec(self, op: Operation, status: int) -> tuple[str, Mapping[str, Any]]:
        responses = op.spec.get("responses") or {}
        for key in (str(status), f"{str(status)[0]}XX", f"{str(status)[0]}xx", "default"):
            if key in responses:
                return f"{op.pointer}/responses/{_escape(key)}", responses[key]
        raise ContractViolation(
            f"{op.method} {op.path}: status {status} is not documented (have {sorted(responses)})"
        )

    def validate_response(
        self, method: str, path: str, status: int, body: Any, content_type: str | None = "application/json"
    ) -> Operation:
        op = self.operation(method, path)
        pointer, resp = self.response_spec(op, status)
        if "$ref" in resp:
            ref = resp["$ref"]
            resp = self.resolve(resp)
            pointer = ref if ref.startswith("#") else pointer
        content = resp.get("content") or {}
        if not content:
            return op
        media = (content_type or "").split(";", 1)[0].strip()
        if media not in content:
            raise ContractViolation(
                f"{op.method} {op.path} {status}: content type {media!r} not in contract {sorted(content)}"
            )
        if "schema" in content[media]:
            ptr = (pointer if pointer.startswith("#") else "") + f"/content/{_escape(media)}/schema"
            self._validate(ptr, body, f"{op.method} {op.path} {status} response")
        return op

    def validate_request(
        self, method: str, path: str, body: Any, content_type: str = "application/json"
    ) -> Operation:
        op = self.operation(method, path)
        rb = op.spec.get("requestBody")
        if rb is None:
            return op
        pointer = f"{op.pointer}/requestBody"
        if "$ref" in rb:
            pointer = rb["$ref"]
            rb = self.resolve(rb)
        content = rb.get("content") or {}
        media = content_type.split(";", 1)[0].strip()
        if media not in content:
            raise ContractViolation(f"{op.method} {op.path}: request content type {media!r} not allowed")
        if "schema" in content[media]:
            self._validate(
                f"{pointer}/content/{_escape(media)}/schema", body, f"{op.method} {op.path} request"
            )
        return op

    def schema_at(self, pointer: str) -> Any:
        return self.registry.resolver(self.base_uri).lookup(self.base_uri + pointer).contents


def find_specs(contracts_dir: str | Path) -> Iterator[Path]:
    root = Path(contracts_dir)
    if not root.is_dir():
        return
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in {".yaml", ".yml", ".json"} and p.stem.startswith("openapi"):
            yield p


class ContractClient:
    """Validates every response of a real service against its contract.

    ``ContractClient(spec, TestClient(app)).get("/v1/jobs/1")`` returns the httpx response or raises
    :class:`ContractViolation`.
    """

    def __init__(self, spec: OpenAPISpec, client: httpx.Client) -> None:
        self.spec = spec
        self.client = client
        self.seen: set[tuple[str, str, int]] = set()

    def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        if "json" in kwargs:
            self.spec.validate_request(method, url, kwargs["json"])
        response = self.client.request(method, url, **kwargs)
        body: Any = None
        if response.content:
            try:
                body = response.json()
            except ValueError:
                body = response.text
        op = self.spec.validate_response(
            method, urlsplit(url).path, response.status_code, body, response.headers.get("content-type")
        )
        self.seen.add((op.method, op.path, response.status_code))
        return response

    def get(self, url: str, **kw: Any) -> httpx.Response:
        return self.request("GET", url, **kw)

    def post(self, url: str, **kw: Any) -> httpx.Response:
        return self.request("POST", url, **kw)

    def put(self, url: str, **kw: Any) -> httpx.Response:
        return self.request("PUT", url, **kw)

    def patch(self, url: str, **kw: Any) -> httpx.Response:
        return self.request("PATCH", url, **kw)

    def delete(self, url: str, **kw: Any) -> httpx.Response:
        return self.request("DELETE", url, **kw)

    def uncovered(self) -> list[str]:
        """Operations never called through this client (coverage hint for contract tests)."""
        called = {(m, p) for m, p, _ in self.seen}
        return [f"{o.method} {o.path}" for o in self.spec.operations if (o.method, o.path) not in called]


# ---------------------------------------------------------------------- examples and mocks
def example_from_schema(spec: OpenAPISpec, schema: Any, depth: int = 0) -> Any:
    """Deterministic minimal instance of ``schema`` (examples > default > const > enum > type)."""
    schema = spec.resolve(schema) if isinstance(schema, Mapping) else schema
    if not isinstance(schema, Mapping) or depth > 12:
        return None
    for key in ("examples",):
        if schema.get(key):
            return schema[key][0]
    for key in ("example", "default", "const"):
        if key in schema:
            return schema[key]
    if schema.get("enum"):
        return schema["enum"][0]
    for key in ("allOf",):
        if schema.get(key):
            merged: dict[str, Any] = {}
            for sub in schema[key]:
                val = example_from_schema(spec, sub, depth + 1)
                if isinstance(val, dict):
                    merged.update(val)
            return merged
    for key in ("oneOf", "anyOf"):
        if schema.get(key):
            return example_from_schema(spec, schema[key][0], depth + 1)
    typ = schema.get("type")
    if isinstance(typ, list):
        typ = next((t for t in typ if t != "null"), "null")
    if typ == "object" or "properties" in schema:
        props = schema.get("properties") or {}
        required = schema.get("required") or list(props)
        return {k: example_from_schema(spec, props[k], depth + 1) for k in required if k in props}
    if typ == "array":
        item = example_from_schema(spec, schema.get("items", {}), depth + 1)
        return [item] * int(schema.get("minItems", 1) or 0)
    if typ == "string":
        fmt = schema.get("format")
        return {
            "date-time": "2026-01-01T00:00:00Z",
            "uuid": "00000000-0000-0000-0000-000000000000",
            "uri": "https://example.org/",
            "date": "2026-01-01",
        }.get(fmt or "", "string")
    if typ == "integer":
        return int(schema.get("minimum", 0))
    if typ == "number":
        return float(schema.get("minimum", 0))
    if typ == "boolean":
        return False
    return None


def _prefer(header: str | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for part in (header or "").replace(",", ";").split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip().lower()] = v.strip().strip('"')
    return out


def build_mock_app(spec: OpenAPISpec) -> Starlette:
    """ASGI mock of a service from its contract.

    Returns the first documented 2xx response by default; ``Prefer: code=404`` or
    ``Prefer: example=<name>`` selects another. Invalid JSON bodies get a 422 problem.
    """

    def make_endpoint(op: Operation) -> Any:
        async def endpoint(request: Request) -> Response:
            prefer = _prefer(request.headers.get("prefer"))
            if op.spec.get("requestBody") and request.headers.get("content-type", "").startswith(
                "application/json"
            ):
                raw = await request.body()
                try:
                    op_body = json.loads(raw) if raw else None
                    spec.validate_request(op.method, op.path, op_body)
                except (ValueError, ContractViolation) as exc:
                    return JSONResponse(
                        {
                            "type": "urn:jane:problem:validation_failed",
                            "title": "Validation failed",
                            "status": 422,
                            "code": "validation_failed",
                            "detail": str(exc),
                        },
                        status_code=422,
                        media_type="application/problem+json",
                    )
            responses = op.spec.get("responses") or {}
            wanted = prefer.get("code")
            status_key: str = (
                wanted
                if wanted is not None and wanted in responses
                else next((k for k in responses if k.startswith("2")), next(iter(responses), "200"))
            )
            resp = spec.resolve(responses.get(status_key, {}))
            status = int(status_key) if status_key.isdigit() else (int(wanted) if wanted else 200)
            content = resp.get("content") or {}
            if not content:
                return Response(status_code=status)
            media, media_obj = next(iter(content.items()))
            examples = media_obj.get("examples") or {}
            if prefer.get("example") in examples:
                body = spec.resolve(examples[prefer["example"]]).get("value")
            elif "example" in media_obj:
                body = media_obj["example"]
            elif examples:
                body = spec.resolve(next(iter(examples.values()))).get("value")
            else:
                body = example_from_schema(spec, media_obj.get("schema", {}))
            return JSONResponse(body, status_code=status, media_type=media)

        return endpoint

    prefix = spec._server_prefix
    routes = [Route(prefix + op.path, make_endpoint(op), methods=[op.method]) for op in spec.operations]
    return Starlette(routes=routes)
