"""API feed options that the schema permits must be reported honestly before a collection starts.

WP-02a rejected ``method: POST``/``body`` and ``emit_items_as_materials: true`` (``supported: false``, 422)
while the core could not execute them. Since WP-16 (R22, ``DiscoveryContext`` 1.1: ``fetch(method="POST",
body=...)`` and ``emit_material``) the core executes them, so validation reports them as supported and a
collection with them is accepted. A protocol-compatible stand-in is registered only to make the type
available here; the strategy itself is tested with the WP-03 package (``strategies/discovery/tests``).
"""

from __future__ import annotations

from typing import Any, cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from jane_web_collector.discovery.builtin import SeedListStrategy
from jane_web_collector.testing import Site, wait_done, web_rules


class AvailableApiFeed(SeedListStrategy):
    type_name = "api_feed"


def _rules(client: TestClient, site: Site, **options: Any) -> dict[str, Any]:
    registry = cast(FastAPI, client.app).state.engine.deps.registry
    registry.register(AvailableApiFeed)
    return web_rules(
        site,
        strategies=[
            {
                "type": "api_feed",
                "url": site.url("/api/v1/products"),
                "items_path": "$.items",
                "url_path": "$.url",
                **options,
            }
        ],
    )


@pytest.mark.parametrize(
    ("options", "pointers"),
    [
        ({"method": "POST", "body": {"q": "phones"}}, ["/strategies/0/method"]),
        ({"emit_items_as_materials": True}, ["/strategies/0/emit_items_as_materials"]),
        (
            {"method": "POST", "body": {}, "emit_items_as_materials": True},
            ["/strategies/0/method", "/strategies/0/emit_items_as_materials"],
        ),
    ],
    ids=["post", "json-materials", "both"],
)
def test_api_feed_post_and_json_item_options_are_supported(
    client: TestClient, site: Site, options: dict[str, Any], pointers: list[str]
) -> None:
    rules = _rules(client, site, **options)
    report = client.post("/v1/rules/validations", json=rules)
    assert report.status_code == 200, report.text
    assert report.json() == {"valid": True, "supported": True, "errors": [], "warnings": []}

    response = client.post(
        "/v1/collections",
        json={"source_kind": "web", "rules": rules},
        headers={"Idempotency-Key": f"api-feed-{'-'.join(pointers)}"},
    )
    assert response.status_code == 202, response.text
    assert wait_done(client, response.json()["job_id"])["status"] == "succeeded"


@pytest.mark.parametrize("options", [{}, {"method": "GET"}], ids=["default", "explicit-get"])
def test_get_api_feed_remains_supported_when_registered(
    client: TestClient, site: Site, options: dict[str, Any]
) -> None:
    rules = _rules(client, site, **options)
    report = client.post("/v1/rules/validations", json=rules)
    assert report.status_code == 200, report.text
    assert report.json() == {"valid": True, "supported": True, "errors": [], "warnings": []}
