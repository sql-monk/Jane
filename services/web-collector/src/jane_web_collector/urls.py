"""URL normalization, URL patterns and scope checks (CollectorRules ``normalization``, ``UrlPattern``, ``scope``)."""

from __future__ import annotations

import fnmatch
import hashlib
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import parse_qsl, quote, unquote, urlencode, urljoin, urlsplit, urlunsplit

__all__ = [
    "Normalizer",
    "Scope",
    "UrlPattern",
    "compile_patterns",
    "material_id",
    "patterns_match",
]

DEFAULT_PORTS = {"http": 80, "https": 443}
# RFC 3986 unreserved characters stay unescaped; everything else outside "safe" is percent-encoded.
_PATH_SAFE = "/:@!$&'()*+,;=-._~%"
_PCT = re.compile(r"%[0-9A-Fa-f]{2}")
_UNRESERVED = re.compile(r"[A-Za-z0-9\-._~]")


def _normalize_pct(text: str, safe: str) -> str:
    """Uppercase percent-escapes, decode escaped unreserved characters, escape unsafe characters."""

    def fix(m: re.Match[str]) -> str:
        char = chr(int(m.group(0)[1:], 16))
        return char if _UNRESERVED.fullmatch(char) else m.group(0).upper()

    return quote(_PCT.sub(fix, text), safe=safe)


def _remove_dot_segments(path: str) -> str:
    out: list[str] = []
    for seg in path.split("/"):
        if seg == "..":
            if len(out) > 1:
                out.pop()
        elif seg != ".":
            out.append(seg)
    result = "/".join(out)
    if path.endswith(("/.", "/..")):
        result += "/"
    return result if result.startswith("/") else "/" + result


@dataclass(frozen=True)
class Normalizer:
    """Applies CollectorRules ``normalization`` (defaults as in the schema)."""

    remove_fragment: bool = True
    lowercase_host: bool = True
    sort_query: bool = True
    strip_query_params: tuple[str, ...] = ()
    trailing_slash: str = "keep"

    @classmethod
    def from_rules(cls, rules: Mapping[str, Any] | None) -> Normalizer:
        cfg = (rules or {}).get("normalization") or {}
        return cls(
            remove_fragment=cfg.get("remove_fragment", True),
            lowercase_host=cfg.get("lowercase_host", True),
            sort_query=cfg.get("sort_query", True),
            strip_query_params=tuple(cfg.get("strip_query_params", ())),
            trailing_slash=cfg.get("trailing_slash", "keep"),
        )

    def normalize(self, url: str, base: str | None = None) -> str | None:
        """Absolute canonical URL, or ``None`` for non-HTTP(S) or malformed URLs."""
        url = url.strip()
        if not url:
            return None
        try:
            if base:
                url = urljoin(base, url)
            parts = urlsplit(url)
        except ValueError:
            return None
        scheme = parts.scheme.lower()
        if scheme not in DEFAULT_PORTS or not parts.hostname:
            return None
        host = parts.hostname  # urlsplit lowercases hostname
        if not self.lowercase_host:
            raw_host = parts.netloc.rsplit("@", 1)[-1]
            host = raw_host.rsplit(":", 1)[0] if not raw_host.startswith("[") else host
        try:
            host = host.encode("idna").decode("ascii") if not host.isascii() else host
            port = parts.port
        except (UnicodeError, ValueError):
            return None
        netloc = host if ":" not in host else f"[{host}]"
        if port is not None and port != DEFAULT_PORTS[scheme]:
            netloc = f"{netloc}:{port}"
        path = _remove_dot_segments(_normalize_pct(parts.path or "/", _PATH_SAFE))
        if self.trailing_slash == "add" and not path.endswith("/") and "." not in path.rsplit("/", 1)[-1]:
            path += "/"
        elif self.trailing_slash == "remove" and path != "/" and path.endswith("/"):
            path = path.rstrip("/") or "/"
        query_pairs = parse_qsl(parts.query, keep_blank_values=True)
        if self.strip_query_params:
            query_pairs = [
                (k, v)
                for k, v in query_pairs
                if not any(fnmatch.fnmatchcase(k, pat) for pat in self.strip_query_params)
            ]
        if self.sort_query:
            query_pairs = sorted(query_pairs)
        query = urlencode(query_pairs, quote_via=quote, safe="/:@!$'()*+,;-._~")
        fragment = "" if self.remove_fragment else parts.fragment
        return urlunsplit((scheme, netloc, path, query, fragment))


