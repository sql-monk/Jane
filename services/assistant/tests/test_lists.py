"""R24 (WP-15): lists of onboarding sessions and improvement runs, so the admin UI recovers after a reload.

Responses go through ``ContractClient`` (schemas of ``listOnboardingSessions`` / ``listImprovementRuns``);
cursor pagination per the conventions (``limit`` clamped to ``pages.max_page_size``, ``next_cursor`` null on the
last page, an unknown cursor is 422). The shared PostgreSQL variant is in ``test_state.py``.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from assistant_fakes import World, world
from assistant_fakes.site import material, page

from jane_assistant.onboarding import Session
from jane_assistant.settings import ServiceLimits, Settings
from jane_assistant.state import InMemoryState
from jane_kit.jobs import Job, JobStatus
from jane_kit.pagination import encode_cursor


def start(w: World, query: str, key: str) -> tuple[str, str]:
    r = w.api.post(
        "/v1/onboarding-sessions",
        json={"query": query, "expected_entity_types": ["product"]},
        headers={"Idempotency-Key": key},
    )
    assert r.status_code == 202
    w.wait(r.json()["job_id"])
    return r.json()["job_id"], r.json()["labels"]["session_id"]


def pages(w: World, path: str, **params: Any) -> list[list[dict[str, Any]]]:
    out: list[list[dict[str, Any]]] = []
    cursor: str | None = None
    while True:
        query = {**params, **({"cursor": cursor} if cursor else {})}
        body = w.api.get(path, params=query).json()
        out.append(body["items"])
        cursor = body["next_cursor"]
        if cursor is None:
            return out


def test_onboarding_sessions_are_listed_newest_first_with_cursor_pages(w: World) -> None:
    started = [start(w, "Shop Example kettles", f"list-{i}")[1] for i in range(3)]
    direct = start(w, "https://shop.example.test/", "list-direct")[1]  # samples and analyses: proposals_ready

    all_pages = pages(w, "/v1/onboarding-sessions", limit=2)
    assert [len(p) for p in all_pages] == [2, 2]
    items = [s for p in all_pages for s in p]
    assert sorted(s["session_id"] for s in items) == sorted([*started, direct])  # each once, none lost
    positions = [(s["created_at"], s["session_id"]) for s in items]
    assert positions == sorted(positions, reverse=True)  # newest first, ties by session_id
    by_id = {s["session_id"]: s for s in items}
    assert by_id[direct]["status"] == "proposals_ready" and by_id[direct]["proposal_count"] >= 1
    assert by_id[direct]["costs"]["currency"] == "USD"
    assert all(
        by_id[s]["status"] == "needs_disambiguation" and by_id[s]["proposal_count"] == 0 for s in started
    )
    for s in items:  # the summary agrees with the full session
        full = w.api.get(f"/v1/onboarding-sessions/{s['session_id']}").json()
        assert {k: full[k] for k in ("status", "query", "created_at", "job_id")} == {
            k: s[k] for k in ("status", "query", "created_at", "job_id")
        }

    ready = w.api.get("/v1/onboarding-sessions", params={"status": "proposals_ready"}).json()
    assert [s["session_id"] for s in ready["items"]] == [direct] and ready["next_cursor"] is None
    both = w.api.get(
        "/v1/onboarding-sessions", params=[("status", "proposals_ready"), ("status", "needs_disambiguation")]
    ).json()
    assert len(both["items"]) == 4


def test_list_parameters_are_checked(w: World) -> None:
    bad_cursor = w.client.get("/v1/onboarding-sessions", params={"cursor": "not-a-cursor"})
    assert bad_cursor.status_code == 422 and bad_cursor.json()["code"] == "validation_failed"
    foreign = w.client.get("/v1/improvement-runs", params={"cursor": "WyJ4Il0"})  # ["x"]: not [position, id]
    assert foreign.status_code == 422
    bad_status = w.client.get("/v1/onboarding-sessions", params={"status": "done"})
    assert bad_status.status_code == 422
    assert w.client.get("/v1/improvement-runs", params={"status": "finished"}).status_code == 422
    empty = w.api.get("/v1/improvement-runs").json()
    assert empty == {"items": [], "next_cursor": None}


def _improve(w: World, package_id: str, key: str, **extra: Any) -> str:
    body = {
        "package": {"package_id": package_id, "version": "1.0.0"},
        "problem_samples": [{"material_ref": {"storage_connection_id": "raw", "object_id": "o"}}],
        **extra,
    }
    r = w.api.post("/v1/improvement-runs", json=body, headers={"Idempotency-Key": key})
    assert r.status_code == 202
    w.wait(r.json()["job_id"])
    return str(r.json()["job_id"])


def test_improvement_runs_are_listed_with_filters(w: World) -> None:
    # The registry fake knows no package: every run fails (404) - the list shows them with their errors.
    a = _improve(w, "shop.extractor", "imp-a", source_id="shop-example", problem_group_id="pg_1")
    b = _improve(w, "shop.extractor", "imp-b", source_id="other-source")
    c = _improve(w, "news.extractor", "imp-c")
    other_kind = w.api.post(  # a job of another kind is not an improvement run
        "/v1/unknown-materials",
        json={
            "source_id": "shop-example",
            "forward_unknown_to_llm": True,
            "material": material(
                "https://shop.example.test/events/1", page("event", "Concert", ""), "shop-example"
            ),
        },
        headers={"Idempotency-Key": "not-an-improvement"},
    )
    assert other_kind.status_code == 202
    w.wait(other_kind.json()["job_id"])

    listed = [j for p in pages(w, "/v1/improvement-runs", limit=1) for j in p]
    assert sorted(j["job_id"] for j in listed) == sorted([a, b, c])
    assert all(j["kind"] == "improvement" and j["status"] == "failed" for j in listed)
    positions = [(j["created_at"], j["job_id"]) for j in listed]
    assert positions == sorted(positions, reverse=True)

    def ids(**params: Any) -> set[str]:
        return {j["job_id"] for j in w.api.get("/v1/improvement-runs", params=params).json()["items"]}

    assert ids(package_id="shop.extractor") == {a, b}
    assert ids(package_id="shop.extractor", source_id="shop-example") == {a}
    assert ids(problem_group_id="pg_1") == {a}
    assert ids(status="failed") == {a, b, c}
    assert ids(status="succeeded") == set()
    first = next(j for j in listed if j["job_id"] == a)
    assert first["labels"] == {
        "package_id": "shop.extractor",
        "source_id": "shop-example",
        "problem_group_id": "pg_1",
    }


def test_page_size_comes_from_the_configured_limit(contracts: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JANE_ASSISTANT_LIMITS__PAGES__MAX_PAGE_SIZE", "1")
    with world(contracts, Settings(log_format="console", contracts_dir=contracts)) as w:
        for i in range(2):
            start(w, "Shop Example kettles", f"cap-{i}")
        body = w.api.get("/v1/onboarding-sessions", params={"limit": 1000}).json()
        assert len(body["items"]) == 1 and body["next_cursor"]  # clamped, not an error
        assert w.violations() == []


# ------------------------------------------------------------------ review 1 (WP-15)
BAD_CURSORS = [
    ["garbage", "onb_x"],  # not a time (PostgreSQL used to fail on ::timestamptz -> 500)
    ["2026-01-01T00:00:00", "job_x"],  # a naive time (compared with aware times -> TypeError, 500)
    ["2026-01-01T00:00:00+00:00", "job_x"],  # another format than the one the service writes
    ["2026-01-01T00:00:00.000000Z", "bad id with spaces"],  # not a service id
    "not-a-list",
    ["2026-01-01T00:00:00.000000Z"],
]


@pytest.mark.parametrize("path", ["/v1/onboarding-sessions", "/v1/improvement-runs"])
@pytest.mark.parametrize("cursor", BAD_CURSORS, ids=lambda c: str(c)[:30])
def test_a_foreign_cursor_is_422_never_500(w: World, path: str, cursor: Any) -> None:
    start(w, "Shop Example kettles", "bad-cursor-session")  # at least one item of each list to compare with
    _improve(w, "shop.extractor", "bad-cursor-run")
    r = w.client.get(path, params={"cursor": encode_cursor(cursor)})
    assert r.status_code == 422, r.text
    assert r.json()["code"] == "validation_failed"
    assert r.json()["errors"][0]["parameter"] == "cursor"


def test_pages_stay_stable_when_items_are_added_between_them(w: World) -> None:
    """Keyset cursor: an item created after page 1 is newer than the cursor - never on a later page, no item
    is repeated or lost (sessions have microsecond ``created_at``, so even one second is ordered)."""
    first = [start(w, "Shop Example kettles", f"stable-{i}")[1] for i in range(3)]
    page1 = w.api.get("/v1/onboarding-sessions", params={"limit": 2}).json()
    newer = start(w, "Shop Example kettles", "stable-new")[1]
    page2 = w.api.get("/v1/onboarding-sessions", params={"limit": 2, "cursor": page1["next_cursor"]}).json()
    seen = [s["session_id"] for s in page1["items"] + page2["items"]]
    assert sorted(seen) == sorted(first) and newer not in seen and page2["next_cursor"] is None
    assert w.api.get("/v1/onboarding-sessions", params={"limit": 1}).json()["items"][0]["session_id"] == newer

    runs = [_improve(w, "shop.extractor", f"stable-run-{i}") for i in range(3)]
    p1 = w.api.get("/v1/improvement-runs", params={"limit": 2}).json()
    late = _improve(w, "shop.extractor", "stable-run-new")
    p2 = w.api.get("/v1/improvement-runs", params={"limit": 2, "cursor": p1["next_cursor"]}).json()
    listed = [j["job_id"] for j in p1["items"] + p2["items"]]
    assert sorted(listed) == sorted(runs) and late not in listed and p2["next_cursor"] is None


def test_status_filter_sees_the_status_get_reports(w: World) -> None:
    """A session stored as ``sampling`` whose job already failed (its instance stopped) is listed under
    ``failed`` - as ``GET`` reports it - and not under ``sampling``."""
    state = w.client.app.state.service_state  # type: ignore[attr-defined]
    job = Job(job_id="job_dead1", kind="onboarding", status=JobStatus.FAILED, error=None)
    session = Session(
        session_id="onb_dead1", query="https://shop.example.test/", request={}, status="sampling"
    )
    session.job_id = job.job_id
    asyncio.run(state.jobs.create(job))
    asyncio.run(state.sessions.save(session))

    def ids(status: str) -> list[str]:
        body = w.api.get("/v1/onboarding-sessions", params={"status": status}).json()
        return [s["session_id"] for s in body["items"]]

    assert ids("failed") == ["onb_dead1"]  # asked first: the stored status is still `sampling` here
    assert ids("sampling") == []
    assert w.api.get("/v1/onboarding-sessions/onb_dead1").json()["status"] == "failed"


def test_memory_job_list_holds_no_job_past_its_retention() -> None:
    """``_ListedMemoryJobs`` lists the store itself: a finished job past ``jobs.job_retention_seconds`` is dropped,
    nothing else keeps its id."""
    state = InMemoryState(ServiceLimits())
    old = datetime.now(UTC) - timedelta(days=2)

    async def scenario() -> list[Job]:
        await state.jobs.create(Job(job_id="job_new1", kind="improvement"))
        # created last, so no later `create` drops it: the list itself applies the retention
        await state.jobs.create(
            Job(
                job_id="job_old1",
                kind="improvement",
                status=JobStatus.FAILED,
                created_at=old,
                finished_at=old,
            )
        )
        return await state.job_list.page("improvement", labels={}, statuses=None, after=None, limit=10)

    assert [j.job_id for j in asyncio.run(scenario())] == ["job_new1"]
    assert asyncio.run(state.jobs.get("job_old1")) is None
