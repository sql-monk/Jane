"""Criterion 9 (S-M2-01, continuation): LLM, storage and collector-rules packages of the one registry.

S-M2-01 (``test_m2_registry.py``) published all four kinds and proved the extractor path: archive from the
registry, ``digest_mismatch``, an immutable fork and an explicit upstream port. This module proves the rest of
criterion 9 by what the executors actually ran and wrote, on an isolated stack of real services (Р): registry
(PostgreSQL + MinIO), orchestrator, Web Collector, storage (files + PostgreSQL) and the LLM gateway with its
handler. SUBSTITUTE (З): the external LLM is the deterministic provider ``fake`` of WP-10 whose answers are
scripted in ``tests/e2e/config/llm-seed.yaml``; the scripted answer for the test-site event page differs when
the request carries the input template of ``e2e.llm-page-triage@1.1.0``, so the answer tells which package
version reached the model.

* LLM: ``e2e.llm-page-triage`` exists only in the registry (the gateway's local package directory has no copy
  and ``package-host`` is not started); its tests and a task stage pinned to its digest run on the gateway; a
  digest of another version is refused. Its fork keeps version 1.0.0 after the parent's 1.1.0, the task pinned
  to the fork's 1.0.0 keeps answering like 1.0.0, and only the explicit port (fork 1.1.0) brings the template.
* storage: task stages pin ``jane.storage-files`` / ``jane.storage-postgresql`` 1.0.0 with the registry digests,
  which storage verifies against the package it executes; version 1.0.0 cannot be replaced in the registry; a
  stage pinned to other content gets ``digest_mismatch`` and writes nothing. The fork stays 1.0.0 until the
  explicit port; storage runs each fork version from the registry in a pinned task or exactly as given in
  ``package_archive`` (ADR-0009) and refuses a substituted archive.
* collector rules: a source pinned to a fork of ``testsite.web-rules`` keeps collecting with the fork's 1.0.0
  rules after the parent excluded ``/pages/*``; a source pinned to the ported fork 1.1.0 applies the exclusion.
* A task stage pinned to a storage fork runs the registry version without ``package_archive``; a foreign digest
  or a substituted archive is refused before any write.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx
import pytest
import yaml

from jane_e2e.clients import JaneClient
from jane_e2e.materials import delivery_key
from jane_e2e.orchestration import (
    TESTSITE,
    create_source,
    create_task,
    list_items,
    put_connections,
    start_run,
    wait_run,
)
from jane_e2e.registry import (
    FILES_DIR,
    POSTGRES_DIR,
    RULES_DIR,
    archive,
    archive_file,
    archive_paths,
    fork,
    key,
    new_parent_version,
    package_diff,
    package_files,
    port_upstream,
    publish,
    publish_storage_packages,
    publish_version,
    ref_of,
    registry_stack,
    run_stage_handler,
    upstream,
    version,
)
from jane_e2e.stack import E2EStack
from jane_e2e.steps import collector_fetch
from jane_e2e.verify import entities, objects_by_source
from jane_registry.archive import canonical_archive, manifest_bytes

pytestmark = [pytest.mark.e2e, pytest.mark.milestone("M2"), pytest.mark.criteria(7, 9)]

E2E_DIR = Path(__file__).resolve().parent
SERVICES = ("registry", "storage", "web-collector", "orchestrator", "llm")
TRIAGE_DIR = E2E_DIR / "packages" / "e2e.llm-page-triage"
TRIAGE, FILES, POSTGRES, RULES = (
    "e2e.llm-page-triage",
    "jane.storage-files",
    "jane.storage-postgresql",
    "testsite.web-rules",
)
SEED = E2E_DIR / "config" / "llm-seed.yaml"
EVENT_PAGE = "/pages/event-spring-meetup"  # testsite page_types: unknown; scripted triage in llm-seed.yaml
TEMPLATE = "prompts/input.md"
TEMPLATE_TEXT = "Page triage input (template 1.1)\nURL: {{material.locator.url}}\n\n{{content}}\n"
SUCCESS = {"field": "result.status", "op": "eq", "value": "success"}
RUN_TIMEOUT_S = float(os.environ.get("JANE_E2E_RUN_TIMEOUT_S", "600"))


def scripted_triage(condition: Callable[[dict[str, Any]], bool]) -> dict[str, Any]:
    """The triage the fake model answers for the first script of ``e2e-fake-scripts`` matching ``condition``."""
    seed = yaml.safe_load(SEED.read_text(encoding="utf-8"))
    (connection,) = [c for c in seed["connections"] if c["connection_id"] == "e2e-fake-scripts"]
    script = next(s for s in connection["params"]["responses"] if condition(s))
    (triage,) = script["output"]["page_triages"]
    return dict(triage)


# The answer to the plain page (versions without the template) and to the page wrapped into template 1.1.
TRIAGE_V1 = scripted_triage(lambda s: s.get("when_data_contains") == "<h1>Spring meetup</h1>")
TRIAGE_V11 = scripted_triage(lambda s: "template 1\\.1" in str(s.get("when_data_matches", "")))


def note(what: str, value: Any = None) -> None:
    """One evidence line for the report (visible with ``pytest -s``)."""
    text = what if value is None else f"{what}: {json.dumps(value, ensure_ascii=False, sort_keys=True)}"
    print(f"[C9] {text}", flush=True)


# ---------------------------------------------------------------------------- stack and packages
@dataclass
class Registry9:
    """The module's stack, its clients, the 1.0.0 versions published in the registry and their local files."""

    stack: E2EStack
    clients: dict[str, JaneClient] = field(default_factory=dict)
    published: dict[str, dict[str, Any]] = field(default_factory=dict)
    sources: dict[str, tuple[dict[str, Any], dict[str, bytes]]] = field(default_factory=dict)

    def __getitem__(self, service: str) -> JaneClient:
        if service not in self.clients:
            self.clients[service] = JaneClient(self.stack.url(service))
        return self.clients[service]

    def ref(self, package_id: str) -> dict[str, str]:
        return ref_of(self.published[package_id])


