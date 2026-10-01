"""End-to-end improvement scenarios on the real assistant app with contract-bound fakes of neighbours.

«Готово, коли» (plan.md WP-11): problem samples -> new version -> activation -> rollback.
"""

from __future__ import annotations

import copy
import time
from typing import Any

import httpx
import pytest
from assistant_fakes import WAIT_S, World
from assistant_fakes.runtime import PRODUCT_CODE_V1, PRODUCT_CODE_V2_BREAKING
from assistant_fakes.site import SITES, material, product
from fastapi.testclient import TestClient

from jane_assistant.packages import extractor_draft
from jane_assistant.settings import Settings
from jane_kit.contracts import ContractClient

PKG = "catalog.product-extractor"
PROBLEM_URL = "https://shop.example.test/product/c-300"
PROBLEM_HTML = product("C-300", "Kettle C-300", "899", price_class="price-new")


def seed(w: World, *, auto_changes_allowed: bool = True, other_source: bool = False) -> None:
    draft = extractor_draft(
        package_id=PKG,
        version="1.2.0",
        title="Product cards",
        entity_type="product",
        key_fields=["sku"],
        entity_schema={"type": "object", "properties": {"sku": {"type": "string"}}},
        module_code=PRODUCT_CODE_V1,
        domains=["shop.example.test"],
        source_kind="web",
        media_types=["text/html"],
        job_id="seed",
        model={},
        reason="onboarding",
    )
    ok = material(
        "https://shop.example.test/product/a-100",
        SITES["shop.example.test"]["https://shop.example.test/product/a-100"],
        "shop-example",
    )
    empty = material(
        "https://shop.example.test/catalog/kettles/",
        SITES["shop.example.test"]["https://shop.example.test/catalog/kettles/"],
        "shop-example",
    )
    draft.add_test(
        "product-a100",
        ok,
        "success",
        [{"entity_type": "product", "fields": {"sku": "A-100", "title": "Kettle A-100"}}],
        "human",
    )
    draft.add_test("category-empty", empty, "empty", None, "human")
    draft.manifest["provenance"] = {"created_by": "human"}
    entry = w.registry.seed(draft.manifest, draft.files, auto_changes_allowed=auto_changes_allowed)
    ref = {"package_id": PKG, "version": "1.2.0", "digest": entry["digest"]}
    w.orchestrator.sources["shop-example"] = {
        "source_id": "shop-example",
        "kind": "web",
        "title": "Shop Example",
        "locator": {"url": "https://shop.example.test/"},
        "change_policy": {"llm_versions": "auto_after_checks"},
        "expected_entity_types": ["product"],
    }
    for task_id, stage_id, source_id, params in [
        ("shop-catalog", "extract-products", "shop-example", None),
        ("shop-price-check", "extract-price", "shop-example", {"fields": ["price"]}),
    ] + ([("other-catalog", "extract-products", "other-shop", {"currency": "EUR"})] if other_source else []):
        stage: dict[str, Any] = {
            "stage_id": stage_id,
            "kind": "handler",
            "handler": dict(ref),
            "inputs": [{"from": "collect"}],
        }
        if params:
            stage["params"] = params
        w.orchestrator.tasks[task_id] = {
            "task_id": task_id,
            "title": task_id,
            "input": {"source_id": source_id},
            "stages": [{"stage_id": "collect", "kind": "collect", "collector": {"collector": "web"}}, stage],
        }
    w.orchestrator.groups["pg_1"] = {
        "group_id": "pg_1",
        "source_id": "shop-example",
        "package": {"package_id": PKG, "version": "1.2.0"},
        "problem": "unrecognized",
        "signature": "missing-selector:.price",
        "count": 2,
        "status": "open",
        "samples": [],
    }
    w.storage.put("obj_c300", material(PROBLEM_URL, PROBLEM_HTML, "shop-example", observation=7))


