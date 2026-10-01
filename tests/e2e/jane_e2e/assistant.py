"""Steps of the source-assistant scenarios (S-M2-06, S-M2-07, R-07) on their own stack with the real registry.

The stack: assistant (WP-11), LLM gateway (WP-10), registry (WP-05), web-collector (WP-02/03), handler-runtime
(WP-06), orchestrator (WP-09), storage (WP-07), testsite, PostgreSQL and MinIO (WP-01). The runtime, the
collector and the orchestrator take packages and rules from the real registry (no ``package-host``).

Substitutes of EXTERNAL systems (**З**): the LLM is the deterministic provider ``fake`` of WP-10 (answers scripted
in tests/e2e/config/llm-seed.yaml), the web search is the ``static`` provider of WP-11.
"""

from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import time
import uuid
import zipfile
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

from jane_e2e.clients import CONTRACTS, JaneClient, spec
from jane_e2e.orchestration import (
    TESTSITE,
    create_source,
    create_task,
    list_items,
    m1_task,
    put_connections,
    start_run,
    wait_run,
)
from jane_e2e.stack import E2EStack, default_project
from jane_e2e.steps import sandbox_limits
from jane_e2e.verify import objects_by_source

PACKAGES = Path(__file__).resolve().parents[1] / "packages"
IMPROVABLE = PACKAGES / "e2e.improvable-product-extractor"
MANIFEST_SCHEMA = (CONTRACTS.parent / "schemas" / "package-manifest.schema.json").as_uri() + "#"
SERVICES = (
    "testsite",
    "registry",
    "handler-runtime",
    "storage",
    "web-collector",
    "orchestrator",
    "llm",
    "assistant",
)
# The stack of these scenarios: the runtime, the collector and the orchestrator use the REAL registry.
REGISTRY_ENV = {
    "JANE_E2E_RUNTIME_REGISTRY_URL": "http://registry:8000",
    "JANE_E2E_REGISTRY_RUNTIME_PROFILES": '["http://handler-runtime:8000/v1/info"]',
    "JANE_E2E_COLLECTOR_REGISTRY_URL": "http://registry:8000",
    "JANE_E2E_ORCHESTRATOR_EXTRA_EXECUTORS": "executors-registry.json",
}

# S-M2-07: the human-written extractor 1.0.0 recognises only in-stock offers.
PRODUCT_URLS = {
    "/product/phone-alpha": "success",  # InStock
    "/product/phone-beta": "success",  # InStock
    "/product/phone-gamma": "unrecognized",  # OutOfStock: not handled by 1.0.0
    "/product/phone-zeta": "unrecognized",  # PreOrder: not handled by 1.0.0
}
PROBLEMS = ("/product/phone-gamma", "/product/phone-zeta")  # p1, p2 of the scripted fix (llm-seed.yaml)
SUCCESSES = ("/product/phone-alpha", "/product/phone-beta")


@dataclass
class Flows:
    stack: E2EStack
    clients: dict[str, JaneClient] = field(default_factory=dict)

    def __getitem__(self, service: str) -> JaneClient:
        if service not in self.clients:
            self.clients[service] = JaneClient(self.stack.url(service))
        return self.clients[service]

    def reconnect(self, service: str) -> JaneClient:
        """A new client of a restarted service: the host port is read again (it may change on Linux)."""
        if old := self.clients.pop(service, None):
            old.close()
        self.clients[service] = JaneClient(self.stack.published_url(service))
        return self.clients[service]

    def close(self) -> None:
        for client in self.clients.values():
            client.close()
        self.clients.clear()


@contextmanager
def assistant_flows(
    name: str, *, label: str | None = None, env: Mapping[str, str] | None = None
) -> Iterator[Flows]:
    """An isolated stack of all services the assistant combines, with the real registry everywhere.

    The compose project is unique (``<default>-<name>-<random>``); ``env`` adds settings of the e2e overlay for
    this stack only; ``label`` names the scenarios in the evidence lines. The stack is removed with its volumes
    at the end unless ``JANE_E2E_KEEP=1``."""
    own = E2EStack(project=f"{default_project()}-{name}-{uuid.uuid4().hex[:6]}")
    own.env().update({**REGISTRY_ENV, **(env or {})})
    flows = Flows(own)
    try:
        if reasons := own.missing(SERVICES):
            pytest.skip("; ".join(reasons))
        own.ensure(*SERVICES)
        expected_rpm = int(os.environ.get("JANE_E2E_LLM_MAX_REQUESTS_PER_MINUTE", "120"))
        for service in ("assistant", "llm"):
            info = flows[service].api(service).get("/v1/info")
            assert info.status_code == 200, info.text
            actual_rpm = info.json()["limits"]["defaults"]["llm"]["max_requests_per_minute"]
            assert actual_rpm == expected_rpm, (service, actual_rpm, expected_rpm)
        note(label or name, "e2e LLM requests/minute", expected_rpm)
        put_connections(flows["orchestrator"])
        yield flows
    finally:
        flows.close()
        if os.environ.get("JANE_E2E_KEEP") != "1":
            own.down(volumes=True)


