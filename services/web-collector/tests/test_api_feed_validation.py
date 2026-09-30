"""API feed options that the schema permits must be reported honestly before a collection starts.

The WP-03 strategy is a neighbour of the core and is not present on main yet. A protocol-compatible
stand-in is registered only to make the type available; these tests exercise the real core validation
and collection endpoint, and never execute the stand-in strategy.
"""

from __future__ import annotations

from typing import Any, cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from jane_web_collector.discovery.builtin import SeedListStrategy
from jane_web_collector.testing import Site, web_rules


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
def test_unsupported_api_feed_options_are_rejected_before_collection(
    client: TestClient, site: Site, options: dict[str, Any], pointers: list[str]
) -> None:
    rules = _rules(client, site, **options)
    report = client.post("/v1/rules/validations", json=rules)
    assert report.status_code == 200, report.text
    body = report.json()
    assert body["valid"] is True and body["supported"] is False
    assert body["errors"] == []
    assert [(w["pointer"], w["code"]) for w in body["warnings"]] == [
        (pointer, "unsupported_strategy") for pointer in pointers
    ]

    response = client.post(
        "/v1/collections",
        json={"source_kind": "web", "rules": rules},
        headers={"Idempotency-Key": f"api-feed-{'-'.join(pointers)}"},
    )
    assert response.status_code == 422, response.text
    problem = response.json()
    assert problem["code"] == "validation_failed"
    assert [(e["pointer"], e["code"]) for e in problem["errors"]] == [
        ("/rules" + pointer, "unsupported_strategy") for pointer in pointers
    ]
    assert site.requests == {}


@pytest.mark.parametrize("options", [{}, {"method": "GET"}], ids=["default", "explicit-get"])
def test_get_api_feed_remains_supported_when_registered(
    client: TestClient, site: Site, options: dict[str, Any]
) -> None:
    rules = _rules(client, site, **options)
    report = client.post("/v1/rules/validations", json=rules)
    assert report.status_code == 200, report.text
    assert report.json() == {"valid": True, "supported": True, "errors": [], "warnings": []}
