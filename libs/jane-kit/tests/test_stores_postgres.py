"""Shared PostgreSQL stores (R17) against a real PostgreSQL (``@pytest.mark.integration``).

PostgreSQL: ``JANE_KIT_PG_DSN`` or the dev stack (``just up --project <p> postgres`` and
``just integration --project <p> libs/jane-kit``). Every test uses its own schema and drops it afterwards.
"""

from __future__ import annotations

import asyncio
import os
import threading
import uuid
from collections.abc import Iterator
from datetime import timedelta
from typing import Any

import pytest

from jane_kit.devstack import load_stack
from jane_kit.errors import Conflict
from jane_kit.idempotency import IdempotencyInProgress, IdempotencyKeyReused, StoredResponse, run_idempotent
from jane_kit.jobs import Job, JobCancellation, JobContext, JobProgress, JobRunner, JobStatus

pytestmark = pytest.mark.integration

psycopg = pytest.importorskip("psycopg")
from psycopg import sql  # noqa: E402

from jane_kit.stores.postgres import PgDatabase, PgIdempotencyStore, PgJobStore, migrate  # noqa: E402


def _dsn() -> str | None:
    if env := os.environ.get("JANE_KIT_PG_DSN"):
        return env
    stack = load_stack()
    if stack is None or "postgres" not in stack.services:
        return None
    return str(stack.get("postgres", "dsn"))


@pytest.fixture
def pg() -> Iterator[tuple[PgDatabase, str]]:
    dsn = _dsn()
    if dsn is None:
        pytest.skip("no PostgreSQL: set JANE_KIT_PG_DSN or run `just up --project <p> postgres`")
    schema = f"kit_{uuid.uuid4().hex[:10]}"
    db = PgDatabase(dsn, max_size=8, connect_timeout_ms=10_000)
    db.open()
    try:
        yield db, schema
    finally:
        db.close()
        with psycopg.connect(dsn, autocommit=True) as conn:
            conn.execute(sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(schema)))


def idem(pg: tuple[PgDatabase, str], owner: str, lease: float = 60.0, **kw: Any) -> PgIdempotencyStore:
    db, schema = pg
    store = PgIdempotencyStore(db.tx, owner=owner, in_progress_lease_s=lease, schema=schema, **kw)
    migrate(db.tx, f"kit-test-{schema}", store, schema=schema)
    return store


def jobs(pg: tuple[PgDatabase, str], owner: str, lease: float = 60.0, **kw: Any) -> PgJobStore:
    db, schema = pg
    store = PgJobStore(db.tx, owner=owner, lease_s=lease, retention_s=3600, schema=schema, **kw)
    migrate(db.tx, f"kit-test-{schema}", store, schema=schema)
    return store


def execute(pg: tuple[PgDatabase, str], query: str, *params: Any) -> list[dict[str, Any]]:
    db, schema = pg
    with db.tx() as conn, conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
        cur.execute(sql.SQL(query).format(s=sql.Identifier(schema)), params)
        return list(cur.fetchall()) if cur.description else []


@pytest.mark.parametrize("layout", ["split", "json"])
async def test_idempotency_semantics_across_instances(pg: tuple[PgDatabase, str], layout: str) -> None:
    a, b = idem(pg, "a", layout=layout), idem(pg, "b", layout=layout)
    calls = 0

    async def handler() -> StoredResponse:
        nonlocal calls
        calls += 1
        return StoredResponse(202, {"job_id": "job_1", "n": [1, 2]}, {"Location": "/v1/jobs/job_1"})

    _, replayed = await run_idempotent(a, "k1", "fp", handler)
    assert not replayed
    again, replayed = await run_idempotent(b, "k1", "fp", handler)
    assert replayed and (again.status_code, again.body) == (202, {"job_id": "job_1", "n": [1, 2]})
    assert again.headers == {"Location": "/v1/jobs/job_1"}
    with pytest.raises(IdempotencyKeyReused):
        await run_idempotent(b, "k1", "other", handler)
    assert await a.begin("k2", "fp", 60) is None
    with pytest.raises(IdempotencyInProgress):
        await run_idempotent(b, "k2", "fp", handler)
    assert calls == 1


async def test_concurrent_claims_of_one_key_run_once(pg: tuple[PgDatabase, str]) -> None:
    stores = [idem(pg, f"i{n}") for n in range(6)]
    results = await asyncio.gather(*(s.begin("race", "fp", 60) for s in stores))
    assert sum(r is None for r in results) == 1  # exactly one claim


async def test_take_over_fencing_and_heartbeat(pg: tuple[PgDatabase, str]) -> None:
    dead, alive = idem(pg, "dead", lease=1.0), idem(pg, "alive")
    assert await dead.begin("k", "fp", 60) is None
    assert await dead.heartbeat() == 1
    record = await alive.begin("k", "fp", 60)
    assert record is not None and record.state == "in_progress"
    execute(pg, "UPDATE {s}.idempotency SET lease_until = clock_timestamp() - interval '1 second'")
    assert await dead.heartbeat() == 0  # an expired claim is not revived
    assert await alive.begin("k", "fp", 60) is None  # taken over
    await dead.complete("k", StoredResponse(200, {"from": "dead"}))  # fenced
    await dead.release("k")  # fenced
    await alive.complete("k", StoredResponse(200, {"from": "alive"}))
    replay = await dead.begin("k", "fp", 60)
    assert replay is not None and replay.response is not None and replay.response.body == {"from": "alive"}
    restarted = idem(pg, "alive")  # same owner name, new process: renews nothing of the old one
    assert await restarted.begin("held", "fp", 60) is None
    assert await idem(pg, "alive").heartbeat() == 0


