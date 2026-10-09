"""``IdempotencyStore`` and ``JobStore`` in a service's own SQLite state file (R17).

For services whose instances share one state file on one host (the collectors; SQLite locking, WAL). The tables
live next to the service's other tables; every write is one ``BEGIN IMMEDIATE`` transaction of the service's own
connection (:class:`SqliteTx`), so it is atomic with respect to the other instances.

* :class:`SqliteIdempotencyStore` - the same semantics as the PostgreSQL store: per-claim token and lease renewed
  by :meth:`~SqliteIdempotencyStore.heartbeat`, take-over of an expired key or of a stopped instance's claim,
  token-fenced ``complete``/``release``. Times are epoch seconds (``REAL``).
* :class:`SqliteJobStore` - jobs with their own ``owner``/``lease_until`` (as :class:`~jane_kit.stores.postgres.PgJobStore`).
* :class:`SqliteWorkJobStore` - jobs that mirror a leased *work row* of the service (a collection of a collector):
  the work row's owner and status are the source of truth (:class:`WorkRows`). Only the work row's lease holder
  writes the job, others may only request ``cancelling``; a terminal job status is stored only when the work row
  already has it; a run that stopped without finishing (lost lease, graceful stop) never makes the job look
  finished, and resubmitting the same ``job_id`` (resume) keeps what the job recorded.

Existing tables are upgraded in place by :meth:`migrate` (missing columns added inside the transaction, so several
processes may open the file at once).
"""

from __future__ import annotations

import asyncio
import json
import logging
import sqlite3
import threading
import time
import uuid
from collections.abc import Iterator
from contextlib import AbstractContextManager, contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from jane_kit.errors import Conflict
from jane_kit.idempotency import IdempotencyRecord, StoredResponse
from jane_kit.jobs import TERMINAL_STATUSES, Job, JobStatus, decide_save, orphaned, resumed

__all__ = [
    "SqliteDatabase",
    "SqliteIdempotencyStore",
    "SqliteJobStore",
    "SqliteTx",
    "SqliteWorkJobStore",
    "WorkRows",
]

log = logging.getLogger(__name__)

_IDENT = frozenset("abcdefghijklmnopqrstuvwxyz_0123456789")
_TERMINAL_VALUES = frozenset(s.value for s in TERMINAL_STATUSES)


def _ident(name: str) -> str:
    if not name or not set(name) <= _IDENT or name[0].isdigit():
        raise ValueError(f"invalid SQL identifier {name!r}")
    return name


class SqliteTx(Protocol):
    def tx(self) -> AbstractContextManager[sqlite3.Connection]:
        """``BEGIN IMMEDIATE`` ... ``COMMIT`` (rollback on error) on the service's connection."""
        ...


def _reader(db: SqliteTx) -> AbstractContextManager[sqlite3.Connection]:
    """``db.read()`` (the connection without a write lock, single statements) if the service has it, else a
    transaction: reads of a job must not hold the file's write lock when they need not."""
    read = getattr(db, "read", None)
    return read() if callable(read) else db.tx()


