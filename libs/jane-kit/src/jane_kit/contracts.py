"""Contract helpers over the OpenAPI 3.1 documents in ``contracts/openapi/`` (WP-00).

* :class:`OpenAPISpec` - load a spec (YAML/JSON) with cross-file ``$ref`` (``common.yaml``,
  ``../schemas/*.schema.json``, ``../examples/*``), list operations (including ``$ref``'d path items),
  validate requests/responses (schemas are JSON Schema 2020-12).
* :class:`ContractClient` - wraps an httpx client (e.g. FastAPI ``TestClient``) and validates every
  response of the real service against the spec. Basis of ``@pytest.mark.contract`` tests.
* :func:`build_mock_app` - an ASGI mock of a neighbour service generated from its spec: first example
  of the first 2xx response; ``Prefer: code=404`` / ``Prefer: example=<name>`` select another (same
  convention as ``contracts/tools/mock.py`` and Prism); invalid request bodies get 422.
* :func:`find_specs` - service specs under ``contracts/openapi`` (documents with ``paths``).
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from functools import cached_property, lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urljoin, urlsplit

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
    "Loc",
    "OpenAPISpec",
    "Operation",
    "build_mock_app",
    "contracts_dir",
    "example_from_schema",
    "find_specs",
]

HTTP_METHODS = ("get", "put", "post", "delete", "options", "head", "patch", "trace")

# Tooling constants of this test/dev helper (not operational limits of a service):
SPEC_CACHE_FILES = 256  # parsed contract files kept in memory
MAX_REF_CHAIN = 32  # $ref -> $ref hops before reporting a cycle
MAX_EXAMPLE_DEPTH = 12  # nesting depth when synthesising an example from a schema
MAX_REPORTED_ERRORS = 10  # validation errors shown in one ContractViolation


class ContractViolation(AssertionError):
    """The request or response does not match the contract."""


@lru_cache(maxsize=SPEC_CACHE_FILES)
def _load_cached(path: str, mtime_ns: int) -> Any:
    text = Path(path).read_text(encoding="utf-8")
    return json.loads(text) if path.lower().endswith(".json") else yaml.safe_load(text)


def _load_file(path: Path) -> Any:
    return _load_cached(str(path), path.stat().st_mtime_ns)


def _uri_to_path(uri: str) -> Path:
    parts = urlsplit(uri)
    if parts.scheme != "file":
        raise ValueError(f"only local $ref files are allowed in contracts, got {uri}")
    raw = unquote(parts.path)
    return Path(raw.lstrip("/") if re.match(r"^/[A-Za-z]:", raw) else raw)


def _escape(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


@dataclass(frozen=True)
class Loc:
    """A node of a contract document together with where it lives (for correct relative ``$ref``)."""

    uri: str
    pointer: str
    node: Any = field(compare=False, repr=False)

    @property
    def ref(self) -> str:
        return f"{self.uri}#{self.pointer}"

    def child(self, *tokens: str | int) -> Loc:
        node, pointer = self.node, self.pointer
        for t in tokens:
            node = node[t]
            pointer += "/" + _escape(str(t))
        return Loc(self.uri, pointer, node)


@dataclass(frozen=True)
class Operation:
    method: str
    path: str
    operation_id: str | None
    loc: Loc
    parameters: tuple[Mapping[str, Any], ...] = ()

    @property
    def spec(self) -> Mapping[str, Any]:
        node: Mapping[str, Any] = self.loc.node
        return node

    @cached_property
    def regex(self) -> re.Pattern[str]:
        parts = re.split(r"(\{[^}/]+\})", self.path)
        pattern = "".join("[^/]+" if p.startswith("{") else re.escape(p) for p in parts)
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
        resource: Resource[Any] = DRAFT202012.create_resource(_load_file(_uri_to_path(uri)))
        return resource

    # ------------------------------------------------------------------ navigation
    def root(self) -> Loc:
        return Loc(self.base_uri, "", self.document)

    def lookup(self, uri: str) -> Loc:
        doc, _, fragment = uri.partition("#")
        contents = self.registry.resolver().lookup(f"{doc}#{fragment}").contents
        return Loc(doc, fragment, contents)

    def follow(self, loc: Loc) -> Loc:
        """Follow ``$ref`` chains of non-schema objects (path items, responses, examples...)."""
        for _ in range(MAX_REF_CHAIN):
            if not (isinstance(loc.node, Mapping) and "$ref" in loc.node):
                return loc
            loc = self.lookup(urljoin(loc.uri, str(loc.node["$ref"])))
        raise ValueError(f"$ref cycle at {loc.ref}")

    def resolve(self, node: Any) -> Any:
        """Follow ``$ref`` for a node that lives in the root document."""
        return self.follow(Loc(self.base_uri, "", node)).node

    @cached_property
    def operations(self) -> list[Operation]:
        ops = []
        paths = self.root().child("paths") if self.document.get("paths") else None
        for path in paths.node if paths else {}:
            assert paths is not None
            item = self.follow(paths.child(path))
            shared = [
                self.follow(item.child("parameters", i)).node
                for i in range(len(item.node.get("parameters", [])))
            ]
            for method in HTTP_METHODS:
                if method not in item.node:
                    continue
                op = item.child(method)
                own = [
                    self.follow(op.child("parameters", i)).node
                    for i in range(len(op.node.get("parameters", [])))
                ]
                names = {(p.get("in"), p.get("name")) for p in own}
                params = tuple(own + [p for p in shared if (p.get("in"), p.get("name")) not in names])
                ops.append(Operation(method.upper(), path, op.node.get("operationId"), op, params))
        return ops

    @cached_property
    def _server_prefix(self) -> str:
        servers = self.document.get("servers") or []
        if servers:
            path = urlsplit(str(servers[0].get("url", ""))).path.rstrip("/")
            if path and "{" not in path:
                return path
        return ""

    def operation(self, method: str, path: str) -> Operation:
        """Find the operation for a concrete path (``/v1/jobs/abc``) or a template."""
        path = path.split("?", 1)[0]
        method = method.upper()
        if self._server_prefix and path.startswith(self._server_prefix):
            path = path[len(self._server_prefix) :] or "/"
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

    # ------------------------------------------------------------------ validation
    def validate_at(self, schema_uri: str, instance: Any, what: str = "instance") -> None:
        """Validate ``instance`` against the schema at ``schema_uri`` (``<doc>#<pointer>``)."""
        validator = Draft202012Validator({"$ref": schema_uri}, registry=self.registry)
        errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
        if errors:
            lines = [
                f"- at /{'/'.join(map(str, e.absolute_path))}: {e.message}"
                for e in errors[:MAX_REPORTED_ERRORS]
            ]
            raise ContractViolation(f"{what} does not match the contract:\n" + "\n".join(lines))

    def validate_component(self, name: str, instance: Any) -> None:
        """Validate against ``#/components/schemas/<name>`` of this document."""
        self.validate_at(f"{self.base_uri}#/components/schemas/{_escape(name)}", instance, name)

    def response(self, op: Operation, status: int) -> Loc:
        responses = op.spec.get("responses") or {}
        for key in (str(status), f"{str(status)[0]}XX", f"{str(status)[0]}xx", "default"):
            if key in responses:
                return self.follow(op.loc.child("responses", key))
        raise ContractViolation(
            f"{op.method} {op.path}: status {status} is not documented (have {sorted(responses)})"
        )

    def validate_response(
        self, method: str, path: str, status: int, body: Any, content_type: str | None = "application/json"
    ) -> Operation:
        op = self.operation(method, path)
        resp = self.response(op, status)
        content = resp.node.get("content") or {}
        if not content:
            return op
        media = (content_type or "").split(";", 1)[0].strip()
        if media not in content:
            raise ContractViolation(
                f"{op.method} {op.path} {status}: content type {media!r} not in contract {sorted(content)}"
            )
        if "schema" in content[media]:
            self.validate_at(
                resp.child("content", media, "schema").ref, body, f"{op.method} {op.path} {status} response"
            )
        return op

    def validate_request(
        self, method: str, path: str, body: Any, content_type: str = "application/json"
    ) -> Operation:
        op = self.operation(method, path)
        if op.spec.get("requestBody") is None:
            return op
        rb = self.follow(op.loc.child("requestBody"))
        content = rb.node.get("content") or {}
        media = content_type.split(";", 1)[0].strip()
        if media not in content:
            raise ContractViolation(f"{op.method} {op.path}: request content type {media!r} not allowed")
        if "schema" in content[media]:
            self.validate_at(rb.child("content", media, "schema").ref, body, f"{op.method} {op.path} request")
        return op


def contracts_dir(start: Path | None = None) -> Path | None:
    """``contracts/`` of this checkout: env ``JANE_CONTRACTS_DIR``, else ``<checkout root>/contracts``.

    The search stops at the checkout root (nearest ancestor with ``.git``), so a git worktree nested
    inside another checkout never picks up that checkout's contracts.
    """
    if env := os.environ.get("JANE_CONTRACTS_DIR"):
        return Path(env) if Path(env).is_dir() else None
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "contracts" / "openapi").is_dir():
            return candidate / "contracts"
        if (candidate / ".git").exists():
            return None
    return None


