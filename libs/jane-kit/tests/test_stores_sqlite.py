"""Shared SQLite stores (R17): idempotency with leases and fencing, jobs with leases, jobs mirroring work rows."""

from __future__ import annotations

import asyncio
import json
import sqlite3
import time
from pathlib import Path

import pytest

from jane_kit.errors import Conflict
from jane_kit.idempotency import IdempotencyInProgress, IdempotencyKeyReused, StoredResponse, run_idempotent
from jane_kit.jobs import Job, JobCancellation, JobContext, JobProgress, JobRunner, JobStatus
from jane_kit.stores.sqlite import SqliteDatabase, SqliteIdempotencyStore, SqliteJobStore, SqliteWorkJobStore


@pytest.fixture
def db(tmp_path: Path) -> SqliteDatabase:
    return SqliteDatabase(tmp_path / "state.sqlite", busy_timeout_ms=5_000)


def idem(db: SqliteDatabase, owner: str, lease: float = 60.0) -> SqliteIdempotencyStore:
    store = SqliteIdempotencyStore(db, owner=owner, in_progress_lease_s=lease)
    store.migrate()
    return store


async def test_idempotency_replay_reuse_and_in_progress_across_instances(db: SqliteDatabase) -> None:
    a, b = idem(db, "a"), idem(db, "b")
    calls = 0

    async def handler() -> StoredResponse:
        nonlocal calls
        calls += 1
        return StoredResponse(202, {"job_id": "job_1"}, {"Location": "/v1/jobs/job_1"})

    first, replayed = await run_idempotent(a, "k1", "fp", handler)
    assert (first.status_code, replayed) == (202, False)
    again, replayed = await run_idempotent(b, "k1", "fp", handler)  # another instance replays it
    assert replayed and again.body == {"job_id": "job_1"} and again.headers["Location"] == "/v1/jobs/job_1"
    with pytest.raises(IdempotencyKeyReused):
        await run_idempotent(b, "k1", "other", handler)
    assert await a.begin("k2", "fp", 60) is None  # claimed, still running
    with pytest.raises(IdempotencyInProgress):
        await run_idempotent(b, "k2", "fp", handler)
    assert calls == 1


async def test_claim_of_a_stopped_instance_is_taken_over_and_the_late_writer_is_fenced(
    db: SqliteDatabase,
) -> None:
    dead, alive = idem(db, "dead", lease=0.2), idem(db, "alive")
    assert await dead.begin("k", "fp", 60) is None
    record = await alive.begin("k", "fp", 60)
    assert record is not None and record.state == "in_progress"  # lease still live: 409 for the client
    await asyncio.sleep(0.3)
    assert await alive.begin("k", "fp", 60) is None  # the stopped instance's claim expired: taken over
    await dead.complete("k", StoredResponse(200, {"from": "dead"}))  # fenced by the token: no effect
    await dead.release("k")
    await alive.complete("k", StoredResponse(200, {"from": "alive"}))
    replay = await dead.begin("k", "fp", 60)
    assert replay is not None and replay.response is not None and replay.response.body == {"from": "alive"}


async def test_heartbeat_renews_only_the_claims_of_this_process(db: SqliteDatabase) -> None:
    a = idem(db, "a", lease=0.5)
    assert await a.begin("k", "fp", 60) is None
    restarted = idem(db, "a", lease=0.5)  # same owner name, new process: holds no claims
    assert await restarted.heartbeat() == 0
    assert await a.heartbeat() == 1
    await asyncio.sleep(0.3)
    assert await a.heartbeat() == 1
    await asyncio.sleep(0.3)
    record = await restarted.begin("k", "fp", 60)
    assert record is not None and record.state == "in_progress"  # renewed: no second execution
    await a.release("k")
    assert await restarted.begin("k", "fp", 60) is None  # released for a retry


async def test_expired_keys_are_forgotten(db: SqliteDatabase) -> None:
    a = idem(db, "a")
    assert await a.begin("k", "fp", 0.1) is None
    await a.complete("k", StoredResponse(200, {}))
    await asyncio.sleep(0.2)
    assert await a.begin("k", "other", 60) is None  # TTL over: a new request


