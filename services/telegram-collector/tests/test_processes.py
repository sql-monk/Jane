"""The collector as separate OS processes: autonomy, recovery after a hard kill, several instances.

* criterion 1: a third-party application uses the collector over HTTP without orchestrator or registry;
* criterion 8: after a hard kill another process continues the collection from the last committed message;
  unacknowledged materials are delivered again with the same observation, nothing is emitted twice;
* several instances on one node share the state: lease + heartbeat, takeover after kill, fencing of a
  stalled owner, cancellation through any instance.
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import httpx
from jsonschema import Draft202012Validator

from jane_telegram_collector.testing import (
    FAST_LIMITS,
    USERNAME,
    ServiceFactory,
    drain,
    make_channel,
    page,
    start,
    telegram_rules,
    wait_done,
)

SLOW_READ = {
    # small history pages and pacing between Telegram calls: the run takes seconds, so it can be interrupted
    "JANE_TELEGRAM_COLLECTOR_LIMITS__COLLECTOR__HISTORY_PAGE_SIZE": "5",
    "JANE_TELEGRAM_COLLECTOR_LIMITS__RATE__MIN_DELAY_MS_PER_HOST": "100",
}


def body(state_key: str, limits: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "source_kind": "telegram",
        "source_id": "news-tg",
        "rules": telegram_rules(USERNAME),
        "state_key": state_key,
        "limits": {"retries": FAST_LIMITS["retries"], **(limits or {})},
    }


def start_slow(api: httpx.Client, state_key: str, limits: dict[str, Any] | None = None) -> str:
    r = api.post(
        "/v1/collections", json=body(state_key, limits), headers={"Idempotency-Key": f"k-{state_key}"}
    )
    assert r.status_code == 202, r.text
    return str(r.json()["job_id"])


def wait_for(api: httpx.Client, cid: str, predicate: Any, timeout: float = 20) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    view: dict[str, Any] = {}
    while time.monotonic() < deadline:
        view = api.get(f"/v1/collections/{cid}").json()
        if predicate(view):
            return view
        time.sleep(0.05)
    raise AssertionError(f"condition not reached: {view}")


def assert_each_message_once(items: list[dict[str, Any]], count: int) -> None:
    observations: dict[str, set[str]] = defaultdict(set)
    for m in items:
        observations[m["material_id"]].add(m["observation_id"])
    assert len(observations) == count, sorted(observations)
    doubled = {k: v for k, v in observations.items() if len(v) > 1}
    assert not doubled, f"messages emitted twice: {doubled}"
    ids = sorted(
        m["locator"]["telegram"]["message_id"] for m in {m["observation_id"]: m for m in items}.values()
    )
    assert ids == list(range(1, count + 1))


def test_third_party_app_uses_the_collector_without_orchestrator(
    service_factory: ServiceFactory, tmp_path: Path, material_validator: Draft202012Validator
) -> None:
    make_channel(tmp_path / "recordings", 12)
    ref = {"package_id": "news-tg.telegram-rules", "version": "1.0.0"}
    folder = tmp_path / "rules" / ref["package_id"] / ref["version"]
    folder.mkdir(parents=True)
    manifest = {
        "schema_version": "1",
        "package_id": ref["package_id"],
        "version": ref["version"],
        "kind": "collector-rules",
        "title": "news channel",
        "entry": {"collector": "telegram", "rules": "rules.json"},
        "tests": [],
        "provenance": {"created_by": "human"},
    }
    (folder / "jane-package.json").write_text(json.dumps(manifest), encoding="utf-8")
    (folder / "rules.json").write_text(json.dumps(telegram_rules(USERNAME)), encoding="utf-8")
    svc = service_factory(JANE_TELEGRAM_COLLECTOR_RULES_DIR=str(tmp_path / "rules"))
    svc.start()
    with svc.client() as api:
        assert api.get("/v1/health").json()["status"] == "ok"
        info = api.get("/v1/info").json()
        assert info["service"] == "telegram-collector"
        assert info["capabilities"]["source_kinds"] == ["telegram"]
        assert "local_dir" in info["capabilities"]["rules_sources"]
        check = api.post("/v1/rules/validations", json=telegram_rules(USERNAME)).json()
        assert check == {"valid": True, "supported": True, "errors": [], "warnings": []}
        one = api.post(
            "/v1/fetches",
            json={"source_kind": "telegram", "telegram": {"channel_username": USERNAME, "message_id": 3}},
        )
        assert one.status_code == 200 and not list(material_validator.iter_errors(one.json()))
        cid = start(
            api, {"source_kind": "telegram", "source_id": "news-tg", "rules_ref": ref, "mode": "incremental"}
        )
        items = drain(api, cid)
        view = wait_done(api, cid)
        state = api.get("/v1/states/news-tg").json()
    assert view["status"] == "succeeded" and view["rules"] == ref
    assert len(items) == 12
    for m in items:
        assert not list(material_validator.iter_errors(m))
        assert m["collector"]["rules"] == ref
    assert state["cursors"]["-1001234567890"]["last_message_id"] == 12
    assert (svc.state_dir / "state.db").is_file()


def test_collection_resumes_after_hard_kill(service_factory: ServiceFactory, tmp_path: Path) -> None:
    make_channel(tmp_path / "recordings", 200)
    first = service_factory(**SLOW_READ)
    first.start()
    received: list[dict[str, Any]] = []
    with first.client() as api:
        cid = start_slow(api, "kill")
        body_ = page(api, cid, limit=10, wait_ms=5000)
        received += body_["items"]
        after = body_["next_cursor"]
        wait_for(api, cid, lambda v: v["stats"]["emitted"] >= 30)
    first.kill()
    with httpx.Client(base_url=first.base, timeout=2, trust_env=False) as dead:
        try:
            dead.get("/v1/health")
            raise AssertionError("the first process still answers")
        except httpx.HTTPError:
            pass

    second = service_factory(**SLOW_READ)
    second.start()
    with second.client() as api:
        view = api.get(f"/v1/collections/{cid}").json()
        assert view["status"] in {"queued", "running"}
        emitted_at_kill = view["stats"]["emitted"]
        assert 30 <= emitted_at_kill < 200
        # continue the stream with the last cursor: unacknowledged materials first, then new ones
        while True:
            body_ = page(api, cid, after, limit=25, wait_ms=2000)
            received += body_["items"]
            after = body_["next_cursor"] or after
            if body_["end_of_stream"]:
                break
        view = wait_done(api, cid)
        job = api.get(f"/v1/jobs/{cid}").json()
    assert view["status"] == "succeeded" and job["status"] == "succeeded"
    assert view["stats"]["emitted"] == 200
    assert_each_message_once(received, 200)
    assert '"resuming collection"' in second.log()


def test_two_instances_share_state_and_take_over_after_kill(
    service_factory: ServiceFactory, tmp_path: Path
) -> None:
    make_channel(tmp_path / "recordings", 80)
    a = service_factory(**SLOW_READ)
    b = service_factory(**SLOW_READ)
    a.start()
    b.start()
    received: list[dict[str, Any]] = []
    with a.client() as api_a, b.client() as api_b:
        cid = start_slow(api_a, "shared", {"queue": {"max_unacked_materials": 10}})
        # the collection runs on A; B reads and acknowledges its materials from the shared state
        body_ = page(api_b, cid, limit=10, wait_ms=5000)
        received += body_["items"]
        body_ = page(api_b, cid, body_["next_cursor"], limit=10, wait_ms=5000)  # acknowledges the first page
        received += body_["items"]
        after = body_["next_cursor"]
        wait_for(api_b, cid, lambda v: v["stats"]["emitted"] >= 12)
        # the same Idempotency-Key through the other instance returns the same job
        again = api_b.post(
            "/v1/collections",
            json=body("shared", {"queue": {"max_unacked_materials": 10}}),
            headers={"Idempotency-Key": "k-shared"},
        )
        assert again.json()["job_id"] == cid and again.headers["Idempotency-Replayed"] == "true"
        a.kill()
        while True:
            body_ = page(api_b, cid, after, limit=7, wait_ms=2000)
            received += body_["items"]
            after = body_["next_cursor"] or after
            if body_["end_of_stream"]:
                break
        view = wait_done(api_b, cid)
    assert view["status"] == "succeeded"
    assert_each_message_once(received, 80)
    assert '"resuming collection"' in b.log()


def test_stalled_owner_is_fenced_out(service_factory: ServiceFactory, tmp_path: Path) -> None:
    make_channel(tmp_path / "recordings", 60)
    a = service_factory(**SLOW_READ)
    b = service_factory(**SLOW_READ)
    a.start()
    b.start()
    with a.client() as api_a, b.client() as api_b:
        cid = start_slow(api_a, "stall", {"queue": {"max_unacked_materials": 10}})
        # freeze A while it waits for the consumer (outside a write transaction: a process frozen inside
        # one would block the shared SQLite file for everybody, which no lease can fix)
        wait_for(api_a, cid, lambda v: v["paused_by_backpressure"])
        time.sleep(0.3)
        a.suspend()  # alive but frozen: no heartbeat, the lease expires, B takes the collection over
        items = drain(api_b, cid, timeout=60)
        view = wait_done(api_b, cid)
        a.resume()  # A wakes up with a stale lease: its next write must be rejected
        time.sleep(3)
        after = api_b.get(f"/v1/collections/{cid}").json()
        job = api_b.get(f"/v1/jobs/{cid}").json()
    assert view["status"] == "succeeded" and after["status"] == "succeeded" and job["status"] == "succeeded"
    assert after["stats"]["emitted"] == 60
    assert_each_message_once(items, 60)
    assert "lease lost" in a.log(), a.log()[-3000:]


def wait_log(svc: Any, text: str, timeout: float = 30) -> None:
    deadline = time.monotonic() + timeout
    while text not in svc.log():
        if time.monotonic() > deadline:
            raise AssertionError(f"{text!r} not in the log")
        time.sleep(0.1)


def freeze_owner_on_backpressure(a: Any, b: Any, api_a: httpx.Client, state_key: str) -> str:
    """Start a collection on A, freeze A while it waits for the consumer; B takes the collection over."""
    cid = start_slow(api_a, state_key, {"queue": {"max_unacked_materials": 10}})
    # frozen outside a write transaction (a process frozen inside one blocks the SQLite file for everybody)
    wait_for(api_a, cid, lambda v: v["paused_by_backpressure"])
    time.sleep(0.3)
    a.suspend()
    wait_log(b, '"resuming collection"')
    return cid


def test_stale_owner_does_not_touch_the_new_owners_paused_flag(
    service_factory: ServiceFactory, tmp_path: Path
) -> None:
    """Review 1: A wakes up while B (the new owner) is paused by backpressure: the flag stays B's."""
    make_channel(tmp_path / "recordings", 60)
    a = service_factory(**SLOW_READ)
    b = service_factory(**SLOW_READ)
    a.start()
    b.start()
    with a.client() as api_a, b.client() as api_b:
        cid = freeze_owner_on_backpressure(a, b, api_a, "flag")
        # B continues and stops at the same full buffer (nobody consumes yet)
        before = wait_for(api_b, cid, lambda v: v["paused_by_backpressure"] and v["stats"]["unacked"] == 10)
        a.resume()
        wait_log(a, "lease lost")
        time.sleep(1.5)  # A has run its heartbeat and its backpressure loop after waking up
        after = api_b.get(f"/v1/collections/{cid}").json()
        assert before["paused_by_backpressure"] is True
        assert after["paused_by_backpressure"] is True, "stale owner cleared the new owner's paused flag"
        assert after["status"] == "running" and after["stats"]["unacked"] == 10
        items = drain(api_b, cid, limit=7, timeout=60)
        view = wait_done(api_b, cid)
        job = api_b.get(f"/v1/jobs/{cid}").json()
    assert view["status"] == "succeeded" and job["status"] == "succeeded"
    assert view["paused_by_backpressure"] is False
    assert view["stats"]["emitted"] == 60
    assert_each_message_once(items, 60)