def find_specs(contracts_dir: str | Path) -> Iterator[Path]:
    """OpenAPI documents that describe a service (have ``paths``), e.g. ``contracts/openapi/*.v1.yaml``."""
    root = Path(contracts_dir)
    if not root.is_dir():
        return
    for p in sorted(root.rglob("*")):
        if not (p.is_file() and p.suffix.lower() in {".yaml", ".yml", ".json"}):
            continue
        try:
            doc = _load_file(p)
        except (ValueError, yaml.YAMLError):
            continue
        if isinstance(doc, dict) and "openapi" in doc and doc.get("paths"):
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
_FORMATS = {
    "date-time": "2026-01-01T00:00:00Z",
    "uuid": "00000000-0000-0000-0000-000000000000",
    "uri": "https://example.org/",
    "uri-reference": "/",
    "date": "2026-01-01",
}


def example_from_schema(spec: OpenAPISpec, schema: Loc | Mapping[str, Any], depth: int = 0) -> Any:
    """Deterministic minimal instance of a schema (examples > default > const > enum > type)."""
    loc = schema if isinstance(schema, Loc) else Loc(spec.base_uri, "", schema)
    loc = spec.follow(loc)
    s = loc.node
    if not isinstance(s, Mapping) or depth > MAX_EXAMPLE_DEPTH:
        return None
    if s.get("examples"):
        return s["examples"][0]
    for key in ("example", "default", "const"):
        if key in s:
            return s[key]
    if s.get("enum"):
        return s["enum"][0]
    if s.get("allOf"):
        merged: dict[str, Any] = {}
        for i in range(len(s["allOf"])):
            val = example_from_schema(spec, loc.child("allOf", i), depth + 1)
            if isinstance(val, dict):
                merged.update(val)
        return merged
    for key in ("oneOf", "anyOf"):
        if s.get(key):
            return example_from_schema(spec, loc.child(key, 0), depth + 1)
    typ = s.get("type")
    if isinstance(typ, list):
        typ = next((t for t in typ if t != "null"), "null")
    if typ == "object" or "properties" in s:
        props = s.get("properties") or {}
        required = s.get("required") or list(props)
        return {
            k: example_from_schema(spec, loc.child("properties", k), depth + 1)
            for k in required
            if k in props
        }
    if typ == "array":
        item = example_from_schema(spec, loc.child("items"), depth + 1) if "items" in s else None
        return [item] * max(1, int(s.get("minItems", 1) or 0))
    if typ == "string":
        return _FORMATS.get(s.get("format") or "", "string")
    if typ == "integer":
        return int(s.get("minimum", 0))
    if typ == "number":
        return float(s.get("minimum", 0))
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