@pytest.fixture(scope="module")
def r9(stack: E2EStack) -> Iterator[Registry9]:
    """Isolated stack (``stack`` - the session one - only checks Docker): every executor takes packages from the
    real registry. Publishes the six built-in storage packages (WP-07 CLI), the test-site rules and the LLM
    triage package as 1.0.0 drafts."""
    with registry_stack("types", SERVICES) as own:
        own.ensure(*SERVICES)
        r9 = Registry9(own)
        try:
            registry = r9["registry"]
            printed = publish_storage_packages(own.url("registry"))
            for package_id, directory in ((FILES, FILES_DIR), (POSTGRES, POSTGRES_DIR)):
                assert f"{package_id}@1.0.0" in printed, printed
                r9.published[package_id] = version(registry, package_id, "1.0.0")
                r9.sources[package_id] = package_files(directory)
            for directory in (RULES_DIR, TRIAGE_DIR):
                manifest, files = package_files(directory)
                r9.published[manifest["package_id"]] = publish(registry, manifest, files)
                r9.sources[manifest["package_id"]] = (manifest, files)
            put_connections(r9["orchestrator"])
            note("stack", {"project": own.project, "published": {p: r9.ref(p) for p in r9.published}})
            yield r9
        finally:
            for client in r9.clients.values():
                client.close()


# ---------------------------------------------------------------------------- task helpers
def collect_stage() -> dict[str, Any]:
    return {"stage_id": "collect", "kind": "collect", "collector": {"collector": "web", "mode": "full"}}


def store_stage(stage_id: str, handler: dict[str, str], connection: str, **inputs: Any) -> dict[str, Any]:
    return {
        "stage_id": stage_id,
        "kind": "handler",
        "handler": handler,
        "connections": {"target": connection},
        "inputs": [{"from": "collect", **inputs}],
    }


