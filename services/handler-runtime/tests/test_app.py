"""HTTP API of handler-runtime (subprocess backend; isolation itself is tested in test_isolation.py)."""

from __future__ import annotations

import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import httpx
import pytest
from fastapi import FastAPI, Response
from fastapi.testclient import TestClient

from jane_extractor_sdk.package import build_archive
from jane_handler_runtime.app import build_app
from jane_handler_runtime.runtime import build_runtime
from jane_handler_runtime.schemas import ContractSchemas, find_contracts_dir
from jane_handler_runtime.settings import Settings

SCHEMAS = ContractSchemas(find_contracts_dir(None))


@pytest.fixture
def client(subprocess_settings: Settings) -> Iterator[TestClient]:
    with TestClient(build_app(subprocess_settings)) as c:
        yield c


def post(client: TestClient, body: dict[str, Any], key: str | None = None) -> httpx.Response:
    key = key or body["delivery"]["delivery_key"]
    return client.post("/v1/invocations", json=body, headers={"Idempotency-Key": key})


def wait_job(client: TestClient, job_id: str, timeout: float = 60) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    job: dict[str, Any] = {}
    while time.monotonic() < deadline:
        job = client.get(f"/v1/jobs/{job_id}").json()
        if job["status"] in {"succeeded", "failed", "cancelled"}:
            return job
        time.sleep(0.05)
    return job


def test_health_info_and_metrics(client: TestClient) -> None:
    health = client.get("/v1/health")
    assert health.status_code == 200
    assert health.json()["checks"]["sandbox"]["status"] == "ok"
    info = client.get("/v1/info").json()
    assert info["service"] == "handler-runtime"
    caps = info["capabilities"]
    assert caps["handler_kinds"] == ["extractor", "transform"]
    assert "lxml" in caps["runtime_profiles"]["python-extractor@1"]["libraries"]
    assert info["limits"]["defaults"]["sandbox"]["wall_time_ms"] == 30_000
    assert info["limits"]["hard_caps"]["sandbox"]["memory_mb"] == 4096
    client.get("/v1/info")
    assert 'route="/v1/info"' in client.get("/metrics").text


def test_sync_invocation_success(client: TestClient, h: Any) -> None:
    body = h.invocation(
        h.example, h.product_material(), context={"trace": {"run_id": "run_1", "stage_id": "extract"}}
    )
    r = post(client, body)
    assert r.status_code == 200, r.text
    result = r.json()
    SCHEMAS.check("handler-result.schema.json", result)
    assert result["status"] == "success"
    assert result["handler"]["digest"] == h.digest(h.example)
    entity = result["output"]["entities"][0]
    assert entity["key"] == {"scope": "testsite", "natural": {"sku": "phone-alpha"}}
    assert entity["schema"] == "testsite.product-extractor@1.0.0#product"
    assert entity["observation"]["observation_id"] == body["inputs"][0]["material"]["observation_id"]
    assert entity["provenance"]["run_id"] == "run_1"
    assert result["inputs"][0]["material_id"] == body["inputs"][0]["material"]["material_id"]
    assert result["duplicate"] is False and result["delivery_key"] == "dk-1"
    stored = client.get(f"/v1/invocations/{result['invocation_id']}")
    assert stored.json() == result


def test_redelivery_is_a_duplicate_without_rerun(client: TestClient, h: Any) -> None:
    body = h.invocation(h.example, h.product_material(), key="dk-dup")
    first = post(client, body).json()
    again = post(client, body)
    assert again.headers["Idempotency-Replayed"] == "true"
    assert again.json()["duplicate"] is True
    assert again.json()["invocation_id"] == first["invocation_id"]
    changed = h.invocation(h.example, h.product_material("product-phone-gamma"), key="dk-dup")
    assert post(client, changed).json()["code"] == "idempotency_key_reused"


def test_four_states(client: TestClient, h: Any) -> None:
    empty = post(client, h.invocation(h.example, h.product_material("category-phones"), key="e")).json()
    assert empty["status"] == "empty" and empty["output"] == {"entities": []}
    unrec = post(
        client,
        h.invocation(
            h.example, h.product_material("product-no-price"), key="u", params={"include_url": False}
        ),
    ).json()
    assert unrec["status"] == "unrecognized"
    assert unrec["unrecognized"] == {
        "partial": True,
        "reason": "product page without a price",
        "signature": "missing-selector:[itemprop=price]",
    }
    failed = post(
        client, h.invocation(h.probe, h.product_material(), key="f", params={"mode": "raise"})
    ).json()
    assert failed["status"] == "failed"
    assert failed["failure"]["kind"] == "execution_error"
    assert "probe failure" in failed["failure"]["message"]
    for result in (empty, unrec, failed):
        SCHEMAS.check("handler-result.schema.json", result)


