"""Review 1 fixes: lease configuration rule, per-request timeouts from run/strategy limits, unknown cursor,
blob delivery through the transit store."""

from __future__ import annotations

import hashlib
import os
import threading
import time
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator

from jane_kit.contracts import OpenAPISpec
from jane_web_collector.app import build_app
from jane_web_collector.testing import (
    FAST_LIMITS,
    REPO_ROOT,
    Site,
    drain,
    errors,
    make_settings,
    start,
    wait_done,
    web_rules,
)

SPEC = OpenAPISpec.load(REPO_ROOT / "contracts" / "openapi" / "collector.v1.yaml")
MATERIAL = (REPO_ROOT / "contracts" / "schemas" / "material.schema.json").resolve().as_uri()
NO_RETRY: dict[str, Any] = {
    **FAST_LIMITS,
    "retries": {"max_attempts": 1, "initial_backoff_ms": 0, "max_backoff_ms": 0},
}


def test_lease_configuration_is_validated(tmp_path: Path) -> None:
    """heartbeat + busy timeout must fit into the lease, otherwise a live owner could lose its collection."""
    with pytest.raises(ValueError, match="must be less than lease_seconds"):
        make_settings(tmp_path, lease_seconds=3, heartbeat_interval_ms=2000, state_busy_timeout_ms=1000)
    with pytest.raises(ValueError, match="must be less than lease_seconds"):
        make_settings(tmp_path, lease_seconds=30, heartbeat_interval_ms=5000, state_busy_timeout_ms=30_000)
    ok = make_settings(tmp_path, lease_seconds=3, heartbeat_interval_ms=500, state_busy_timeout_ms=1000)
    assert ok.heartbeat_interval_ms == 500


class _Slow(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass

    def do_GET(self) -> None:
        if self.path != "/robots.txt":
            time.sleep(1.0)
        body = b"<html><title>slow</title></html>"
        self.send_response(404 if self.path == "/robots.txt" else 200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


@pytest.fixture
def slow() -> Iterator[str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Slow)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


def _rules(base: str, **strategy: Any) -> dict[str, Any]:
    return {
        "collector": "web",
        "scope": {"allowed_domains": ["127.0.0.1"]},
        "strategies": [{"type": "seed_list", "urls": [base + "/page"], **strategy}],
    }


def test_request_and_strategy_timeouts_apply_per_request(client: TestClient, slow: str) -> None:
    # request level: 200 ms against a 1 s response -> the URL fails with a timeout
    short = {**NO_RETRY, "timeouts": {"request_timeout_ms": 200}}
    cid = start(client, {"source_kind": "web", "rules": _rules(slow), "limits": short})
    assert drain(client, cid) == []
    [err] = errors(client, cid)
    assert err["code"] == "source_unavailable" and "Timeout" in err["message"]
    assert (
        client.get(f"/v1/collections/{cid}").json()["effective_limits"]["timeouts"]["request_timeout_ms"]
        == 200
    )
    # strategy level works the same way
    strategy_limits = {"timeouts": {"request_timeout_ms": 200}}
    cid = start(
        client, {"source_kind": "web", "rules": _rules(slow, limits=strategy_limits), "limits": NO_RETRY}
    )
    assert drain(client, cid) == []
    assert "Timeout" in errors(client, cid)[0]["message"]
    # platform default (30 s) -> the same slow page is fetched
    cid = start(client, {"source_kind": "web", "rules": _rules(slow), "limits": NO_RETRY})
    assert len(drain(client, cid)) == 1


def test_unknown_cursor_is_rejected(client: TestClient, site: Site) -> None:
    rules = web_rules(site, strategies=[{"type": "seed_list", "urls": [site.url("/about")]}])
    cid = start(client, {"source_kind": "web", "rules": rules, "limits": FAST_LIMITS})
    wait_done(client, cid)
    r = client.get(f"/v1/collections/{cid}/materials", params={"after": "c_0000000000000099"})
    assert r.status_code == 422 and r.json()["errors"][0]["parameter"] == "after"
    page = client.get(f"/v1/collections/{cid}/materials").json()
    assert len(page["items"]) == 1  # nothing was acknowledged by the bad cursor


def _check_blob(material: dict[str, Any]) -> Path:
    errs = [
        e.message
        for e in Draft202012Validator({"$ref": MATERIAL}, registry=SPEC.registry).iter_errors(material)
    ]
    assert errs == []
    content = material["content"]
    assert content["kind"] == "blob" and content["store"] == "transit" and content["expires_at"].endswith("Z")
    parts = urlsplit(content["uri"])
    path = Path(unquote(parts.path.lstrip("/") if os.name == "nt" else parts.path))
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == content["sha256"] == material["revision"]["content_sha256"]
    assert len(raw) == content["size_bytes"]
    return path


def test_blob_delivery_and_transit_cleanup(tmp_path: Path, site: Site) -> None:
    transit = tmp_path / "transit"
    with TestClient(build_app(make_settings(tmp_path, transit_dir=transit))) as client:
        # explicit blob on the synchronous fetch
        r = client.post(
            "/v1/fetches", json={"source_kind": "web", "url": site.url("/about"), "content_delivery": "blob"}
        )
        assert r.status_code == 200, r.text
        fetched = _check_blob(r.json())
        # auto: a page up to transfer.inline_max_bytes inline, a larger one as blob
        urls = [site.url("/about"), site.url("/product/phone-alpha")]
        sizes = [
            client.post("/v1/fetches", json={"source_kind": "web", "url": u}).json()["content"]["size_bytes"]
            for u in urls
        ]
        assert sizes[0] < sizes[1]
        limits = {**FAST_LIMITS, "transfer": {"inline_max_bytes": sizes[0]}}
        cid = start(client, {"source_kind": "web", "rules": web_rules(site), "urls": urls, "limits": limits})
        by_url = {m["locator"]["canonical_url"]: m for m in drain(client, cid)}
        small, large = by_url[urls[0]], by_url[urls[1]]
        assert small["content"]["kind"] == "inline" and small["content"]["size_bytes"] == sizes[0]
        blob = _check_blob(large)
        assert blob.stat().st_size == sizes[1]
        # the producer's cleaner removes transit files after transfer.transit_ttl_seconds
        engine = client.app.state.engine  # type: ignore[attr-defined]
        old = time.time() - engine.limits.transfer.transit_ttl_seconds - 10
        os.utime(fetched, (old, old))
        engine.gc()
        assert not fetched.exists()
        assert blob.exists()  # still within its TTL