def new_task(
    r9: Registry9,
    name: str,
    urls: list[str],
    stages: list[dict[str, Any]],
    rules: dict[str, str] | None = None,
) -> tuple[str, str]:
    """A source pinned to ``rules`` (default: registry rules 1.0.0) and its task; returns (source, task)."""
    source_id = f"c9-{name}"
    create_source(r9["orchestrator"], source_id, collector_rules=rules or r9.ref(RULES))
    task = {
        "task_id": f"{source_id}-task",
        "title": f"e2e criterion 9 {name}",
        "input": {"source_id": source_id, "urls": [TESTSITE + u for u in urls]},
        "stages": [collect_stage(), *stages],
    }
    create_task(r9["orchestrator"], task)
    return source_id, str(task["task_id"])


def run_task(orch: JaneClient, task_id: str) -> dict[str, Any]:
    run = wait_run(orch, start_run(orch, task_id), timeout_s=RUN_TIMEOUT_S)
    assert run["status"] == "succeeded", run
    return run


def assert_fork_unchanged(registry: JaneClient, first: dict[str, Any], first_archive: bytes) -> None:
    """The fork's published version: same document (digest, file list) and byte-for-byte the same archive."""
    ref = ref_of(first)
    now = version(registry, ref["package_id"], ref["version"])
    assert (now["digest"], now["files"], now["manifest"]) == (
        first["digest"],
        first["files"],
        first["manifest"],
    )
    assert archive(registry, ref["package_id"], ref["version"], ref["digest"]) == first_archive


def ported_fork(
    registry: JaneClient, first: dict[str, Any], first_archive: bytes, parent_next: dict[str, Any]
) -> tuple[dict[str, Any], bytes]:
    """Explicit port of the parent's next version into the fork (same version number); the fork's
    ``fork_of`` and its first version stay as they were."""
    fork_id = first["manifest"]["package_id"]
    ported = port_upstream(registry, fork_id, parent_next["version"], parent_next["version"])
    assert ported["manifest"]["fork_of"] == first["manifest"]["fork_of"], ported["manifest"]
    assert ported["manifest"]["provenance"]["upstream_port"]["parent_version"] == parent_next["version"]
    assert ported["digest"] not in {first["digest"], parent_next["digest"]}
    assert_fork_unchanged(registry, first, first_archive)
    assert upstream(registry, fork_id)["newer_parent_versions"] == []
    return ported, archive(registry, fork_id, ported["version"], ported["digest"])


# ---------------------------------------------------------------------------- LLM
def llm_invoke(llm: JaneClient, handler: dict[str, str], key_: str) -> httpx.Response:
    """Direct handler.v1 call of the LLM handler (outside a task) with one data input."""
    body = {
        "handler": handler,
        "inputs": [{"kind": "data", "data": {"note": "criterion 9 digest check"}}],
        "context": {"trace": {"stage_id": "c9-digest-check"}},
        "delivery": {"delivery_key": key_},
        "mode": "sync",
    }
    return llm.api("handler").post("/v1/invocations", json=body, headers={"Idempotency-Key": key_})


def triage_task(r9: Registry9, name: str, handler: dict[str, str]) -> tuple[str, str]:
    """collect (the event page) -> triage (LLM package ``handler``) -> store-triage (PostgreSQL, pinned)."""
    triage = {"stage_id": "triage", "kind": "handler", "handler": handler, "inputs": [{"from": "collect"}]}
    store = store_stage("store-triage", r9.ref(POSTGRES), "results-pg", select="output", when=SUCCESS)
    store["inputs"][0]["from"] = "triage"
    return new_task(r9, name, [EVENT_PAGE], [triage, store])


