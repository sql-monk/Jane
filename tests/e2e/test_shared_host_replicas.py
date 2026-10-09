"""L2 / R15: two Docker Web Collectors share per-host pacing, slots and dead-owner TTL.

The collector is unmodified. A test-only wrapper records arrivals at the REAL testsite, including robots.txt.
Every collector request and response is validated against collector.v1. See README.shared-hosts.md.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path
from typing import Any

import httpx
import pytest

from jane_e2e.clients import JaneClient
from jane_e2e.stack import E2EStack, default_project
from jane_e2e.verify import site_paths

pytestmark = [pytest.mark.e2e, pytest.mark.criteria(8, 13)]

TTL_S = int(os.environ.get("JANE_E2E_SHARED_HOST_TTL_SECONDS", "8"))
HOST_POLL_MS = int(os.environ.get("JANE_E2E_SHARED_HOST_POLL_MS", "50"))
BUSY_MS = int(os.environ.get("JANE_E2E_SHARED_HOST_BUSY_TIMEOUT_MS", "500"))
WAIT_S = float(os.environ.get("JANE_E2E_SHARED_HOST_WAIT_S", "90"))
PROBE_POLL_S = float(os.environ.get("JANE_E2E_SHARED_HOST_PROBE_POLL_S", "0.05"))
TIMING_SLACK_S = float(os.environ.get("JANE_E2E_SHARED_HOST_TIMING_SLACK_S", "0.05"))
TTL_SLACK_S = float(os.environ.get("JANE_E2E_SHARED_HOST_TTL_SLACK_S", "0.5"))
INTERVAL_MS = int(os.environ.get("JANE_E2E_SHARED_HOST_INTERVAL_MS", "250"))
PARALLEL_HOLD_S = float(os.environ.get("JANE_E2E_SHARED_HOST_HOLD_S", "0.4"))
PAGES = int(os.environ.get("JANE_E2E_SHARED_HOST_PAGES", "8"))
PACE_PARALLEL = int(os.environ.get("JANE_E2E_SHARED_HOST_PACE_PARALLEL", "4"))
FAST_RPS = float(os.environ.get("JANE_E2E_SHARED_HOST_FAST_RPS", "1000"))
CONTROL = "/_e2e/host-probe"
STATE_DIR = "/var/lib/jane-web-collector"
TESTSITE = "http://testsite:8080"


@dataclass
class Replicas:
    stack: E2EStack
    collectors: tuple[JaneClient, JaneClient]
    probe: httpx.Client

    def snapshot(self) -> dict[str, Any]:
        response = self.probe.get(CONTROL)
        response.raise_for_status()
        return dict(response.json())

    def control(self, **body: Any) -> dict[str, Any]:
        response = self.probe.put(CONTROL, json=body)
        response.raise_for_status()
        return dict(response.json())


@pytest.fixture(scope="module")
def replicas(stack: E2EStack) -> Iterator[Replicas]:
    """The session stack checks Docker availability; this module starts only its own isolated project."""
    own = E2EStack(
        project=f"{default_project()}-shared-hosts-{uuid.uuid4().hex[:6]}",
        overlays=(Path(__file__).with_name("compose.host-limits.yaml"),),
    )
    own.env().update(
        {
            "JANE_E2E_SHARED_HOST_TTL_SECONDS": str(TTL_S),
            "JANE_E2E_SHARED_HOST_POLL_MS": str(HOST_POLL_MS),
            "JANE_E2E_SHARED_HOST_BUSY_TIMEOUT_MS": str(BUSY_MS),
            "JANE_E2E_HOST_PROBE_GATE_TIMEOUT_S": str(WAIT_S + TTL_S),
        }
    )
    opened: list[JaneClient] = []
    probe: httpx.Client | None = None
    try:
        own.ensure("web-collector")
        own.scale("web-collector", 2)
        ids = [own.container("web-collector", index) for index in (1, 2)]
        assert len(set(ids)) == 2, ids
        mounts = []
        pids = []
        for index, container in enumerate(ids, 1):
            inspected = own._run(["docker", "inspect", container])
            data = json.loads(inspected.stdout)[0]
            pids.append(data["State"]["Pid"])
            (mount,) = [m for m in data["Mounts"] if m["Destination"] == STATE_DIR]
            assert mount["Type"] == "volume", mount
            mounts.append(mount["Name"])
            actual = json.loads(
                own.exec(
                    "web-collector",
                    "python",
                    "-c",
                    "import json,os; print(json.dumps({k:os.environ[k] for k in "
                    "['JANE_WEB_COLLECTOR_STATE_DIR',"
                    "'JANE_WEB_COLLECTOR_LIMITS__COLLECTOR__SHARED_HOST_LIMITS',"
                    "'JANE_WEB_COLLECTOR_LIMITS__COLLECTOR__SHARED_HOST_TTL_SECONDS',"
                    "'JANE_WEB_COLLECTOR_LIMITS__COLLECTOR__SHARED_HOST_POLL_MS']}))",
                    index=index,
                )
            )
            assert actual["JANE_WEB_COLLECTOR_STATE_DIR"] == STATE_DIR
            assert actual["JANE_WEB_COLLECTOR_LIMITS__COLLECTOR__SHARED_HOST_LIMITS"] == "true"
            assert int(actual["JANE_WEB_COLLECTOR_LIMITS__COLLECTOR__SHARED_HOST_TTL_SECONDS"]) == TTL_S
            assert int(actual["JANE_WEB_COLLECTOR_LIMITS__COLLECTOR__SHARED_HOST_POLL_MS"]) == HOST_POLL_MS
        assert len(set(pids)) == 2 and all(pid > 0 for pid in pids), pids
        assert mounts[0] == mounts[1] and mounts[0].startswith(own.project), mounts
        print(
            f"L2 Docker topology: {json.dumps({'project': own.project, 'containers': ids, 'pids': pids, 'state_volumes': mounts, 'shared_host_ttl_seconds': TTL_S, 'shared_host_poll_ms': HOST_POLL_MS})}"
        )
        opened = [JaneClient(own.url("web-collector", index)) for index in (1, 2)]
        probe = httpx.Client(base_url=own.url("testsite"), timeout=WAIT_S)
        yield Replicas(own, (opened[0], opened[1]), probe)
    finally:
        for client in opened:
            client.close()
        if probe is not None:
            probe.close()
        own.down(volumes=True)


def _events(snapshot: dict[str, Any], *markers: str) -> list[dict[str, Any]]:
    return sorted(
        (event for event in snapshot["events"] if event["marker"] in markers),
        key=lambda event: event["started"],
    )


def _wait_events(
    replicas: Replicas, marker: str, *, finished: bool = False, timeout_s: float = WAIT_S
) -> list[dict[str, Any]]:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        events = [event for event in _events(replicas.snapshot(), marker) if event["path"] != "/robots.txt"]
        if events and (not finished or all(event["ended"] is not None for event in events)):
            return events
        time.sleep(PROBE_POLL_S)
    raise TimeoutError(f"no {'finished ' if finished else ''}product request for {marker}")


def _rules(marker: str, urls: list[str]) -> dict[str, Any]:
    return {
        "collector": "web",
        "scope": {"allowed_domains": ["testsite"]},
        "strategies": [{"type": "seed_list", "urls": urls}],
        "fetch": {"user_agent": marker},
    }


def _limits(parallel: int, interval_ms: int) -> dict[str, Any]:
    return {
        "concurrency": {"max_parallel_fetches": PACE_PARALLEL, "max_parallel_fetches_per_host": parallel},
        "rate": {
            "requests_per_second_per_host": FAST_RPS,
            "min_delay_ms_per_host": interval_ms,
            "respect_crawl_delay": False,
        },
        "timeouts": {"request_timeout_ms": int(WAIT_S * 1000)},
        "retries": {"max_attempts": 1},
    }


def _drain(collector: JaneClient, collection_id: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    materials: list[dict[str, Any]] = []
    after: str | None = None
    deadline = time.monotonic() + WAIT_S
    while time.monotonic() < deadline:
        response = collector.api("collector").get(
            f"/v1/collections/{collection_id}/materials",
            params={"wait_ms": 500, **({"after": after} if after else {})},
        )
        assert response.status_code == 200, response.text
        page = response.json()
        materials.extend(page["items"])
        after = page.get("next_cursor") or after
        if page["end_of_stream"]:
            view = collector.api("collector").get(f"/v1/collections/{collection_id}")
            assert view.status_code == 200, view.text
            assert view.json()["status"] == "succeeded", view.text
            return materials, view.json()
    raise TimeoutError(f"collection {collection_id} did not finish")


def _measure(events: list[dict[str, Any]], markers: tuple[str, str]) -> dict[str, Any]:
    assert events and all(event["ended"] is not None for event in events), events
    changes = sorted([(event["started"], 1) for event in events] + [(event["ended"], -1) for event in events])
    active = peak = 0
    for _, delta in changes:
        active += delta
        peak = max(peak, active)
    starts = [event["started"] for event in events]
    page_times = [
        [event["started"] for event in events if event["marker"] == marker and event["path"] != "/robots.txt"]
        for marker in markers
    ]
    assert all(len(times) == PAGES for times in page_times), page_times
    assert max(times[0] for times in page_times) < min(times[-1] for times in page_times), page_times
    return {
        "requests": len(events),
        "product_requests_per_replica": [len(times) for times in page_times],
        "max_in_flight": peak,
        "min_start_gap_s": min(b - a for a, b in pairwise(starts)),
        "start_span_s": starts[-1] - starts[0],
        "requests_by_replica": [event["marker"] for event in events],
    }


def test_l2_two_docker_replicas_share_host_parallelism_and_interval(replicas: Replicas) -> None:
    """One phase saturates a single shared slot; another measures pacing with immediately returned pages."""
    assert PAGES >= 3 and PARALLEL_HOLD_S > 0
    assert 0 <= TIMING_SLACK_S < INTERVAL_MS / 1000
    assert PACE_PARALLEL > 1 and 0 < 1 / FAST_RPS < INTERVAL_MS / 1000
    products = site_paths("product")
    assert len(products) >= PAGES, products
    for phase, parallel, interval_ms, delay in (
        ("parallel", 1, 0, PARALLEL_HOLD_S),
        ("interval", PACE_PARALLEL, INTERVAL_MS, 0),
    ):
        prefix = f"JaneHostProbe/{uuid.uuid4().hex}-{phase}"
        markers = (f"{prefix}-a", f"{prefix}-b")
        collections = []
        for index, marker in enumerate(markers):
            replicas.control(marker=marker, delay_s=delay)
            urls = [TESTSITE + path for path in products[:PAGES]]
            response = (
                replicas.collectors[index]
                .api("collector")
                .post(
                    "/v1/collections",
                    json={
                        "source_kind": "web",
                        "source_id": f"l2-{uuid.uuid4().hex}",
                        "rules": _rules(marker, urls),
                        "limits": _limits(parallel, interval_ms),
                    },
                    headers={"Idempotency-Key": uuid.uuid4().hex},
                )
            )
            assert response.status_code == 202, response.text
            collections.append(response.json()["job_id"])
        for collector, collection_id in zip(replicas.collectors, collections, strict=True):
            materials, view = _drain(collector, collection_id)
            assert len(materials) == PAGES, view
            assert {material["locator"]["canonical_url"] for material in materials} == {
                TESTSITE + path for path in products[:PAGES]
            }
            assert view["effective_limits"]["concurrency"]["max_parallel_fetches_per_host"] == parallel, view
            assert view["effective_limits"]["rate"]["min_delay_ms_per_host"] == interval_ms, view
        measured = _measure(_events(replicas.snapshot(), *markers), markers)
        print(f"L2 {phase}: {json.dumps(measured)}")
        assert measured["max_in_flight"] <= parallel, measured
        if phase == "parallel":
            assert measured["max_in_flight"] == parallel, measured
        else:
            interval = interval_ms / 1000
            assert measured["min_start_gap_s"] >= interval - TIMING_SLACK_S, measured
            assert measured["start_span_s"] >= (measured["requests"] - 1) * interval - TIMING_SLACK_S, (
                measured
            )


def test_l2_killed_replica_releases_shared_host_within_ttl(replicas: Replicas) -> None:
    """A live gated fetch renews its slot beyond TTL; SIGKILL leaves that slot to expire for the survivor."""
    prefix = f"JaneHostProbe/{uuid.uuid4().hex}-ttl"
    dead, survivor = f"{prefix}-a", f"{prefix}-b"
    url = TESTSITE + "/product/phone-alpha"
    replicas.control(marker=dead, gate=True)
    replicas.control(marker=survivor)

    def fetch(index: int, marker: str) -> httpx.Response:
        return (
            replicas.collectors[index]
            .api("collector")
            .post(
                "/v1/fetches",
                json={
                    "source_kind": "web",
                    "url": url,
                    "rules": _rules(marker, [url]),
                    "limits": _limits(1, 0),
                },
            )
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        killed_fetch = pool.submit(fetch, 0, dead)
        try:
            _wait_events(replicas, dead)
            survivor_fetch = pool.submit(fetch, 1, survivor)
            began = time.monotonic()
            live_window = TTL_S * 4 / 3
            while time.monotonic() - began < live_window:
                assert not _events(replicas.snapshot(), survivor), (
                    "the live replica lost its slot before the kill"
                )
                assert not killed_fetch.done() and not survivor_fetch.done(), (
                    "a gated/queued fetch completed early"
                )
                time.sleep(PROBE_POLL_S)
            held_s = time.monotonic() - began
            replicas.control(mark="kill_started")
            replicas.stack.kill_instance("web-collector", 1)
            killed = replicas.control(mark="kill_completed")
            assert not _events(killed, survivor), "the survivor started before the dead owner's slot expired"
            # End the fixture's disconnected HTTP handler; this cannot release the slot in the dead process.
            replicas.control(release=dead)
            _wait_events(replicas, dead, finished=True)
            allowed_s = TTL_S + HOST_POLL_MS / 1000 + TTL_SLACK_S
            started = _wait_events(replicas, survivor, timeout_s=allowed_s)[0]["started"]
            response = survivor_fetch.result(timeout=WAIT_S)
            assert response.status_code == 200, response.text
            assert response.json()["locator"]["canonical_url"] == url, response.text
            with pytest.raises(httpx.TransportError):
                killed_fetch.result(timeout=WAIT_S)
            marks = killed["marks"]
            kill_duration = marks["kill_completed"] - marks["kill_started"]
            lag = started - marks["kill_completed"]
            measured = {
                "live_slot_held_s": held_s,
                "shared_host_ttl_seconds": TTL_S,
                "shared_host_poll_s": HOST_POLL_MS / 1000,
                "kill_duration_s": kill_duration,
                "successor_start_after_kill_s": lag,
                "allowed_after_kill_s": allowed_s,
            }
            print(f"L2 dead-owner TTL: {json.dumps(measured)}")
            assert lag >= 0, measured
            assert lag <= allowed_s, measured
        finally:
            replicas.control(release=dead)