def material_id(canonical_url: str) -> str:
    """``web:`` + sha256(canonical URL)[:32] (material.schema.json)."""
    return "web:" + hashlib.sha256(canonical_url.encode("utf-8")).hexdigest()[:32]


def _glob_to_regex(glob: str) -> re.Pattern[str]:
    out = []
    i = 0
    while i < len(glob):
        c = glob[i]
        if c == "*":
            if glob[i : i + 2] == "**":
                out.append(".*")
                i += 2
                continue
            out.append("[^/]*")
        elif c == "?":
            out.append("[^/]")
        else:
            out.append(re.escape(c))
        i += 1
    return re.compile("".join(out) + r"\Z", re.DOTALL)


@dataclass(frozen=True)
class UrlPattern:
    """``glob`` is matched against the canonical URL without scheme (``host[:port]/path?query``);
    ``regex`` is searched in the whole canonical URL."""

    type: str
    value: str
    regex: re.Pattern[str] = field(compare=False, repr=False)

    @classmethod
    def from_rule(cls, rule: Mapping[str, Any]) -> UrlPattern:
        kind = rule.get("type", "glob")
        value = str(rule["value"])
        regex = re.compile(value) if kind == "regex" else _glob_to_regex(value)
        return cls(kind, value, regex)

    def matches(self, canonical_url: str) -> bool:
        if self.type == "regex":
            return self.regex.search(canonical_url) is not None
        without_scheme = canonical_url.split("://", 1)[-1]
        return self.regex.match(without_scheme) is not None


def compile_patterns(rules: Sequence[Mapping[str, Any]] | None) -> tuple[UrlPattern, ...]:
    return tuple(UrlPattern.from_rule(r) for r in rules or ())


def patterns_match(patterns: Sequence[UrlPattern], url: str) -> bool:
    return any(p.matches(url) for p in patterns)


@dataclass(frozen=True)
class Scope:
    """CollectorRules ``scope``: domains, schemes, path prefixes, include and exclude (exclude wins)."""

    allowed_domains: tuple[str, ...]
    include_subdomains: bool = False
    allowed_schemes: tuple[str, ...] = ("https", "http")
    path_prefixes: tuple[str, ...] = ()
    include: tuple[UrlPattern, ...] = ()
    exclude: tuple[UrlPattern, ...] = ()

    @classmethod
    def from_rules(cls, rules: Mapping[str, Any] | None) -> Scope | None:
        cfg = (rules or {}).get("scope")
        if not cfg:
            return None
        return cls(
            allowed_domains=tuple(d.lower().rstrip(".") for d in cfg["allowed_domains"]),
            include_subdomains=bool(cfg.get("include_subdomains", False)),
            allowed_schemes=tuple(cfg.get("allowed_schemes") or ("https", "http")),
            path_prefixes=tuple(cfg.get("path_prefixes") or ()),
            include=compile_patterns(cfg.get("include")),
            exclude=compile_patterns(cfg.get("exclude")),
        )

    def domain_allowed(self, host: str) -> bool:
        host = host.lower().rstrip(".")
        for domain in self.allowed_domains:
            if host == domain or (self.include_subdomains and host.endswith("." + domain)):
                return True
        return False

    def check(self, canonical_url: str) -> str | None:
        """``None`` if in scope, else a short reason (for diagnostics)."""
        parts = urlsplit(canonical_url)
        if parts.scheme not in self.allowed_schemes:
            return f"scheme {parts.scheme} not allowed"
        if not self.domain_allowed(parts.hostname or ""):
            return f"host {parts.hostname} not in allowed_domains"
        path = unquote(parts.path) or "/"
        if self.path_prefixes and not any(path.startswith(p) for p in self.path_prefixes):
            return "path outside path_prefixes"
        if patterns_match(self.exclude, canonical_url):
            return "matches scope.exclude"
        if self.include and not patterns_match(self.include, canonical_url):
            return "does not match scope.include"
        return None