def triaged(r9: Registry9, source_id: str, task_id: str, handler: dict[str, str]) -> dict[str, Any]:
    """Run the triage task; returns what the model answered (``page_type``, ``summary``, ``suggested_fix``).

    The LLM handler reports the package it loaded (id, version, digest of the archive) - it must be the pinned
    one, in its result and in the orchestrator's trace; the stored entity is that answer."""
    orch, llm = r9["orchestrator"], r9["llm"]
    run = run_task(orch, task_id)
    assert run_stage_handler(orch, run["run_id"], "triage") == handler
    assert run_stage_handler(orch, run["run_id"], "store-triage") == r9.ref(POSTGRES)
    (item,) = list_items(orch, run["run_id"], "triage")
    response = llm.api("handler").get(f"/v1/invocations/{item['invocation_id']}")
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["status"] == "success" and result["handler"] == handler, result
    assert result["usage"]["llm"]["provider"] == "e2e-fake", result["usage"]
    (entity,) = result["output"]["entities"]
    assert entity["entity_type"] == "page_triage"
    assert entity["schema"] == f"{handler['package_id']}@{handler['version']}#page_triage"
    (stored,) = entities(r9["storage"], "results-pg", source_id, "page_triage")
    assert stored["fields"] == entity["fields"], (stored, entity)
    answer = {k: v for k, v in entity["fields"].items() if k != "material_id"}
    note(f"triage {task_id}", {"handler": handler, "answer": answer, "run": run["run_id"]})
    return answer


def test_llm_package_from_registry_runs_in_tasks_and_its_fork_stays_pinned(
    r9: Registry9, run_id: str
) -> None:
    registry, llm = r9["registry"], r9["llm"]
    parent = r9.published[TRIAGE]
    parent_ref = r9.ref(TRIAGE)
    assert TRIAGE_V1 != TRIAGE_V11

    # The package's own tests run on the LLM gateway against the registry archive (no local copy anywhere).
    started = llm.api("handler").post(
        "/v1/test-runs", json={"handler": parent_ref, "tests": "all"}, headers={"Idempotency-Key": key()}
    )
    assert started.status_code == 202, started.text
    job = llm.wait_job("handler", started.json()["job_id"])
    assert job["status"] == "succeeded", job
    report = job["result"]
    assert report["package"] == parent_ref, report["package"]
    assert (report["passed"], report["failed"]) == (2, 0), report
    note("package tests on the gateway", {c["name"]: c["actual_status"] for c in report["cases"]})

    # 1. A task stage pinned to the registry digest: the gateway executes exactly that archive.
    parent_task = triage_task(r9, f"llm-parent-{run_id}", parent_ref)
    assert triaged(r9, *parent_task, parent_ref) == TRIAGE_V1

    # 2. A fork of the LLM package, pinned in its own task.
    fork_id = f"{TRIAGE}-{run_id}"
    fork_v1 = fork(registry, parent, fork_id)
    fork_v1_ref = ref_of(fork_v1)
    fork_v1_archive = archive(registry, fork_id, "1.0.0", fork_v1_ref["digest"])
    fork_task = triage_task(r9, f"llm-fork-{run_id}", fork_v1_ref)
    assert triaged(r9, *fork_task, fork_v1_ref) == TRIAGE_V1

    # 3. The parent's 1.1.0 wraps the page into an input template; the fork does not change.
    def add_template(manifest: dict[str, Any], files: dict[str, bytes]) -> None:
        manifest["entry"]["input_template"] = TEMPLATE
        files[TEMPLATE] = TEMPLATE_TEXT.encode("utf-8")

    manifest, files = r9.sources[TRIAGE]
    parent_v2 = publish_version(
        registry, *new_parent_version(manifest, files, "1.1.0", "Input template for the page.", add_template)
    )
    parent_v2_ref = ref_of(parent_v2)
    assert TEMPLATE in archive_paths(archive(registry, TRIAGE, "1.1.0", parent_v2_ref["digest"]))
    assert_fork_unchanged(registry, fork_v1, fork_v1_archive)
    assert TEMPLATE not in archive_paths(fork_v1_archive)
    assert upstream(registry, fork_id)["newer_parent_versions"] == ["1.1.0"]
    changed_files, changed_manifest = package_diff(registry, fork_id, "1.0.0", "parent:1.1.0")
    assert changed_files[TEMPLATE] == "added", changed_files
    assert changed_manifest["/entry/input_template"] == "add", changed_manifest

    # The gateway refuses an archive whose digest is not the pinned one (1.0.0 with the digest of 1.1.0).
    wrong = llm_invoke(llm, {**parent_ref, "digest": parent_v2_ref["digest"]}, f"c9-llm-wrong-{run_id}")
    assert wrong.status_code == 422 and wrong.json()["code"] == "digest_mismatch", wrong.text

    # Tasks pinned to 1.0.0 (parent and fork) answer as before; a task pinned to the parent's 1.1.0 shows
    # that the new version does change the answer.
    assert triaged(r9, *parent_task, parent_ref) == TRIAGE_V1
    assert triaged(r9, *fork_task, fork_v1_ref) == TRIAGE_V1
    parent_v2_task = triage_task(r9, f"llm-parent-v2-{run_id}", parent_v2_ref)
    assert triaged(r9, *parent_v2_task, parent_v2_ref) == TRIAGE_V11

    # 4. Only the explicit port brings the parent's change into the fork, as a new fork version.
    ported, ported_archive = ported_fork(registry, fork_v1, fork_v1_archive, parent_v2)
    assert ported["manifest"]["entry"]["input_template"] == TEMPLATE
    assert archive_file(ported_archive, TEMPLATE) == TEMPLATE_TEXT.encode("utf-8")
    ported_task = triage_task(r9, f"llm-fork-ported-{run_id}", ref_of(ported))
    assert triaged(r9, *ported_task, ref_of(ported)) == TRIAGE_V11

    # 5. The task pinned to the fork's 1.0.0 still executes exactly that version.
    assert triaged(r9, *fork_task, fork_v1_ref) == TRIAGE_V1


