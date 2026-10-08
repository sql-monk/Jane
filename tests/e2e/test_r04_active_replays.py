"""R-04 (criterion 8) while the work is still running: a replay with the same ``Idempotency-Key`` /
``delivery_key`` reaches an executor before the first request's work has finished.

``test_r04_idempotency.py`` covers replays after the work (same instance, another replica, after ``docker kill``)
and the Web Collector during an active collection; this module covers the other executors. What the contract
expects (``common.yaml#/components/parameters/IdempotencyKey``, ``contracts/docs/errors.md``):

* an asynchronous operation (``202`` + ``Job``) has already answered, so the replay gets the stored answer -
  ``202``, the same ``job_id``, ``Idempotency-Replayed: true`` - while the job still runs;
* a synchronous call that has not answered yet gets ``409 idempotency_in_progress`` (``retryable``) and, once it
  has finished, the stored result with ``Idempotency-Replayed: true`` (handler.v1: ``duplicate: true``);
* another body under the same key is ``422 idempotency_key_reused`` - also while the first one runs.

Every scenario also checks that nothing happened twice and that the first work finished normally.

The window of "work still running" is made deterministic, never guessed with sleeps:

* Telegram Collector - per-call pacing ``limits.rate.min_delay_ms_per_host`` over several recorded channels
  (as in the Web Collector scenario); the collection is polled until it runs with some channels fetched
  and others left;
* handler-runtime and orchestrator - the fixture ``tests/e2e/packages/e2e.slow-product-extractor`` keeps one
  extraction in its sandbox for ``params.delay_seconds``; the sandbox is observed by its Docker labels;
* storage, LLM gateway (``/v1/invocations``) and assistant (``/v1/unknown-materials``) - the material content is
  a blob whose ``download_url`` is a *gate* of the ``package-host`` stand-in (``jane_e2e.active.Gate``): the
  service is inside its work while the gate holds its download, and the gate counts downloads;
* registry - ``docker pause`` of MinIO, where the registry stores archives: a port job and a publication cannot
  finish until it is unpaused.

Substitutes (**З**): the recorded Telegram backend, the LLM provider ``fake``, the gate standing in for the blob
store behind ``download_url``. Not covered here (no mechanism holds the work without changing other components,
see docs/delivery/WP-13.md, "WP-13r"): ``/v1/completions`` of the LLM gateway and the onboarding/improvement jobs
of the assistant - the fake provider answers at once.

Operational observations outside the contracts: Docker labels of runtime sandboxes (``io.jane.invocation-id``,
``io.jane.package``, ``io.jane.e2e-project``) and the gate counters of the stand-in.
"""

from __future__ import annotations

import hashlib
import os
from collections.abc import Callable
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import pytest

from jane_e2e.active import gate, package_ref, wait_for
from jane_e2e.clients import TERMINAL_JOB_STATES, JaneClient
from jane_e2e.materials import delivery_key, fetch_page, standin_web_material
from jane_e2e.orchestration import TESTSITE, create_source, create_task, list_items, m1_task, wait_run
from jane_e2e.registry import (
    FILES_DIR,
    fork,
    key,
    new_parent_version,
    package_files,
    publish,
    publish_body,
    publish_version,
)
from jane_e2e.stack import SANDBOX_PROJECT_LABEL, E2EStack
from jane_e2e.steps import sandbox_limits
from jane_e2e.verify import assert_effects_once, entities, objects_by_source
from jane_extractor_sdk.package import build_archive
from jane_telegram_collector.recorded import Recording  # type: ignore[import-untyped]

pytestmark = [pytest.mark.e2e, pytest.mark.milestone("M2"), pytest.mark.criteria(8)]