def test_migration_keeps_legacy_rows_readable(tmp_path: Path) -> None:
    """A state file of the collectors before R17: ``idempotency`` without lease/owner/token columns."""
    path = tmp_path / "old.sqlite"
    raw = sqlite3.connect(path)
    raw.executescript(
        "CREATE TABLE idempotency (key TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, state TEXT NOT NULL, "
        "expires_at REAL NOT NULL, response TEXT);"
        "CREATE TABLE jobs (job_id TEXT PRIMARY KEY, body TEXT NOT NULL);"
    )
    raw.execute(
        "INSERT INTO idempotency VALUES ('old', 'fp', 'completed', ?, ?)",
        (time.time() + 600, json.dumps({"status_code": 202, "body": {"job_id": "j"}, "headers": {}})),
    )
    raw.execute("INSERT INTO idempotency VALUES ('busy', 'fp', 'in_progress', ?, NULL)", (time.time() + 600,))
    raw.commit()
    raw.close()
    db = SqliteDatabase(path, busy_timeout_ms=5_000)
    store = idem(db, "new")
    store.migrate()  # idempotent
    replay = store.begin_sync("old", "fp", 60)
    assert replay is not None and replay.response is not None and replay.response.status_code == 202
    busy = store.begin_sync("busy", "fp", 60)  # a legacy claim has no lease: it keeps its TTL
    assert busy is not None and busy.state == "in_progress"


# ---------------------------------------------------------------------------------------------- own-lease jobs
def jobs(db: SqliteDatabase, owner: str, lease: float = 60.0) -> SqliteJobStore:
    store = SqliteJobStore(db, owner=owner, lease_s=lease, retention_s=3600)
    store.migrate()
    return store


async def test_job_is_shared_and_a_stopped_owner_is_reaped(db: SqliteDatabase) -> None:
    a, b = jobs(db, "a", lease=0.2), jobs(db, "b")
    job = Job(job_id="job_1", kind="demo")
    await a.create(job)
    with pytest.raises(Conflict):
        await b.create(job)
    await a.save(job.model_copy(update={"status": JobStatus.RUNNING}))
    seen = await b.get("job_1")
    assert seen is not None and seen.status == JobStatus.RUNNING
    await asyncio.sleep(0.3)
    failed = await b.get("job_1")
    assert failed is not None and failed.status == JobStatus.FAILED
    assert failed.error is not None and failed.error.code == "service_unavailable" and failed.error.retryable
    await a.save(job.model_copy(update={"status": JobStatus.SUCCEEDED}))  # the late owner is fenced
    final = await b.get("job_1")
    assert final is not None and final.status == JobStatus.FAILED


async def test_cancel_from_another_instance_wins_over_a_stale_success(db: SqliteDatabase) -> None:
    a, b = jobs(db, "a"), jobs(db, "b")
    job = Job(job_id="job_2", kind="demo", status=JobStatus.RUNNING)
    await a.create(job)
    await b.save(job.model_copy(update={"status": JobStatus.SUCCEEDED}))  # not the owner: ignored
    await b.save(
        job.model_copy(
            update={
                "status": JobStatus.CANCELLING,
                "cancellation": JobCancellation(requested_at=job.created_at),
            }
        )
    )
    await a.save(job.model_copy(update={"progress": JobProgress(completed=3)}))  # progress keeps cancelling
    current = await b.get("job_2")
    assert current is not None and current.status == JobStatus.CANCELLING and current.progress is not None
    await a.save(job.model_copy(update={"status": JobStatus.SUCCEEDED, "result": {"x": 1}}))
    done = await b.get("job_2")
    assert done is not None and done.status == JobStatus.CANCELLED and done.result is None
    assert done.cancellation is not None


async def test_heartbeat_and_sweep(db: SqliteDatabase) -> None:
    a = jobs(db, "a", lease=0.4)
    await a.create(Job(job_id="job_3", kind="demo"))
    await a.create(Job(job_id="job_4", kind="demo"))
    await a.save(Job(job_id="job_4", kind="demo", status=JobStatus.SUCCEEDED))
    await asyncio.sleep(0.25)
    assert await a.heartbeat() == 1  # only the unfinished job of this process
    await asyncio.sleep(0.25)
    assert await jobs(db, "b").sweep() == 0  # renewed
    await asyncio.sleep(0.5)
    assert await jobs(db, "b").sweep() == 1


async def test_runner_on_the_sqlite_store(db: SqliteDatabase) -> None:
    runner = JobRunner(store=jobs(db, "a"))

    async def work(ctx: JobContext) -> dict[str, int]:
        await ctx.progress(1, 2)
        return {"n": 2}

    job = await runner.submit("demo", work)
    done = await runner.wait(job.job_id)
    assert done.status == JobStatus.SUCCEEDED and done.result == {"n": 2}