def test_llm_refuses_a_digest_of_another_version_also_after_caching_it(r9: Registry9, run_id: str) -> None:
    registry, llm = r9["registry"], r9["llm"]
    manifest, files = r9.sources[TRIAGE]
    own = {**json.loads(json.dumps(manifest)), "package_id": f"{TRIAGE}-cache-{run_id}"}

    def reword(next_manifest: dict[str, Any], next_files: dict[str, bytes]) -> None:
        path = next_manifest["entry"]["instructions"]
        next_files[path] = next_files[path] + b"\nKeep the summary under twenty words.\n"

    v1_ref = ref_of(publish(registry, own, files))
    v2_ref = ref_of(publish_version(registry, *new_parent_version(own, files, "1.0.1", "Shorter.", reword)))
    foreign = {**v1_ref, "digest": v2_ref["digest"]}
    cold = llm_invoke(llm, foreign, f"c9-llm-cold-{run_id}")
    if cold.status_code != 422 or cold.json().get("code") != "digest_mismatch":
        pytest.fail(f"cold cache must refuse the foreign digest: {cold.status_code} {cold.text}")
    warm = llm_invoke(llm, v2_ref, f"c9-llm-warm-{run_id}")
    if warm.status_code != 200 or warm.json()["handler"] != v2_ref:
        pytest.fail(f"pinned 1.0.1 must run: {warm.status_code} {warm.text}")

    again = llm_invoke(llm, foreign, f"c9-llm-again-{run_id}")
    note(
        "LLM foreign digest after caching",
        {"requested": foreign, "status": again.status_code, "ran": again.json().get("handler")},
    )
    if again.status_code == 200 and again.json()["handler"] == v2_ref:
        pytest.fail(f"a reference to 1.0.0 with the 1.0.1 digest executed {again.json()['handler']}")
    assert again.status_code == 422 and again.json()["code"] == "digest_mismatch", again.text


# ---------------------------------------------------------------------------- storage
def raw_task(r9: Registry9, name: str, urls: list[str], files_ref: dict[str, str]) -> tuple[str, str]:
    """collect -> store-raw (files, ``files_ref``) || store-raw-pg (PostgreSQL, registry digest)."""
    stages = [
        store_stage("store-raw", files_ref, "raw-files"),
        store_stage("store-raw-pg", r9.ref(POSTGRES), "results-pg"),
    ]
    return new_task(r9, name, urls, stages)


def raw_objects(storage: JaneClient, connection: str, source_id: str) -> dict[str, dict[str, Any]]:
    """``observation_id -> stored object`` of a source in one connection."""
    return {
        o["material"]["observation_id"]: o["object"]
        for o in objects_by_source(storage, connection, source_id)
    }