PACKAGES = Path(__file__).resolve().parent / "packages"
SLOW_EXTRACTOR = PACKAGES / "e2e.slow-product-extractor"
LLM_TRIAGE = PACKAGES / "e2e.llm-page-triage"
PRODUCT = "/product/phone-alpha"
UNKNOWN_PAGE = "/pages/event-spring-meetup"  # page_types: unknown; the triage script answers "event"
# How long one slow extraction stays in its sandbox: the replays are sent while it runs (window, not a timing).
ACTIVE_DELAY_S = float(os.environ.get("JANE_E2E_R04_ACTIVE_DELAY_S", "12"))
# Upper bound of every wait (conditions are polled).
WAIT_S = float(os.environ.get("JANE_E2E_R04_ACTIVE_WAIT_S", "300"))
TELEGRAM_CHANNELS = 6  # one message each; with the pacing below the collection lasts well over 10 s
TELEGRAM_PACING_MS = 1000
INVOCATION_LABEL = "io.jane.invocation-id"
PACKAGE_LABEL = "io.jane.package"
REPLAYED = "Idempotency-Replayed"


# ---------------------------------------------------------------------------- assertions
def assert_in_progress(response: httpx.Response) -> None:
    assert response.status_code == 409, response.text
    problem = response.json()
    assert problem["code"] == "idempotency_in_progress", problem
    assert problem.get("retryable") is True, problem
    assert REPLAYED not in response.headers


def assert_key_reused(response: httpx.Response) -> None:
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "idempotency_key_reused", response.text


def assert_replayed(response: httpx.Response, first: httpx.Response) -> None:
    """The stored answer of ``first`` again (``202`` + Job of an asynchronous operation)."""
    assert response.status_code == first.status_code, response.text
    assert response.headers.get(REPLAYED) == "true", dict(response.headers)
    assert response.json() == first.json()


def job_status(service: JaneClient, api: str, job_id: str) -> str:
    r = service.api(api).get(f"/v1/jobs/{job_id}")
    assert r.status_code == 200, r.text
    return str(r.json()["status"])


def running(service: JaneClient, api: str, job_id: str) -> bool | None:
    """True once the job is ``running``; fails if it ended before the replays."""
    status = job_status(service, api, job_id)
    assert status not in TERMINAL_JOB_STATES, f"job {job_id} already {status}"
    return True if status == "running" else None


def llm_usage(llm: JaneClient, task_id: str) -> dict[str, Any]:
    r = llm.api("llm").get("/v1/usage", params={"scope_type": "task", "scope_id": task_id})
    assert r.status_code == 200, r.text
    return dict(r.json())


def page_material(stack: E2EStack, path: str, source_id: str) -> tuple[httpx.Response, dict[str, Any]]:
    page = fetch_page(stack.url("testsite") + path)
    material = standin_web_material(
        page, source_id=source_id, observation_id=f"obs_{source_id.replace('-', '_')}"
    )
    return page, material


def slow_limits(delay_s: float) -> dict[str, Any]:
    """Limits of one slow extraction: the sandbox outlives ``delay_s`` and a synchronous call still answers
    synchronously, so its key stays ``in_progress`` for the whole call (no stored 202)."""
    wall = max(int(sandbox_limits()["sandbox"]["wall_time_ms"]), int((delay_s + 30) * 1000))
    return {
        "sandbox": {"wall_time_ms": wall},
        "timeouts": {"sync_response_max_ms": wall + 10_000, "invocation_timeout_ms": wall + 30_000},
    }


class Sandboxes:
    """Invocation ids of the runtime sandboxes of one package in this stack, as seen while polling."""

    def __init__(self, stack: E2EStack, package: dict[str, str]) -> None:
        self.stack = stack
        self.labels = {
            SANDBOX_PROJECT_LABEL: stack.project,
            PACKAGE_LABEL: f"{package['package_id']}@{package['version']}",
        }
        self.seen: set[str] = set()

    def poll(self) -> set[str]:
        active = set(self.stack.running_label_values(self.labels, INVOCATION_LABEL))
        self.seen |= active
        return active

    def wait_new(self, known: set[str]) -> str:
        """Wait for a running sandbox whose invocation id is not in ``known``."""

        def fresh() -> str | None:
            new = self.poll() - known
            return sorted(new)[0] if new else None

        return wait_for("slow extraction running in a sandbox", fresh, WAIT_S, poll_s=0.2)