def test_schema_mismatch_is_failed(client: TestClient, h: Any) -> None:
    result = post(
        client, h.invocation(h.probe, h.product_material(), key="s", params={"mode": "bad_entity"})
    ).json()
    assert result["status"] == "failed"
    assert result["failure"]["kind"] == "schema_mismatch"
    assert result["diagnostics"]["validation_errors"][0]["pointer"] == "/entities/0/fields/id"
    SCHEMAS.check("handler-result.schema.json", result)


def test_network_attempt_is_a_sandbox_violation(client: TestClient, h: Any) -> None:
    body = h.invocation(
        h.probe, h.product_material(), key="n", params={"mode": "network", "host": "127.0.0.1", "port": 9}
    )
    result = post(client, body).json()
    assert result["status"] == "failed"
    assert result["failure"]["kind"] == "sandbox_violation"
    events = {v["event"] for v in result["failure"]["details"]["violations"]}
    assert events & {"socket.getaddrinfo", "socket.connect"}


def test_output_limit_from_request(client: TestClient, h: Any) -> None:
    body = h.invocation(
        h.probe,
        h.product_material(),
        key="o",
        params={"mode": "output", "bytes": 5000},
        limits={"sandbox": {"max_output_bytes": 1000}, "crawl": {"max_depth": 1}},
    )
    result = post(client, body).json()
    assert result["failure"]["kind"] == "resource_exceeded"
    assert result["failure"]["details"]["max_output_bytes"] == 1000


def test_timeout_in_subprocess_backend(client: TestClient, h: Any) -> None:
    body = h.invocation(
        h.probe,
        h.product_material(),
        key="t",
        params={"mode": "sleep"},
        limits={"sandbox": {"wall_time_ms": 1500}},
    )
    started = time.monotonic()
    result = post(client, body).json()
    assert time.monotonic() - started < 20
    assert result["failure"]["kind"] == "timeout"
    assert result["failure"]["details"]["wall_time_ms"] == 1500


def test_async_mode_returns_job(client: TestClient, h: Any) -> None:
    r = post(client, h.invocation(h.example, h.product_material(), key="a", mode="async"))
    assert r.status_code == 202
    assert r.headers["Location"] == f"/v1/jobs/{r.json()['job_id']}"
    job = wait_job(client, r.json()["job_id"])
    assert job["status"] == "succeeded"
    assert job["result"]["status"] == "success"
    again = post(client, h.invocation(h.example, h.product_material(), key="a", mode="async"))
    assert again.status_code == 200 and again.json()["duplicate"] is True


@pytest.mark.parametrize(
    ("change", "code"),
    [
        ({"params": {"default_currency": "hryvnia"}}, "validation_failed"),
        ({"inputs": []}, "validation_failed"),
        (
            {
                "handler": {
                    "package_id": "testsite.product-extractor",
                    "version": "1.0.0",
                    "digest": "sha256:" + "0" * 64,
                }
            },
            "digest_mismatch",
        ),
        ({"handler": {"package_id": "other.package", "version": "1.0.0"}}, "validation_failed"),
    ],
    ids=["params", "no-inputs", "digest", "wrong-package"],
)
def test_invalid_requests(client: TestClient, h: Any, change: dict[str, Any], code: str) -> None:
    body = {**h.invocation(h.example, h.product_material(), key=f"bad-{code}"), **change}
    r = post(client, body)
    assert r.status_code == 422, r.text
    assert r.json()["code"] == code


def test_idempotency_key_must_match_delivery_key(client: TestClient, h: Any) -> None:
    r = post(client, h.invocation(h.example, h.product_material(), key="k1"), key="k2")
    assert r.status_code == 422
    assert (
        client.post("/v1/invocations", json=h.invocation(h.example, h.product_material())).status_code == 422
    )


def test_dependency_not_allowed(client: TestClient, h: Any, tmp_path: Path) -> None:
    import json
    import shutil

    pkg = tmp_path / "pkg"
    shutil.copytree(h.example, pkg)
    manifest = json.loads((pkg / "jane-package.json").read_text(encoding="utf-8"))
    manifest["dependencies"]["python"] = ["requests>=2"]
    (pkg / "jane-package.json").write_text(json.dumps(manifest), encoding="utf-8")
    r = post(client, h.invocation(pkg, h.product_material(), key="dep"))
    assert r.status_code == 422
    assert r.json()["code"] == "dependency_not_allowed"
    assert "requests is not available" in r.json()["detail"]