def store_with_archive(
    storage: JaneClient, handler: dict[str, str], package: bytes, material: dict[str, Any]
) -> httpx.Response:
    """handler.v1 call of storage with the package given as ``package_archive`` (ADR-0009)."""
    key_ = delivery_key("c9-archive", handler["digest"], material["observation_id"])
    body = {
        "handler": handler,
        "package_archive": {
            "kind": "inline",
            "media_type": "application/zip",
            "encoding": "base64",
            "data": base64.b64encode(package).decode("ascii"),
            "size_bytes": len(package),
            "sha256": hashlib.sha256(package).hexdigest(),
        },
        "connections": {"target": "raw-files"},
        "inputs": [{"kind": "material", "material": material}],
        "context": {"trace": {"stage_id": "c9-archive"}},
        "delivery": {"delivery_key": key_},
    }
    return storage.api("handler").post("/v1/invocations", json=body, headers={"Idempotency-Key": key_})


def test_storage_stages_pin_registry_digests_and_storage_forks_stay_pinned(
    r9: Registry9, run_id: str
) -> None:
    registry, orch, storage = r9["registry"], r9["orchestrator"], r9["storage"]
    parent = r9.published[FILES]
    files_ref, pg_ref = r9.ref(FILES), r9.ref(POSTGRES)
    parent_archive = archive(registry, FILES, "1.0.0", files_ref["digest"])

    # 1. Storage stages pinned to the registry digests: storage checks them against the package it executes
    # and reports that package (id, version, digest) in its result and the orchestrator's trace.
    source_id, task_id = raw_task(r9, f"storage-{run_id}", ["/product/phone-alpha"], files_ref)
    first = run_task(orch, task_id)
    assert run_stage_handler(orch, first["run_id"], "store-raw") == files_ref
    assert run_stage_handler(orch, first["run_id"], "store-raw-pg") == pg_ref
    stored = raw_objects(storage, "raw-files", source_id)
    assert [o["media_type"] for o in stored.values()] == ["text/html"], stored
    assert len(raw_objects(storage, "results-pg", source_id)) == 1

    # 2. A fork of jane.storage-files, then the parent's 1.1.0: web pages stored as a JSON Material document.
    fork_id = f"{FILES}-{run_id}"
    fork_v1 = fork(registry, parent, fork_id)
    fork_v1_ref = ref_of(fork_v1)
    fork_v1_archive = archive(registry, fork_id, "1.0.0", fork_v1_ref["digest"])
    assert fork_v1["manifest"]["required_connections"] == parent["manifest"]["required_connections"]

    def raw_as_json(manifest: dict[str, Any], files: dict[str, bytes]) -> None:
        manifest["entry"]["format"]["raw"] = "json"

    manifest, files = r9.sources[FILES]
    parent_v2_manifest, parent_v2_files = new_parent_version(
        manifest, files, "1.1.0", "RAW of web pages as a JSON Material document.", raw_as_json
    )
    parent_v2 = publish_version(registry, parent_v2_manifest, parent_v2_files)
    assert parent_v2["digest"] != files_ref["digest"]

    # The published 1.0.0 cannot be replaced: the same content under 1.0.0 is refused, the archive stays.
    replaced = registry.api("registry").post(
        f"/v1/packages/{FILES}/versions",
        json={
            "manifest": {**parent_v2_manifest, "version": "1.0.0"},
            "files": {
                p: {"encoding": "utf-8", "data": d.decode("utf-8")} for p, d in parent_v2_files.items()
            },
        },
        headers={"Idempotency-Key": key()},
    )
    assert replaced.status_code == 409 and replaced.json()["code"] == "version_exists", replaced.text
    assert archive(registry, FILES, "1.0.0", files_ref["digest"]) == parent_archive

    assert_fork_unchanged(registry, fork_v1, fork_v1_archive)
    assert upstream(registry, fork_id)["newer_parent_versions"] == ["1.1.0"]
    _, changed_manifest = package_diff(registry, fork_id, "1.0.0", "parent:1.1.0")
    assert changed_manifest["/entry/format/raw"] == "add", changed_manifest

    # 3. The pinned task after the parent's new version: the same package, RAW still stored as HTML.
    # The forked task below distinguishes versions through their actual storage output.
    second = run_task(orch, task_id)
    assert run_stage_handler(orch, second["run_id"], "store-raw") == files_ref
    stored = raw_objects(storage, "raw-files", source_id)
    assert len(stored) == 2 and {o["media_type"] for o in stored.values()} == {"text/html"}, stored

    # 4. A stage pinned to content that storage does not execute (1.0.0 with the 1.1.0 digest) is refused
    # before any write.
    foreign = {**files_ref, "digest": parent_v2["digest"]}
    wrong_source, wrong_task = raw_task(r9, f"storage-wrong-{run_id}", ["/product/phone-alpha"], foreign)
    wrong = wait_run(orch, start_run(orch, wrong_task), timeout_s=RUN_TIMEOUT_S)
    (refused,) = list_items(orch, wrong["run_id"], "store-raw")
    assert refused["status"] == "failed" and refused["error"]["code"] == "digest_mismatch", refused
    assert raw_objects(storage, "raw-files", wrong_source) == {}
    assert len(raw_objects(storage, "results-pg", wrong_source)) == 1  # the correctly pinned branch ran
    note("storage stage pinned to a foreign digest", {"run": wrong["status"], "error": refused["error"]})

    # 5. The explicit port gives the fork its 1.1.0; storage executes each fork version exactly as given in
    # package_archive (autonomous use, ADR-0009) and refuses a substituted archive.
    ported, ported_archive = ported_fork(registry, fork_v1, fork_v1_archive, parent_v2)
    assert ported["manifest"]["entry"]["format"]["raw"] == "json"
    collector = r9["web-collector"]
    direct_source = f"c9-storage-direct-{run_id}"
    written: dict[str, str] = {}
    for ref, package in ((fork_v1_ref, fork_v1_archive), (ref_of(ported), ported_archive)):
        material = collector_fetch(collector, f"{TESTSITE}/product/phone-beta", direct_source)
        response = store_with_archive(storage, ref, package, material)
        assert response.status_code == 200, response.text
        result = response.json()
        assert result["status"] == "success" and result["handler"] == ref, result
        (ack,) = result["output"]["writes"]
        assert ack["status"] == "written", ack
        written[ref["version"]] = raw_objects(storage, "raw-files", direct_source)[
            material["observation_id"]
        ]["media_type"]
    assert written == {"1.0.0": "text/html", "1.1.0": "application/json"}, written

    substituted = {path: archive_file(fork_v1_archive, path) for path in archive_paths(fork_v1_archive)}
    tampered = dict(json.loads(substituted["jane-package.json"]), description="Substituted content.")
    substituted["jane-package.json"] = manifest_bytes(tampered)
    material = collector_fetch(collector, f"{TESTSITE}/product/phone-beta", direct_source)
    response = store_with_archive(storage, fork_v1_ref, canonical_archive(substituted), material)
    assert response.status_code == 422 and response.json()["code"] == "digest_mismatch", response.text
    assert material["observation_id"] not in raw_objects(storage, "raw-files", direct_source)
    note("storage fork versions via package_archive", written)