def request(policy: dict[str, Any] | None = None, **extra: Any) -> dict[str, Any]:
    ok_url = "https://shop.example.test/product/b-200"
    body: dict[str, Any] = {
        "package": {"package_id": PKG, "version": "1.2.0"},
        "source_id": "shop-example",
        "problem_group_id": "pg_1",
        "problem_samples": [
            {
                "material_ref": {"storage_connection_id": "raw-files", "object_id": "obj_c300"},
                "diagnostics": [
                    {
                        "level": "warning",
                        "code": "extract.missing_selector",
                        "message": "selector .price matched 0 elements",
                    }
                ],
                "result": {
                    "invocation_id": "inv_1",
                    "handler": {"package_id": PKG, "version": "1.2.0"},
                    "handler_kind": "extractor",
                    "status": "unrecognized",
                    "inputs": [{"kind": "material"}],
                    "unrecognized": {"partial": True, "signature": "missing-selector:.price"},
                    "started_at": "2026-09-27T10:00:00Z",
                    "finished_at": "2026-09-27T10:00:01Z",
                },
            },
            {
                "material": material(
                    "https://shop.example.test/product/d-410",
                    product("D-410", "Mixer D-410", "1799", price_class="price-new"),
                    "shop-example",
                )
            },
        ],
        "successful_examples": [
            {
                "material": material(ok_url, SITES["shop.example.test"][ok_url], "shop-example"),
                "result": {
                    "invocation_id": "inv_2",
                    "handler": {"package_id": PKG, "version": "1.2.0"},
                    "handler_kind": "extractor",
                    "status": "success",
                    "inputs": [{"kind": "material"}],
                    "started_at": "2026-09-27T10:00:00Z",
                    "finished_at": "2026-09-27T10:00:01Z",
                    "output": {
                        "entities": [
                            {
                                "entity_type": "product",
                                "key": {"scope": "shop-example", "natural": {"sku": "B-200"}},
                                "fields": {
                                    "sku": "B-200",
                                    "title": "Kettle B-200",
                                    "price": {"amount": 1499.0, "currency": "UAH"},
                                },
                                "observation": {
                                    "observation_id": "obs_b200",
                                    "observed_at": "2026-09-27T10:00:00Z",
                                },
                            }
                        ]
                    },
                },
            },
        ],
        "policy": policy or {"approval": "auto_after_checks", "allow_fork": True},
        "limits": {
            "max_improvement_attempts": 3,
            "budget": {"amount": 1, "currency": "USD", "period": "run"},
        },
    }
    body.update(extra)
    return body


def run(w: World, body: dict[str, Any], key: str = "imp-1") -> dict[str, Any]:
    r = w.api.post("/v1/improvement-runs", json=body, headers={"Idempotency-Key": key})
    assert r.status_code == 202, r.text
    return w.result(r.json()["job_id"], "ImprovementResult")


def stage_version(w: World, task_id: str, stage_id: str) -> str:
    return str(w.orchestrator.stage(task_id, stage_id)["handler"]["version"])


def test_problem_samples_to_new_version_activation_and_rollback(w: World) -> None:
    seed(w)
    result = run(w, request())
    assert result["outcome"] == "new_version", result
    assert result["version"]["package_id"] == PKG and result["version"]["version"] == "1.2.1"
    assert result["activated"] is True and result["attempts"] == 1
    assert result["costs"]["amount"] > 0
    contexts = [r["context"] for r in result["test_reports"]]
    assert contexts == [
        "tests",
        "bindings:shop-catalog/extract-products",
        "bindings:shop-price-check/extract-price",
    ]
    assert all(r["report"]["failed"] == 0 for r in result["test_reports"])

    new = w.registry.versions[PKG]["1.2.1"]
    tests = new["manifest"]["tests"]
    assert [t["name"] for t in tests[:2]] == ["product-a100", "category-empty"]  # old tests kept
    assert [t["origin"] for t in tests if t["name"].startswith("problem-")] == [
        "problem_sample",
        "problem_sample",
    ]
    assert new["manifest"]["provenance"]["based_on"] == {"package_id": PKG, "version": "1.2.0"}
    assert new["manifest"]["provenance"]["llm"]["reason"] == "improvement"
    assert new["status"] == "approved" and new["test_status"] == "passed"
    assert len(new["test_reports"]) == 3
    assert w.registry.versions[PKG]["1.2.0"]["status"] == "approved"  # the old version is untouched

    # the model got grouped problems, code, diagnostics and successful examples - as data only
    req = next(r for r in w.llm.requests if r["output_schema"]["title"].endswith("improve_extractor.v1"))
    names = [p["name"] for p in req["data"]]
    assert {"package", "files", "problems", "problem_p1", "problem_p2", "success_s1"} <= set(names)
    assert "missing-selector:.price" in next(p["text"] for p in req["data"] if p["name"] == "problems")
    assert "price-new" not in req["instructions"]

    assert stage_version(w, "shop-catalog", "extract-products") == "1.2.1"
    assert stage_version(w, "shop-price-check", "extract-price") == "1.2.1"
    assert [a["kind"] for a in w.orchestrator.activations[("shop-catalog", "extract-products")]] == [
        "auto_activate"
    ]
    assert w.orchestrator.groups["pg_1"]["status"] == "resolved"
    assert w.orchestrator.groups["pg_1"]["assistant_job_id"]

    # rollback by the admin through the orchestrator API returns the stage to the previous version
    admin = TestClient(w.orchestrator.app)
    r = admin.post(
        "/v1/tasks/shop-catalog/stages/extract-products/activations",
        json={"kind": "rollback", "reason": "regression"},
        headers={"Idempotency-Key": "admin-rb"},
    )
    assert r.status_code == 200 and r.json()["package"]["version"] == "1.2.0"
    assert stage_version(w, "shop-catalog", "extract-products") == "1.2.0"
    history = admin.get("/v1/tasks/shop-catalog/stages/extract-products/activations").json()["items"]
    assert [a["kind"] for a in history] == ["rollback", "auto_activate"]