async def test_gc_deletes_expired_keys(pg: tuple[PgDatabase, str]) -> None:
    a = idem(pg, "a")
    for n in range(3):
        assert await a.begin(f"k{n}", "fp", 60) is None
        await a.complete(f"k{n}", StoredResponse(200, {}))
    execute(
        pg,
        "UPDATE {s}.idempotency SET expires_at = clock_timestamp() - interval '1 second' WHERE key <> 'k2'",
    )
    assert await a.gc() == 2
    assert [r["key"] for r in execute(pg, "SELECT key FROM {s}.idempotency")] == ["k2"]


def test_migration_of_earlier_layouts(pg: tuple[PgDatabase, str]) -> None:
    """Tables of the services before R17: registry/llm (``response`` jsonb, no lease or token; llm jobs in a
    ``job`` column without owner/lease) and handler-runtime/assistant (split columns, lease, no token)."""
    db, schema = pg
    with db.tx() as conn:
        conn.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
        conn.execute(
            sql.SQL(
                "CREATE TABLE {}.legacy_idem (key text PRIMARY KEY, fingerprint text NOT NULL, state text NOT NULL, "
                "response jsonb, expires_at timestamptz NOT NULL)"
            ).format(sql.Identifier(schema))
        )
        conn.execute(
            sql.SQL(
                "INSERT INTO {}.legacy_idem VALUES ('old', 'fp', 'completed', %s, now() + interval '1 hour')"
            ).format(sql.Identifier(schema)),
            (psycopg.types.json.Jsonb({"status_code": 201, "body": {"a": 1}, "headers": {"X": "y"}}),),
        )
        conn.execute(
            sql.SQL(
                "CREATE TABLE {}.legacy_jobs (job_id text PRIMARY KEY, job jsonb NOT NULL, "
                "updated_at timestamptz NOT NULL DEFAULT now())"
            ).format(sql.Identifier(schema))
        )
        done = Job(job_id="job_done", kind="demo", status=JobStatus.SUCCEEDED, result={"ok": True})
        done = done.model_copy(update={"finished_at": done.created_at + timedelta(seconds=1)})
        running = Job(job_id="job_running", kind="demo", status=JobStatus.RUNNING)
        for job in (done, running):
            conn.execute(
                sql.SQL("INSERT INTO {}.legacy_jobs (job_id, job) VALUES (%s, %s)").format(
                    sql.Identifier(schema)
                ),
                (job.job_id, psycopg.types.json.Jsonb(job.model_dump(mode="json"))),
            )
    store = PgIdempotencyStore(
        db.tx, owner="new", in_progress_lease_s=60, schema=schema, table="legacy_idem", layout="json"
    )
    job_store = PgJobStore(
        db.tx, owner="new", lease_s=60, retention_s=3600, schema=schema, table="legacy_jobs", doc_column="job"
    )
    threads = [
        threading.Thread(
            target=migrate, args=(db.tx, f"kit-test-{schema}", store, job_store), kwargs={"schema": schema}
        )
        for _ in range(4)
    ]  # several instances start at once
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    replay = store.begin_sync("old", "fp", 60)
    assert replay is not None and replay.response == StoredResponse(201, {"a": 1}, {"X": "y"})
    assert job_store.get_sync("job_done") == done
    legacy = job_store.get_sync("job_running")  # one lease of grace, then reaped like any orphan
    assert legacy is not None and legacy.status == JobStatus.RUNNING
    execute(pg, "UPDATE {s}.legacy_jobs SET lease_until = clock_timestamp() - interval '1 second'")
    reaped = job_store.get_sync("job_running")
    assert reaped is not None and reaped.status == JobStatus.FAILED
    rows = execute(
        pg, "SELECT job_id, finished_at IS NOT NULL AS finished FROM {s}.legacy_jobs ORDER BY job_id"
    )
    assert rows == [{"job_id": "job_done", "finished": True}, {"job_id": "job_running", "finished": True}]


