"""Reusable steps of the scenarios: each step calls a real service through its contract."""

from __future__ import annotations

import base64
import hashlib
import os
from pathlib import Path
from typing import Any

from jane_e2e.clients import JaneClient
from jane_e2e.materials import delivery_key
from jane_extractor_sdk.package import build_archive

__all__ = [
    "EXTRACTOR_DIR",
    "collector_fetch",
    "extract",
    "extractor_archive",
    "extractor_ref",
    "sandbox_limits",
    "store",
]

ROOT = Path(__file__).resolve().parents[3]
EXTRACTOR_DIR = ROOT / "libs" / "extractor-sdk" / "examples" / "testsite-product-extractor"


def sandbox_limits() -> dict[str, Any]:
    """Request-level limits of sandbox calls (contract ``limits``), from the environment.

    ``JANE_E2E_SANDBOX_WALL_TIME_MS`` (default 60000): the runtime's own default (30000) was once exceeded on
    Docker Desktop for Windows by a slow container start (see docs/delivery/WP-13.md); the e2e run uses a
    wider wall time so that a slow engine is not mistaken for a defect of the scenario.
    """
    wall = int(os.environ.get("JANE_E2E_SANDBOX_WALL_TIME_MS", "60000"))
    return {"sandbox": {"wall_time_ms": wall}, "timeouts": {"invocation_timeout_ms": wall + 30000}}


def extractor_archive(package_dir: Path = EXTRACTOR_DIR) -> tuple[dict[str, Any], bytes]:
    """Local package: handler ref (id, version, digest of the canonical SDK archive) and the archive bytes."""
    archive = build_archive(package_dir)
    handler = {
        "package_id": "testsite.product-extractor",
        "version": "1.0.0",
        "digest": "sha256:" + hashlib.sha256(archive).hexdigest(),
    }
    return handler, archive


def collector_fetch(collector: JaneClient, url: str, source_id: str) -> dict[str, Any]:
    """One page through the real Web Collector (collector.v1 fetchMaterial) - a new observation each call."""
    body = {
        "source_kind": "web",
        "source_id": source_id,
        "url": url,
        "rules_ref": {"package_id": "testsite.web-rules", "version": "1.0.0"},
    }
    r = collector.api("collector").post("/v1/fetches", json=body)
    assert r.status_code == 200, r.text
    material: dict[str, Any] = r.json()
    assert material["collector"]["name"] == "web-collector", material["collector"]
    return material


def extractor_ref(package_dir: Path = EXTRACTOR_DIR) -> tuple[dict[str, Any], dict[str, Any]]:
    """Local package (not from the registry): handler ref + inline ContentRef of its archive."""
    archive = build_archive(package_dir)
    sha = hashlib.sha256(archive).hexdigest()
    manifest_id = {"package_id": "testsite.product-extractor", "version": "1.0.0"}
    handler = {**manifest_id, "digest": f"sha256:{sha}"}
    content = {
        "kind": "inline",
        "media_type": "application/zip",
        "encoding": "base64",
        "data": base64.b64encode(archive).decode("ascii"),
        "size_bytes": len(archive),
        "sha256": sha,
    }
    return handler, content


def extract(
    runtime: JaneClient, material: dict[str, Any], run_id: str, stage_id: str = "extract-products"
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run the example extractor on ``material`` in the sandbox runtime (handler.v1, sync); (body, result)."""
    handler, archive = extractor_ref()
    body = {
        "handler": handler,
        "package_archive": archive,
        "inputs": [{"kind": "material", "material": material}],
        "context": {
            "trace": {
                "run_id": f"run_{run_id}",
                "stage_id": stage_id,
                "source_id": material["source"]["source_id"],
            }
        },
        "delivery": {"delivery_key": delivery_key(run_id, stage_id, material["observation_id"])},
        "mode": "sync",
        "limits": sandbox_limits(),
    }
    _, result = runtime.invoke(body)
    return body, result


def store(
    storage: JaneClient,
    *,
    package_id: str,
    connection: str,
    inputs: list[dict[str, Any]],
    run_id: str,
    stage_id: str,
    key_part: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Write through the storage handler; returns (request body, HandlerResult)."""
    body = {
        "handler": {"package_id": package_id, "version": "1.0.0"},
        "connections": {"target": connection},
        "inputs": inputs,
        "context": {"trace": {"run_id": f"run_{run_id}", "stage_id": stage_id}},
        "delivery": {"delivery_key": delivery_key(run_id, stage_id, key_part)},
    }
    _, result = storage.invoke(body)
    return body, result