class SqliteDatabase:
    """A SQLite state file shared by the processes of one host (WAL, ``busy_timeout_ms`` lock wait)."""

    def __init__(self, path: Path, *, busy_timeout_ms: int) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._lock = threading.RLock()
        self._db = sqlite3.connect(
            str(path), timeout=busy_timeout_ms / 1000, isolation_level=None, check_same_thread=False
        )
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA synchronous=NORMAL")

    @contextmanager
    def tx(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            self._db.execute("BEGIN IMMEDIATE")
            try:
                yield self._db
            except BaseException:
                self._db.execute("ROLLBACK")
                raise
            self._db.execute("COMMIT")

    @contextmanager
    def read(self) -> Iterator[sqlite3.Connection]:
        """The connection for single-statement reads (autocommit; no write lock)."""
        with self._lock:
            yield self._db

    def close(self) -> None:
        with self._lock:
            self._db.close()


def _columns(db: sqlite3.Connection, table: str) -> set[str]:
    return {str(row[1]) for row in db.execute(f"PRAGMA table_info({table})")}


def _add_columns(db: sqlite3.Connection, table: str, columns: dict[str, str]) -> None:
    present = _columns(db, table)
    for name, decl in columns.items():
        if name not in present:
            db.execute(f"ALTER TABLE {table} ADD COLUMN {name} {decl}")


# ---------------------------------------------------------------------------------------------- idempotency
class SqliteIdempotencyStore:
    """jane-kit ``IdempotencyStore`` on table ``table`` (``key``, ``fingerprint``, ``state``, ``expires_at``,
    ``response`` JSON text, ``lease_until``, ``owner``, ``token``)."""

    def __init__(
        self, db: SqliteTx, *, owner: str, in_progress_lease_s: float, table: str = "idempotency"
    ) -> None:
        if in_progress_lease_s <= 0:
            raise ValueError("in_progress_lease_s must be positive")
        self.db = db
        self.owner = owner
        self.lease_s = float(in_progress_lease_s)
        self.table = _ident(table)
        self._claims: dict[str, str] = {}
        self._lock = threading.Lock()

    def migrate(self) -> None:
        with self.db.tx() as db:
            db.execute(
                f"CREATE TABLE IF NOT EXISTS {self.table} (key TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, "
                "state TEXT NOT NULL, expires_at REAL NOT NULL, response TEXT, lease_until REAL, owner TEXT, "
                "token TEXT)"
            )
            _add_columns(db, self.table, {"lease_until": "REAL", "owner": "TEXT", "token": "TEXT"})

    def begin_sync(self, key: str, fingerprint: str, ttl_s: float) -> IdempotencyRecord | None:
        now = time.time()
        token = uuid.uuid4().hex
        t = self.table
        with self.db.tx() as db:
            db.execute(
                f"DELETE FROM {t} WHERE expires_at <= ? OR "  # noqa: S608 - validated identifier
                "(state = 'in_progress' AND lease_until IS NOT NULL AND lease_until <= ?)",
                (now, now),
            )
            row = db.execute(f"SELECT * FROM {t} WHERE key = ?", (key,)).fetchone()  # noqa: S608
            if row is None:
                db.execute(
                    f"INSERT INTO {t} (key, fingerprint, state, expires_at, lease_until, owner, token) "  # noqa: S608
                    "VALUES (?, ?, 'in_progress', ?, ?, ?, ?)",
                    (key, fingerprint, now + float(ttl_s), now + self.lease_s, self.owner, token),
                )
        if row is None:
            with self._lock:
                self._claims[key] = token
            return None
        response = None
        if row["state"] == "completed" and row["response"]:
            data = json.loads(row["response"])
            response = StoredResponse(
                int(data["status_code"]), data.get("body"), dict(data.get("headers") or {})
            )
        return IdempotencyRecord(
            str(row["key"]),
            str(row["fingerprint"]),
            "completed" if row["state"] == "completed" else "in_progress",
            float(row["expires_at"]),
            response,
        )

    def complete_sync(self, key: str, response: StoredResponse) -> None:
        with self._lock:
            token = self._claims.pop(key, None)
        if token is None:
            log.warning("idempotency key completed without a claim of this instance", extra={"key": key})
            return
        doc = json.dumps(
            {"status_code": response.status_code, "body": response.body, "headers": dict(response.headers)},
            default=str,
        )
        with self.db.tx() as db:
            done = db.execute(
                f"UPDATE {self.table} SET state = 'completed', response = ?, lease_until = NULL "  # noqa: S608
                "WHERE key = ? AND state = 'in_progress' AND token = ?",
                (doc, key, token),
            ).rowcount
        if not done:
            log.warning("idempotency claim was taken over before completion", extra={"key": key})

    def release_sync(self, key: str) -> None:
        with self._lock:
            token = self._claims.pop(key, None)
        if token is None:
            return
        with self.db.tx() as db:
            db.execute(
                f"DELETE FROM {self.table} WHERE key = ? AND state = 'in_progress' AND token = ?",  # noqa: S608
                (key, token),
            )

    def heartbeat_sync(self) -> int:
        with self._lock:
            tokens = list(self._claims.values())
        if not tokens:
            return 0
        now = time.time()
        marks = ",".join("?" for _ in tokens)
        with self.db.tx() as db:
            return int(
                db.execute(
                    f"UPDATE {self.table} SET lease_until = ? WHERE token IN ({marks}) "  # noqa: S608
                    "AND state = 'in_progress' AND lease_until > ?",
                    (now + self.lease_s, *tokens, now),
                ).rowcount
            )

    async def begin(self, key: str, fingerprint: str, ttl_s: float) -> IdempotencyRecord | None:
        return await asyncio.to_thread(self.begin_sync, key, fingerprint, ttl_s)

    async def complete(self, key: str, response: StoredResponse) -> None:
        await asyncio.to_thread(self.complete_sync, key, response)

    async def release(self, key: str) -> None:
        await asyncio.to_thread(self.release_sync, key)

    async def heartbeat(self) -> int:
        return await asyncio.to_thread(self.heartbeat_sync)


# ---------------------------------------------------------------------------------------------- jobs
class _SqliteJobs:
    def __init__(self, db: SqliteTx, *, table: str, doc_column: str) -> None:
        self.db = db
        self.table = _ident(table)
        self.doc = _ident(doc_column)

    def _load(self, db: sqlite3.Connection, job_id: str) -> sqlite3.Row | None:
        row: sqlite3.Row | None = db.execute(
            f"SELECT * FROM {self.table} WHERE job_id = ?",  # noqa: S608 - validated identifiers
            (job_id,),
        ).fetchone()
        return row

    def _job(self, row: sqlite3.Row | None) -> Job | None:
        return Job.model_validate_json(row[self.doc]) if row is not None else None

    def get_sync(self, job_id: str) -> Job | None:
        with _reader(self.db) as db:
            return self._job(self._load(db, job_id))

    async def create(self, job: Job) -> None:
        await asyncio.to_thread(self.create_sync, job)

    async def get(self, job_id: str) -> Job | None:
        return await asyncio.to_thread(self.get_sync, job_id)

    async def save(self, job: Job) -> None:
        await asyncio.to_thread(self.save_sync, job)

    def create_sync(self, job: Job) -> None:  # pragma: no cover - overridden
        raise NotImplementedError

    def save_sync(self, job: Job) -> None:  # pragma: no cover - overridden
        raise NotImplementedError


class SqliteJobStore(_SqliteJobs):
    """jane-kit ``JobStore`` with its own ``owner``/``lease_until`` (epoch seconds), like the PostgreSQL store."""

    def __init__(
        self,
        db: SqliteTx,
        *,
        owner: str,
        lease_s: float,
        retention_s: float,
        table: str = "jobs",
        doc_column: str = "doc",
    ) -> None:
        if lease_s <= 0:
            raise ValueError("lease_s must be positive")
        super().__init__(db, table=table, doc_column=doc_column)
        self.owner = owner
        self.lease_s = float(lease_s)
        self.retention_s = float(retention_s)
        self._owned: set[str] = set()
        self._lock = threading.Lock()

    def migrate(self) -> None:
        with self.db.tx() as db:
            db.execute(
                f"CREATE TABLE IF NOT EXISTS {self.table} (job_id TEXT PRIMARY KEY, {self.doc} TEXT NOT NULL, "
                "owner TEXT, lease_until REAL, finished_at REAL)"
            )
            _add_columns(db, self.table, {"owner": "TEXT", "lease_until": "REAL", "finished_at": "REAL"})

    def create_sync(self, job: Job) -> None:
        now = time.time()
        with self.db.tx() as db:
            db.execute(
                f"DELETE FROM {self.table} WHERE finished_at IS NOT NULL AND finished_at < ?",  # noqa: S608
                (now - self.retention_s,),
            )
            if self._load(db, job.job_id) is not None:
                raise Conflict(f"job {job.job_id} already exists")
            db.execute(
                f"INSERT INTO {self.table} (job_id, {self.doc}, owner, lease_until, finished_at) "  # noqa: S608
                "VALUES (?, ?, ?, ?, ?)",
                (job.job_id, job.model_dump_json(), self.owner, now + self.lease_s, _epoch(job.finished_at)),
            )
        if job.status not in TERMINAL_STATUSES:
            with self._lock:
                self._owned.add(job.job_id)

    def _reap(self, db: sqlite3.Connection, row: sqlite3.Row) -> Job:
        current = Job.model_validate_json(row[self.doc])
        done = current if current.status in TERMINAL_STATUSES else orphaned(current, row["owner"])
        db.execute(
            f"UPDATE {self.table} SET {self.doc} = ?, finished_at = ? WHERE job_id = ?",  # noqa: S608
            (done.model_dump_json(), _epoch(done.finished_at) or time.time(), done.job_id),
        )
        return done

    def get_sync(self, job_id: str) -> Job | None:
        with self.db.tx() as db:
            row = self._load(db, job_id)
            if row is None:
                return None
            job = Job.model_validate_json(row[self.doc])
            expired = row["lease_until"] is None or float(row["lease_until"]) <= time.time()
            if job.status in TERMINAL_STATUSES or row["finished_at"] is not None or not expired:
                return job
            return self._reap(db, row)

    def save_sync(self, job: Job) -> None:
        if job.status in TERMINAL_STATUSES:
            with self._lock:
                self._owned.discard(job.job_id)
        with self.db.tx() as db:
            row = self._load(db, job.job_id)
            if row is None or row["finished_at"] is not None:
                return
            live = row["lease_until"] is not None and float(row["lease_until"]) > time.time()
            saved = decide_save(
                Job.model_validate_json(row[self.doc]), job, mine=row["owner"] == self.owner, live=live
            )
            if saved is None:
                return
            db.execute(
                f"UPDATE {self.table} SET {self.doc} = ?, finished_at = ? WHERE job_id = ?",  # noqa: S608
                (
                    saved.model_dump_json(),
                    _epoch(saved.finished_at) if saved.status in TERMINAL_STATUSES else None,
                    saved.job_id,
                ),
            )

    def heartbeat_sync(self) -> int:
        with self._lock:
            owned = list(self._owned)
        if not owned:
            return 0
        now = time.time()
        marks = ",".join("?" for _ in owned)
        with self.db.tx() as db:
            return int(
                db.execute(
                    f"UPDATE {self.table} SET lease_until = ? WHERE job_id IN ({marks}) AND owner = ? "  # noqa: S608
                    "AND finished_at IS NULL AND lease_until > ?",
                    (now + self.lease_s, *owned, self.owner, now),
                ).rowcount
            )

    def sweep_sync(self) -> int:
        with self.db.tx() as db:
            rows = db.execute(
                f"SELECT * FROM {self.table} WHERE finished_at IS NULL "  # noqa: S608
                "AND (lease_until IS NULL OR lease_until <= ?)",
                (time.time(),),
            ).fetchall()
            for row in rows:
                self._reap(db, row)
            return len(rows)

    async def heartbeat(self) -> int:
        return await asyncio.to_thread(self.heartbeat_sync)

    async def sweep(self) -> int:
        return await asyncio.to_thread(self.sweep_sync)


class WorkRows(Protocol):
    """The service's leased work rows (one per job, same id), read inside the job store's transaction."""

    def work_row(self, db: sqlite3.Connection, job_id: str) -> tuple[str | None, str] | None:
        """``(owner, status)`` of the work row, ``None`` if there is none."""
        ...

    def cancel_unstarted(self, db: sqlite3.Connection, job_id: str, owner: str) -> bool:
        """End a work row that ``owner`` holds and that never started (``queued``) as ``cancelled``."""
        ...


class SqliteWorkJobStore(_SqliteJobs):
    """jane-kit ``JobStore`` whose jobs mirror the service's leased work rows (see the module docstring).

    No lease of its own: the work row's lease is renewed by the run and taken over by another instance, which
    resumes the work and resubmits the job under the same ``job_id``.
    """

    def __init__(
        self,
        db: SqliteTx,
        work: WorkRows,
        *,
        owner: str,
        table: str = "jobs",
        doc_column: str = "body",
    ) -> None:
        super().__init__(db, table=table, doc_column=doc_column)
        self.work = work
        self.owner = owner

    def migrate(self) -> None:
        with self.db.tx() as db:
            db.execute(
                f"CREATE TABLE IF NOT EXISTS {self.table} (job_id TEXT PRIMARY KEY, {self.doc} TEXT NOT NULL)"
            )

    def _put(self, db: sqlite3.Connection, job: Job) -> None:
        db.execute(
            f"INSERT INTO {self.table} (job_id, {self.doc}) VALUES (?, ?) "  # noqa: S608
            f"ON CONFLICT(job_id) DO UPDATE SET {self.doc} = excluded.{self.doc}",
            (job.job_id, job.model_dump_json()),
        )

    def create_sync(self, job: Job) -> None:
        with self.db.tx() as db:
            existing = self._job(self._load(db, job.job_id))
            if existing is None:
                self._put(db, job)
            elif existing.status not in TERMINAL_STATUSES:
                # resumed after a restart or a take-over: keep what the job already recorded
                self._put(db, resumed(existing, job))

    def _decide(self, db: sqlite3.Connection, current: Job | None, job: Job) -> Job | None:
        if current is not None and current.status in TERMINAL_STATUSES:
            return None  # a terminal job never changes
        now = datetime.now(UTC)
        if (
            job.status != JobStatus.CANCELLING
            and current is not None
            and current.status == JobStatus.CANCELLING
        ):
            # a cancellation requested elsewhere stays visible: progress keeps ``cancelling``, the end keeps the record
            keep: dict[str, object] = {"cancellation": current.cancellation}
            if job.status not in TERMINAL_STATUSES:
                keep["status"] = JobStatus.CANCELLING
            job = job.model_copy(update=keep)
        row = self.work.work_row(db, job.job_id)
        if row is not None:
            owner, status = row
            if job.status != JobStatus.CANCELLING and owner is not None and owner != self.owner:
                return None  # a run that lost its lease must not overwrite the new owner's job
            if job.status in TERMINAL_STATUSES and status != job.status.value:
                if job.status == JobStatus.CANCELLED and status == "queued":
                    # cancelled before the run started: nothing ran, the work row ends here as well
                    if not self.work.cancel_unstarted(db, job.job_id, self.owner):
                        return None
                elif status in _TERMINAL_VALUES:
                    job = job.model_copy(update={"status": JobStatus(status)})
                else:
                    return None  # the work is not finished: the job stays non-terminal (it will be resumed)
        if job.status in TERMINAL_STATUSES and job.finished_at is None:
            job = job.model_copy(update={"finished_at": now})
        return job.model_copy(update={"updated_at": now})

    def save_sync(self, job: Job) -> None:
        with self.db.tx() as db:
            saved = self._decide(db, self._job(self._load(db, job.job_id)), job)
            if saved is not None:
                self._put(db, saved)


def _epoch(value: datetime | None) -> float | None:
    return value.timestamp() if value is not None else None