def test_stalled_owner_wakes_while_the_new_owner_works(
    service_factory: ServiceFactory, tmp_path: Path
) -> None:
    """Review 1: A is unfrozen in the middle of B's run (B reading and emitting): A writes nothing more."""
    make_channel(tmp_path / "recordings", 120)
    a = service_factory(**SLOW_READ)
    b = service_factory(**SLOW_READ)
    a.start()
    b.start()
    received: list[dict[str, Any]] = []
    with a.client() as api_a, b.client() as api_b:
        cid = freeze_owner_on_backpressure(a, b, api_a, "wake")
        after: str | None = None
        resumed = False
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            body_ = page(api_b, cid, after, limit=5, wait_ms=2000)
            received += body_["items"]
            after = body_["next_cursor"] or after
            if not resumed and len({m["observation_id"] for m in received}) >= 40:
                view = api_b.get(f"/v1/collections/{cid}").json()
                assert view["status"] == "running" and view["stats"]["emitted"] < 120
                a.resume()  # B is still reading the channel
                resumed = True
            if body_["end_of_stream"]:
                break
        assert resumed
        view = wait_done(api_b, cid)
        job = api_b.get(f"/v1/jobs/{cid}").json()
    assert view["status"] == "succeeded" and job["status"] == "succeeded"
    assert view["stats"]["emitted"] == 120
    assert_each_message_once(received, 120)
    assert "lease lost" in a.log(), a.log()[-3000:]


def test_cancellation_through_another_instance(service_factory: ServiceFactory, tmp_path: Path) -> None:
    make_channel(tmp_path / "recordings", 40)
    a = service_factory()
    b = service_factory()
    a.start()
    b.start()
    with a.client() as api_a, b.client() as api_b:
        cid = start(api_a, body("cancel", {"queue": {"max_unacked_materials": 3}}))
        wait_for(api_b, cid, lambda v: v["paused_by_backpressure"])
        r = api_b.post(f"/v1/jobs/{cid}/cancel", json={"reason": "stop"})
        assert r.status_code == 202
        view = wait_for(api_a, cid, lambda v: v["status"] == "cancelled")
        job = api_a.get(f"/v1/jobs/{cid}").json()
    assert view["status"] == "cancelled" and job["status"] == "cancelled"
    assert job["cancellation"]["reason"] == "stop"
