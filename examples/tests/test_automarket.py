"""Validate the actual packages and scheduled documents, including entity fields omitted by SDK tests."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

import httpx
import pytest

from jane_kit.contracts import ContractClient

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("setup_automarket", ROOT / "automarket" / "setup_automarket.py")
assert SPEC and SPEC.loader
automarket = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(automarket)


def test_all_archives_documents_and_fixture_entity_fields() -> None:
    assert automarket.check_offline() == []


@pytest.mark.parametrize("retryable", [False, True])
def test_package_job_retries_only_explicitly_retryable_failures(retryable: bool) -> None:
    ref = automarket.local_refs()["autos.rst-car-ads"]
    first_key = hashlib.sha256(f"automarket-test:{ref['digest']}".encode()).hexdigest()
    keys: list[str] = []

    def respond(request: httpx.Request) -> httpx.Response:
        key = request.headers["Idempotency-Key"]
        keys.append(key)
        job: dict[str, Any] = {
            "job_id": "job_retry0" if key == first_key else "job_retry1",
            "kind": "test_run",
            "status": "failed" if key == first_key else "succeeded",
            "created_at": "2026-10-11T00:00:00Z",
        }
        if key == first_key:
            job["error"] = {
                "type": "about:blank",
                "title": "Service unavailable",
                "status": 503,
                "code": "service_unavailable",
                "retryable": retryable,
            }
        else:
            job["result"] = {"passed": 11, "failed": 0}
        return httpx.Response(202, json=job)

    api = automarket.ex.Api("http://handler.test", "handler", token=None)
    api.http.close()
    api.http = httpx.Client(base_url="http://handler.test", transport=httpx.MockTransport(respond))
    api.client = ContractClient(automarket.ex.spec("handler"), api.http)
    try:
        if retryable:
            assert automarket.test_package(api, ref, 10, 0.001, 2) == {"passed": 11, "failed": 0}
            assert keys[0] != keys[1]
            automarket.test_package(api, ref, 10, 0.001, 2)
            assert keys[:2] == keys[2:]
        else:
            with pytest.raises(RuntimeError, match="service_unavailable"):
                automarket.test_package(api, ref, 10, 0.001, 2)
            assert keys == [first_key]
    finally:
        api.close()


@pytest.mark.parametrize("failure", [None, "upload", "permission"])
def test_generated_upload_restores_registry_policy(failure: str | None) -> None:
    policies: list[bool] = []
    allowed = False

    def respond(request: httpx.Request) -> httpx.Response:
        nonlocal allowed
        if request.method == "PATCH":
            assert request.headers["if-match"] == '"policy"'
            allowed = json.loads(request.content)["auto_changes_allowed"]
            policies.append(allowed)
            if allowed and failure == "permission":
                raise httpx.RemoteProtocolError("permission response interrupted")
        if request.url.path.endswith("/versions"):
            assert allowed
            if failure == "upload":
                raise httpx.RemoteProtocolError("upload interrupted")
            return httpx.Response(
                409,
                headers={"Content-Type": "application/problem+json"},
                json={"type": "about:blank", "title": "Conflict", "status": 409, "code": "conflict"},
            )
        return httpx.Response(
            200,
            headers={"ETag": '"policy"'},
            json={
                "package_id": "autos.rst-car-ads",
                "kind": "extractor",
                "title": "RST",
                "auto_changes_allowed": allowed,
                "deprecated": False,
                "created_at": "2026-10-11T00:00:00Z",
                "updated_at": "2026-10-11T00:00:00Z",
            },
        )

    api = automarket.ex.Api("http://registry.test", "registry", token=None)
    api.http.close()
    api.http = httpx.Client(base_url="http://registry.test", transport=httpx.MockTransport(respond))
    api.client = ContractClient(automarket.ex.spec("registry"), api.http)
    try:
        directory = automarket.package_dirs()["autos.rst-car-ads"]
        with pytest.raises(RuntimeError, match="explicit --allow-generated-packages"):
            automarket.upload_version(api, "autos.rst-car-ads", directory)
        assert policies == []
        if failure:
            with pytest.raises(httpx.RemoteProtocolError):
                automarket.upload_version(api, "autos.rst-car-ads", directory, allow_generated=True)
        else:
            assert (
                automarket.upload_version(
                    api, "autos.rst-car-ads", directory, allow_generated=True
                ).status_code
                == 409
            )
        assert policies == [True, False]
        assert not allowed
    finally:
        api.close()


@pytest.mark.parametrize("site", ["autoria", "rst"])
def test_scheduled_task_extracts_only_complete_ad_pages(site: str) -> None:
    refs = automarket.local_refs()
    task = automarket.task_doc(site, refs)
    assert task["schedule"] == {
        "type": "interval",
        "interval_seconds": 21600,
        "enabled": True,
        "overlap": "skip",
    }
    extractor = next(s for s in task["stages"] if s["stage_id"] == "extract-ad")
    assert extractor["bindings"] == [{"sections": ["ad"]}]
    assert all(s.get("on_failure") == "fail_run" for s in task["stages"] if s["kind"] == "handler")


@pytest.mark.parametrize("site", ["autoria", "rst"])
def test_rules_classify_their_real_ad_fixtures(site: str) -> None:
    from jane_web_collector.urls import Scope, compile_patterns, patterns_match

    directories = automarket.package_dirs()
    rules = automarket.ex.read_json(directories[f"autos.{site}-rules"] / "rules.json")
    scope = Scope.from_rules(rules)
    assert scope
    extractor_id = automarket.SITES[site][4]
    manifest = automarket.ex.read_json(directories[extractor_id] / "jane-package.json")
    details = [
        c["input"]["url"]
        for c in manifest["tests"]
        if c["expected_status"] == "success"
        and ("/auto_" in c["input"]["url"] or c["input"]["url"].count("/") >= 7)
    ]
    assert details, "no real detail fixtures"
    for url in details:
        assert scope.check(url) is None, url
        sections = [
            section["section_id"]
            for section in rules["sections"]
            if patterns_match(compile_patterns(section["patterns"]), url)
        ]
        assert sections == ["ad"], url


@pytest.mark.parametrize(
    ("variant", "message"),
    [
        ("empty", "no entities written"),
        ("task-disabled", "schedule is not active"),
        ("schedule-disabled", "schedule is not active"),
        ("manual", "schedule is not active"),
        ("run-running", "has not succeeded"),
        ("wrong-task", "has not succeeded"),
        ("unavailable-active", "unavailable source must have no active scan"),
    ],
)
def test_incomplete_catalog_verification_fails(variant: str, message: str) -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/sources/autos-avtobazar":
            return httpx.Response(
                200,
                json={
                    "source_id": "autos-avtobazar",
                    "kind": "web",
                    "title": "Avtobazar.ua",
                    "locator": {"url": "https://avtobazar.ua/"},
                    "labels": {"availability": "unavailable"},
                },
            )
        if request.url.path == "/v1/tasks/ads-avtobazar":
            task = automarket.task_doc("autoria", automarket.local_refs())
            task["task_id"] = "ads-avtobazar"
            task["schedule"] = {"type": "manual", "enabled": variant == "unavailable-active"}
            return httpx.Response(200, json=task)
        if request.url.path.startswith("/v1/runs/"):
            return httpx.Response(
                200,
                json={
                    "run_id": "run_empty",
                    "task_id": "ads-rst" if variant == "wrong-task" else "ads-autoria",
                    "status": "running" if variant == "run-running" else "succeeded",
                    "trigger": "manual",
                    "created_at": "2026-10-11T00:00:00Z",
                },
            )
        if request.url.path.startswith("/v1/tasks/"):
            task = automarket.task_doc("autoria", automarket.local_refs())
            if variant == "task-disabled":
                task["enabled"] = False
            if variant == "schedule-disabled":
                task["schedule"]["enabled"] = False
            if variant == "manual":
                task["schedule"]["type"] = "manual"
            return httpx.Response(200, json=task)
        return httpx.Response(200, json={"items": [], "next_cursor": None})

    def api(contract: str) -> Any:
        service = automarket.ex.Api("https://jane.example.test", contract)
        service.http.close()
        service.http = httpx.Client(
            base_url="https://jane.example.test", transport=httpx.MockTransport(respond)
        )
        service.client = ContractClient(automarket.ex.spec(contract), service.http)
        return service

    orch, storage = api("orchestrator"), api("storage")
    try:
        services = automarket.ex.Services(orch, orch, storage)
        with pytest.raises(RuntimeError, match=message):
            automarket.verify_catalog(services, {"autoria": "run_empty", "rst": "run_empty"})
    finally:
        orch.close()
        storage.close()
