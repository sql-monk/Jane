"""Checks of effects through the public read APIs (storage.v1) - 'exactly once', history, stored bytes."""

from __future__ import annotations

import base64
import json
from collections import Counter
from pathlib import Path
from typing import Any

from jane_e2e.clients import JaneClient

__all__ = [
    "assert_effects_once",
    "entities",
    "history",
    "objects_by_source",
    "raw_bytes",
    "site_paths",
]

ROOT = Path(__file__).resolve().parents[3]
EXPECTED_URLS = ROOT / "tests" / "fixtures" / "testsite" / "expected_urls.json"


def site_paths(page_type: str) -> list[str]:
    """Paths of the test site by ``page_types`` (product, news, unknown, category, news-list)."""
    data = json.loads(EXPECTED_URLS.read_text(encoding="utf-8"))
    return sorted(p for p, t in data["page_types"].items() if t == page_type)


def expected_set(name: str) -> set[str]:
    data = json.loads(EXPECTED_URLS.read_text(encoding="utf-8"))
    return set(data["sets"][name])


def raw_bytes(material: dict[str, Any]) -> bytes:
    content = material["content"]
    if content["encoding"] == "utf-8":
        return str(content["data"]).encode("utf-8")
    return base64.b64decode(content["data"])


def _pages(client: JaneClient, path: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    cursor: str | None = None
    while True:
        q = {**params, "limit": 500, **({"cursor": cursor} if cursor else {})}
        r = client.api("storage").get(path, params=q)
        assert r.status_code == 200, r.text
        body = r.json()
        out.extend(body["items"])
        cursor = body.get("next_cursor")
        if not cursor:
            return out


def objects_by_source(storage: JaneClient, connection: str, source_id: str) -> list[dict[str, Any]]:
    return _pages(storage, "/v1/objects", {"connection_id": connection, "source_id": source_id})


def entities(
    storage: JaneClient, connection: str, scope: str, entity_type: str = "product"
) -> list[dict[str, Any]]:
    return _pages(
        storage, "/v1/entities", {"connection_id": connection, "entity_type": entity_type, "scope": scope}
    )


def history(
    storage: JaneClient, connection: str, canonical_key: str, entity_type: str = "product"
) -> list[dict[str, Any]]:
    return _pages(
        storage,
        "/v1/entity-history",
        {"connection_id": connection, "entity_type": entity_type, "key": canonical_key},
    )


def assert_effects_once(
    storage: JaneClient,
    source_id: str,
    *,
    materials: int,
    products: int,
    raw_connection: str = "raw-files",
    entities_connection: str = "results-pg",
    observations_per_material: int = 1,
) -> dict[str, Any]:
    """Every observation stored exactly once, every product exactly once with one history event per observation."""
    objs = objects_by_source(storage, raw_connection, source_id)
    per_obs = Counter(o["material"]["observation_id"] for o in objs)
    dup = {k: v for k, v in per_obs.items() if v > 1}
    assert not dup, f"RAW stored more than once per observation: {dup}"
    per_material = Counter(o["material"]["material_id"] for o in objs)
    assert len(per_material) == materials, (len(per_material), materials, sorted(per_material))
    assert set(per_material.values()) == {observations_per_material}, per_material
    ents = entities(storage, entities_connection, source_id)
    assert len(ents) == products, (len(ents), products, [e["canonical_key"] for e in ents])
    for e in ents:
        events = history(storage, entities_connection, e["canonical_key"])
        assert len(events) == observations_per_material, (e["canonical_key"], len(events))
        assert e["version"] == observations_per_material, e
    return {"objects": objs, "entities": ents}
