"""Own state store of the Web Collector (SQLite, WAL): nobody else reads these tables (ADR-0009).

Holds collections (runs) with their lease, the frontier (queue + per-run dedup: primary key
``(collection_id, url)``), strategy snapshots, the buffer of emitted-but-unacknowledged materials, URL
errors, the per-``state_key`` URL history used for revisits (ETag, Last-Modified, content hash, outgoing
links), managed connections, jobs and idempotency keys.

Every processed page is committed in one transaction (new URLs + page status + material + URL history +
strategy snapshots + stats), so a killed process resumes from a consistent point. Several processes may
share the same file on one host (SQLite locking); a collection is executed by the instance holding its lease.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from collections.abc import Iterable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = ["FrontierRow", "StateStore"]

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
    meta TEXT NOT NULL DEFAULT '{}',
    effective_limits TEXT,
    paused INTEGER NOT NULL DEFAULT 0,
    owner TEXT,
    lease_until REAL NOT NULL DEFAULT 0,
    acked_seq INTEGER NOT NULL DEFAULT 0,
    expired INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS collections_state_key ON collections(state_key);
CREATE TABLE IF NOT EXISTS frontier (
    collection_id TEXT NOT NULL,
    url TEXT NOT NULL,
    status TEXT NOT NULL,
    priority INTEGER NOT NULL,
    seq INTEGER NOT NULL,
    depth INTEGER NOT NULL,
    kind TEXT NOT NULL,
    strategy_id TEXT,
    parent_url TEXT,
    section TEXT,
    lastmod TEXT,
    PRIMARY KEY (collection_id, url)
);
CREATE INDEX IF NOT EXISTS frontier_next ON frontier(collection_id, status, priority DESC, seq);
CREATE TABLE IF NOT EXISTS strategy_state (
    collection_id TEXT NOT NULL,
    strategy_id TEXT NOT NULL,
    state TEXT NOT NULL,
    PRIMARY KEY (collection_id, strategy_id)
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
CREATE TABLE IF NOT EXISTS url_state (
    state_key TEXT NOT NULL,
    url TEXT NOT NULL,
    fetched_at REAL NOT NULL,
    status INTEGER,
    etag TEXT,
    last_modified TEXT,
    content_sha256 TEXT,
    links TEXT,
    PRIMARY KEY (state_key, url)
);
CREATE TABLE IF NOT EXISTS state_cursors (
    state_key TEXT NOT NULL,
    strategy_id TEXT NOT NULL,
    cursor TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (state_key, strategy_id)
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

Fence = tuple[str, str]
"""``(collection_id, owner)``: a transaction with a fence commits only while ``owner`` holds a valid lease."""


class LeaseLost(Exception):
    """This instance no longer holds the lease of the collection (another instance took it over)."""


@dataclass(frozen=True)
class FrontierRow:
    url: str
    priority: int
    depth: int
    kind: str
    strategy_id: str | None
    parent_url: str | None = None
    section: str | None = None
    lastmod: str | None = None


def _dumps(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False, sort_keys=True)


class StateStore:
    def __init__(self, path: Path, *, busy_timeout_ms: int = 10_000) -> None:
        """``busy_timeout_ms``: how long a writer waits for another process holding the SQLite lock
        (configuration: ``JANE_WEB_COLLECTOR_STATE_BUSY_TIMEOUT_MS``, must stay below the lease)."""
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._lock = threading.RLock()
        self._db = sqlite3.connect(
            str(path), timeout=busy_timeout_ms / 1000, isolation_level=None, check_same_thread=False
        )
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA synchronous=NORMAL")
        self._db.executescript(SCHEMA)

    def close(self) -> None:
        with self._lock:
            self._db.close()

    @contextmanager
    def tx(self, fence: Fence | None = None) -> Iterator[sqlite3.Connection]:
        """``BEGIN IMMEDIATE`` transaction. With ``fence`` the transaction is rolled back and
        :class:`LeaseLost` raised unless the owner still holds a valid lease (fencing of a run that
        another instance has taken over)."""
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

    # ------------------------------------------------------------------ counters
    def next_counter(self, db: sqlite3.Connection, name: str) -> int:
        db.execute(
            "INSERT INTO counters(name, value) VALUES (?, 1) "
            "ON CONFLICT(name) DO UPDATE SET value = value + 1",
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
        status: str,
        request: Mapping[str, Any],
        rules: Mapping[str, Any],
        rules_ref: Mapping[str, Any] | None,
        created_at: str,
        effective_limits: Mapping[str, Any],
    ) -> None:
        with self.tx() as db:
            db.execute(
                "INSERT INTO collections(collection_id, state_key, status, request, rules, rules_ref, "
                "created_at, effective_limits) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    collection_id,
                    state_key,
                    status,
                    _dumps(request),
                    _dumps(rules),
                    _dumps(rules_ref) if rules_ref else None,
                    created_at,
                    _dumps(effective_limits),
                ),
            )

    def get_collection(self, collection_id: str) -> dict[str, Any] | None:
        row = self._one("SELECT * FROM collections WHERE collection_id = ?", (collection_id,))
        if row is None:
            return None
        out = dict(row)
        for key in ("request", "rules", "rules_ref", "stats", "meta", "effective_limits"):
            if out.get(key) is not None:
                out[key] = json.loads(out[key])
        return out

    def set_status(
        self,
        collection_id: str,
        status: str,
        *,
        finished_at: str | None = None,
        db: sqlite3.Connection | None = None,
    ) -> None:
        sql = "UPDATE collections SET status = ?, finished_at = COALESCE(?, finished_at), finished_ts = ? WHERE collection_id = ?"
        args = (status, finished_at, time.time() if finished_at else None, collection_id)
        if db is not None:
            db.execute(sql, args)
        else:
            with self.tx() as tx:
                tx.execute(sql, args)

    def get_status(self, collection_id: str) -> str | None:
        row = self._one("SELECT status FROM collections WHERE collection_id = ?", (collection_id,))
        return str(row[0]) if row else None

    def set_meta(self, collection_id: str, meta: Mapping[str, Any]) -> None:
        with self.tx() as db:
            db.execute(
                "UPDATE collections SET meta = ? WHERE collection_id = ?", (_dumps(meta), collection_id)
            )

    def set_paused(self, collection_id: str, paused: bool, *, fence: Fence) -> None:
        """Only the current lease holder may change a run's backpressure state."""
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

    def set_status_if_owner(
        self, collection_id: str, owner: str, status: str, *, finished_at: str | None
    ) -> bool:
        """Terminal status written only by the lease holder (a run that lost its lease must not overwrite it)."""
        with self.tx() as db:
            cur = db.execute(
                "UPDATE collections SET status = ?, finished_at = COALESCE(?, finished_at), finished_ts = ?, "
                "lease_until = 0 WHERE collection_id = ? AND owner = ?",
                (status, finished_at, time.time() if finished_at else None, collection_id, owner),
            )
            return cur.rowcount == 1

    def claim(self, collection_id: str, owner: str, lease_seconds: float) -> bool:
        """Take (or renew) the lease of a non-terminal collection."""
        now = time.time()
        with self.tx() as db:
            cur = db.execute(
                "UPDATE collections SET owner = ?, lease_until = ? WHERE collection_id = ? "
                "AND status IN ('queued', 'running', 'cancelling') AND (owner IS NULL OR owner = ? OR lease_until < ?)",
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
        now = time.time()
        rows = self._all(
            "SELECT collection_id FROM collections WHERE status IN ('queued', 'running', 'cancelling') "
            "AND (owner IS NULL OR owner = ? OR lease_until < ?) ORDER BY created_at",
            (owner, now),
        )
        return [str(r[0]) for r in rows]

    def active_for_state_key(self, state_key: str) -> list[str]:
        rows = self._all(
            "SELECT collection_id FROM collections WHERE state_key = ? AND status IN ('queued', 'running', 'cancelling')",
            (state_key,),
        )
        return [str(r[0]) for r in rows]

    def expire_finished(self, older_than_ts: float) -> list[str]:
        """Drop buffers and frontier of collections finished before ``older_than_ts``; keep a tombstone (410)."""
        with self.tx() as db:
            rows = db.execute(
                "SELECT collection_id FROM collections WHERE expired = 0 AND finished_ts IS NOT NULL AND finished_ts < ?",
                (older_than_ts,),
            ).fetchall()
            ids = [str(r[0]) for r in rows]
            for cid in ids:
                for table in ("frontier", "strategy_state", "materials", "errors"):
                    db.execute(f"DELETE FROM {table} WHERE collection_id = ?", (cid,))  # noqa: S608
                db.execute(
                    "UPDATE collections SET expired = 1, request = '{}', rules = '{}' WHERE collection_id = ?",
                    (cid,),
                )
            return ids

    # ------------------------------------------------------------------ frontier
    def add_urls(
        self, db: sqlite3.Connection, collection_id: str, rows: Iterable[FrontierRow], status: str = "pending"
    ) -> int:
        added = 0
        for row in rows:
            seq = self.next_counter(db, f"frontier:{collection_id}")
            cur = db.execute(
                "INSERT OR IGNORE INTO frontier(collection_id, url, status, priority, seq, depth, kind, strategy_id, "
                "parent_url, section, lastmod) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    collection_id,
                    row.url,
                    status,
                    row.priority,
                    seq,
                    row.depth,
                    row.kind,
                    row.strategy_id,
                    row.parent_url,
                    row.section,
                    row.lastmod,
                ),
            )
            added += cur.rowcount
        return added

    def frontier_row(self, collection_id: str, url: str) -> sqlite3.Row | None:
        return self._one("SELECT * FROM frontier WHERE collection_id = ? AND url = ?", (collection_id, url))

    def known(self, collection_id: str, url: str) -> bool:
        return (
            self._one("SELECT 1 FROM frontier WHERE collection_id = ? AND url = ?", (collection_id, url))
            is not None
        )

    def take_pending(self, collection_id: str, limit: int, fence: Fence | None = None) -> list[FrontierRow]:
        with self.tx(fence) as db:
            rows = db.execute(
                "SELECT * FROM frontier WHERE collection_id = ? AND status = 'pending' "
                "ORDER BY priority DESC, seq LIMIT ?",
                (collection_id, limit),
            ).fetchall()
            for r in rows:
                db.execute(
                    "UPDATE frontier SET status = 'inflight' WHERE collection_id = ? AND url = ?",
                    (collection_id, r["url"]),
                )
        return [
            FrontierRow(
                url=r["url"],
                priority=r["priority"],
                depth=r["depth"],
                kind=r["kind"],
                strategy_id=r["strategy_id"],
                parent_url=r["parent_url"],
                section=r["section"],
                lastmod=r["lastmod"],
            )
            for r in rows
        ]

    def mark_url(self, db: sqlite3.Connection, collection_id: str, url: str, status: str) -> None:
        db.execute(
            "UPDATE frontier SET status = ? WHERE collection_id = ? AND url = ?", (status, collection_id, url)
        )

    def reset_inflight(self, collection_id: str, fence: Fence | None = None) -> int:
        with self.tx(fence) as db:
            return db.execute(
                "UPDATE frontier SET status = 'pending' WHERE collection_id = ? AND status = 'inflight'",
                (collection_id,),
            ).rowcount

    def frontier_counts(self, collection_id: str) -> dict[str, int]:
        rows = self._all(
            "SELECT status, COUNT(*) FROM frontier WHERE collection_id = ? GROUP BY status", (collection_id,)
        )
        return {str(r[0]): int(r[1]) for r in rows}

    def drop_pending(self, collection_id: str, fence: Fence | None = None) -> int:
        """Budget reached: pending and stale in-flight URLs are dropped (not fetched in this run)."""
        with self.tx(fence) as db:
            return db.execute(
                "UPDATE frontier SET status = 'dropped' WHERE collection_id = ? AND status IN ('pending', 'inflight')",
                (collection_id,),
            ).rowcount

    def frontier_size_for_state_key(self, state_key: str) -> int:
        row = self._one(
            "SELECT COUNT(*) FROM frontier f JOIN collections c ON c.collection_id = f.collection_id "
            "WHERE c.state_key = ? AND c.status IN ('queued', 'running', 'cancelling') AND f.status IN ('pending', 'inflight')",
            (state_key,),
        )
        return int(row[0]) if row else 0

    # ------------------------------------------------------------------ strategy state
    def save_strategy_states(
        self, db: sqlite3.Connection, collection_id: str, states: Mapping[str, Any]
    ) -> None:
        for strategy_id, state in states.items():
            db.execute(
                "INSERT INTO strategy_state(collection_id, strategy_id, state) VALUES (?, ?, ?) "
                "ON CONFLICT(collection_id, strategy_id) DO UPDATE SET state = excluded.state",
                (collection_id, strategy_id, _dumps(state)),
            )

    def load_strategy_states(self, collection_id: str) -> dict[str, Any]:
        rows = self._all(
            "SELECT strategy_id, state FROM strategy_state WHERE collection_id = ?", (collection_id,)
        )
        return {str(r[0]): json.loads(r[1]) for r in rows}

    def save_cursors(
        self, db: sqlite3.Connection, state_key: str, cursors: Mapping[str, Any], now: str
    ) -> None:
        for strategy_id, cursor in cursors.items():
            db.execute(
                "INSERT INTO state_cursors(state_key, strategy_id, cursor, updated_at) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(state_key, strategy_id) DO UPDATE SET cursor = excluded.cursor, updated_at = excluded.updated_at",
                (state_key, strategy_id, _dumps(cursor), now),
            )

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

    # ------------------------------------------------------------------ URL history (revisits)
    def url_state(self, state_key: str, url: str) -> dict[str, Any] | None:
        row = self._one("SELECT * FROM url_state WHERE state_key = ? AND url = ?", (state_key, url))
        if row is None:
            return None
        out = dict(row)
        out["links"] = json.loads(out["links"]) if out.get("links") else []
        return out

    def put_url_state(
        self,
        db: sqlite3.Connection,
        state_key: str,
        url: str,
        *,
        status: int | None,
        etag: str | None,
        last_modified: str | None,
        content_sha256: str | None,
        links: Sequence[str] | None,
    ) -> None:
        db.execute(
            "INSERT INTO url_state(state_key, url, fetched_at, status, etag, last_modified, content_sha256, links) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(state_key, url) DO UPDATE SET "
            "fetched_at = excluded.fetched_at, status = excluded.status, "
            "etag = COALESCE(excluded.etag, url_state.etag), "
            "last_modified = COALESCE(excluded.last_modified, url_state.last_modified), "
            "content_sha256 = COALESCE(excluded.content_sha256, url_state.content_sha256), "
            "links = COALESCE(excluded.links, url_state.links)",
            (
                state_key,
                url,
                time.time(),
                status,
                etag,
                last_modified,
                content_sha256,
                _dumps(list(links)) if links is not None else None,
            ),
        )

    def state_summary(self, state_key: str) -> dict[str, Any] | None:
        known = self._one("SELECT COUNT(*), MAX(fetched_at) FROM url_state WHERE state_key = ?", (state_key,))
        cursors = self._all(
            "SELECT strategy_id, cursor, updated_at FROM state_cursors WHERE state_key = ?", (state_key,)
        )
        has_collections = self._one(
            "SELECT MAX(created_at) FROM collections WHERE state_key = ?", (state_key,)
        )
        known_urls = int(known[0]) if known else 0
        if not known_urls and not cursors and not (has_collections and has_collections[0]):
            return None
        return {
            "known_urls": known_urls,
            "last_fetch_ts": known[1] if known else None,
            "cursors": {str(r[0]): json.loads(r[1]) for r in cursors},
            "cursor_updated_at": max((str(r[2]) for r in cursors), default=None),
            "last_collection_at": has_collections[0] if has_collections else None,
        }

    def delete_state(self, state_key: str) -> None:
        with self.tx() as db:
            db.execute("DELETE FROM url_state WHERE state_key = ?", (state_key,))
            db.execute("DELETE FROM state_cursors WHERE state_key = ?", (state_key,))

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
