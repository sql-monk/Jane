"""Shared helpers for contract tools: loading files, a referencing registry, $ref resolution.

Stdlib + PyYAML + referencing only. Imported by check_contracts.py, mock.py and compat.py
(they add this directory to sys.path).
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urldefrag, urlparse
from urllib.request import url2pathname

import yaml

CONTRACTS_DIR = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = CONTRACTS_DIR / "schemas"
OPENAPI_DIR = CONTRACTS_DIR / "openapi"
EXAMPLES_DIR = CONTRACTS_DIR / "examples"
API_NAMES = ("collector", "handler", "storage", "registry", "orchestrator", "llm", "assistant")


class _NoDatesLoader(yaml.SafeLoader):
    """SafeLoader that keeps timestamps as strings (JSON semantics)."""


for _ch, _resolvers in list(_NoDatesLoader.yaml_implicit_resolvers.items()):
    _NoDatesLoader.yaml_implicit_resolvers[_ch] = [
        (tag, rx) for tag, rx in _resolvers if tag != "tag:yaml.org,2002:timestamp"
    ]


def load_file(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix in (".yaml", ".yml"):
        return yaml.load(text, Loader=_NoDatesLoader)  # noqa: S506 - SafeLoader subclass
    return json.loads(text)


def uri_to_path(uri: str) -> Path:
    parsed = urlparse(uri)
    if parsed.scheme != "file":
        raise ValueError(f"only file:// references are supported, got {uri!r}")
    return Path(url2pathname(unquote(parsed.path)))


@lru_cache(maxsize=None)
def load_uri(uri: str) -> Any:
    return load_file(uri_to_path(urldefrag(uri)[0]))


def pointer_get(doc: Any, pointer: str) -> Any:
    if pointer in ("", "/"):
        return doc
    node = doc
    for raw in pointer.lstrip("/").split("/"):
        part = unquote(raw).replace("~1", "/").replace("~0", "~")
        if isinstance(node, list):
            node = node[int(part)]
        else:
            node = node[part]
    return node


def pointer_escape(part: str) -> str:
    return part.replace("~", "~0").replace("/", "~1")


def resolve_ref(ref: str, base_uri: str) -> tuple[Any, str]:
    """Resolve a $ref relative to base_uri. Returns (node, absolute uri with fragment)."""
    from urllib.parse import urljoin

    absolute = urljoin(base_uri, ref)
    doc_uri, fragment = urldefrag(absolute)
    return pointer_get(load_uri(doc_uri), fragment), f"{doc_uri}#{fragment}"


def deref(node: Any, base_uri: str, max_depth: int = 32) -> tuple[Any, str]:
    """Follow a chain of Reference Objects ({"$ref": ...}) until a non-reference node."""
    uri = base_uri
    for _ in range(max_depth):
        if isinstance(node, dict) and "$ref" in node and len(node) <= 3 and set(node) <= {"$ref", "summary", "description"}:
            node, uri = resolve_ref(node["$ref"], uri)
        else:
            return node, uri
    raise RecursionError(f"too many nested $ref starting at {base_uri}")


def build_registry():
    """referencing.Registry with every schema/OpenAPI file, plus lazy retrieval of other file:// URIs."""
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012

    def retrieve(uri: str) -> Resource:
        return Resource.from_contents(load_uri(uri), default_specification=DRAFT202012)

    resources = []
    for path in sorted(SCHEMAS_DIR.rglob("*.json")) + sorted(OPENAPI_DIR.glob("*.yaml")):
        resources.append((path.as_uri(), Resource.from_contents(load_file(path), default_specification=DRAFT202012)))
    return Registry(retrieve=retrieve).with_resources(resources)


def openapi_files() -> list[Path]:
    return sorted(OPENAPI_DIR.glob("*.v1.yaml"))


HTTP_METHODS = ("get", "put", "post", "delete", "patch", "head", "options", "trace")


def iter_operations(doc: Any, doc_uri: str):
    """Yield (path, method, operation, operation_base_uri, path_item_base_uri)."""
    for path, item in (doc.get("paths") or {}).items():
        item_node, item_uri = deref(item, doc_uri)
        for method in HTTP_METHODS:
            if method in item_node:
                yield path, method, item_node[method], item_uri, item_node
