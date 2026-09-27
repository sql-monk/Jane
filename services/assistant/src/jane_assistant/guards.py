"""Guards against untrusted model output (ТЗ §11: source content is data, not instructions).

The model may be steered by a prompt injection inside a page. Whatever it answers is therefore
checked before it can take effect:

* collector rules: only known discovery strategies, URLs and patterns inside the source's hosts
  (the selected candidate plus domains the *user* allowed in ``crawl_hints``), ``robots`` always
  ``respect``, no ``llm_explore`` (ADR-0010), no per-rule limits (limits come from configuration);
  then JSON Schema (``collector-rules.schema.json``) and the collector's own ``validateRules``;
* generated code: parses, defines the entry callable, imports only allowed modules, calls no
  dangerous builtins (the runtime sandbox of WP-06 is the real barrier; this is an early reject);
* manifests: ``package-manifest.schema.json`` before publishing.
"""

from __future__ import annotations

import ast
import json
from collections.abc import Iterable
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from jane_kit.contracts import contracts_dir as find_contracts_dir

__all__ = [
    "ALLOWED_STRATEGIES",
    "CodeCheck",
    "RulesCheck",
    "SchemaValidator",
    "check_code",
    "sanitize_web_rules",
]

ALLOWED_STRATEGIES: dict[str, set[str]] = {
    # type -> properties kept from model output (see collector-rules.schema.json)
    "seed_list": {"urls", "section", "priority", "strategy_id"},
    "recursive": {"seeds", "follow", "link_sources", "section", "priority", "strategy_id"},
    "sitemap": {"urls", "use_robots_txt", "section", "priority", "strategy_id"},
    "feed": {"urls", "autodiscover", "section", "priority", "strategy_id"},
    "listing": {
        "start_urls",
        "item_links",
        "next_page",
        "page_param",
        "search",
        "section",
        "priority",
        "strategy_id",
    },
    "url_template": {
        "template",
        "variables",
        "stop_after_consecutive_misses",
        "section",
        "priority",
        "strategy_id",
    },
    "api_feed": {
        "url",
        "items_path",
        "url_path",
        "lastmod_path",
        "pagination",
        "section",
        "priority",
        "strategy_id",
    },
}
_REQUIRED_URLS = {"seed_list": "urls", "listing": "start_urls", "api_feed": "url", "url_template": "template"}
DANGEROUS_CALLS = frozenset(
    {"eval", "exec", "compile", "__import__", "open", "input", "breakpoint", "globals", "vars"}
)


def _host_allowed(host: str | None, allowed: Iterable[str]) -> bool:
    if not host:
        return False
    host = host.lower()
    return any(host == a or host.endswith("." + a) for a in allowed)


def _url_allowed(url: Any, allowed: Iterable[str]) -> bool:
    if not isinstance(url, str):
        return False
    parts = urlsplit(url.replace("{", "").replace("}", ""))
    return parts.scheme in {"http", "https"} and _host_allowed(parts.hostname, allowed)


def _glob_allowed(pattern: Any, allowed: Iterable[str]) -> bool:
    if not isinstance(pattern, str) or not pattern:
        return False
    host = pattern.split("/", 1)[0]
    return "*" not in host and _host_allowed(host, allowed)


@dataclass
class RulesCheck:
    rules: dict[str, Any] | None
    rejected: list[str] = field(default_factory=list)