def test_storage_fork_pinned_in_a_task_runs_that_fork(r9: Registry9, run_id: str) -> None:
    registry, orch, storage = r9["registry"], r9["orchestrator"], r9["storage"]
    fork_ref = ref_of(fork(registry, r9.published[FILES], f"{FILES}-task-{run_id}"))
    source_id, task_id = new_task(
        r9,
        f"storage-fork-{run_id}",
        ["/product/phone-alpha"],
        [store_stage("store-raw", fork_ref, "raw-files")],
    )
    run = wait_run(orch, start_run(orch, task_id), timeout_s=RUN_TIMEOUT_S)
    (item,) = list_items(orch, run["run_id"], "store-raw")
    note(
        "storage fork pinned in a task",
        {"run": run["status"], "item": item["status"], "error": item.get("error")},
    )
    assert item["status"] == "completed", item
    assert run_stage_handler(orch, run["run_id"], "store-raw") == fork_ref
    assert len(raw_objects(storage, "raw-files", source_id)) == 1


# ---------------------------------------------------------------------------- collector rules
RULES_URLS = ["/product/phone-alpha", "/pages/careers"]


def collected(r9: Registry9, source_id: str, task_id: str, rules_ref: dict[str, str]) -> set[str]:
    """Run the RAW task of a source pinned to ``rules_ref``; returns the paths the collector delivered in this run.

    Every delivered material carries the rules it was collected with (``collector.rules``)."""
    orch, storage = r9["orchestrator"], r9["storage"]
    run = run_task(orch, task_id)
    observations = {i["observation_id"] for i in list_items(orch, run["run_id"], "store-raw")}
    objects = [
        o
        for o in objects_by_source(storage, "raw-files", source_id)
        if o["material"]["observation_id"] in observations
    ]
    assert len(objects) == len(observations) == run["counters"]["materials"], (objects, run["counters"])
    for o in objects:
        detail = storage.api("storage").get(
            f"/v1/objects/{o['object']['object_id']}", params={"connection_id": "raw-files"}
        )
        assert detail.status_code == 200, detail.text
        material = detail.json()["material"]
        assert material["collector"]["name"] == "web-collector"
        assert material["collector"]["rules"] == rules_ref, material["collector"]
    paths = {str(o["material"]["url"]).removeprefix(TESTSITE) for o in objects}
    note(f"collected {task_id}", {"rules": rules_ref, "paths": sorted(paths), "run": run["run_id"]})
    return paths