def _problem(status: int, code: str, detail: str) -> JSONResponse:
    return JSONResponse(
        {
            "type": f"urn:jane:problem:{code}",
            "title": code.replace("_", " ").capitalize(),
            "status": status,
            "code": code,
            "retryable": False,
            "detail": detail,
        },
        status_code=status,
        media_type="application/problem+json",
    )


def build_mock_app(spec: OpenAPISpec) -> Starlette:
    """ASGI mock of a service from its contract (see module docstring)."""

    def make_endpoint(op: Operation) -> Any:
        async def endpoint(request: Request) -> Response:
            prefer = _prefer(request.headers.get("prefer"))
            if op.spec.get("requestBody") and request.headers.get("content-type", "").startswith(
                "application/json"
            ):
                raw = await request.body()
                try:
                    payload = json.loads(raw) if raw else None
                except ValueError:
                    return _problem(400, "bad_request", "request body is not valid JSON")
                try:
                    spec.validate_request(op.method, op.path, payload)
                except ContractViolation as exc:
                    return _problem(422, "validation_failed", str(exc))
            responses = op.spec.get("responses") or {}
            wanted = prefer.get("code")
            status_key: str = (
                wanted
                if wanted is not None and wanted in responses
                else next((k for k in responses if k.startswith("2")), next(iter(responses), "200"))
            )
            status = int(status_key) if status_key.isdigit() else (int(wanted) if wanted else 200)
            if status_key not in responses:
                return Response(status_code=status)
            resp = spec.follow(op.loc.child("responses", status_key))
            content = resp.node.get("content") or {}
            if not content:
                return Response(status_code=status)
            media = next(iter(content))
            media_loc = resp.child("content", media)
            examples = media_loc.node.get("examples") or {}
            name = prefer.get("example")
            if name is not None and name in examples:
                body = spec.follow(media_loc.child("examples", name)).node.get("value")
            elif "example" in media_loc.node:
                body = media_loc.node["example"]
            elif examples:
                body = spec.follow(media_loc.child("examples", next(iter(examples)))).node.get("value")
            elif "schema" in media_loc.node:
                body = example_from_schema(spec, media_loc.child("schema"))
            else:
                body = None
            return JSONResponse(body, status_code=status, media_type=media)

        return endpoint

    routes = [
        Route(spec._server_prefix + op.path, make_endpoint(op), methods=[op.method]) for op in spec.operations
    ]
    return Starlette(routes=routes)
