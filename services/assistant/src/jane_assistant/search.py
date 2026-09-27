"""Source search: turn a site/channel name into candidates (plan.md WP-11, ТЗ §8, §13.1 п.2).

A direct URL, ``@username`` or ``t.me/<name>`` needs no search. Otherwise the configured provider
is asked:

* ``static`` - a JSON catalogue of known sources (offline, for closed environments and dev);
* ``http_json`` - an HTTP search endpoint returning JSON (field paths are configurable);
* tests inject their own :class:`SearchProvider`.

Candidates carry a confidence in ``[0, 1]``; the onboarding flow auto-selects only a clear winner
(``limits.onboarding.auto_select_confidence`` and ``auto_select_margin``), otherwise it asks the user
(``needs_disambiguation``).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol
from urllib.parse import quote, urlsplit

import httpx

from jane_kit.errors import JaneError

__all__ = [
    "Candidate",
    "HttpJsonSearchProvider",
    "NoSearchProvider",
    "SearchProvider",
    "StaticSearchProvider",
    "direct_candidate",
    "score",
]

_TG = re.compile(r"^(?:@|(?:https?://)?t\.me/)([A-Za-z0-9_]{4,64})/?$")
_WORD = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class Candidate:
    title: str
    url: str | None = None
    telegram_username: str | None = None
    description: str | None = None
    confidence: float = 0.0

    @property
    def source_kind(self) -> str:
        return "telegram" if self.telegram_username else "web"

    def wire(self, candidate_id: str) -> dict[str, Any]:
        out: dict[str, Any] = {"candidate_id": candidate_id, "title": self.title}
        for key in ("url", "telegram_username", "description"):
            if getattr(self, key):
                out[key] = getattr(self, key)
        out["confidence"] = round(max(0.0, min(1.0, self.confidence)), 4)
        return out


class SearchProvider(Protocol):
    async def search(self, query: str, source_kind: str | None, limit: int) -> list[Candidate]: ...


def direct_candidate(query: str, source_kind: str | None) -> Candidate | None:
    """``https://…`` / ``@channel`` / ``t.me/channel`` -> a single certain candidate."""
    q = query.strip()
    if m := _TG.match(q):
        return Candidate(title=f"@{m.group(1)}", telegram_username=m.group(1), confidence=1.0)
    parts = urlsplit(q)
    if parts.scheme in {"http", "https"} and parts.hostname:
        if source_kind == "telegram" and parts.hostname == "t.me":
            name = parts.path.strip("/").split("/")[0]
            return Candidate(title=f"@{name}", telegram_username=name, confidence=1.0)
        return Candidate(title=parts.hostname, url=q, confidence=1.0)
    return None


def _words(text: str) -> set[str]:
    return set(_WORD.findall(text.lower()))


def score(query: str, *texts: str | None) -> float:
    """Share of query words found in the candidate's texts (title, aliases, url, description)."""
    wanted = _words(query)
    if not wanted:
        return 0.0
    have: set[str] = set()
    for t in texts:
        if t:
            have |= _words(t)
    return len(wanted & have) / len(wanted)


class NoSearchProvider:
    async def search(self, query: str, source_kind: str | None, limit: int) -> list[Candidate]:
        raise JaneError(
            "no search provider configured; give an exact URL or @channel", code="validation_failed"
        )


class StaticSearchProvider:
    """Catalogue file: ``[{"title", "url"?, "telegram_username"?, "description"?, "aliases"?: []}]``."""

    def __init__(self, entries: list[dict[str, Any]]) -> None:
        self.entries = entries

    @classmethod
    def from_file(cls, path: Path) -> StaticSearchProvider:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError(f"{path}: expected a JSON array of sources")
        return cls(data)

    async def search(self, query: str, source_kind: str | None, limit: int) -> list[Candidate]:
        out = []
        for e in self.entries:
            cand = Candidate(
                title=str(e["title"]),
                url=e.get("url"),
                telegram_username=e.get("telegram_username"),
                description=e.get("description"),
            )
            if source_kind and cand.source_kind != source_kind:
                continue
            s = score(query, cand.title, " ".join(e.get("aliases") or []), cand.url, cand.telegram_username)
            s = 0.8 * s + 0.2 * score(query, cand.description)
            if s > 0:
                out.append(Candidate(**{**cand.__dict__, "confidence": s}))
        out.sort(key=lambda c: (-c.confidence, c.title))
        return out[:limit]


class HttpJsonSearchProvider:
    def __init__(
        self,
        url_template: str,
        *,
        items_path: str = "results",
        title_field: str = "title",
        url_field: str = "url",
        description_field: str = "description",
        http: httpx.AsyncClient | None = None,
    ) -> None:
        if "{query}" not in url_template:
            raise ValueError("search_url_template must contain {query}")
        self.url_template = url_template
        self.items_path = items_path
        self.fields = (title_field, url_field, description_field)
        self.http = http

    async def search(self, query: str, source_kind: str | None, limit: int) -> list[Candidate]:
        client = self.http or httpx.AsyncClient()
        try:
            r = await client.get(self.url_template.replace("{query}", quote(query)))
            r.raise_for_status()
            body: Any = r.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise JaneError(f"search provider failed: {exc}", code="upstream_unavailable") from exc
        finally:
            if self.http is None:
                await client.aclose()
        for key in self.items_path.split(".") if self.items_path else []:
            body = body.get(key, []) if isinstance(body, dict) else []
        title_f, url_f, desc_f = self.fields
        out = []
        for item in body if isinstance(body, list) else []:
            if not isinstance(item, dict) or not item.get(title_f):
                continue
            cand = Candidate(title=str(item[title_f]), url=item.get(url_f), description=item.get(desc_f))
            if source_kind and cand.source_kind != source_kind:
                continue
            s = 0.8 * score(query, cand.title, cand.url) + 0.2 * score(query, cand.description)
            out.append(Candidate(**{**cand.__dict__, "confidence": s}))
        out.sort(key=lambda c: -c.confidence)
        return out[:limit]
