"""Own state store of the Telegram Collector (SQLite, WAL): nobody else reads these tables (ADR-0009).

Tables: collections (runs) with their lease, per-run channel progress, persistent channel cursors per
``state_key`` (last message id, edit watermark, ``pts``), seen revisions per ``state_key`` (to tell an edit
from a repeated delivery of the same revision), the buffer of emitted-but-unacknowledged materials, errors,
managed connections, jobs, idempotency keys and counters.

Every emitted message is committed in one transaction (material + run progress + cursor + seen revision +
stats), fenced by the run's lease: a killed process resumes from a consistent point and a run that lost its
lease cannot write anything. Several processes may share the file on one host (SQLite locking).
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from .materials import SEQUENCE_SCALE

__all__ = ["SCHEMA_VERSION", "Fence", "LeaseLost", "StateFileTooNew", "StateStore"]

SCHEMA_VERSION = 1
"""``PRAGMA user_version`` of the state file - the format marker. 1 (WP-16, R04): ``tg_seen.sequence`` is in
``revision.sequence`` units (epoch seconds x ``SEQUENCE_SCALE`` + the revision number within the second); a
version 0 file (seconds, collectors before WP-16) is migrated when a process opens it. A file of a newer version
than the code knows is refused (:class:`StateFileTooNew`). Collectors before WP-16 do not read the marker: run
them on a migrated file and they take the stored sequences for seconds, so every known message looks newer than
its edits and no edit is emitted - instances sharing one ``STATE_DIR`` are upgraded together (README)."""


class StateFileTooNew(RuntimeError):
    """The state file was written by a newer collector (``PRAGMA user_version`` > :data:`SCHEMA_VERSION`)."""


SCHEMA = """
CREATE TABLE IF NOT EXISTS collections (
    collection_id TEXT PRIMARY KEY,
    state_key TEXT NOT NULL,
    status TEXT NOT NULL,
    request TEXT NOT NULL,
    rules TEXT NOT NULL,
    rules_ref TEXT,
    created_at TEXT NOT NULL,
    finished_at TEXT,
    finished_ts REAL,
    stats TEXT NOT NULL DEFAULT '{}',
    result TEXT,
    effective_limits TEXT,
    paused INTEGER NOT NULL DEFAULT 0,
    owner TEXT,
    lease_until REAL NOT NULL DEFAULT 0,
    acked_seq INTEGER NOT NULL DEFAULT 0,
    expired INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS collections_state_key ON collections(state_key);
CREATE TABLE IF NOT EXISTS channel_progress (
    collection_id TEXT NOT NULL,
    channel_key TEXT NOT NULL,
    progress TEXT NOT NULL,
    PRIMARY KEY (collection_id, channel_key)
);
CREATE TABLE IF NOT EXISTS tg_cursors (
    state_key TEXT NOT NULL,
    channel_id TEXT NOT NULL,
    cursor TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (state_key, channel_id)
);
CREATE TABLE IF NOT EXISTS tg_seen (
    state_key TEXT NOT NULL,
    material_id TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    content_sha256 TEXT NOT NULL,
    PRIMARY KEY (state_key, material_id)
);
CREATE TABLE IF NOT EXISTS materials (
    collection_id TEXT NOT NULL,
    seq INTEGER NOT NULL,
    observation_id TEXT NOT NULL,
    material TEXT NOT NULL,
    PRIMARY KEY (collection_id, seq)
);
CREATE TABLE IF NOT EXISTS errors (
    collection_id TEXT NOT NULL,
    seq INTEGER NOT NULL,
    error TEXT NOT NULL,
    PRIMARY KEY (collection_id, seq)
);
CREATE TABLE IF NOT EXISTS connections (
    connection_id TEXT PRIMARY KEY,
    body TEXT NOT NULL,
    etag TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    body TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS idempotency (
    key TEXT PRIMARY KEY,
    fingerprint TEXT NOT NULL,
    state TEXT NOT NULL,
    expires_at REAL NOT NULL,
    response TEXT
);
CREATE TABLE IF NOT EXISTS counters (
    name TEXT PRIMARY KEY,
    value INTEGER NOT NULL
);
"""

ACTIVE = ("queued", "running", "cancelling")

Fence = tuple[str, str]
"""``(collection_id, owner)``: a transaction with a fence commits only while ``owner`` holds a valid lease."""


class LeaseLost(Exception):
    """This instance no longer holds the lease of the collection (another instance took it over)."""


def _dumps(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False, sort_keys=True)


class StateStore:
    def __init__(self, path: Path, *, busy_timeout_ms: int) -> None:
        """``busy_timeout_ms``: how long a writer waits for another process holding the SQLite lock
        (``JANE_TELEGRAM_COLLECTOR_STATE_BUSY_TIMEOUT_MS``, validated to stay below the lease)."""
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._lock = threading.RLock()
        self._db = sqlite3.connect(
            str(path), timeout=busy_timeout_ms / 1000, isolation_level=None, check_same_thread=False
        )
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA synchronous=NORMAL")
        version = int(self._db.execute("PRAGMA user_version").fetchone()[0])
        if version > SCHEMA_VERSION:  # written by a newer collector: its format is unknown here
            self._db.close()
            raise StateFileTooNew(
                f"{path}: state file version {version} is newer than this collector supports ({SCHEMA_VERSION})"
            )
        self._db.executescript(SCHEMA)
        self._migrate()

    def _migrate(self) -> None:
        """Bring a state file of an older version to :data:`SCHEMA_VERSION` (one transaction, once per file)."""
        with self.tx() as db:
            version = int(db.execute("PRAGMA user_version").fetchone()[0])
            if version > SCHEMA_VERSION:  # another process upgraded the file meanwhile
                raise StateFileTooNew(f"{self.path}: state file version {version} > {SCHEMA_VERSION}")
            if version < 1:
                db.execute("UPDATE tg_seen SET sequence = sequence * ?", (SEQUENCE_SCALE,))
            if version < SCHEMA_VERSION:
                db.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")

    def schema_version(self) -> int:
        row = self._one("PRAGMA user_version")
        return int(row[0]) if row else 0

    def close(self) -> None:
        with self._lock:
            self._db.close()

    @contextmanager
    def tx(self, fence: Fence | None = None) -> Iterator[sqlite3.Connection]:
        """``BEGIN IMMEDIATE`` transaction. With ``fence`` it is rolled back and :class:`LeaseLost` raised
        unless the owner still holds a valid lease."""
        with self._lock:
            self._db.execute("BEGIN IMMEDIATE")
            try:
                if fence is not None:
                    row = self._db.execute(
                        "SELECT owner, lease_until FROM collections WHERE collection_id = ?", (fence[0],)
                    ).fetchone()
                    if row is None or row[0] != fence[1] or float(row[1]) <= time.time():
                        raise LeaseLost(fence[0])
                yield self._db
            except BaseException:
                self._db.execute("ROLLBACK")
                raise
            self._db.execute("COMMIT")

    def _one(self, sql: str, args: Sequence[Any] = ()) -> sqlite3.Row | None:
        with self._lock:
            row: sqlite3.Row | None = self._db.execute(sql, args).fetchone()
            return row

    def _all(self, sql: str, args: Sequence[Any] = ()) -> list[sqlite3.Row]:
        with self._lock:
            return list(self._db.execute(sql, args).fetchall())

    def ping(self) -> None:
        self._one("SELECT 1")

    def next_counter(self, db: sqlite3.Connection, name: str) -> int:
        db.execute(
            "INSERT INTO counters(name, value) VALUES (?, 1) ON CONFLICT(name) DO UPDATE SET value = value + 1",
            (name,),
        )
        row = db.execute("SELECT value FROM counters WHERE name = ?", (name,)).fetchone()
        return int(row[0])

    # ------------------------------------------------------------------ collections
    def create_collection(
        self,
        collection_id: str,
        *,
        state_key: str,
        request: Mapping[str, Any],
        rules: Mapping[str, Any],
        rules_ref: Mapping[str, Any] | None,
        created_at: str,
        effective_limits: Mapping[str, Any],
        owner: str,
        lease_seconds: float,
    ) -> bool:
        """Create a queued collection owned by ``owner``; False if ``state_key`` is used by an active one."""
        with self.tx() as db:
            busy = db.execute(
                f"SELECT 1 FROM collections WHERE state_key = ? AND status IN {ACTIVE}",  # noqa: S608
                (state_key,),
            ).fetchone()
            if busy is not None:
                return False
            db.execute(
                "INSERT INTO collections(collection_id, state_key, status, request, rules, rules_ref, created_at, "
                "effective_limits, owner, lease_until) VALUES (?, ?, 'queued', ?, ?, ?, ?, ?, ?, ?)",
                (
                    collection_id,
                    state_key,
                    _dumps(request),
                    _dumps(rules),
                    _dumps(rules_ref) if rules_ref else None,
                    created_at,
                    _dumps(effective_limits),
                    owner,
                    time.time() + lease_seconds,
                ),
            )
            return True

    def get_collection(self, collection_id: str) -> dict[str, Any] | None:
        row = self._one("SELECT * FROM collections WHERE collection_id = ?", (collection_id,))
        if row is None:
            return None
        out = dict(row)
        for key in ("request", "rules", "rules_ref", "stats", "effective_limits", "result"):
            if out.get(key) is not None:
                out[key] = json.loads(out[key])
        return out

    def get_status(self, collection_id: str) -> str | None:
        row = self._one("SELECT status FROM collections WHERE collection_id = ?", (collection_id,))
        return str(row[0]) if row else None

    def set_running(self, db: sqlite3.Connection, collection_id: str) -> None:
        db.execute(
            "UPDATE collections SET status = 'running' WHERE collection_id = ? AND status = 'queued'",
            (collection_id,),
        )

    def finish(
        self, db: sqlite3.Connection, collection_id: str, status: str, finished_at: str, result: Any = None
    ) -> None:
        db.execute(
            "UPDATE collections SET status = ?, finished_at = ?, finished_ts = ?, lease_until = 0, result = ? "
            "WHERE collection_id = ?",
            (status, finished_at, time.time(), _dumps(result) if result is not None else None, collection_id),
        )

    def finish_if_owner(
        self, collection_id: str, owner: str, status: str, finished_at: str, result: Any = None
    ) -> bool:
        """Terminal status written only by the holder of a valid lease (fenced like every other run write)."""
        try:
            with self.tx((collection_id, owner)) as db:
                if (
                    db.execute(
                        f"SELECT 1 FROM collections WHERE collection_id = ? AND status IN {ACTIVE}",  # noqa: S608
                        (collection_id,),
                    ).fetchone()
                    is None
                ):
                    return False
                self.finish(db, collection_id, status, finished_at, result)
                return True
        except LeaseLost:
            return False

    def set_paused(self, collection_id: str, paused: bool, fence: Fence) -> None:
        """Backpressure flag of a run: written only under the run's lease (:class:`LeaseLost` otherwise)."""
        with self.tx(fence) as db:
            db.execute(
                "UPDATE collections SET paused = ? WHERE collection_id = ?", (int(paused), collection_id)
            )

    def save_stats(self, db: sqlite3.Connection, collection_id: str, stats: Mapping[str, Any]) -> None:
        db.execute("UPDATE collections SET stats = ? WHERE collection_id = ?", (_dumps(stats), collection_id))

    def lease(self, collection_id: str) -> tuple[str | None, float]:
        row = self._one(
            "SELECT owner, lease_until FROM collections WHERE collection_id = ?", (collection_id,)
        )
        return (row[0], float(row[1])) if row else (None, 0.0)

    def claim(self, collection_id: str, owner: str, lease_seconds: float) -> bool:
        """Take (or renew) the lease of a non-terminal collection."""
        now = time.time()
        with self.tx() as db:
            cur = db.execute(
                f"UPDATE collections SET owner = ?, lease_until = ? WHERE collection_id = ? "  # noqa: S608
                f"AND status IN {ACTIVE} AND (owner IS NULL OR owner = ? OR lease_until < ?)",
                (owner, now + lease_seconds, collection_id, owner, now),
            )
            return cur.rowcount == 1

    def release(self, collection_id: str, owner: str) -> None:
        with self.tx() as db:
            db.execute(
                "UPDATE collections SET lease_until = 0 WHERE collection_id = ? AND owner = ?",
                (collection_id, owner),
            )

    def resumable(self, owner: str) -> list[str]:
        """Non-terminal collections whose lease expired (or that this instance owned)."""
        rows = self._all(
            f"SELECT collection_id FROM collections WHERE status IN {ACTIVE} "  # noqa: S608
            "AND (owner IS NULL OR owner = ? OR lease_until < ?) ORDER BY created_at",
            (owner, time.time()),
        )
        return [str(r[0]) for r in rows]

    def active_for_state_key(self, state_key: str) -> list[str]:
        rows = self._all(
            f"SELECT collection_id FROM collections WHERE state_key = ? AND status IN {ACTIVE}",  # noqa: S608
            (state_key,),
        )
        return [str(r[0]) for r in rows]

    def expire_finished(self, older_than_ts: float) -> list[str]:
        """Drop buffers of collections finished before ``older_than_ts``; keep a tombstone (410)."""
        with self.tx() as db:
            rows = db.execute(
                "SELECT collection_id FROM collections WHERE expired = 0 AND finished_ts IS NOT NULL AND finished_ts < ?",
                (older_than_ts,),
            ).fetchall()
            ids = [str(r[0]) for r in rows]
            for cid in ids:
                for table in ("channel_progress", "materials", "errors"):
                    db.execute(f"DELETE FROM {table} WHERE collection_id = ?", (cid,))  # noqa: S608
                db.execute(
                    "UPDATE collections SET expired = 1, request = '{}', rules = '{}' WHERE collection_id = ?",
                    (cid,),
                )
            return ids

    # ------------------------------------------------------------------ run progress
    def get_progress(self, collection_id: str, channel_key: str) -> dict[str, Any] | None:
        row = self._one(
            "SELECT progress FROM channel_progress WHERE collection_id = ? AND channel_key = ?",
            (collection_id, channel_key),
        )
        return json.loads(row[0]) if row else None

    def put_progress(
        self, db: sqlite3.Connection, collection_id: str, channel_key: str, progress: Mapping[str, Any]
    ) -> None:
        db.execute(
            "INSERT INTO channel_progress(collection_id, channel_key, progress) VALUES (?, ?, ?) "
            "ON CONFLICT(collection_id, channel_key) DO UPDATE SET progress = excluded.progress",
            (collection_id, channel_key, _dumps(progress)),
        )

    # ------------------------------------------------------------------ cursors and seen revisions
    def get_cursor(self, state_key: str, channel_id: str) -> dict[str, Any] | None:
        row = self._one(
            "SELECT cursor FROM tg_cursors WHERE state_key = ? AND channel_id = ?", (state_key, channel_id)
        )
        return json.loads(row[0]) if row else None

    def put_cursor(
        self, db: sqlite3.Connection, state_key: str, channel_id: str, cursor: Mapping[str, Any], now: str
    ) -> None:
        db.execute(
            "INSERT INTO tg_cursors(state_key, channel_id, cursor, updated_at) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(state_key, channel_id) DO UPDATE SET cursor = excluded.cursor, updated_at = excluded.updated_at",
            (state_key, channel_id, _dumps(cursor), now),
        )

    def latest_seen(self, material_id: str) -> tuple[int, str] | None:
        """The newest revision of the message emitted under any ``state_key`` (``sequence``, text sha256)."""
        row = self._one(
            "SELECT sequence, content_sha256 FROM tg_seen WHERE material_id = ? ORDER BY sequence DESC LIMIT 1",
            (material_id,),
        )
        return (int(row[0]), str(row[1])) if row else None

    def seen(self, state_key: str, material_id: str) -> tuple[int, str] | None:
        row = self._one(
            "SELECT sequence, content_sha256 FROM tg_seen WHERE state_key = ? AND material_id = ?",
            (state_key, material_id),
        )
        return (int(row[0]), str(row[1])) if row else None

    def put_seen(
        self, db: sqlite3.Connection, state_key: str, material_id: str, sequence: int, sha: str
    ) -> None:
        db.execute(
            "INSERT INTO tg_seen(state_key, material_id, sequence, content_sha256) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(state_key, material_id) DO UPDATE SET sequence = excluded.sequence, "
            "content_sha256 = excluded.content_sha256 WHERE excluded.sequence >= tg_seen.sequence",
            (state_key, material_id, sequence, sha),
        )

    def state_summary(self, state_key: str) -> dict[str, Any] | None:
        cursors = self._all(
            "SELECT channel_id, cursor, updated_at FROM tg_cursors WHERE state_key = ?", (state_key,)
        )
        last = self._one("SELECT MAX(created_at) FROM collections WHERE state_key = ?", (state_key,))
        if not cursors and not (last and last[0]):
            return None
        return {
            "cursors": {str(r[0]): json.loads(r[1]) for r in cursors},
            "updated_at": max((str(r[2]) for r in cursors), default=None) or (last[0] if last else None),
        }

    def delete_state(self, state_key: str) -> None:
        with self.tx() as db:
            db.execute("DELETE FROM tg_cursors WHERE state_key = ?", (state_key,))
            db.execute("DELETE FROM tg_seen WHERE state_key = ?", (state_key,))

    # ------------------------------------------------------------------ materials buffer
    def append_material(
        self, db: sqlite3.Connection, collection_id: str, observation_id: str, material: Mapping[str, Any]
    ) -> int:
        seq = self.next_counter(db, f"materials:{collection_id}")
        db.execute(
            "INSERT INTO materials(collection_id, seq, observation_id, material) VALUES (?, ?, ?, ?)",
            (collection_id, seq, observation_id, _dumps(material)),
        )
        return seq

    def materials_after(
        self, collection_id: str, after_seq: int, limit: int
    ) -> list[tuple[int, dict[str, Any]]]:
        rows = self._all(
            "SELECT seq, material FROM materials WHERE collection_id = ? AND seq > ? ORDER BY seq LIMIT ?",
            (collection_id, after_seq, limit),
        )
        return [(int(r[0]), json.loads(r[1])) for r in rows]

    def ack(self, collection_id: str, upto_seq: int) -> int:
        """Acknowledge every material with ``seq <= upto_seq``; returns how many were newly acknowledged."""
        with self.tx() as db:
            removed = db.execute(
                "DELETE FROM materials WHERE collection_id = ? AND seq <= ?", (collection_id, upto_seq)
            ).rowcount
            db.execute(
                "UPDATE collections SET acked_seq = MAX(acked_seq, ?) WHERE collection_id = ?",
                (upto_seq, collection_id),
            )
            return removed

    def unacked_count(self, collection_id: str) -> int:
        row = self._one("SELECT COUNT(*) FROM materials WHERE collection_id = ?", (collection_id,))
        return int(row[0]) if row else 0

    def emitted_count(self, collection_id: str) -> int:
        row = self._one("SELECT value FROM counters WHERE name = ?", (f"materials:{collection_id}",))
        return int(row[0]) if row else 0

    # ------------------------------------------------------------------ errors
    def add_error(self, db: sqlite3.Connection, collection_id: str, error: Mapping[str, Any]) -> None:
        seq = self.next_counter(db, f"errors:{collection_id}")
        db.execute(
            "INSERT INTO errors(collection_id, seq, error) VALUES (?, ?, ?)",
            (collection_id, seq, _dumps(error)),
        )

    def errors_after(
        self, collection_id: str, after_seq: int, limit: int
    ) -> list[tuple[int, dict[str, Any]]]:
        rows = self._all(
            "SELECT seq, error FROM errors WHERE collection_id = ? AND seq > ? ORDER BY seq LIMIT ?",
            (collection_id, after_seq, limit),
        )
        return [(int(r[0]), json.loads(r[1])) for r in rows]

    # ------------------------------------------------------------------ connections
    def get_connection(self, connection_id: str) -> tuple[dict[str, Any], str] | None:
        row = self._one("SELECT body, etag FROM connections WHERE connection_id = ?", (connection_id,))
        return (json.loads(row[0]), str(row[1])) if row else None

    def put_connection(self, connection_id: str, body: Mapping[str, Any], etag: str) -> bool:
        """Returns True if created."""
        with self.tx() as db:
            existed = db.execute(
                "SELECT 1 FROM connections WHERE connection_id = ?", (connection_id,)
            ).fetchone()
            db.execute(
                "INSERT INTO connections(connection_id, body, etag) VALUES (?, ?, ?) "
                "ON CONFLICT(connection_id) DO UPDATE SET body = excluded.body, etag = excluded.etag",
                (connection_id, _dumps(body), etag),
            )
            return existed is None

    def delete_connection(self, connection_id: str) -> bool:
        with self.tx() as db:
            return (
                db.execute("DELETE FROM connections WHERE connection_id = ?", (connection_id,)).rowcount == 1
            )

    def list_connections(self, after: str | None, limit: int) -> list[dict[str, Any]]:
        rows = self._all(
            "SELECT body FROM connections WHERE connection_id > ? ORDER BY connection_id LIMIT ?",
            (after or "", limit),
        )
        return [json.loads(r[0]) for r in rows]

    # ------------------------------------------------------------------ jobs / idempotency (jane-kit protocols)
    def get_job(self, job_id: str) -> str | None:
        row = self._one("SELECT body FROM jobs WHERE job_id = ?", (job_id,))
        return str(row[0]) if row else None

    def put_job(self, job_id: str, body: str) -> None:
        with self.tx() as db:
            db.execute(
                "INSERT INTO jobs(job_id, body) VALUES (?, ?) ON CONFLICT(job_id) DO UPDATE SET body = excluded.body",
                (job_id, body),
            )

    def update_job(
        self, job_id: str, decide: Callable[[str | None, str | None, str | None], str | None]
    ) -> None:
        """Read the collection's ``(owner, status)`` and the stored job and write ``decide(...)`` (``None`` =
        keep) in one ``BEGIN IMMEDIATE`` transaction: no other instance can claim the lease in between."""
        with self.tx() as db:
            row = db.execute(
                "SELECT owner, status FROM collections WHERE collection_id = ?", (job_id,)
            ).fetchone()
            current = db.execute("SELECT body FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
            body = decide(
                row[0] if row else None, str(row[1]) if row else None, str(current[0]) if current else None
            )
            if body is not None:
                db.execute(
                    "INSERT INTO jobs(job_id, body) VALUES (?, ?) "
                    "ON CONFLICT(job_id) DO UPDATE SET body = excluded.body",
                    (job_id, body),
                )

    def idem_begin(self, key: str, fingerprint: str, ttl_s: float) -> sqlite3.Row | None:
        now = time.time()
        with self.tx() as db:
            db.execute("DELETE FROM idempotency WHERE expires_at <= ?", (now,))
            row: sqlite3.Row | None = db.execute("SELECT * FROM idempotency WHERE key = ?", (key,)).fetchone()
            if row is not None:
                return row
            db.execute(
                "INSERT INTO idempotency(key, fingerprint, state, expires_at) VALUES (?, ?, 'in_progress', ?)",
                (key, fingerprint, now + ttl_s),
            )
            return None

    def idem_complete(self, key: str, response: str) -> None:
        with self.tx() as db:
            db.execute(
                "UPDATE idempotency SET state = 'completed', response = ? WHERE key = ?", (response, key)
            )

    def idem_release(self, key: str) -> None:
        with self.tx() as db:
            db.execute("DELETE FROM idempotency WHERE key = ? AND state = 'in_progress'", (key,))
