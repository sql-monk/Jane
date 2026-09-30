"""Review 2: a run that stops without finishing (lease lost, shutdown) never makes the job or the
collection look finished; cancellation never ends as "succeeded"."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from jane_kit.jobs import Job, JobStatus
from jane_web_collector.app import build_app
from jane_web_collector.state import StateStore
from jane_web_collector.stores import SqliteJobStore
from jane_web_collector.testing import FAST_LIMITS, Site, make_settings, start, wait_done, web_rules


def _collection(state: StateStore, cid: str, owner: str) -> None:
    state.create_collection(
        cid,
        state_key=cid,
        status="running",
        request={},
        rules={},
        rules_ref=None,
        created_at="2026-09-27T00:00:00Z",
        effective_limits={},
    )
    assert state.claim(cid, owner, 30)


async def _status(store: SqliteJobStore, job_id: str) -> JobStatus:
    job = await store.get(job_id)
    assert job is not None
    return job.status


async def test_terminal_job_only_with_finished_collection(tmp_path: Path) -> None:
    state = StateStore(tmp_path / "state.db")
    store = SqliteJobStore(state, "instance-a")
    _collection(state, "job_x", "instance-a")
    await store.create(Job(job_id="job_x", kind="collection", status=JobStatus.RUNNING))
    # the run left through LeaseLost and returned normally: jane-kit would mark the job succeeded
    await store.save(
        Job(job_id="job_x", kind="collection", status=JobStatus.SUCCEEDED, result={"handed_over": True})
    )
    assert await _status(store, "job_x") == JobStatus.RUNNING
    # graceful shutdown cancels the local task: the job must not become "cancelled" either
    await store.save(Job(job_id="job_x", kind="collection", status=JobStatus.CANCELLED))
    assert await _status(store, "job_x") == JobStatus.RUNNING
    # once the final fenced transaction marked the collection succeeded, the job may follow
    state.set_status("job_x", "succeeded", finished_at="2026-09-27T00:01:00Z")
    await store.save(Job(job_id="job_x", kind="collection", status=JobStatus.SUCCEEDED))
    assert await _status(store, "job_x") == JobStatus.SUCCEEDED
    # another instance may only request cancellation
    _collection(state, "job_y", "instance-a")
    other = SqliteJobStore(state, "instance-b")
    await store.create(Job(job_id="job_y", kind="collection", status=JobStatus.RUNNING))
    await other.save(Job(job_id="job_y", kind="collection", status=JobStatus.FAILED))
    assert await _status(store, "job_y") == JobStatus.RUNNING
    await other.save(Job(job_id="job_y", kind="collection", status=JobStatus.CANCELLING))
    assert await _status(store, "job_y") == JobStatus.CANCELLING
    state.close()


def test_view_is_not_finished_while_collection_runs(tmp_path: Path, site: Site) -> None:
    with TestClient(build_app(make_settings(tmp_path))) as client:
        body = {
            "source_kind": "web",
            "rules": web_rules(site),
            "urls": [site.url("/")],
            "limits": FAST_LIMITS,
        }
        cid = start(client, body)
        wait_done(client, cid)
        state: StateStore = client.app.state.store  # type: ignore[attr-defined]
        # a terminal job next to a collection that is not finished (e.g. resumed): not finished for readers
        state.set_status(cid, "running")
        view = client.get(f"/v1/collections/{cid}").json()
        page = client.get(f"/v1/collections/{cid}/materials").json()
        assert view["status"] == "running" and page["collection_status"] == "running"
        assert page["end_of_stream"] is False
        state.set_status(cid, "succeeded", finished_at="2026-09-27T00:00:00Z")
        assert client.get(f"/v1/collections/{cid}").json()["status"] == "succeeded"


def test_cancel_near_the_end_is_not_succeeded(client: TestClient, site: Site) -> None:
    limits = {**FAST_LIMITS, "rate": {"requests_per_second_per_host": 5, "min_delay_ms_per_host": 0}}
    urls = [site.url("/about"), site.url("/catalog/")]
    cid = start(client, {"source_kind": "web", "rules": web_rules(site), "urls": urls, "limits": limits})
    assert client.post(f"/v1/jobs/{cid}/cancel", json={"reason": "test"}).status_code in (200, 202)
    view = wait_done(client, cid)
    job = client.get(f"/v1/jobs/{cid}").json()
    assert view["status"] == job["status"] == "cancelled", (view["status"], job["status"])
