"""``url_template`` strategy: URLs from an RFC 6570 level-1 template (``#/$defs/UrlTemplateStrategy``).

``variables`` gives each ``{name}`` of ``template`` a ``range`` (``start``..``end`` inclusive, ``step``;
descending when ``start > end``) or a list of ``values``; values are percent-encoded as RFC 6570 simple string
expansion requires. Variables are combined in the order they appear in the template (the last one changes
fastest). At most ``crawl.max_seed_urls`` URLs are generated.

* Without ``stop_after_consecutive_misses`` all URLs are proposed at once as material candidates (the core
  fetches them in parallel within its limits).
* With ``stop_after_consecutive_misses: N`` the URLs are fetched one after another through ``ctx.fetch``
  (as materials) and the innermost variable stops after N consecutive 404/410 responses; then the next value
  of the outer variables starts. Other failures and refused URLs do not count as misses. After a restart the
  walk starts again: already emitted URLs cost no request and count as hits, so the result is the same.
"""

from __future__ import annotations

import re
from collections.abc import AsyncIterator, Iterator, Mapping
from typing import Any, ClassVar
from urllib.parse import quote

from jane_contracts.discovery import DiscoveredUrl, DiscoveryContext, FetchedResource, FetchRejected

from ._common import bump, limit

__all__ = ["UrlTemplateStrategy", "expand", "template_variables", "variable_values"]

_VARIABLE = re.compile(r"\{([a-z_][a-z0-9_]*)\}")
MISS_STATUSES = frozenset({404, 410})


def template_variables(template: str) -> list[str]:
    return list(dict.fromkeys(_VARIABLE.findall(template)))


def expand(template: str, values: Mapping[str, Any]) -> str:
    """RFC 6570 level 1: ``{var}`` -> the value with every non-unreserved character percent-encoded."""
    return _VARIABLE.sub(lambda m: quote(str(values[m.group(1)]), safe=""), template)


def variable_values(spec: Mapping[str, Any]) -> Iterator[Any]:
    """Lazy values of one variable (a huge range is never materialized)."""
    if "values" in spec:
        yield from spec["values"]
        return
    rng = spec["range"]
    start, end, step = int(rng["start"]), int(rng["end"]), int(rng.get("step", 1))
    if step < 1:
        raise ValueError("url_template: range.step must be >= 1")
    if start <= end:
        yield from range(start, end + 1, step)
    else:
        yield from range(start, end - 1, -step)


class UrlTemplateStrategy:
    type_name: ClassVar[str] = "url_template"

    def __init__(self, config: Mapping[str, Any], strategy_id: str) -> None:
        self.config = config
        self.strategy_id = strategy_id
        self.template = str(config["template"])
        self.variables: Mapping[str, Any] = config.get("variables") or {}
        self.names = template_variables(self.template)
        missing = [name for name in self.names if name not in self.variables]
        if missing:
            raise ValueError(f"url_template: no values for {', '.join(missing)} in variables")
        misses = config.get("stop_after_consecutive_misses")
        self.stop_after: int | None = int(misses) if misses else None
        self.stats: dict[str, int] = {}

    def combinations(self, names: list[str] | None = None) -> Iterator[dict[str, Any]]:
        """All assignments in template order, lazily (the last variable changes fastest)."""
        names = self.names if names is None else names
        if not names:
            yield {}
            return
        head, rest = names[0], names[1:]
        for value in variable_values(self.variables[head]):
            for tail in self.combinations(rest):
                yield {head: value, **tail}

    async def seeds(self, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
        self.stats = {}  # seeds are re-run from scratch after a restart
        cap = limit(ctx, "crawl.max_seed_urls")
        if self.stop_after is None:
            for count, values in enumerate(self.combinations()):
                if count >= cap:
                    self._over_cap(ctx, cap)
                    return
                bump(self.stats, "urls")
                yield DiscoveredUrl(url=expand(self.template, values), strategy_id=self.strategy_id, depth=0)
            return
        await self._walk(
            ctx, cap
        )  # fetches through ctx.fetch (the core emits the materials), proposes nothing

    async def _walk(self, ctx: DiscoveryContext, cap: int) -> None:
        assert self.stop_after is not None
        outer, inner = self.names[:-1], self.names[-1]
        count = 0
        for fixed in self.combinations(outer):
            misses = 0
            for value in variable_values(self.variables[inner]):
                if ctx.is_cancelled():
                    return
                if count >= cap:
                    self._over_cap(ctx, cap)
                    return
                count += 1
                url = expand(self.template, {**fixed, inner: value})
                try:
                    resource = await ctx.fetch(url, kind="material")
                except FetchRejected as exc:
                    if exc.code in {"limit_exceeded", "rate_limited"}:
                        ctx.log.warning("url_template stopped: budget exhausted", extra={"reason": str(exc)})
                        return
                    bump(self.stats, "refused")
                    continue
                bump(self.stats, "urls")
                if resource is not None and resource.status in MISS_STATUSES:
                    misses += 1
                    bump(self.stats, "misses")
                    if misses >= self.stop_after:
                        bump(self.stats, "stopped_by_misses")
                        ctx.log.info(
                            "url_template: consecutive misses, next combination",
                            extra={"last": url, "misses": misses},
                        )
                        break
                else:
                    misses = 0

    def _over_cap(self, ctx: DiscoveryContext, cap: int) -> None:
        bump(self.stats, "stopped_by_max_seed_urls")
        ctx.log.warning("url_template stopped at crawl.max_seed_urls", extra={"limit": cap})

    async def on_fetched(
        self, resource: FetchedResource, ctx: DiscoveryContext
    ) -> AsyncIterator[DiscoveredUrl]:
        return
        yield  # pragma: no cover - makes this an async generator

    def snapshot(self) -> Mapping[str, Any]:
        return {"stats": dict(self.stats)} if self.stats else {}

    def restore(self, state: Mapping[str, Any]) -> None:
        self.stats = dict(state.get("stats") or {})
