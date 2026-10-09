"""Contract tests: every collector.v1 operation of the real app, responses validated by ContractClient."""

from __future__ import annotations

import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import pytest
from fastapi.testclient import TestClient

from jane_kit.contracts import ContractClient, OpenAPISpec
from jane_web_collector.testing import FAST_LIMITS, REPO_ROOT, Site, wait_timeout_s, web_rules

pytestmark = pytest.mark.contract

SPEC = OpenAPISpec.load(REPO_ROOT / "contracts" / "openapi" / "collector.v1.yaml")


@contextmanager
def _failing_site() -> Iterator[str]:
    """A site whose robots.txt allows everything and whose every page answers 500 (a source error)."""

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            pass

        def do_GET(self) -> None:
            ok = self.path == "/robots.txt"
            body = b"User-agent: *\nAllow: /\n" if ok else b"internal error"
            self.send_response(200 if ok else 500)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _wait_paused(client: TestClient, cid: str) -> dict[str, Any]:
    """Wait until the collection stands on backpressure (its unacknowledged buffer is full)."""
    deadline = time.monotonic() + wait_timeout_s()
    view: dict[str, Any] = {}
    while time.monotonic() < deadline:
        view = client.get(f"/v1/collections/{cid}").json()
        if view["paused_by_backpressure"]:
            return view
        time.sleep(0.05)
    raise AssertionError(f"collection {cid} did not pause on backpressure: {view}")