# ---------------------------------------------------------------------------- Telegram Collector
def collection_result(
    collector: JaneClient, collection_id: str
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    api = collector.api("collector")

    def finished() -> dict[str, Any] | None:
        r = api.get(f"/v1/collections/{collection_id}")
        assert r.status_code == 200, r.text
        view = dict(r.json())
        return view if view["status"] in TERMINAL_JOB_STATES else None

    view = wait_for(f"collection {collection_id} finished", finished, WAIT_S, poll_s=0.25)
    assert view["status"] == "succeeded", view
    page = api.get(f"/v1/collections/{collection_id}/materials")
    assert page.status_code == 200, page.text
    assert page.json()["end_of_stream"], page.json()
    return view, list(page.json()["items"])


def test_r_04_telegram_replay_while_collection_is_running(
    stack: E2EStack, require: Callable[..., None], client: Callable[..., JaneClient], run_id: str
) -> None:
    require("telegram-collector")
    collector = client("telegram-collector")
    api = collector.api("collector")
    channels = []
    for i in range(TELEGRAM_CHANNELS):
        username = f"r04a_{run_id}_{i}"
        digits = int(hashlib.sha256(username.encode()).hexdigest()[:12], 16) % 10**10
        recording = Recording.create(
            stack.telegram_recordings_dir,
            channel_id=f"-100{digits:010d}",
            username=username,
            title=f"R-04 active {i}",
        )
        recording.post(f"R-04 active event {i}", date=datetime(2026, 9, 1, 10, i, tzinfo=UTC))
        channels.append({"username": username})
    body: dict[str, Any] = {
        "source_kind": "telegram",
        "source_id": f"r04-tg-active-{run_id}",
        "state_key": f"r04-tg-active-{run_id}",
        "rules": {"collector": "telegram", "channels": channels},
        "mode": "full",
        "limits": {"rate": {"min_delay_ms_per_host": TELEGRAM_PACING_MS}},
    }
    headers = {"Idempotency-Key": f"r04-tg-active-{run_id}"}
    first = api.post("/v1/collections", json=body, headers=headers)
    assert first.status_code == 202, first.text
    collection_id = first.json()["job_id"]

    def running_with_channels_left() -> dict[str, Any] | None:
        r = api.get(f"/v1/collections/{collection_id}")
        assert r.status_code == 200, r.text
        view = dict(r.json())
        assert view["status"] not in TERMINAL_JOB_STATES, view
        fetched = view["stats"]["fetched"]
        # some channels done, others still left: the collection is producing materials when it is replayed
        return view if view["status"] == "running" and 1 <= fetched < len(channels) else None

    before = wait_for("Telegram collection running mid-way", running_with_channels_left, WAIT_S)
    replay = api.post("/v1/collections", json=body, headers=headers)
    assert_replayed(replay, first)
    assert replay.json()["job_id"] == collection_id
    assert_key_reused(api.post("/v1/collections", json={**body, "mode": "incremental"}, headers=headers))
    during = api.get(f"/v1/collections/{collection_id}")
    assert during.status_code == 200, during.text
    assert during.json()["status"] == "running", during.text
    assert during.json()["stats"]["fetched"] < len(channels), during.text

    final, materials = collection_result(collector, collection_id)
    print(
        f"\nR-04 telegram: replay at fetched={before['stats']['fetched']}/{len(channels)}, final {final['stats']}"
    )
    assert final["stats"]["fetched"] == len(channels), final
    assert final["stats"]["duplicates"] == 0, final
    assert len(materials) == len(channels), materials
    assert len({m["material_id"] for m in materials}) == len(channels), materials
    assert_replayed(api.post("/v1/collections", json=body, headers=headers), first)


# ---------------------------------------------------------------------------- handler-runtime
@pytest.mark.parametrize("mode", ["sync", "async"])
def test_r_04_runtime_replay_while_invocation_is_running(
    stack: E2EStack, require: Callable[..., None], client: Callable[..., JaneClient], run_id: str, mode: str
) -> None:
    require("testsite", "handler-runtime")
    runtime = client("handler-runtime")
    api = runtime.api("handler")
    handler, archive = package_ref(SLOW_EXTRACTOR)
    source_id = f"r04-rt-{mode}-{run_id}"
    _, material = page_material(stack, PRODUCT, source_id)
    body: dict[str, Any] = {
        "handler": handler,
        "package_archive": archive,
        "params": {"delay_seconds": ACTIVE_DELAY_S},
        "inputs": [{"kind": "material", "material": material}],
        "context": {
            "trace": {"run_id": f"run_{run_id}", "stage_id": "extract-products", "source_id": source_id}
        },
        "delivery": {"delivery_key": delivery_key(run_id, "r04-active-runtime", mode)},
        "mode": mode,
        "limits": slow_limits(ACTIVE_DELAY_S),
    }
    headers = {"Idempotency-Key": body["delivery"]["delivery_key"]}
    other_mode = {**body, "mode": "async" if mode == "sync" else "sync"}
    sandboxes = Sandboxes(stack, handler)
    known = sandboxes.poll()

    if mode == "sync":
        with ThreadPoolExecutor(1) as pool:
            first_api = client("handler-runtime").api("handler")
            pending: Future[httpx.Response] = pool.submit(
                first_api.post, "/v1/invocations", json=body, headers=headers
            )
            invocation = sandboxes.wait_new(known)
            assert_in_progress(api.post("/v1/invocations", json=body, headers=headers))
            assert_key_reused(api.post("/v1/invocations", json=other_mode, headers=headers))
            assert not pending.done(), "the first call ended before the replays"
            assert invocation in sandboxes.poll(), "the sandbox ended before the replays"
            first = pending.result(timeout=WAIT_S)
        assert first.status_code == 200, first.text
        result = first.json()
    else:
        first = api.post("/v1/invocations", json=body, headers=headers)
        assert first.status_code == 202, first.text
        job_id = first.json()["job_id"]
        invocation = sandboxes.wait_new(known)
        assert_replayed(api.post("/v1/invocations", json=body, headers=headers), first)
        assert_key_reused(api.post("/v1/invocations", json=other_mode, headers=headers))
        assert job_status(runtime, "handler", job_id) == "running"
        assert invocation in sandboxes.poll(), "the sandbox ended before the replays"
        job = runtime.wait_job("handler", job_id, timeout_s=WAIT_S)
        assert job["status"] == "succeeded", job
        result = job["result"]

    assert result["status"] == "success", result
    assert result["invocation_id"] == invocation, (result["invocation_id"], invocation)
    after = api.post("/v1/invocations", json=body, headers=headers)
    assert after.status_code == 200, after.text
    assert after.headers.get(REPLAYED) == "true"
    assert after.json()["duplicate"] is True
    assert after.json()["invocation_id"] == invocation
    sandboxes.poll()
    # the handler ran once: one sandbox for the key, whose invocation is the stored result
    assert sandboxes.seen - known == {invocation}, sandboxes.seen - known
    stored = api.get(f"/v1/invocations/{invocation}")
    assert stored.status_code == 200, stored.text


# ---------------------------------------------------------------------------- storage
def test_r_04_storage_replay_while_write_is_running(
    stack: E2EStack, require: Callable[..., None], client: Callable[..., JaneClient], run_id: str
) -> None:
    require("testsite", "storage", "package-host")
    storage = client("storage")
    api = storage.api("handler")
    source_id = f"r04-store-{run_id}"
    page, material = page_material(stack, PRODUCT, source_id)
    with gate(stack, f"r04-storage-{run_id}", page.content, material["content"]["media_type"]) as held:
        material["content"] = held.content_ref(material["content"].get("charset"))
        body: dict[str, Any] = {
            "handler": {"package_id": "jane.storage-files", "version": "1.0.0"},
            "connections": {"target": "raw-files"},
            "inputs": [{"kind": "material", "material": material}],
            "context": {
                "trace": {"run_id": f"run_{run_id}", "stage_id": "store-raw", "source_id": source_id}
            },
            "delivery": {"delivery_key": delivery_key(run_id, "store-raw", material["observation_id"])},
        }
        headers = {"Idempotency-Key": body["delivery"]["delivery_key"]}
        with ThreadPoolExecutor(1) as pool:
            first_api = client("storage").api("handler")
            pending = pool.submit(first_api.post, "/v1/invocations", json=body, headers=headers)
            held.wait_held()
            assert_in_progress(api.post("/v1/invocations", json=body, headers=headers))
            assert_key_reused(api.post("/v1/invocations", json={**body, "mode": "async"}, headers=headers))
            assert not pending.done(), "the write ended before the replays"
            assert objects_by_source(storage, "raw-files", source_id) == []
            assert held.status()["requests"] == 1, held.status()
            held.release()
            first = pending.result(timeout=WAIT_S)
        downloads = held.status()

    assert first.status_code == 200, first.text
    result = first.json()
    assert result["status"] == "success", result
    assert result["output"]["writes"][0]["status"] == "written", result
    assert downloads["requests"] == 1 and downloads["served"] == 1, downloads
    after = api.post("/v1/invocations", json=body, headers=headers)
    assert after.status_code == 200, after.text
    assert after.headers.get(REPLAYED) == "true"
    assert after.json()["duplicate"] is True, after.json()
    assert after.json()["output"]["writes"][0]["status"] == "duplicate", after.json()
    stored = result["output"]["writes"][0]["object"]  # bytes checked by storage against content.sha256
    objects = objects_by_source(storage, "raw-files", source_id)
    assert len(objects) == 1, objects
    assert objects[0]["object"]["object_id"] == stored["object_id"], objects
    assert objects[0]["material"]["observation_id"] == material["observation_id"], objects


# ---------------------------------------------------------------------------- LLM gateway
@pytest.mark.parametrize("mode", ["sync", "async"])
def test_r_04_llm_replay_while_invocation_is_running(
    stack: E2EStack, require: Callable[..., None], client: Callable[..., JaneClient], run_id: str, mode: str
) -> None:
    require("testsite", "llm", "package-host")
    llm = client("llm")
    api = llm.api("handler")
    handler, archive = package_ref(LLM_TRIAGE)
    source_id = task_id = f"r04-llm-{mode}-{run_id}"
    page, material = page_material(stack, UNKNOWN_PAGE, source_id)
    with gate(stack, f"r04-llm-{mode}-{run_id}", page.content, material["content"]["media_type"]) as held:
        material["content"] = held.content_ref(material["content"].get("charset"))
        body: dict[str, Any] = {
            "handler": handler,
            "package_archive": archive,
            "inputs": [{"kind": "material", "material": material}],
            "context": {
                "trace": {
                    "run_id": f"run_{run_id}",
                    "stage_id": "triage",
                    "task_id": task_id,
                    "source_id": source_id,
                }
            },
            "delivery": {"delivery_key": delivery_key(run_id, "r04-active-llm", mode)},
            "mode": mode,
        }
        headers = {"Idempotency-Key": body["delivery"]["delivery_key"]}
        other_mode = {**body, "mode": "async" if mode == "sync" else "sync"}
        if mode == "sync":
            with ThreadPoolExecutor(1) as pool:
                first_api = client("llm").api("handler")
                pending = pool.submit(first_api.post, "/v1/invocations", json=body, headers=headers)
                held.wait_held()
                assert_in_progress(api.post("/v1/invocations", json=body, headers=headers))
                assert_key_reused(api.post("/v1/invocations", json=other_mode, headers=headers))
                assert not pending.done(), "the call ended before the replays"
                assert llm_usage(llm, task_id)["totals"]["requests"] == 0
                held.release()
                first = pending.result(timeout=WAIT_S)
            assert first.status_code == 200, first.text
            result = first.json()
        else:
            first = api.post("/v1/invocations", json=body, headers=headers)
            assert first.status_code == 202, first.text
            job_id = first.json()["job_id"]
            held.wait_held()
            assert_replayed(api.post("/v1/invocations", json=body, headers=headers), first)
            assert_key_reused(api.post("/v1/invocations", json=other_mode, headers=headers))
            assert job_status(llm, "llm", job_id) == "running"
            assert llm_usage(llm, task_id)["totals"]["requests"] == 0
            held.release()
            job = llm.wait_job("llm", job_id, timeout_s=WAIT_S)
            assert job["status"] == "succeeded", job
            result = job["result"]
        downloads = held.status()

    assert result["status"] == "success", result
    assert downloads["requests"] == 1 and downloads["served"] == 1, downloads
    usage = llm_usage(llm, task_id)
    assert usage["totals"]["requests"] == 1, usage
    after = api.post("/v1/invocations", json=body, headers=headers)
    assert after.headers.get(REPLAYED) == "true"
    if mode == "sync":
        assert after.status_code == 200, after.text
        assert after.json()["duplicate"] is True
        assert after.json()["invocation_id"] == result["invocation_id"]
    else:
        assert_replayed(after, first)
        assert llm.wait_job("llm", job_id)["result"]["invocation_id"] == result["invocation_id"]
    assert llm_usage(llm, task_id) == usage
    assert held.status()["requests"] == 1, held.status()


# ---------------------------------------------------------------------------- registry
def test_r_04_registry_replay_while_port_job_and_publication_are_running(
    stack: E2EStack, require: Callable[..., None], client: Callable[..., JaneClient], run_id: str
) -> None:
    require("registry")
    registry = client("registry")
    api = registry.api("registry")
    manifest, files = package_files(FILES_DIR)
    parent_id, fork_id = f"e2e.r04-parent-{run_id}", f"e2e.r04-fork-{run_id}"
    manifest = {**manifest, "package_id": parent_id}
    parent = publish(registry, manifest, files)
    fork(registry, parent, fork_id)

    def describe(text: str) -> Callable[[dict[str, Any], dict[str, bytes]], None]:
        def change(m: dict[str, Any], _: dict[str, bytes]) -> None:
            m["description"] = text

        return change

    publish_version(
        registry, *new_parent_version(manifest, files, "1.1.0", "R-04 1.1.0", describe("R-04 1.1.0"))
    )
    manifest_12, files_12 = new_parent_version(manifest, files, "1.2.0", "R-04 1.2.0", describe("R-04 1.2.0"))
    port_path = f"/v1/packages/{fork_id}/upstream-ports"
    port_body = {"parent_version": "1.1.0", "new_version": "1.1.0"}
    port_headers = {"Idempotency-Key": key()}
    publish_path = f"/v1/packages/{parent_id}/versions"
    version_body = publish_body(manifest_12, files_12)
    publish_headers = {"Idempotency-Key": key()}

    def publish_12() -> httpx.Response:
        return (
            client("registry").api("registry").post(publish_path, json=version_body, headers=publish_headers)
        )

    stack.pause_instance("minio")  # archives live in MinIO: nothing that writes one can finish
    paused = True
    try:
        # 1. asynchronous: the port job is accepted and cannot publish its version
        first = api.post(port_path, json=port_body, headers=port_headers)
        assert first.status_code == 202, first.text
        job_id = first.json()["job_id"]
        wait_for("port job running", lambda: running(registry, "registry", job_id), WAIT_S)
        assert_replayed(api.post(port_path, json=port_body, headers=port_headers), first)
        assert_key_reused(
            api.post(port_path, json={**port_body, "new_version": "1.2.0"}, headers=port_headers)
        )
        port_during = job_status(registry, "registry", job_id)
        assert port_during == "running", port_during

        # 2. synchronous: two identical publications race for the key; one holds it, the other gets 409
        with ThreadPoolExecutor(2) as pool:
            racing = [pool.submit(publish_12) for _ in range(2)]
            done, rest = wait(racing, timeout=60, return_when=FIRST_COMPLETED)
            assert len(done) == 1 and len(rest) == 1, (done, rest)
            assert_in_progress(next(iter(done)).result())
            assert_key_reused(
                api.post(publish_path, json={**version_body, "files": {}}, headers=publish_headers)
            )
            holder = next(iter(rest))
            assert not holder.done(), "the publication ended while MinIO was paused"
            stack.unpause_instance("minio")
            paused = False
            published = holder.result(timeout=WAIT_S)
    finally:
        if paused:
            stack.unpause_instance("minio")

    assert published.status_code == 201, published.text
    job = registry.wait_job("registry", job_id, timeout_s=WAIT_S)
    print(f"\nR-04 registry: port job {port_during} during the replays, then {job['status']}")
    assert job["status"] == "succeeded", job
    assert job["result"]["version"] == "1.1.0", job["result"]
    assert_replayed(api.post(port_path, json=port_body, headers=port_headers), first)
    replay_published = api.post(publish_path, json=version_body, headers=publish_headers)
    assert_replayed(replay_published, published)

    def versions(package_id: str) -> list[str]:
        r = api.get(f"/v1/packages/{package_id}/versions")
        assert r.status_code == 200, r.text
        assert r.json()["next_cursor"] is None, r.json()
        return sorted(v["version"] for v in r.json()["items"])

    assert versions(fork_id) == ["1.0.0", "1.1.0"]
    assert versions(parent_id) == ["1.0.0", "1.1.0", "1.2.0"]


# ---------------------------------------------------------------------------- assistant
def test_r_04_assistant_replay_while_unknown_material_job_is_running(
    stack: E2EStack, require: Callable[..., None], client: Callable[..., JaneClient], run_id: str
) -> None:
    # The orchestrator runs because the assistant is configured with it: unreachable, it fails the job after the
    # LLM call (httpx.ConnectError escapes run_unknown) - a defect outside R-04, docs/delivery/WP-13.md "WP-13r".
    require("testsite", "llm", "assistant", "package-host", "orchestrator")
    assistant, llm = client("assistant"), client("llm")
    api = assistant.api("assistant")
    source_id = task_id = f"r04-asst-{run_id}"
    page, material = page_material(stack, UNKNOWN_PAGE, source_id)
    with gate(stack, f"r04-assistant-{run_id}", page.content, material["content"]["media_type"]) as held:
        material["content"] = held.content_ref(material["content"].get("charset"))
        body = {
            "source_id": source_id,
            "task_id": task_id,
            "forward_unknown_to_llm": True,
            "material": material,
        }
        headers = {"Idempotency-Key": f"r04-asst-{run_id}"}
        first = api.post("/v1/unknown-materials", json=body, headers=headers)
        assert first.status_code == 202, first.text
        job_id = first.json()["job_id"]
        held.wait_held()
        assert_replayed(api.post("/v1/unknown-materials", json=body, headers=headers), first)
        assert_key_reused(
            api.post("/v1/unknown-materials", json={**body, "task_id": f"{task_id}-other"}, headers=headers)
        )
        assert job_status(assistant, "assistant", job_id) == "running"
        assert llm_usage(llm, task_id)["totals"]["requests"] == 0
        held.release()
        job = assistant.wait_job("assistant", job_id, timeout_s=WAIT_S)
        downloads = held.status()

    assert job["status"] == "succeeded", job
    assert downloads["requests"] == 1 and downloads["served"] == 1, downloads
    usage = llm_usage(llm, task_id)
    assert usage["totals"]["requests"] == 1, usage
    assert_replayed(api.post("/v1/unknown-materials", json=body, headers=headers), first)
    assert assistant.wait_job("assistant", job_id) == job
    assert llm_usage(llm, task_id) == usage
    assert held.status()["requests"] == 1, held.status()


# ---------------------------------------------------------------------------- orchestrator
def test_r_04_orchestrator_replay_while_run_and_reprocessing_are_active(
    stack: E2EStack, orchestrated: JaneClient, client: Callable[..., JaneClient], run_id: str
) -> None:
    orch, storage = orchestrated, client("storage")
    api = orch.api("orchestrator")
    handler, _ = package_ref(SLOW_EXTRACTOR)
    stack.publish_local_package(handler["package_id"], handler["version"], build_archive(SLOW_EXTRACTOR))
    source_id = task_id = f"e2e-{run_id}-r04-active"
    task = m1_task(task_id, source_id, [TESTSITE + PRODUCT], handler)
    [extract] = [s for s in task["stages"] if s["stage_id"] == "extract-products"]
    extract["params"] = {"delay_seconds": ACTIVE_DELAY_S}
    extract["limits"] = slow_limits(ACTIVE_DELAY_S)
    create_source(orch, source_id)
    create_task(orch, task)
    sandboxes = Sandboxes(stack, handler)
    since = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    def run_status(run: str) -> str:
        r = api.get(f"/v1/runs/{run}")
        assert r.status_code == 200, r.text
        return str(r.json()["status"])

    def replay_while_active(
        path: str, body: dict[str, Any], changed: dict[str, Any]
    ) -> tuple[httpx.Response, str]:
        headers = {"Idempotency-Key": key()}
        known = sandboxes.poll()
        before = set(sandboxes.seen)  # includes the sandboxes of the earlier phase
        first = api.post(path, json=body, headers=headers)
        assert first.status_code == 202, first.text
        run = str(first.json()["job_id"])
        invocation = sandboxes.wait_new(known)
        assert run_status(run) == "running"
        assert_replayed(api.post(path, json=body, headers=headers), first)
        assert_key_reused(api.post(path, json=changed, headers=headers))
        assert run_status(run) == "running"
        assert invocation in sandboxes.poll(), "the extraction ended before the replays"
        final = wait_run(orch, run, timeout_s=WAIT_S)
        assert final["status"] == "succeeded", final
        assert_replayed(api.post(path, json=body, headers=headers), first)
        sandboxes.poll()
        assert sandboxes.seen - before == {invocation}, sandboxes.seen - before  # one extraction call
        return first, run

    def runs_of_task() -> dict[str, str]:
        r = api.get("/v1/runs", params={"task_id": task_id, "limit": 50})
        assert r.status_code == 200, r.text
        return {str(x["run_id"]): str(x["trigger"]) for x in r.json()["items"]}

    # 1. start of a run, replayed while the run extracts
    run_body = {"reason": "R-04 while active"}
    _, run = replay_while_active(f"/v1/tasks/{task_id}/runs", run_body, {"reason": "R-04 other reason"})
    assert list(runs_of_task()) == [run], runs_of_task()
    assert_effects_once(storage, source_id, materials=1, products=1)

    # 2. reprocessing of the stored RAW, replayed while it extracts again
    [item] = list_items(orch, run, "extract-products")
    reprocess = {
        "task_id": task_id,
        "stored_materials": {
            "storage_connection_id": "raw-files",
            "material_ids": [item["material_id"]],
            "since": since,
        },
        "from_stage": "extract-products",
        "reason": "R-04 reprocessing while active",
    }
    _, rerun = replay_while_active(
        "/v1/reprocessing", reprocess, {**reprocess, "reason": "R-04 other reason"}
    )
    runs = runs_of_task()
    assert set(runs) == {run, rerun}, runs
    assert runs[rerun] == "reprocess", runs
    [product] = entities(storage, "results-pg", source_id)
    print(f"\nR-04 orchestrator: runs {runs}, product {product['canonical_key']} v{product['version']}")
    # one history event from the run and one from the single reprocessing run; the RAW is stored once
    assert product["version"] == 2, product
    assert len(objects_by_source(storage, "raw-files", source_id)) == 1