# ---------------------------------------------------------------------------------------------- work-row jobs
class Work:
    """Leased work rows of a service (the collectors' ``collections``)."""

    def __init__(self, db: SqliteDatabase) -> None:
        with db.tx() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS work (id TEXT PRIMARY KEY, owner TEXT, status TEXT NOT NULL)"
            )
        self.db = db

    def put(self, job_id: str, owner: str | None, status: str) -> None:
        with self.db.tx() as conn:
            conn.execute("INSERT OR REPLACE INTO work VALUES (?, ?, ?)", (job_id, owner, status))

    def status(self, job_id: str) -> str:
        with self.db.tx() as conn:
            return str(conn.execute("SELECT status FROM work WHERE id = ?", (job_id,)).fetchone()[0])

    def work_row(self, db: sqlite3.Connection, job_id: str) -> tuple[str | None, str] | None:
        row = db.execute("SELECT owner, status FROM work WHERE id = ?", (job_id,)).fetchone()
        return (row[0], str(row[1])) if row else None

    def cancel_unstarted(self, db: sqlite3.Connection, job_id: str, owner: str) -> bool:
        return (
            db.execute(
                "UPDATE work SET status = 'cancelled' WHERE id = ? AND status = 'queued' AND owner = ?",
                (job_id, owner),
            ).rowcount
            == 1
        )


def work_jobs(db: SqliteDatabase, work: Work, owner: str) -> SqliteWorkJobStore:
    store = SqliteWorkJobStore(db, work, owner=owner)
    store.migrate()
    return store


async def test_work_job_mirrors_the_work_row(db: SqliteDatabase) -> None:
    work = Work(db)
    a, b = work_jobs(db, work, "a"), work_jobs(db, work, "b")
    work.put("c1", "a", "running")
    job = Job(job_id="c1", kind="collection", status=JobStatus.RUNNING)
    await a.create(job)
    await a.save(job.model_copy(update={"status": JobStatus.SUCCEEDED}))  # the work is not finished yet
    assert (await b.get("c1")).status == JobStatus.RUNNING  # type: ignore[union-attr]
    await b.save(job.model_copy(update={"progress": JobProgress(completed=9)}))  # not the lease holder
    assert (await b.get("c1")).progress is None  # type: ignore[union-attr]
    work.put("c1", "b", "running")  # b took the lease over and resumes under the same job id
    await b.create(Job(job_id="c1", kind="collection", idempotency_key="other"))
    resumed = await b.get("c1")
    assert resumed is not None and resumed.created_at == job.created_at and resumed.idempotency_key is None
    await a.save(job.model_copy(update={"status": JobStatus.CANCELLED}))  # the old owner is fenced
    work.put("c1", "b", "succeeded")
    await b.save(job.model_copy(update={"status": JobStatus.FAILED}))  # mirrors the work row's status
    final = await a.get("c1")
    assert final is not None and final.status == JobStatus.SUCCEEDED
    await a.save(final.model_copy(update={"status": JobStatus.CANCELLING}))  # terminal never changes
    assert (await a.get("c1")).status == JobStatus.SUCCEEDED  # type: ignore[union-attr]


async def test_work_job_cancelled_before_it_started(db: SqliteDatabase) -> None:
    work = Work(db)
    a, b = work_jobs(db, work, "a"), work_jobs(db, work, "b")
    work.put("c2", "a", "queued")
    job = Job(job_id="c2", kind="collection")
    await a.create(job)
    await b.save(
        job.model_copy(
            update={
                "status": JobStatus.CANCELLING,
                "cancellation": JobCancellation(requested_at=job.created_at),
            }
        )
    )  # any instance may request cancellation
    await a.save(job.model_copy(update={"progress": JobProgress(completed=1)}))
    assert (await a.get("c2")).status == JobStatus.CANCELLING  # type: ignore[union-attr]
    await a.save(job.model_copy(update={"status": JobStatus.CANCELLED}))
    assert work.status("c2") == "cancelled"
    assert (await b.get("c2")).status == JobStatus.CANCELLED  # type: ignore[union-attr]
    cancelled = await b.get("c2")
    assert cancelled is not None and cancelled.cancellation is not None  # the request's record is kept
    await b.create(Job(job_id="c2", kind="collection"))  # resubmitting a finished job changes nothing
    assert await b.get("c2") == cancelled