def test_every_operation_matches_the_contract(
    client: TestClient, site: Site, monkeypatch: pytest.MonkeyPatch
) -> None:
    api = ContractClient(SPEC, client)
    api.get("/v1/health")
    api.get("/v1/info")

    # fetch: 200, 403 (robots), 422 (out of scope), 404 (the site has no such page), 400 (bad JSON)
    assert api.post("/v1/fetches", json={"source_kind": "web", "url": site.url("/about")}).status_code == 200
    assert (
        api.post("/v1/fetches", json={"source_kind": "web", "url": site.url("/private/x")}).status_code == 403
    )
    rules = web_rules(site)
    out = api.post(
        "/v1/fetches", json={"source_kind": "web", "url": "https://elsewhere.example.org/", "rules": rules}
    )
    assert out.status_code == 422 and out.json()["code"] == "out_of_scope"
    missing = api.post("/v1/fetches", json={"source_kind": "web", "url": site.url("/missing-page")})
    assert missing.status_code == 404 and missing.json()["details"] == {"http_status": 404}
    # 502: the source still answers 5xx after the retries (review 1 of WP-16)
    once = {"retries": {"max_attempts": 2, "initial_backoff_ms": 0, "max_backoff_ms": 0}}
    with _failing_site() as failing:
        boom = api.post("/v1/fetches", json={"source_kind": "web", "url": failing + "/boom", "limits": once})
    assert boom.status_code == 502, boom.text
    assert boom.json()["code"] == "source_unavailable" and boom.json()["retryable"] is True
    assert boom.json()["details"] == {"http_status": 500, "attempts": 2}
    bad = api.request("POST", "/v1/fetches", content=b"{", headers={"content-type": "application/json"})
    assert bad.status_code == 400

    # rules validation: valid and invalid
    assert api.post("/v1/rules/validations", json=rules).json()["valid"] is True
    raw = client.post("/v1/rules/validations", json={"collector": "web", "scope": {}, "strategies": []})
    SPEC.validate_response("POST", "/v1/rules/validations", raw.status_code, raw.json())
    assert raw.json()["valid"] is False and raw.json()["errors"]

    # collections: 202, replay, 422, 409 (state_key busy), get, materials, errors.
    # The collection holds at most one unacknowledged material, so it cannot finish before this test
    # cancels it: the 409 and 202 below are checked on a running collection however slowly the test runs
    # (a 4 req/s crawl was expected to outlast these steps; under load it finished first: 204, not 409).
    body = {
        "source_kind": "web",
        "source_id": "contract",
        "rules": rules,
        "limits": {**FAST_LIMITS, "queue": {"max_unacked_materials": 1}},
    }
    first = api.post("/v1/collections", json=body, headers={"Idempotency-Key": "c-1"})
    assert first.status_code == 202
    cid = first.json()["job_id"]
    replay = api.post("/v1/collections", json=body, headers={"Idempotency-Key": "c-1"})
    assert replay.json()["job_id"] == cid and replay.headers["Idempotency-Replayed"] == "true"
    busy = api.post("/v1/collections", json=body, headers={"Idempotency-Key": "c-2"})
    assert busy.status_code == 409
    no_rules = client.post("/v1/collections", json={"source_kind": "web"}, headers={"Idempotency-Key": "c-3"})
    SPEC.validate_response(
        "POST", "/v1/collections", no_rules.status_code, no_rules.json(), no_rules.headers["content-type"]
    )
    assert no_rules.status_code == 422
    tg = api.post(
        "/v1/collections",
        json={"source_kind": "telegram", "rules": rules},
        headers={"Idempotency-Key": "c-4"},
    )
    assert tg.status_code == 422
    api.get(f"/v1/collections/{cid}")
    api.get(f"/v1/jobs/{cid}")
    _wait_paused(client, cid)
    page = api.get(f"/v1/collections/{cid}/materials", params={"limit": 3, "wait_ms": 2000}).json()
    assert len(page["items"]) == 1 and page["collection_status"] == "running", page
    # acknowledges the material: the collector may emit one more and stands on backpressure again
    api.get(f"/v1/collections/{cid}/materials", params={"after": page["next_cursor"], "limit": 3})
    api.get(f"/v1/collections/{cid}/errors", params={"limit": 1})
    assert api.get("/v1/collections/job_nope").status_code == 404
    assert api.get("/v1/collections/job_nope/materials").status_code == 404
    assert api.get("/v1/collections/job_nope/errors").status_code == 404

    # state while running -> DELETE conflicts; cancel the job; then state reads and resets
    assert api.get(f"/v1/collections/{cid}").json()["status"] == "running"
    assert api.delete("/v1/states/contract").status_code == 409
    assert api.post(f"/v1/jobs/{cid}/cancel", json={"reason": "contract test"}).status_code == 202
    deadline = time.monotonic() + wait_timeout_s()
    while api.get(f"/v1/jobs/{cid}").json()["status"] != "cancelled" and time.monotonic() < deadline:
        time.sleep(0.05)
    assert api.get(f"/v1/collections/{cid}").json()["status"] == "cancelled"
    assert api.post(f"/v1/jobs/{cid}/cancel").status_code == 200
    assert api.get("/v1/jobs/job_nope").status_code == 404
    assert api.post("/v1/jobs/job_nope/cancel").status_code == 404
    assert api.get("/v1/states/contract").json()["collector"] == "web"
    assert api.delete("/v1/states/contract").status_code == 204
    assert api.get("/v1/states/contract").status_code in (200, 404)
    assert api.get("/v1/states/never-used").status_code == 404

    # connections
    monkeypatch.setenv("JANE_SECRET_SITE_TOKEN", "x")
    conn = {
        "connection_id": "site-auth",
        "kind": "http",
        "params": {"auth_scheme": "bearer"},
        "secret_refs": {"token": "env:JANE_SECRET_SITE_TOKEN"},
    }
    created = api.put("/v1/connections/site-auth", json=conn)
    assert created.status_code == 201
    etag = created.headers["ETag"]
    assert api.put("/v1/connections/site-auth", json=conn, headers={"If-Match": etag}).status_code == 200
    assert api.put("/v1/connections/site-auth", json=conn, headers={"If-Match": '"stale"'}).status_code == 412
    leaked = api.put("/v1/connections/site-auth", json={**conn, "params": {"password": "hunter2"}})
    assert leaked.status_code == 422 and leaked.json()["code"] == "secret_detected"
    assert api.get("/v1/connections").json()["items"][0]["connection_id"] == "site-auth"
    assert api.get("/v1/connections/site-auth").headers["ETag"] == etag
    tested = api.post("/v1/connections/site-auth/test").json()
    assert tested["ok"] is True and tested["secrets_resolved"] == {"token": True}
    assert api.delete("/v1/connections/site-auth").status_code == 204
    assert api.get("/v1/connections/site-auth").status_code == 404
    assert api.delete("/v1/connections/site-auth").status_code == 404
    assert api.post("/v1/connections/site-auth/test").status_code == 404

    assert api.uncovered() == []