def test_refused_activation_on_one_binding_rolls_back_the_others(w: World) -> None:
    seed(w)
    w.orchestrator.refuse_auto.add(("shop-price-check", "extract-price"))
    result = run(w, request())
    assert result["outcome"] == "new_version" and result["activated"] is False
    kinds = [a["kind"] for a in w.orchestrator.activations[("shop-catalog", "extract-products")]]
    assert kinds == ["auto_activate", "rollback"]
    assert stage_version(w, "shop-catalog", "extract-products") == "1.2.0"
    assert stage_version(w, "shop-price-check", "extract-price") == "1.2.0"
    assert "refused" in w.orchestrator.groups["pg_1"]["note"]
    assert w.orchestrator.groups["pg_1"]["status"] == "in_progress"


def test_manual_approval_publishes_a_draft_without_activation(w: World) -> None:
    seed(w)
    result = run(w, request({"approval": "manual"}))
    assert result["outcome"] == "new_version" and result["activated"] is False
    assert w.registry.versions[PKG]["1.2.1"]["status"] == "draft"
    assert ("shop-catalog", "extract-products") not in w.orchestrator.activations
    assert w.orchestrator.groups["pg_1"]["status"] == "in_progress"
    assert "manual approval" in w.orchestrator.groups["pg_1"]["note"]


def test_package_with_forbidden_auto_changes_gets_a_proposal_only(w: World) -> None:
    seed(w, auto_changes_allowed=False)
    result = run(w, request())
    assert result["outcome"] == "proposal_only" and result["activated"] is False
    assert result["version"]["version"] == "1.2.1"
    assert list(w.registry.versions[PKG]) == ["1.2.0"]  # nothing published
    assert not w.registry.app.called("publishPackageVersion")
    assert w.orchestrator.groups["pg_1"]["status"] == "unresolved"


def test_attempts_are_limited_and_unresolved_is_reported(w: World) -> None:
    seed(w)
    w.llm.knobs.improve_invalid = True  # every attempt imports subprocess -> rejected before tests
    body = request()
    body["limits"]["max_improvement_attempts"] = 2
    result = run(w, body)
    assert result["outcome"] == "unresolved" and result["attempts"] == 2
    assert "subprocess" in result["unresolved_reason"]
    assert w.llm.steps().count("improve_extractor") == 2
    assert not w.handler.app.called("startTestRun")
    group = w.orchestrator.groups["pg_1"]
    assert group["status"] == "unresolved" and "subprocess" in group["note"]


def test_budget_exhaustion_stops_the_run(w: World) -> None:
    seed(w)
    body = request()
    body["limits"]["budget"]["amount"] = 0.005
    result = run(w, body)
    assert result["outcome"] == "unresolved"
    assert "budget" in result["unresolved_reason"]
    assert w.orchestrator.groups["pg_1"]["status"] == "unresolved"


def test_breaking_change_of_a_shared_package_becomes_a_fork(w: World) -> None:
    seed(w, other_source=True)
    w.llm.knobs.improve_code = PRODUCT_CODE_V2_BREAKING
    w.llm.knobs.improve_schema_change = "breaking"
    result = run(w, request())
    assert result["outcome"] == "fork_created", result
    fork_id = result["version"]["package_id"]
    assert fork_id == "catalog.product-extractor.shop-example"
    manifest = w.registry.versions[fork_id][result["version"]["version"]]["manifest"]
    assert manifest["fork_of"]["package_id"] == PKG
    assert result["version"]["version"] == "2.0.0"
    assert list(w.registry.versions[PKG]) == ["1.2.0"]  # parent unchanged
    assert stage_version(w, "other-catalog", "extract-products") == "1.2.0"  # other source untouched
    assert w.orchestrator.stage("shop-catalog", "extract-products")["handler"]["package_id"] == fork_id
    assert result["activated"] is True