def test_collector_rules_fork_pinned_in_a_source_keeps_its_rules(r9: Registry9, run_id: str) -> None:
    registry = r9["registry"]
    parent = r9.published[RULES]
    stages = [store_stage("store-raw", r9.ref(FILES), "raw-files")]

    # 1. A fork of the rules; a source pinned to its 1.0.0 collects both URLs.
    fork_id = f"{RULES}-{run_id}"
    fork_v1 = fork(registry, parent, fork_id)
    fork_v1_ref = ref_of(fork_v1)
    fork_v1_archive = archive(registry, fork_id, "1.0.0", fork_v1_ref["digest"])
    pinned = new_task(r9, f"rules-fork-{run_id}", RULES_URLS, stages, rules=fork_v1_ref)
    assert collected(r9, *pinned, fork_v1_ref) == set(RULES_URLS)

    # 2. The parent's 1.1.0 excludes /pages/*; the fork and the pinned source do not change.
    def exclude_pages(manifest: dict[str, Any], files: dict[str, bytes]) -> None:
        rules = json.loads(files["rules.json"])
        rules["scope"]["exclude"].append({"value": "*/pages/*"})
        files["rules.json"] = (json.dumps(rules, indent=2) + "\n").encode("utf-8")

    manifest, files = r9.sources[RULES]
    parent_v2 = publish_version(
        registry, *new_parent_version(manifest, files, "1.1.0", "Exclude /pages/*.", exclude_pages)
    )
    parent_v2_archive = archive(registry, RULES, "1.1.0", parent_v2["digest"])
    assert_fork_unchanged(registry, fork_v1, fork_v1_archive)
    assert upstream(registry, fork_id)["newer_parent_versions"] == ["1.1.0"]
    assert package_diff(registry, fork_id, "1.0.0", "parent:1.1.0")[0]["rules.json"] == "modified"
    assert collected(r9, *pinned, fork_v1_ref) == set(RULES_URLS)

    # 3. Only the explicit port brings the exclusion; a source pinned to the fork's 1.1.0 applies it.
    ported, ported_archive = ported_fork(registry, fork_v1, fork_v1_archive, parent_v2)
    assert archive_file(ported_archive, "rules.json") == archive_file(parent_v2_archive, "rules.json")
    ported_ref = ref_of(ported)
    excluding = new_task(r9, f"rules-ported-{run_id}", RULES_URLS, stages, rules=ported_ref)
    assert collected(r9, *excluding, ported_ref) == {"/product/phone-alpha"}

    # 4. The source pinned to the fork's 1.0.0 still collects with exactly those rules.
    assert collected(r9, *pinned, fork_v1_ref) == set(RULES_URLS)
