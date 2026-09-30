"""Several collector processes on one node sharing one state directory (review 1).

* reads and cancellation work through any instance; a killed owner's collection is taken over;
* a live but stalled owner (process suspended longer than the lease) loses the collection to another
  instance and, when it wakes up, cannot write anything (lease fencing);
* in both cases the result is exactly ``sets.recursive`` and no URL is delivered twice.
"""

from __future__ import annotations

import contextlib
import sqlite3
import time
from collections import Counter
from typing import Any

import httpx
import psutil  # type: ignore[import-untyped]
import pytest

from jane_web_collector.testing import FAST_LIMITS, ServiceFactory, Site, drain, start, wait_done, web_rules

SLOW: dict[str, Any] = {
    **FAST_LIMITS,
    "rate": {"requests_per_second_per_host": 10, "min_delay_ms_per_host": 0},
    "concurrency": {"max_parallel_fetches": 2, "max_parallel_fetches_per_host": 2},
}


def _wait_fetched(api: httpx.Client, cid: str, n: int, timeout: float = 30) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    view: dict[str, Any] = {}
    while time.monotonic() < deadline:
        view = api.get(f"/v1/collections/{cid}").json()
        if view["stats"]["fetched"] >= n:
            return view
        time.sleep(0.05)
    raise AssertionError(f"not enough progress: {view}")


def _assert_exact_once(site: Site, expected: set[str], delivered: list[dict[str, Any]]) -> None:
    per_url = Counter(m["locator"]["canonical_url"] for m in delivered)
    assert set(per_url) == site.canonical(expected)
    # a URL may be re-delivered only as the same observation (not acknowledged yet), never re-fetched
    observations: dict[str, set[str]] = {}
    for m in delivered:
        observations.setdefault(m["locator"]["canonical_url"], set()).add(m["observation_id"])
    twice = {u: obs for u, obs in observations.items() if len(obs) > 1}
    assert twice == {}, twice


def test_two_instances_share_state_and_take_over_after_kill(
    service_factory: ServiceFactory, site: Site, expected_sets: dict[str, set[str]]
) -> None:
    a = service_factory()
    a.start()
    b = service_factory(state_dir=a.state_dir)
    b.start()
    with (
        httpx.Client(base_url=a.base, timeout=10) as api_a,
        httpx.Client(base_url=b.base, timeout=10) as api_b,
    ):
        c1 = start(api_a, {"source_kind": "web", "source_id": "s1", "rules": web_rules(site), "limits": SLOW})
        c2 = start(api_b, {"source_kind": "web", "source_id": "s2", "rules": web_rules(site), "limits": SLOW})
        _wait_fetched(api_a, c1, 5)
        page = api_b.get(f"/v1/collections/{c1}/materials", params={"limit": 3}).json()  # read via B
        assert page["items"]
        assert api_a.post(f"/v1/jobs/{c2}/cancel", json={"reason": "test"}).status_code == 202  # cancel via A
        deadline = time.monotonic() + 20
        while api_a.get(f"/v1/collections/{c2}").json()["status"] != "cancelled":
            assert time.monotonic() < deadline, "c2 not cancelled"
            time.sleep(0.1)
        a.kill()
        rest = drain(api_b, c1, timeout=90)
        done = wait_done(api_b, c1, timeout=60)
    assert done["status"] == "succeeded", done
    assert done["stats"]["frontier_size"] == 0
    _assert_exact_once(site, expected_sets["recursive"], page["items"] + rest)


@pytest.mark.parametrize("hold_db_lock", [False, True], ids=["b-takes-over", "db-locked-no-takeover"])
def test_stalled_owner_is_fenced_out(
    service_factory: ServiceFactory, site: Site, expected_sets: dict[str, set[str]], hold_db_lock: bool
) -> None:
    """A is frozen longer than the lease. ``b-takes-over``: B claims the collection meanwhile.
    ``db-locked-no-takeover``: the SQLite write lock is held during the freeze (as when A is frozen inside a
    transaction), so B cannot claim; A wakes up with an expired lease that is still its own.
    Either way the consumer must never see a finished collection before it really is finished."""
    a = service_factory()
    a.start()
    b = service_factory(state_dir=a.state_dir)
    b.start()
    assert a.proc is not None
    # the venv's python.exe on Windows is a launcher with the interpreter as a child: freeze the whole tree
    parent = psutil.Process(a.proc.pid)
    frozen = [parent, *parent.children(recursive=True)]
    with httpx.Client(base_url=b.base, timeout=10) as api_b:
        with httpx.Client(base_url=a.base, timeout=10) as api_a:
            c1 = start(
                api_a, {"source_kind": "web", "source_id": "s1", "rules": web_rules(site), "limits": SLOW}
            )
            _wait_fetched(api_a, c1, 8)
        for proc in frozen:
            proc.suspend()  # alive but hung: no heartbeat, requests in flight, pending writes
        lock = None
        try:
            if hold_db_lock:
                lock = sqlite3.connect(str(a.state_dir / "state.db"), timeout=0.5, isolation_level=None)
                with contextlib.suppress(sqlite3.OperationalError):  # A may itself hold it, frozen mid-write
                    lock.execute("BEGIN IMMEDIATE")
            time.sleep(5)  # > lease (3 s) + resume interval (1 s)
        finally:
            if lock is not None:
                with contextlib.suppress(sqlite3.OperationalError):
                    lock.execute("ROLLBACK")
                lock.close()
            for proc in frozen:
                proc.resume()  # A wakes up; whoever holds the lease continues, the other writes nothing
        materials = drain(api_b, c1, timeout=90)  # stops at the first end_of_stream
        at_end = api_b.get(f"/v1/collections/{c1}").json()
        done = wait_done(api_b, c1, timeout=60)
        time.sleep(3)  # give the woken instance time to try to finish or resume its run
        final = api_b.get(f"/v1/collections/{c1}").json()
        job = api_b.get(f"/v1/jobs/{c1}").json()
        more = api_b.get(f"/v1/collections/{c1}/materials").json()
    # end_of_stream only when the collection really finished: nothing open, nothing more to come
    assert at_end["status"] == "succeeded" and at_end["stats"]["frontier_size"] == 0, at_end
    assert done["status"] == "succeeded", done
    assert final["status"] == "succeeded" and final["stats"]["frontier_size"] == 0, final
    assert final["stats"]["emitted"] == at_end["stats"]["emitted"] == len(expected_sets["recursive"])
    # nothing new after end_of_stream (only the last, not yet acknowledged page may be re-delivered as is)
    assert {m["observation_id"] for m in more["items"]} <= {m["observation_id"] for m in materials}
    assert more["end_of_stream"] is True
    assert job["status"] == "succeeded" and "handed_over" not in (job.get("result") or {}), job
    _assert_exact_once(site, expected_sets["recursive"], materials)