def test_test_run_reports_every_case(client: TestClient, h: Any) -> None:
    sample = h.product_material("product-phone-gamma")
    expected_entity = {
        "entity_type": "product",
        "key": {"scope": "testsite", "natural": {"sku": "phone-gamma"}},
        "fields": {"sku": "phone-gamma", "availability": "in_stock"},
        "observation": {"observation_id": sample["observation_id"], "observed_at": sample["fetched_at"]},
    }
    body = {
        "handler": {"package_id": "testsite.product-extractor", "version": "1.0.0"},
        "package_archive": h.archive_ref(h.example),
        "tests": "all",
        "extra_cases": [
            {
                "name": "problem-sample",
                "input": {"kind": "material", "material": sample},
                "expected_status": "success",
                "expected": {"entities": [expected_entity]},
                "compare": "subset",
            }
        ],
    }
    r = client.post("/v1/test-runs", json=body, headers={"Idempotency-Key": "tr-1"})
    assert r.status_code == 202, r.text
    job = wait_job(client, r.json()["job_id"])
    report = job["result"]
    SCHEMAS.check("handler-result.schema.json#/$defs/TestReport", report)
    assert report["passed"] == 5 and report["failed"] == 1
    bad = next(c for c in report["cases"] if not c["passed"])
    assert bad["name"] == "problem-sample"
    assert bad["differences"][0]["pointer"] == "/entities/0/fields/availability"
    assert all(c["result"]["test_mode"] is True for c in report["cases"])


def test_package_from_registry(subprocess_settings: Settings, h: Any) -> None:
    """The registry neighbour is a fake of ``downloadPackageArchive`` (registry.v1.yaml)."""
    from jane_kit.contracts import OpenAPISpec

    spec = OpenAPISpec.load(h.repo / "contracts" / "openapi" / "registry.v1.yaml")
    assert spec.by_id("downloadPackageArchive").path == "/v1/packages/{package_id}/versions/{version}/archive"
    archive = build_archive(h.example)
    fake = FastAPI()
    calls: list[str] = []

    @fake.get("/v1/packages/{package_id}/versions/{version}/archive")
    def download(package_id: str, version: str) -> Response:
        calls.append(f"{package_id}@{version}")
        if (package_id, version) != ("testsite.product-extractor", "1.0.0"):
            return Response(status_code=404)
        return Response(archive, media_type="application/zip", headers={"ETag": f'"{h.digest(h.example)}"'})

    settings = subprocess_settings.model_copy(update={"registry_url": "http://registry.test"})
    runtime = build_runtime(settings, registry_transport=httpx.ASGITransport(app=fake))
    with TestClient(build_app(settings, runtime)) as c:
        body = h.invocation(h.example, h.product_material(), key="reg")
        del body["package_archive"]
        body["handler"]["digest"] = h.digest(h.example)
        assert post(c, body).json()["status"] == "success"
        missing = {**body, "handler": {"package_id": "testsite.product-extractor", "version": "9.9.9"}}
        r = post(c, missing, key="reg")
        assert r.status_code in {404, 422}
        r = post(c, {**missing, "delivery": {"delivery_key": "reg-2"}})
        assert r.status_code == 404 and r.json()["code"] == "not_found"
    assert calls[0] == "testsite.product-extractor@1.0.0"


def test_file_blobs_only_under_allowed_roots(subprocess_settings: Settings, h: Any, tmp_path: Path) -> None:
    archive = build_archive(h.example)
    path = tmp_path / "blobs" / "pkg.zip"
    path.parent.mkdir()
    path.write_bytes(archive)
    ref = {
        "kind": "blob",
        "uri": path.as_uri(),
        "media_type": "application/zip",
        "size_bytes": len(archive),
        "sha256": h.archive_ref(h.example)["sha256"],
    }
    body = h.invocation(h.example, h.product_material(), key="blob")
    body["package_archive"] = ref
    with TestClient(build_app(subprocess_settings)) as c:
        r = post(c, body)
        assert r.status_code == 422 and "allowed roots" in r.json()["detail"]
    allowed = subprocess_settings.model_copy(update={"blob_roots": [tmp_path / "blobs"]})
    with TestClient(build_app(allowed)) as c:
        assert post(c, body).json()["status"] == "success"


def test_subprocess_backend_is_refused_unless_allowed(tmp_path: Path, h: Any) -> None:
    settings = Settings(log_format="console", sandbox_backend="subprocess", package_cache_dir=tmp_path / "c")
    with TestClient(build_app(settings)) as c:
        assert c.get("/v1/health").status_code == 503
        r = post(c, h.invocation(h.example, h.product_material(), key="refused"))
        assert r.status_code == 503
        assert r.json()["code"] == "service_unavailable"
