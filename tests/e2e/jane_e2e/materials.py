"""Explicitly labelled stand-ins for components that are not merged into main yet.

:func:`standin_web_material` replaces the Web Collector (WP-02) in M1 scenarios until it is merged: the page is
fetched from the real test site over HTTP and wrapped into a ``Material`` (contracts/schemas/material.schema.json)
with ``collector.name = STANDIN_COLLECTOR``, so every stored object shows it did not come from the collector.
Scenarios that use it are marked "замінник колектора" in docs/acceptance and never count as proof of the
collector's own behaviour.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Any

import httpx

from jane_extractor_sdk.package import material_from_bytes

__all__ = ["STANDIN_COLLECTOR", "delivery_key", "fetch_page", "standin_web_material"]

STANDIN_COLLECTOR = "e2e-standin-collector"


def fetch_page(url: str, timeout_s: float = 30.0) -> httpx.Response:
    r = httpx.get(url, timeout=timeout_s, follow_redirects=True)
    r.raise_for_status()
    return r


def standin_web_material(
    response: httpx.Response, *, source_id: str, observation_id: str, section: str | None = None
) -> dict[str, Any]:
    """``Material`` built from a real HTTP response of the test site (stand-in for the Web Collector)."""
    media_type = response.headers.get("content-type", "text/html").split(";", 1)[0].strip()
    material = material_from_bytes(
        response.content,
        media_type=media_type,
        url=str(response.url),
        source_id=source_id,
        charset=response.charset_encoding,
        fetched_at=datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    material["observation_id"] = observation_id
    material["source"]["name"] = f"e2e {source_id}"
    material["locator"]["final_url"] = str(response.url)
    material["format"]["content_kind"] = "page"
    material["http"] = {
        "status": response.status_code,
        "headers": {
            k: v for k, v in response.headers.items() if k in {"content-type", "etag", "last-modified"}
        },
    }
    if etag := response.headers.get("etag"):
        material["revision"]["source_revision"] = etag
    if section:
        material["discovery"] = {"strategy": "explicit", "depth": 0, "section": section}
    material["collector"] = {"name": STANDIN_COLLECTOR, "version": "0"}
    return material


def delivery_key(*parts: str) -> str:
    """Deterministic delivery key (the orchestrator derives it the same way from run/stage/input)."""
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