async def test_jobs_fencing_reaping_and_cancellation(pg: tuple[PgDatabase, str]) -> None:
    """Ported from handler-runtime ``test_expired_job_fails_and_old_owner_cannot_overwrite``."""
    a, b = jobs(pg, "dead-owner"), jobs(pg, "new-owner")
    job = Job(job_id=f"job_{uuid.uuid4().hex}", kind="test_run")
    await a.create(job)
    with pytest.raises(Conflict):
        await b.create(job)
    running = job.model_copy(update={"status": JobStatus.RUNNING})
    await a.save(running)
    execute(
        pg,
        "UPDATE {s}.jobs SET lease_until = clock_timestamp() + interval '1 second' WHERE job_id = %s",
        job.job_id,
    )
    assert await a.heartbeat() == 1
    renewed = execute(
        pg,
        "SELECT lease_until > clock_timestamp() + interval '20 seconds' AS ok FROM {s}.jobs WHERE job_id = %s",
        job.job_id,
    )
    assert renewed[0]["ok"] is True
    live = await b.get(job.job_id)
    assert live is not None and live.status == JobStatus.RUNNING
    execute(
        pg,
        "UPDATE {s}.jobs SET lease_until = clock_timestamp() - interval '1 second' WHERE job_id = %s",
        job.job_id,
    )
    failed = await b.get(job.job_id)
    assert failed is not None and failed.status == JobStatus.FAILED
    assert failed.error is not None and failed.error.code == "service_unavailable" and failed.error.retryable
    await a.save(running.model_copy(update={"status": JobStatus.SUCCEEDED}))
    assert (await b.get(job.job_id)).status == JobStatus.FAILED  # type: ignore[union-attr]

    # fencing holds before another instance has observed the expired lease
    second = Job(job_id=f"job_{uuid.uuid4().hex}", kind="test_run")
    await a.create(second)
    execute(
        pg,
        "UPDATE {s}.jobs SET lease_until = clock_timestamp() - interval '1 second' WHERE job_id = %s",
        second.job_id,
    )
    await a.save(second.model_copy(update={"status": JobStatus.SUCCEEDED}))
    assert (await b.get(second.job_id)).status == JobStatus.FAILED  # type: ignore[union-attr]

    # b's cancellation wins over a's success prepared from an older running snapshot
    third = Job(job_id=f"job_{uuid.uuid4().hex}", kind="test_run")
    await a.create(third)
    await b.save(third.model_copy(update={"status": JobStatus.SUCCEEDED}))  # not the owner: ignored
    await b.save(
        third.model_copy(
            update={
                "status": JobStatus.CANCELLING,
                "cancellation": JobCancellation(requested_at=third.created_at),
            }
        )
    )
    await a.save(third.model_copy(update={"progress": JobProgress(completed=1)}))
    assert (await b.get(third.job_id)).status == JobStatus.CANCELLING  # type: ignore[union-attr]
    await a.save(third.model_copy(update={"status": JobStatus.SUCCEEDED}))
    cancelled = await b.get(third.job_id)
    assert (
        cancelled is not None
        and cancelled.status == JobStatus.CANCELLED
        and cancelled.cancellation is not None
    )

    # a cancelling job of a stopped owner ends cancelled
    fourth = Job(job_id=f"job_{uuid.uuid4().hex}", kind="test_run")
    await a.create(fourth)
    await b.save(fourth.model_copy(update={"status": JobStatus.CANCELLING}))
    execute(
        pg,
        "UPDATE {s}.jobs SET lease_until = clock_timestamp() - interval '1 second' WHERE job_id = %s",
        fourth.job_id,
    )
    assert await b.sweep() == 1
    assert (await a.get(fourth.job_id)).status == JobStatus.CANCELLED  # type: ignore[union-attr]


async def test_runner_page_and_release_owned(pg: tuple[PgDatabase, str]) -> None:
    a = jobs(pg, "a")
    runner = JobRunner(store=a)
    gate = asyncio.Event()

    async def work(ctx: JobContext) -> dict[str, int]:
        await ctx.progress(1, 2)
        await gate.wait()
        return {"n": 1}

    first = await runner.submit("demo", work, labels={"session_id": "s1"})
    second = await runner.submit("demo", work, labels={"session_id": "s2"})
    await runner.submit("other", work, labels={"session_id": "s1"})
    page = await a.page("demo", labels={}, statuses=None, after=None, limit=10)
    assert [j.job_id for j in page] == [second.job_id, first.job_id]  # newest first
    only = await a.page("demo", labels={"session_id": "s1"}, statuses=None, after=None, limit=10)
    assert [j.job_id for j in only] == [first.job_id]
    after = await a.page(
        "demo", labels={}, statuses=None, after=(page[0].created_at, page[0].job_id), limit=10
    )
    assert [j.job_id for j in after] == [page[1].job_id]
    gate.set()
    done = await runner.wait(first.job_id)
    assert done.status == JobStatus.SUCCEEDED and done.result == {"n": 1}
    assert [
        j.job_id for j in await a.page("demo", labels={}, statuses=["succeeded"], after=None, limit=10)
    ] == [j.job_id for j in await a.page("demo", labels={}, statuses=None, after=None, limit=10)]
    blocked = asyncio.Event()

    async def hang(ctx: JobContext) -> None:
        await blocked.wait()

    hanging = await runner.submit("demo", hang)
    await asyncio.sleep(0.2)
    await runner.shutdown()
    assert await a.release_owned("instance a shut down") >= 1
    stopped = await a.get(hanging.job_id)
    assert stopped is not None and stopped.status == JobStatus.CANCELLED
    assert stopped.cancellation is not None and stopped.cancellation.reason == "instance a shut down"