@pytest.mark.parametrize("allow_fork", [False, True])
def test_failure_on_another_sources_binding(w: World, allow_fork: bool) -> None:
    seed(w, other_source=True)
    w.handler.fail_params.append(
        {"currency": "EUR"}
    )  # the runtime rejects the new version with other-shop's params
    body = request({"approval": "manual", "allow_fork": allow_fork})
    body["limits"]["max_improvement_attempts"] = 2
    result = run(w, body)
    if allow_fork:
        assert result["outcome"] == "fork_created"
        assert result["attempts"] == 1
    else:
        assert result["outcome"] == "unresolved"
        assert "other-catalog" in result["unresolved_reason"]
        assert list(w.registry.versions[PKG]) == ["1.2.0"]


def test_entity_type_expansion_is_only_suggested(w: World) -> None:
    seed(w)
    w.llm.knobs.improve_suggested = ["review", "product", "Bad Name"]
    result = run(w, request({"approval": "manual"}))
    assert result["suggested_entity_types"] == ["review"]
    assert w.orchestrator.sources["shop-example"]["expected_entity_types"] == ["product"]  # the user decides


def test_invalid_requests(w: World) -> None:
    seed(w)
    bad = request()
    bad["problem_samples"] = []
    assert (
        w.client.post("/v1/improvement-runs", json=bad, headers={"Idempotency-Key": "b1"}).status_code == 422
    )
    no_key = w.client.post("/v1/improvement-runs", json=request())
    assert no_key.status_code == 422 and no_key.json()["errors"][0]["parameter"] == "Idempotency-Key"
    body = copy.deepcopy(request())
    body["limits"] = {"max_improvement_attempts": -1}
    assert (
        w.client.post("/v1/improvement-runs", json=body, headers={"Idempotency-Key": "b2"}).status_code == 422
    )


class _ResetOnce(httpx.AsyncBaseTransport):
    """A neighbour reached through a pooled keep-alive connection that the neighbour has just closed.

    The first ``method path`` request fails the way httpx reports it, ``httpx.ReadError`` (connection reset),
    and never reaches the neighbour; later requests pass through. Seen in test_process_e2e under load: uvicorn
    (every Jane service, ``jane_kit.service.run``) closes a connection idle for 5 s (``timeout_keep_alive``)
    and the client reuses it at the same moment (``keepalive_expiry`` is 5 s in httpx as well)."""

    def __init__(self, inner: httpx.AsyncBaseTransport, method: str, path: str) -> None:
        self.inner = inner
        self.method = method
        self.path = path
        self.resets = 0

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        if not self.resets and request.method == self.method and request.url.path == self.path:
            self.resets += 1
            raise httpx.ReadError("connection reset by peer", request=request)
        return await self.inner.handle_async_request(request)


@pytest.mark.xfail(
    strict=True,
    reason="defect of jane_kit.clients.ServiceClient (WP-01): httpx.ReadError of a reset pooled connection is "
    "not retried even for GET or a POST with Idempotency-Key; the job fails (docs/delivery/WP-11.md, WP-11d)",
)
@pytest.mark.parametrize(
    ("method", "path"),
    [("GET", f"/v1/packages/{PKG}"), ("POST", f"/v1/packages/{PKG}/versions")],
    ids=["get-package", "publish-version"],
)
def test_a_reset_pooled_connection_does_not_fail_the_run(w: World, method: str, path: str) -> None:
    seed(w)
    reset = _ResetOnce(w.extra["transports"]["registry"], method, path)
    w.extra["transports"] = {**w.extra["transports"], "registry": reset}
    with w.instance(Settings(log_format="console", contracts_dir=w.contracts)) as client:
        api = ContractClient(w.spec, client)
        r = api.post("/v1/improvement-runs", json=request(), headers={"Idempotency-Key": "imp-reset"})
        assert r.status_code == 202, r.text
        deadline = time.monotonic() + WAIT_S
        while (job := api.get(f"/v1/jobs/{r.json()['job_id']}").json())["status"] not in {
            "succeeded",
            "failed",
            "cancelled",
        }:
            assert time.monotonic() < deadline, job
            time.sleep(0.01)
    assert reset.resets == 1  # the scenario really went through a reset connection
    assert job["status"] == "succeeded", job.get("error")
    assert job["result"]["outcome"] == "new_version" and job["result"]["activated"] is True
    assert w.registry.versions[PKG]["1.2.1"]["status"] == "approved"