# ---------------------------------------------------------------------------- generic steps
def new_key() -> str:
    return uuid.uuid4().hex


def note(scenario: str, what: str, value: Any = None) -> None:
    """One evidence line for the report (visible with ``pytest -s``)."""
    text = what if value is None else f"{what}: {json.dumps(value, ensure_ascii=False, sort_keys=True)}"
    print(f"[{scenario}] {text}", flush=True)


def poll(what: str, read: Any, done: Any, timeout_s: float = 900.0, poll_s: float = 1.0) -> Any:
    deadline = time.monotonic() + timeout_s
    while True:
        value = read()
        if done(value):
            return value
        if time.monotonic() > deadline:
            raise TimeoutError(f"{what}: not done after {timeout_s}s: {json.dumps(value)[:3000]}")
        time.sleep(poll_s)


def llm_usage(llm: JaneClient, **params: str) -> dict[str, Any]:
    r = llm.api("llm").get("/v1/usage", params=params)
    assert r.status_code == 200, r.text
    return dict(r.json())


def by_purpose(llm: JaneClient) -> dict[str, int]:
    rows = llm_usage(llm, group_by="purpose")["items"]
    return {str(row["purpose"]): int(row["requests"]) for row in rows}


# ---------------------------------------------------------------------------- registry and runtime
def registry_version(registry: JaneClient, ref: dict[str, Any]) -> dict[str, Any]:
    r = registry.api("registry").get(f"/v1/packages/{ref['package_id']}/versions/{ref['version']}")
    assert r.status_code == 200, r.text
    return dict(r.json())


def registry_package(registry: JaneClient, package_id: str) -> tuple[dict[str, Any], str]:
    r = registry.api("registry").get(f"/v1/packages/{package_id}")
    assert r.status_code == 200, r.text
    return dict(r.json()), r.headers["etag"]