def sanitize_web_rules(
    proposal: dict[str, Any], allowed_domains: list[str], hints: dict[str, Any] | None = None
) -> RulesCheck:
    """Build ``WebRules`` from a model proposal keeping only what stays inside ``allowed_domains``."""
    rejected: list[str] = []
    strategies: list[dict[str, Any]] = []
    for raw in proposal.get("strategies") or []:
        if not isinstance(raw, dict):
            continue
        kind = raw.get("type")
        if kind not in ALLOWED_STRATEGIES:
            rejected.append(f"strategy {kind!r} is not allowed")
            continue
        s: dict[str, Any] = {"type": kind}
        for key in ALLOWED_STRATEGIES[kind]:
            if key in raw:
                s[key] = raw[key]
        for key in ("urls", "seeds", "start_urls"):
            if key in s:
                urls = (
                    [u for u in s[key] if _url_allowed(u, allowed_domains)]
                    if isinstance(s[key], list)
                    else []
                )
                dropped = len(s[key]) - len(urls) if isinstance(s[key], list) else 1
                if dropped:
                    rejected.append(f"{kind}.{key}: {dropped} URL(s) outside {allowed_domains}")
                if urls:
                    s[key] = urls
                else:
                    del s[key]
        for key in ("url", "template"):
            if key in s and not _url_allowed(s[key], allowed_domains):
                rejected.append(f"{kind}.{key}: URL outside {allowed_domains}")
                del s[key]
        if (
            kind == "listing"
            and isinstance(s.get("search"), dict)
            and not _url_allowed(s["search"].get("url_template"), allowed_domains)
        ):
            rejected.append("listing.search: URL outside the source")
            del s["search"]
        if kind == "recursive" and "follow" in s:
            s["follow"] = [
                {"type": "glob", "value": p}
                for p in (s["follow"] if isinstance(s["follow"], list) else [])
                if _glob_allowed(p if isinstance(p, str) else (p or {}).get("value"), allowed_domains)
            ] or None
            if s["follow"] is None:
                del s["follow"]
        need = _REQUIRED_URLS.get(kind)
        if need and need not in s:
            rejected.append(f"strategy {kind} dropped: no URL inside the source")
            continue
        strategies.append(s)
    if not strategies:
        return RulesCheck(None, [*rejected, "no usable strategy left"])

    scope: dict[str, Any] = {"allowed_domains": sorted(set(allowed_domains))}
    hint_scope = (hints or {}).get("scope") or {}
    for key in ("include_subdomains", "path_prefixes", "allowed_schemes", "include"):
        if key in hint_scope:
            scope[key] = hint_scope[key]
    exclude = [
        {"type": "glob", "value": p}
        for p in proposal.get("exclude") or []
        if isinstance(p, str) and _glob_allowed(p, allowed_domains)
    ]
    exclude += list(hint_scope.get("exclude") or [])
    if exclude:
        scope["exclude"] = exclude
    rules: dict[str, Any] = {
        "collector": "web",
        "scope": scope,
        "strategies": strategies,
        "robots": {"mode": "respect"},
    }
    sections = []
    for sec in proposal.get("sections") or []:
        patterns = [p for p in sec.get("patterns") or [] if _glob_allowed(p, allowed_domains)]
        sid = str(sec.get("section_id", "")).lower()
        if patterns and sid:
            sections.append({"section_id": sid, "patterns": [{"type": "glob", "value": p} for p in patterns]})
        elif sid:
            rejected.append(f"section {sid}: no pattern inside the source")
    if sections:
        rules["sections"] = sections
    return RulesCheck(rules, rejected)


@dataclass
class CodeCheck:
    ok: bool
    problems: list[str] = field(default_factory=list)


def check_code(source: str, callable_name: str, allowed_modules: Iterable[str]) -> CodeCheck:
    allowed = set(allowed_modules)
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return CodeCheck(False, [f"syntax error: {exc.msg} (line {exc.lineno})"])
    problems = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] not in allowed:
                    problems.append(f"import of {alias.name} is not allowed")
        elif isinstance(node, ast.ImportFrom):
            mod = (node.module or "").split(".")[0]
            if node.level == 0 and mod not in allowed:
                problems.append(f"import from {node.module} is not allowed")
        elif (
            isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in DANGEROUS_CALLS
        ):
            problems.append(f"call of {node.func.id}() is not allowed")
        elif isinstance(node, ast.Attribute) and node.attr.startswith("__") and node.attr.endswith("__"):
            problems.append(f"dunder attribute access {node.attr} is not allowed")
    if not any(isinstance(n, ast.FunctionDef) and n.name == callable_name for n in tree.body):
        problems.append(f"module does not define {callable_name}()")
    return CodeCheck(not problems, problems)


class SchemaValidator:
    """Validates documents against ``contracts/schemas/*.schema.json`` when they are available."""

    def __init__(self, schemas_dir: Path | None) -> None:
        self.schemas_dir = schemas_dir if schemas_dir and schemas_dir.is_dir() else None

    @classmethod
    def locate(cls, configured: Path | None) -> SchemaValidator:
        candidates = [configured] if configured else []
        found = find_contracts_dir(Path(__file__).parent)
        if found:
            candidates.append(found)
        candidates.append(Path("/app/contracts"))
        for c in candidates:
            if c and (c / "schemas").is_dir():
                return cls(c / "schemas")
        return cls(None)

    @property
    def available(self) -> bool:
        return self.schemas_dir is not None

    def errors(self, schema_file: str, instance: Any) -> list[str]:
        if self.schemas_dir is None:
            return []
        validator = _validator(str((self.schemas_dir / schema_file).resolve()))
        return [
            f"/{'/'.join(map(str, e.absolute_path))}: {e.message}"
            for e in sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
        ]


def _retrieve(uri: str) -> Resource[Any]:
    from urllib.parse import unquote
    from urllib.request import url2pathname

    path = Path(url2pathname(unquote(urlsplit(uri).path)))
    return DRAFT202012.create_resource(json.loads(path.read_text(encoding="utf-8")))


@lru_cache(maxsize=16)
def _validator(path: str) -> Draft202012Validator:
    uri = Path(path).as_uri()
    registry: Registry[Any] = Registry(retrieve=_retrieve)  # type: ignore[call-arg]
    return Draft202012Validator({"$ref": uri}, registry=registry)
