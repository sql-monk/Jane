"""``params.api_base`` that ``urllib`` cannot parse (bad port, broken IPv6 brackets) is a 422, never a 500."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from jane_llm.connections import ConnectionPolicy

INVALID = ["https://api.anthropic.com:99999", "https://api.anthropic.com:abc", "https://[::1"]


@pytest.mark.parametrize("api_base", INVALID)
def test_policy_reports_an_unparsable_api_base(api_base: str) -> None:
    error = ConnectionPolicy().api_base_error(api_base)
    assert error is not None and "not a valid URL" in error


@pytest.mark.parametrize("api_base", INVALID)
def test_put_connection_with_unparsable_api_base_is_422(client: TestClient, api_base: str) -> None:
    doc = {
        "connection_id": "bad-port",
        "kind": "llm_provider",
        "params": {"api_base": api_base},
        "secret_refs": {"api_key": "env:JANE_SECRET_X"},
    }
    r = client.put("/v1/connections/bad-port", json=doc)
    assert r.status_code == 422, r.text
    assert r.json()["errors"][0]["pointer"] == "/params/api_base"
    assert r.json()["errors"][0]["code"] == "api_base_not_allowed"
    assert client.get("/v1/connections").json()["items"] == []


def test_stored_connection_with_unparsable_api_base_fails_validation_at_call_time(
    client: TestClient, h: Any
) -> None:
    store = client.app.state.store  # type: ignore[attr-defined]
    store.put_doc(  # stored behind the API's back (old data, direct DB edit)
        "connection",
        "legacy",
        {
            "connection_id": "legacy",
            "kind": "llm_provider",
            "params": {"api_base": "https://api.anthropic.com:99999"},
            "secret_refs": {"api_key": "env:JANE_SECRET_X"},
        },
    )
    provider = {
        "provider_id": "anthropic",
        "kind": "anthropic",
        "connection_id": "legacy",
        "enabled": True,
        "models": [
            {
                "model_id": "claude-opus-5",
                "pricing": {"input_per_mtok": 5, "output_per_mtok": 25, "currency": "USD"},
            }
        ],
    }
    assert client.put("/v1/providers/anthropic", json=provider).status_code == 200
    r = client.post("/v1/completions", json=h.completion(model="anthropic/claude-opus-5"), headers=h.idem())
    assert r.status_code == 422 and "api_base" in r.json()["detail"]
    tested = client.post("/v1/connections/legacy/test")
    assert tested.status_code == 200 and tested.json()["ok"] is False