def archive_digest(registry: JaneClient, ref: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Digest of the canonical archive the registry serves, and the manifest inside it."""
    r = registry.api("registry").get(f"/v1/packages/{ref['package_id']}/versions/{ref['version']}/archive")
    assert r.status_code == 200, r.text
    digest = "sha256:" + hashlib.sha256(r.content).hexdigest()
    assert r.headers["etag"] == f'"{digest}"'
    with zipfile.ZipFile(io.BytesIO(r.content)) as archive:
        return digest, json.loads(archive.read("jane-package.json"))


def runtime_tests(runtime: JaneClient, ref: dict[str, Any]) -> dict[str, Any]:
    """Tests of a PUBLISHED version in the real runtime: the archive comes from the registry by reference
    (``handler.v1`` ``startTestRun`` without ``package_archive``), its digest is checked by the runtime."""
    body = {"handler": ref, "tests": "all", "limits": sandbox_limits()}
    r = runtime.api("handler").post("/v1/test-runs", json=body, headers={"Idempotency-Key": new_key()})
    assert r.status_code == 202, r.text
    job = runtime.wait_job("handler", r.json()["job_id"])
    assert job["status"] == "succeeded", job
    return dict(job["result"])


def publish_fixture(
    registry: JaneClient, directory: Path, package_id: str, *, auto_changes_allowed: bool = True
) -> dict[str, Any]:
    """A human-written fixture package published to the real registry under a per-run id; returns the
    ``PackageVersion``. The manifest is checked against the contract schema first."""
    manifest = json.loads((directory / "jane-package.json").read_text(encoding="utf-8"))
    manifest["package_id"] = package_id
    spec("registry").validate_at(MANIFEST_SCHEMA, manifest, f"{directory.name}/jane-package.json")
    files: dict[str, dict[str, str]] = {}
    for path in sorted(directory.rglob("*")):
        if path.is_file() and path.name != "jane-package.json" and "__pycache__" not in path.parts:
            files[path.relative_to(directory).as_posix()] = {
                "encoding": "base64",
                "data": base64.b64encode(path.read_bytes()).decode("ascii"),
            }
    created = registry.api("registry").post(
        "/v1/packages",
        json={
            "package_id": package_id,
            "kind": manifest["kind"],
            "title": manifest["title"],
            "auto_changes_allowed": auto_changes_allowed,
        },
        headers={"Idempotency-Key": new_key()},
    )
    assert created.status_code == 201, created.text
    published = registry.api("registry").post(
        f"/v1/packages/{package_id}/versions",
        json={"manifest": manifest, "files": files},
        headers={"Idempotency-Key": new_key()},
    )
    assert published.status_code == 201, published.text
    return dict(published.json())


def approve(registry: JaneClient, ref: dict[str, Any], reason: str) -> None:
    r = registry.api("registry").post(
        f"/v1/packages/{ref['package_id']}/versions/{ref['version']}/status",
        json={"status": "approved", "reason": reason},
        headers={"Idempotency-Key": new_key()},
    )
    assert r.status_code == 200, r.text


def ref_of(version: dict[str, Any]) -> dict[str, Any]:
    return {k: version[k] for k in ("package_id", "version", "digest")}


# ---------------------------------------------------------------------------- orchestrator
def stage_handler(orch: JaneClient, task_id: str, stage_id: str) -> dict[str, Any]:
    r = orch.api("orchestrator").get(f"/v1/tasks/{task_id}")
    assert r.status_code == 200, r.text
    (stage,) = [s for s in r.json()["stages"] if s["stage_id"] == stage_id]
    return dict(stage["handler"])


def activations(orch: JaneClient, task_id: str, stage_id: str) -> list[dict[str, Any]]:
    r = orch.api("orchestrator").get(f"/v1/tasks/{task_id}/stages/{stage_id}/activations")
    assert r.status_code == 200, r.text
    return list(r.json()["items"])


def problem_group(orch: JaneClient, source_id: str, package_id: str) -> dict[str, Any]:
    r = orch.api("orchestrator").get("/v1/problem-groups", params={"source_id": source_id})
    assert r.status_code == 200, r.text
    (group,) = [g for g in r.json()["items"] if (g.get("package") or {}).get("package_id") == package_id]
    return dict(group)


def items_by_path(orch: JaneClient, run_id: str, stage_id: str, path_of: dict[str, str]) -> dict[str, Any]:
    return {path_of[i["material_id"]]: i for i in list_items(orch, run_id, stage_id)}


def reprocess(
    orch: JaneClient, task_id: str, material_ids: list[str], since: str, reason: str
) -> dict[str, Any]:
    """``/v1/reprocessing`` of stored RAW from the extractor stage on. ``since`` keeps RAW stored by earlier
    scenarios on a reused stack out: material ids depend only on the URL, and the orchestrator filters the
    objects of the connection by ``material_ids`` only (not by the task's source - see WP-13.md)."""
    body = {
        "task_id": task_id,
        "stored_materials": {
            "storage_connection_id": "raw-files",
            "material_ids": material_ids,
            "since": since,
        },
        "from_stage": "extract-products",
        "reason": reason,
    }
    r = orch.api("orchestrator").post("/v1/reprocessing", json=body, headers={"Idempotency-Key": new_key()})
    assert r.status_code == 202, r.text
    run = wait_run(orch, r.json()["job_id"])
    assert run["status"] == "succeeded", run
    return run


# ---------------------------------------------------------------------------- improvement (S-M2-07, R-07)
def samples_of(
    runtime: JaneClient, run_items: dict[str, Any], stored: dict[str, str], paths: tuple[str, ...]
) -> list[dict[str, Any]]:
    """``ProblemSample`` documents: the stored RAW by reference and the runtime's own ``HandlerResult``."""
    out = []
    for path in paths:
        item = run_items[path]
        r = runtime.api("handler").get(f"/v1/invocations/{item['invocation_id']}")
        assert r.status_code == 200, r.text
        result = r.json()
        sample: dict[str, Any] = {
            "material_ref": {"storage_connection_id": "raw-files", "object_id": stored[item["material_id"]]},
            "result": result,
        }
        if messages := (result.get("diagnostics") or {}).get("messages"):
            sample["diagnostics"] = messages
        out.append(sample)
    return out


def start_improvement(assistant: JaneClient, body: dict[str, Any]) -> str:
    """``POST /v1/improvement-runs`` with a fresh ``Idempotency-Key``; returns the job id."""
    r = assistant.api("assistant").post(
        "/v1/improvement-runs", json=body, headers={"Idempotency-Key": new_key()}
    )
    assert r.status_code == 202, r.text
    return str(r.json()["job_id"])


def improve(assistant: JaneClient, body: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    job_id = start_improvement(assistant, body)
    job = assistant.wait_job("assistant", job_id, timeout_s=600)
    assert job["status"] == "succeeded", job
    return str(job["job_id"]), dict(job["result"])


@dataclass
class Improvable:
    """S-M2-07 set-up: extractor 1.0.0 in the registry, a source that allows automatic LLM versions, two tasks
    bound to it, a first run that left two pages ``unrecognized``, and the improvement request built from it."""

    package_id: str
    v1: dict[str, Any]  # PackageVersion 1.0.0 as published
    source_id: str
    task_id: str  # the catalog task (all four product pages)
    recheck_id: str  # a second binding of the same package
    first: dict[str, Any]  # the first run
    stored: dict[str, str]  # material id -> object id of the stored RAW
    path_of: dict[str, str]  # material id -> site path
    run1: dict[str, Any]  # site path -> extract-products item of the first run
    group: dict[str, Any]  # the problem group of the first run
    request: dict[str, Any]  # ImprovementRequest

    @property
    def old(self) -> dict[str, Any]:
        return ref_of(self.v1)

    @property
    def mid(self) -> dict[str, str]:
        return {p: m for m, p in self.path_of.items()}


def prepare_improvable(flows: Flows, prefix: str, scenario: str) -> Improvable:
    """Publishes the fixture extractor as ``<prefix>.improvable-product-extractor`` 1.0.0 (approved), creates
    the source ``<prefix>`` (``llm_versions: auto_after_checks``) with the catalog and recheck tasks, runs the
    catalog task once and reads the problem group: 1.0.0 does not recognise out-of-stock and pre-order cards."""
    registry, runtime = flows["registry"], flows["handler-runtime"]
    orch, storage = flows["orchestrator"], flows["storage"]
    package_id = f"{prefix}.improvable-product-extractor"
    v1 = publish_fixture(registry, IMPROVABLE, package_id)
    assert v1["manifest"]["provenance"]["created_by"] == "human"
    old = ref_of(v1)
    approve(registry, old, "e2e: human-written baseline")
    source_id = prefix
    create_source(orch, source_id, change_policy={"llm_versions": "auto_after_checks"})
    task_id, recheck_id = f"{prefix}-catalog", f"{prefix}-recheck"
    create_task(orch, m1_task(task_id, source_id, [TESTSITE + p for p in PRODUCT_URLS], old))
    create_task(orch, m1_task(recheck_id, source_id, [TESTSITE + SUCCESSES[0]], old))

    first = wait_run(orch, start_run(orch, task_id))
    assert first["status"] == "succeeded", first
    stored_objects = objects_by_source(storage, "raw-files", source_id)
    stored = {o["material"]["material_id"]: o["object"]["object_id"] for o in stored_objects}
    path_of = {
        o["material"]["material_id"]: o["material"]["url"].removeprefix(TESTSITE) for o in stored_objects
    }
    assert set(path_of.values()) == set(PRODUCT_URLS), path_of
    mid = {p: m for m, p in path_of.items()}
    run1 = items_by_path(orch, first["run_id"], "extract-products", path_of)
    assert {p: i["result_status"] for p, i in run1.items()} == PRODUCT_URLS
    note(scenario, "run 1 (1.0.0)", {p: i["result_status"] for p, i in sorted(run1.items())})
    group = problem_group(orch, source_id, package_id)
    note(
        scenario,
        "problem group",
        {k: group[k] for k in ("problem", "signature", "count", "status", "package")},
    )
    assert (group["problem"], group["signature"], group["count"]) == (
        "unrecognized",
        "unknown-availability",
        2,
    )
    assert group["package"]["version"] == "1.0.0" and group["status"] == "open", group
    assert {s["material_id"] for s in group.get("samples") or []} <= {mid[p] for p in PROBLEMS}, group

    request = {
        "package": {"package_id": package_id, "version": "1.0.0"},
        "source_id": source_id,
        "problem_group_id": group["group_id"],
        "problem_samples": samples_of(runtime, run1, stored, PROBLEMS),
        "successful_examples": samples_of(runtime, run1, stored, SUCCESSES),
        "policy": {"approval": "auto_after_checks", "allow_fork": True},
    }
    return Improvable(
        package_id, v1, source_id, task_id, recheck_id, first, stored, path_of, run1, group, request
    )
