"""robots.txt (RFC 9309): parsing, matching and the per-host cache.

* Groups by ``User-agent``; the group whose product token matches the crawler's token (case-insensitive
  prefix match of the most specific token) wins, else ``*``; several groups with the same token merge.
* ``Allow``/``Disallow`` with ``*`` and ``$``; the longest matching rule wins, ``Allow`` on a tie.
* ``Crawl-delay`` (non-standard) and ``Sitemap`` lines are kept.
* Fetch outcome: 2xx -> parse; 4xx -> everything allowed; 5xx / network error -> everything disallowed
  (the RFC's "unreachable" case), retried after the cache TTL.
"""

from __future__ import annotations

import asyncio
import re
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from urllib.parse import unquote, urlsplit

__all__ = ["RobotsCache", "RobotsRules", "parse_robots"]


def _rule_regex(path: str) -> re.Pattern[str]:
    anchored = path.endswith("$")
    if anchored:
        path = path[:-1]
    body = ".*".join(re.escape(part) for part in path.split("*"))
    return re.compile(body + ("\\Z" if anchored else ""), re.DOTALL)


@dataclass(frozen=True)
class _Rule:
    allow: bool
    path: str
    regex: re.Pattern[str] = field(compare=False)

    @property
    def weight(self) -> int:
        return len(self.path)


@dataclass
class RobotsRules:
    rules: list[_Rule] = field(default_factory=list)
    crawl_delay: float | None = None
    sitemaps: list[str] = field(default_factory=list)
    allow_all: bool = False
    disallow_all: bool = False

    def allowed(self, url: str) -> bool:
        if self.disallow_all:
            return False
        if self.allow_all:
            return True
        parts = urlsplit(url)
        target = unquote(parts.path or "/") + (f"?{parts.query}" if parts.query else "")
        if target == "/robots.txt":
            return True
        best: _Rule | None = None
        for rule in self.rules:
            if rule.regex.match(target) and (
                best is None or rule.weight > best.weight or (rule.weight == best.weight and rule.allow)
            ):
                best = rule
        return best is None or best.allow


def parse_robots(text: str, token: str) -> RobotsRules:
    """Rules for the crawler with product ``token`` (e.g. ``JaneBot``)."""
    token = token.lower()
    groups: list[tuple[list[str], list[tuple[str, str]]]] = []
    sitemaps: list[str] = []
    agents: list[str] = []
    lines: list[tuple[str, str]] = []
    in_rules = False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        key, value = (s.strip() for s in line.split(":", 1))
        key = key.lower()
        if key == "sitemap":
            sitemaps.append(value)
        elif key == "user-agent":
            if in_rules:
                groups.append((agents, lines))
                agents, lines, in_rules = [], [], False
            agents.append(value.lower())
        elif key in {"allow", "disallow", "crawl-delay"}:
            if not agents:
                continue
            in_rules = True
            lines.append((key, value))
    if agents:
        groups.append((agents, lines))

    def specificity(agent: str) -> int:
        if agent == "*":
            return 0
        return len(agent) if token.startswith(agent) or agent.startswith(token) else -1

    best = max((specificity(a) for agents_, _ in groups for a in agents_), default=-1)
    result = RobotsRules(sitemaps=sitemaps)
    if best < 0:
        result.allow_all = True
        return result
    for agents_, lines_ in groups:
        if not any(specificity(a) == best for a in agents_):
            continue
        for key, value in lines_:
            if key == "crawl-delay":
                try:
                    result.crawl_delay = max(result.crawl_delay or 0.0, float(value))
                except ValueError:
                    continue
            elif value:  # empty Disallow means "allow everything" -> no rule
                path = unquote(value)
                result.rules.append(_Rule(key == "allow", path, _rule_regex(path)))
    return result


FetchRobots = Callable[[str], Awaitable[tuple[int, str] | None]]
"""Fetch ``robots.txt`` URL -> (HTTP status, text) or ``None`` on a network error."""


class RobotsCache:
    """Per-origin robots rules with TTL. ``fetch`` is provided by the fetcher (same client and limits)."""

    def __init__(self, fetch: FetchRobots, token: str, ttl_seconds: float) -> None:
        self._fetch = fetch
        self.token = token
        self.ttl = ttl_seconds
        self._cache: dict[str, tuple[float, RobotsRules]] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    @staticmethod
    def origin(url: str) -> str:
        parts = urlsplit(url)
        return f"{parts.scheme}://{parts.netloc}"

    async def rules_for(self, url: str) -> RobotsRules:
        origin = self.origin(url)
        lock = self._locks.setdefault(origin, asyncio.Lock())
        async with lock:  # one robots.txt request per origin even with parallel fetches
            return await self._rules_for(origin)

    async def _rules_for(self, origin: str) -> RobotsRules:
        cached = self._cache.get(origin)
        now = time.monotonic()
        if cached and now - cached[0] < self.ttl:
            return cached[1]
        outcome = await self._fetch(origin + "/robots.txt")
        if outcome is None:
            rules = RobotsRules(disallow_all=True)
        else:
            status, text = outcome
            if 200 <= status < 300:
                rules = parse_robots(text, self.token)
            elif 400 <= status < 500:
                rules = RobotsRules(allow_all=True)
            else:
                rules = RobotsRules(disallow_all=True)
        self._cache[origin] = (now, rules)
        return rules

    async def allowed(self, url: str) -> bool:
        return (await self.rules_for(url)).allowed(url)
