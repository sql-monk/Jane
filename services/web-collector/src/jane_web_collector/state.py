"""Own state store of the Web Collector (SQLite, WAL): nobody else reads these tables (ADR-0009).

Holds collections (runs) with their lease, the frontier (queue + per-run dedup: primary key
``(collection_id, url)``), strategy snapshots, the buffer of emitted-but-unacknowledged materials, URL
errors, the per-``state_key`` URL history used for revisits (ETag, Last-Modified, content hash, outgoing
links), managed connections, jobs and idempotency keys (tables of jane-kit's shared SQLite stores, R17) and the
per-host schedule shared by the instances
(``host_users``, ``host_schedule``, ``host_slots``: :mod:`.shared_hosts`, R15).

Every processed page is committed in one transaction (new URLs + page status + material + URL history +
strategy snapshots + stats), so a killed process resumes from a consistent point. Several processes may
share the same file on one host (SQLite locking); a collection is executed by the instance holding its lease.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
import zlib
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import asdict, dataclass
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
    seen_before INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (collection_id, url)
);
CREATE INDEX IF NOT EXISTS frontier_next ON frontier(collection_id, status, priority DESC, seq);
CREATE TABLE IF NOT EXISTS deferred_crawls (
    collection_id TEXT PRIMARY KEY,
    state_key TEXT NOT NULL,
    fingerprint TEXT NOT NULL,
    seeded TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS deferred_crawls_match ON deferred_crawls(state_key, fingerprint);
CREATE TABLE IF NOT EXISTS frontier_overflow (
    collection_id TEXT NOT NULL,
    url TEXT NOT NULL,
    priority INTEGER NOT NULL,
    seq INTEGER NOT NULL,
    row BLOB NOT NULL,
    seen_before INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (collection_id, url)
);
CREATE INDEX IF NOT EXISTS overflow_next ON frontier_overflow(collection_id, priority DESC, seq);
CREATE TABLE IF NOT EXISTS frontier_loans (
    donor_id TEXT NOT NULL,
    url TEXT NOT NULL,
    borrower_id TEXT NOT NULL,
    completed INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (donor_id, url)
);
CREATE INDEX IF NOT EXISTS loans_borrower ON frontier_loans(borrower_id, url);
CREATE TABLE IF NOT EXISTS seed_navigation (
    collection_id TEXT NOT NULL,
    strategy_id TEXT NOT NULL,
    url TEXT NOT NULL,
    resource TEXT NOT NULL,
    body BLOB NOT NULL,
    PRIMARY KEY (collection_id, strategy_id, url)
);
CREATE INDEX IF NOT EXISTS seed_navigation_lookup ON seed_navigation(strategy_id, url, collection_id);
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
CREATE TABLE IF NOT EXISTS host_users (
    host TEXT NOT NULL,
    instance_id TEXT NOT NULL,
    interval_s REAL NOT NULL,
    parallel INTEGER NOT NULL,
    expires_at REAL NOT NULL,
    PRIMARY KEY (host, instance_id)
);
CREATE TABLE IF NOT EXISTS host_schedule (
    host TEXT PRIMARY KEY,
    last_start REAL NOT NULL DEFAULT 0,
    not_before REAL NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS host_slots (
    host TEXT NOT NULL,
    token TEXT NOT NULL,
    instance_id TEXT NOT NULL,
    expires_at REAL NOT NULL,
    PRIMARY KEY (host, token)
);
CREATE TABLE IF NOT EXISTS host_waiters (
    host TEXT NOT NULL,
    token TEXT NOT NULL,
    since REAL NOT NULL,
    expires_at REAL NOT NULL,
    PRIMARY KEY (host, token)
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
        with self.tx() as db:
            if "seen_before" not in {row[1] for row in db.execute("PRAGMA table_info(frontier)")}:
                db.execute("ALTER TABLE frontier ADD COLUMN seen_before INTEGER NOT NULL DEFAULT 0")
                db.execute(
                    "UPDATE frontier SET seen_before = EXISTS (SELECT 1 FROM url_state u JOIN collections c "
                    "ON c.state_key = u.state_key WHERE c.collection_id = frontier.collection_id "
                    "AND u.url = frontier.url AND u.status BETWEEN 200 AND 399)"
                )
            db.execute(
                "CREATE INDEX IF NOT EXISTS frontier_pending_order "
                "ON frontier(collection_id, status, seen_before, priority DESC, seq)"
            )
            self._init_frontier_counts(db)
        if "seen_before" not in {row[1] for row in self._db.execute("PRAGMA table_info(frontier_overflow)")}:
            self._db.execute(
                "ALTER TABLE frontier_overflow ADD COLUMN seen_before INTEGER NOT NULL DEFAULT 0"
            )
            self._db.execute(
                "UPDATE frontier_overflow SET seen_before = EXISTS (SELECT 1 FROM url_state u JOIN collections c "
                "ON c.state_key = u.state_key WHERE c.collection_id = frontier_overflow.collection_id "
                "AND u.url = frontier_overflow.url AND u.status BETWEEN 200 AND 399)"
            )
            self._db.execute(
                "INSERT OR REPLACE INTO counters SELECT 'overflow:' || collection_id, COUNT(*) "
                "FROM frontier_overflow GROUP BY collection_id"
            )
        self._db.execute(
            "CREATE INDEX IF NOT EXISTS overflow_rank ON frontier_overflow(collection_id, seen_before, priority DESC, seq)"
        )

    def close(self) -> None:
        with self._lock:
            self._db.close()

    @staticmethod
    def _init_frontier_counts(db: sqlite3.Connection) -> None:
        """Backfill once, then count every frontier transition in its original transaction.

        Triggers also cover bulk adoption, fencing rollbacks and retention deletes. Counting the
        whole catalog on each heartbeat or admission batch would otherwise stall the event loop.
        """
        exists = db.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'frontier_status_counts'"
        ).fetchone()
        db.execute(
            "CREATE TABLE IF NOT EXISTS frontier_status_counts (collection_id TEXT NOT NULL, "
            "status TEXT NOT NULL, kind TEXT NOT NULL, value INTEGER NOT NULL, "
            "PRIMARY KEY (collection_id, status, kind))"
        )
        if exists is None:
            db.execute(
                "INSERT INTO frontier_status_counts SELECT collection_id, status, kind, COUNT(*) "
                "FROM frontier GROUP BY collection_id, status, kind"
            )
        increment = (
            "INSERT INTO frontier_status_counts VALUES (NEW.collection_id, NEW.status, NEW.kind, 1) "
            "ON CONFLICT(collection_id, status, kind) DO UPDATE SET value = value + 1;"
        )
        decrement = (
            "UPDATE frontier_status_counts SET value = value - 1 WHERE collection_id = OLD.collection_id "
            "AND status = OLD.status AND kind = OLD.kind; "
            "DELETE FROM frontier_status_counts WHERE collection_id = OLD.collection_id "
            "AND status = OLD.status AND kind = OLD.kind AND value = 0;"
        )
        db.execute(
            "CREATE TRIGGER IF NOT EXISTS frontier_count_insert AFTER INSERT ON frontier BEGIN "
            + increment
            + " END"
        )
        db.execute(
            "CREATE TRIGGER IF NOT EXISTS frontier_count_delete AFTER DELETE ON frontier BEGIN "
            + decrement
            + " END"
        )
        db.execute(
            "CREATE TRIGGER IF NOT EXISTS frontier_count_update AFTER UPDATE OF collection_id, status, kind "
            "ON frontier WHEN OLD.collection_id <> NEW.collection_id OR OLD.status <> NEW.status "
            "OR OLD.kind <> NEW.kind BEGIN " + decrement + increment + " END"
        )

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
                succeeded = self.get_status(cid) == "succeeded"
                checkpointed = db.execute(
                    "SELECT 1 FROM deferred_crawls WHERE collection_id = ?", (cid,)
                ).fetchone()
                # A bounded successful run's unfinished crawl outlives its result/material retention.
                keep = {"deferred", "loaned"} if succeeded else set()
                if succeeded and checkpointed:
                    keep.update(("pending", "inflight"))
                physical = db.execute(
                    "SELECT status FROM frontier_status_counts WHERE collection_id = ? GROUP BY status",
                    (cid,),
                ).fetchall()
                # Equality on each terminal status deletes only its rows, without scanning the
                # multi-million pending tail on every bounded run's retention pass.
                for physical_status in physical:
                    if physical_status[0] not in keep:
                        db.execute(
                            "DELETE FROM frontier WHERE collection_id = ? AND status = ?",
                            (cid, physical_status[0]),
                        )
                has_deferred = any(physical_status[0] in keep for physical_status in physical)
                if succeeded and not has_deferred and self.overflow_count(cid):
                    has_deferred = True
                if succeeded and not has_deferred:
                    # The latest replay checkpoint may own no URLs itself while older donors still
                    # hold the tail. Its discovery snapshot must survive retention as well.
                    has_deferred = db.execute(
                        "SELECT 1 FROM deferred_crawls checkpoint JOIN deferred_crawls donor "
                        "ON donor.state_key = checkpoint.state_key AND donor.fingerprint = checkpoint.fingerprint "
                        "JOIN collections c ON c.collection_id = donor.collection_id "
                        "WHERE checkpoint.collection_id = ? AND c.status = 'succeeded' "
                        "AND (EXISTS (SELECT 1 FROM frontier_status_counts f WHERE f.collection_id = donor.collection_id "
                        "AND f.status IN ('pending', 'inflight', 'deferred', 'loaned')) "
                        "OR EXISTS (SELECT 1 FROM counters o WHERE o.name = 'overflow:' || donor.collection_id "
                        "AND o.value > 0)) LIMIT 1",
                        (cid,),
                    ).fetchone()
                tables = (
                    ("materials", "errors")
                    if has_deferred
                    else ("strategy_state", "seed_navigation", "frontier_overflow", "materials", "errors")
                )
                for table in tables:
                    db.execute(f"DELETE FROM {table} WHERE collection_id = ?", (cid,))  # noqa: S608
                if not has_deferred:
                    db.execute("DELETE FROM deferred_crawls WHERE collection_id = ?", (cid,))
                    db.execute("UPDATE counters SET value = 0 WHERE name = ?", (f"overflow:{cid}",))
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
                "parent_url, section, lastmod, seen_before) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
                "EXISTS (SELECT 1 FROM url_state u JOIN collections c ON c.state_key = u.state_key "
                "WHERE c.collection_id = ? AND u.url = ? AND u.status BETWEEN 200 AND 399))",
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
                    collection_id,
                    row.url,
                ),
            )
            added += cur.rowcount
        return added

    def frontier_row(self, collection_id: str, url: str) -> sqlite3.Row | None:
        return self._one("SELECT * FROM frontier WHERE collection_id = ? AND url = ?", (collection_id, url))

    def known(self, collection_id: str, url: str) -> bool:
        return (
            self._one(
                "SELECT 1 FROM frontier WHERE collection_id = ? AND url = ? "
                "UNION ALL SELECT 1 FROM frontier_overflow WHERE collection_id = ? AND url = ? LIMIT 1",
                (collection_id, url, collection_id, url),
            )
            is not None
        )

    def add_overflow(self, db: sqlite3.Connection, collection_id: str, row: FrontierRow) -> int:
        """Compressed durable disk spool; these candidates do not occupy the bounded active queue."""
        seq = self.next_counter(db, f"frontier:{collection_id}")
        added = db.execute(
            "INSERT OR IGNORE INTO frontier_overflow(collection_id, url, priority, seq, row, seen_before) "
            "VALUES (?, ?, ?, ?, ?, EXISTS (SELECT 1 FROM url_state u JOIN collections c ON c.state_key = u.state_key "
            "WHERE c.collection_id = ? AND u.url = ? AND u.status BETWEEN 200 AND 399))",
            (
                collection_id,
                row.url,
                row.priority,
                seq,
                sqlite3.Binary(zlib.compress(_dumps(asdict(row)).encode())),
                collection_id,
                row.url,
            ),
        ).rowcount
        self._overflow_delta(db, collection_id, added)
        return added

    def _overflow_delta(self, db: sqlite3.Connection, collection_id: str, delta: int) -> None:
        if delta:
            db.execute(
                "INSERT INTO counters(name, value) VALUES (?, ?) ON CONFLICT(name) DO UPDATE SET value = value + excluded.value",
                (f"overflow:{collection_id}", delta),
            )

    def overflow_count(self, collection_id: str) -> int:
        row = self._one("SELECT value FROM counters WHERE name = ?", (f"overflow:{collection_id}",))
        return int(row[0]) if row else 0

    def promote_overflow(
        self,
        db: sqlite3.Connection,
        collection_id: str,
        limit: int,
        *,
        status: str = "pending",
        revisits: int | None = None,
        materials_only: bool = False,
    ) -> int:
        if limit <= 0:
            return 0
        if revisits is None:
            rows = db.execute(
                "SELECT * FROM frontier_overflow WHERE collection_id = ? "
                "ORDER BY seen_before, priority DESC, seq LIMIT ?",
                (collection_id, limit),
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM frontier_overflow WHERE collection_id = ? AND seen_before = ? "
                "ORDER BY priority DESC, seq LIMIT ?",
                (collection_id, revisits, limit),
            ).fetchall()
        added = 0
        for raw in rows:
            candidate = FrontierRow(**json.loads(zlib.decompress(raw["row"])))
            if materials_only and candidate.kind != "material":
                continue
            added += self.add_urls(db, collection_id, [candidate], status=status)
            removed = db.execute(
                "DELETE FROM frontier_overflow WHERE collection_id = ? AND url = ?",
                (collection_id, raw["url"]),
            ).rowcount
            self._overflow_delta(db, collection_id, -removed)
        return added

    def spool_known_pending(self, db: sqlite3.Connection, collection_id: str) -> bool:
        row = db.execute(
            "SELECT * FROM frontier WHERE collection_id = ? AND status = 'pending' AND seen_before = 1 "
            "ORDER BY priority, seq DESC LIMIT 1",
            (collection_id,),
        ).fetchone()
        if row is None:
            return False
        candidate = FrontierRow(**{key: row[key] for key in FrontierRow.__dataclass_fields__})
        self.add_overflow(db, collection_id, candidate)
        db.execute("DELETE FROM frontier WHERE collection_id = ? AND url = ?", (collection_id, candidate.url))
        return True

    def take_pending(
        self, collection_id: str, limit: int, fence: Fence | None = None, *, materials_only: bool = False
    ) -> list[FrontierRow]:
        with self.tx(fence) as db:
            mode = db.execute(
                "SELECT COALESCE(json_extract(request, '$.mode'), 'full') FROM collections WHERE collection_id = ?",
                (collection_id,),
            ).fetchone()
            if mode is not None and mode[0] == "incremental":
                rows = db.execute(
                    "SELECT * FROM frontier WHERE collection_id = ? AND status = 'pending' "
                    "AND (? = 0 OR kind = 'material') ORDER BY seen_before, priority DESC, seq LIMIT ?",
                    (collection_id, int(materials_only), limit),
                ).fetchall()
            else:
                rows = db.execute(
                    "SELECT * FROM frontier WHERE collection_id = ? AND status = 'pending' "
                    "AND (? = 0 OR kind = 'material') ORDER BY priority DESC, seq LIMIT ?",
                    (collection_id, int(materials_only), limit),
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
        if status != "pending":
            removed = db.execute(
                "DELETE FROM frontier_overflow WHERE collection_id = ? AND url = ?", (collection_id, url)
            ).rowcount
            self._overflow_delta(db, collection_id, -removed)
        if status not in ("pending", "inflight", "deferred", "loaned"):
            db.execute(
                "UPDATE frontier_loans SET completed = 1 WHERE borrower_id = ? AND url = ?",
                (collection_id, url),
            )

    def reset_inflight(self, collection_id: str, fence: Fence | None = None) -> int:
        with self.tx(fence) as db:
            return db.execute(
                "UPDATE frontier SET status = 'pending' WHERE collection_id = ? AND status = 'inflight'",
                (collection_id,),
            ).rowcount

    def frontier_counts(self, collection_id: str) -> dict[str, int]:
        rows = self._all(
            "SELECT status, SUM(value) FROM frontier_status_counts WHERE collection_id = ? GROUP BY status",
            (collection_id,),
        )
        counts = {str(r[0]): int(r[1]) for r in rows}
        checkpoint = self._one(
            "SELECT 1 FROM deferred_crawls d JOIN collections c ON c.collection_id = d.collection_id "
            "WHERE d.collection_id = ? AND c.status = 'succeeded'",
            (collection_id,),
        )
        if checkpoint:
            deferred = counts.pop("pending", 0) + counts.pop("inflight", 0)
            if deferred:
                counts["deferred"] = counts.get("deferred", 0) + deferred
        overflow = self.overflow_count(collection_id)
        if overflow:
            counts["overflow"] = overflow
        return counts

    def drop_pending(self, collection_id: str, fence: Fence | None = None) -> int:
        """Budget reached: pending and stale in-flight URLs are dropped (not fetched in this run)."""
        with self.tx(fence) as db:
            return db.execute(
                "UPDATE frontier SET status = 'dropped' WHERE collection_id = ? AND status IN ('pending', 'inflight')",
                (collection_id,),
            ).rowcount

    def defer_pending(
        self,
        db: sqlite3.Connection,
        collection_id: str,
        state_key: str,
        fingerprint: str,
        seeded: Sequence[str],
    ) -> int:
        """Atomically checkpoint the collection, leaving its potentially millions of rows untouched.

        Pending/inflight rows of this successful checkpoint are logically deferred. Legacy physical
        deferred rows remain readable; only the bounded batch actually borrowed changes ownership.
        """
        counts = self.frontier_counts(collection_id)
        count = counts.get("pending", 0) + counts.get("inflight", 0)
        if count or self.overflow_count(collection_id) or self.continuation_size(state_key, fingerprint):
            db.execute(
                "INSERT OR REPLACE INTO deferred_crawls VALUES (?, ?, ?, ?)",
                (collection_id, state_key, fingerprint, _dumps(list(seeded))),
            )
        else:
            db.execute("DELETE FROM seed_navigation WHERE collection_id = ?", (collection_id,))
        return count

    def settle_loans(
        self,
        db: sqlite3.Connection,
        *,
        borrower_id: str | None = None,
        state_key: str | None = None,
        fingerprint: str | None = None,
    ) -> None:
        """Successful borrowers durably own their checkpoint; failed/cancelled ones return unfinished loans.

        Completion is recorded with each page transaction, so recovery also works after retention
        removes a failed borrower's frontier. Its already processed pages are never loaned twice.
        """
        rows = db.execute(
            "SELECT l.*, c.status AS borrower_status FROM frontier_loans l "
            "JOIN collections c ON c.collection_id = l.borrower_id "
            "JOIN deferred_crawls d ON d.collection_id = l.donor_id "
            "WHERE (? IS NOT NULL AND l.borrower_id = ?) OR "
            "(? IS NULL AND d.state_key = ? AND d.fingerprint = ? AND c.status IN ('failed', 'cancelled'))",
            (borrower_id, borrower_id, borrower_id, state_key, fingerprint),
        ).fetchall()
        for loan in rows:
            status = "transferred" if borrower_id is not None or loan["completed"] else "deferred"
            self.mark_url(db, loan["donor_id"], loan["url"], status)
            if status == "transferred":
                db.execute(
                    "DELETE FROM frontier WHERE collection_id = ? AND url = ? AND "
                    "EXISTS (SELECT 1 FROM collections c WHERE c.collection_id = frontier.collection_id AND c.expired = 1)",
                    (loan["donor_id"], loan["url"]),
                )
            db.execute(
                "DELETE FROM frontier_loans WHERE donor_id = ? AND url = ?", (loan["donor_id"], loan["url"])
            )

    def adopt_deferred(
        self,
        db: sqlite3.Connection,
        collection_id: str,
        state_key: str,
        fingerprint: str,
        limit: int,
        admit: Callable[[FrontierRow], FrontierRow | None],
    ) -> tuple[list[FrontierRow], list[str], dict[str, Any]]:
        """Atomically claim a bounded batch, validating it against the new run's effective policy.

        Finished/cancelled/failed runs cannot supply each other's queue. The old collection keeps any
        unclaimed tail, so adoption is bounded even for multi-million URL catalogs.
        """
        self.settle_loans(db, state_key=state_key, fingerprint=fingerprint)
        donors = db.execute(
            "SELECT d.collection_id, d.seeded FROM deferred_crawls d "
            "JOIN collections c ON c.collection_id = d.collection_id "
            "WHERE d.state_key = ? AND d.fingerprint = ? AND c.status = 'succeeded' "
            "AND (EXISTS (SELECT 1 FROM frontier_status_counts f WHERE f.collection_id = d.collection_id "
            "AND f.status IN ('pending', 'inflight', 'deferred')) "
            "OR EXISTS (SELECT 1 FROM frontier_overflow o WHERE o.collection_id = d.collection_id)) "
            "ORDER BY c.created_at, d.collection_id",
            (state_key, fingerprint),
        ).fetchall()
        context = db.execute(
            "SELECT d.collection_id, d.seeded FROM deferred_crawls d "
            "JOIN collections c ON c.collection_id = d.collection_id "
            "WHERE d.state_key = ? AND d.fingerprint = ? AND c.status = 'succeeded' "
            "ORDER BY c.finished_ts DESC, d.collection_id DESC LIMIT 1",
            (state_key, fingerprint),
        ).fetchone()
        accepted: list[FrontierRow] = []
        seeded: list[str] = json.loads(context["seeded"]) if context else []
        snapshots: dict[str, Any] = self.load_strategy_states(context["collection_id"]) if context else {}
        # Prefer unseen URLs across *all* old runs, including a newer donor's discovered tail.
        for revisits in (0, 1):
            for donor in donors:
                cid = donor["collection_id"]
                self.promote_overflow(db, cid, limit - len(accepted), status="deferred", revisits=revisits)
                rows = []
                for physical_status in ("pending", "inflight", "deferred"):
                    rows.extend(
                        db.execute(
                            "SELECT * FROM frontier WHERE collection_id = ? AND status = ? AND seen_before = ? "
                            "ORDER BY priority DESC, seq LIMIT ?",
                            (cid, physical_status, revisits, limit - len(accepted)),
                        ).fetchall()
                    )
                # Each status uses its index independently. Merge at most three bounded windows,
                # preserving priority without a SQL sort over the donor's entire catalog.
                rows.sort(key=lambda raw: (-raw["priority"], raw["seq"]))
                rows = rows[: limit - len(accepted)]
                for raw in rows:
                    row = admit(FrontierRow(**{key: raw[key] for key in FrontierRow.__dataclass_fields__}))
                    if row is not None and self.add_urls(db, collection_id, [row]):
                        accepted.append(row)
                    if row is not None:
                        self.mark_url(db, cid, raw["url"], "loaned")
                        db.execute(
                            "INSERT OR REPLACE INTO frontier_loans VALUES (?, ?, ?, 0)",
                            (cid, raw["url"], collection_id),
                        )
                    else:
                        self.mark_url(db, cid, raw["url"], "skipped")
                if len(accepted) >= limit:
                    return accepted, seeded, snapshots
        return accepted, seeded, snapshots

    def has_deferred_url(self, state_key: str, fingerprint: str, url: str) -> bool:
        return (
            self._one(
                "SELECT 1 FROM deferred_crawls d JOIN collections c ON c.collection_id = d.collection_id "
                "JOIN frontier f ON f.collection_id = d.collection_id AND f.url = ? "
                "WHERE d.state_key = ? AND d.fingerprint = ? AND c.status = 'succeeded' "
                "AND f.status IN ('pending', 'inflight', 'deferred', 'loaned') "
                "UNION ALL SELECT 1 FROM deferred_crawls d JOIN collections c ON c.collection_id = d.collection_id "
                "JOIN frontier_overflow o ON o.collection_id = d.collection_id AND o.url = ? "
                "WHERE d.state_key = ? AND d.fingerprint = ? AND c.status = 'succeeded' LIMIT 1",
                (url, state_key, fingerprint, url, state_key, fingerprint),
            )
            is not None
        )

    def continuation_size(self, state_key: str, fingerprint: str) -> int:
        row = self._one(
            "SELECT SUM(f.value) FROM deferred_crawls d JOIN collections c ON c.collection_id = d.collection_id "
            "JOIN frontier_status_counts f ON f.collection_id = d.collection_id "
            "WHERE d.state_key = ? AND d.fingerprint = ? AND c.status IN ('queued', 'running', 'succeeded') "
            "AND f.status IN ('pending', 'inflight', 'deferred')",
            (state_key, fingerprint),
        )
        overflow = self._one(
            "SELECT SUM(o.value) FROM deferred_crawls d JOIN counters o ON o.name = 'overflow:' || d.collection_id "
            "JOIN collections c ON c.collection_id = d.collection_id "
            "WHERE d.state_key = ? AND d.fingerprint = ? AND c.status IN ('queued', 'running', 'succeeded')",
            (state_key, fingerprint),
        )
        return (int(row[0] or 0) if row else 0) + (int(overflow[0] or 0) if overflow else 0)

    def save_seed_navigation(
        self,
        db: sqlite3.Connection,
        collection_id: str,
        strategy_id: str,
        url: str,
        resource: Mapping[str, Any],
        body: bytes,
    ) -> None:
        db.execute(
            "INSERT OR REPLACE INTO seed_navigation VALUES (?, ?, ?, ?, ?)",
            (collection_id, strategy_id, url, _dumps(resource), sqlite3.Binary(zlib.compress(body))),
        )

    def seed_navigation(
        self,
        collection_id: str,
        strategy_id: str,
        url: str,
        *,
        state_key: str | None = None,
        fingerprint: str | None = None,
    ) -> tuple[dict[str, Any], bytes] | None:
        row = self._one(
            "SELECT resource, body FROM seed_navigation WHERE collection_id = ? AND strategy_id = ? AND url = ?",
            (collection_id, strategy_id, url),
        )
        if row is None and state_key is not None and fingerprint is not None:
            # An immutable successful donor's navigation can be replayed without copying its XML
            # BLOBs to every budget-sized borrower. Start from the exact URL index, not all donors.
            row = self._one(
                "SELECT n.resource, n.body FROM seed_navigation n INDEXED BY seed_navigation_lookup "
                "JOIN deferred_crawls d ON d.collection_id = n.collection_id "
                "JOIN collections c ON c.collection_id = d.collection_id "
                "WHERE n.strategy_id = ? AND n.url = ? AND d.state_key = ? AND d.fingerprint = ? "
                "AND c.status = 'succeeded' ORDER BY c.finished_ts DESC, d.collection_id DESC LIMIT 1",
                (strategy_id, url, state_key, fingerprint),
            )
        return (json.loads(row[0]), zlib.decompress(row[1])) if row else None

    def clear_seed_navigation(
        self,
        db: sqlite3.Connection,
        collection_id: str,
        strategy_id: str,
        state_key: str,
        fingerprint: str,
        seeded: Sequence[str],
    ) -> None:
        db.execute(
            "DELETE FROM seed_navigation WHERE collection_id = ? AND strategy_id = ?",
            (collection_id, strategy_id),
        )
        # Donor replay context stays immutable until this borrower succeeds. A failure must be
        # able to return its unfinished loan together with the donor's original discovery state.

    def complete_discovery(
        self, db: sqlite3.Connection, state_key: str, fingerprint: str, seeded: Sequence[str]
    ) -> None:
        db.execute(
            "DELETE FROM seed_navigation WHERE collection_id IN (SELECT collection_id FROM deferred_crawls "
            "WHERE state_key = ? AND fingerprint = ?) AND strategy_id IN (SELECT value FROM json_each(?))",
            (state_key, fingerprint, _dumps(list(seeded))),
        )
        db.execute(
            "UPDATE deferred_crawls SET seeded = ? WHERE state_key = ? AND fingerprint = ?",
            (_dumps(list(seeded)), state_key, fingerprint),
        )

    def clear_continuation(self, db: sqlite3.Connection, state_key: str, fingerprint: str) -> None:
        db.execute(
            "DELETE FROM seed_navigation WHERE collection_id IN "
            "(SELECT collection_id FROM deferred_crawls WHERE state_key = ? AND fingerprint = ?)",
            (state_key, fingerprint),
        )
        db.execute(
            "DELETE FROM deferred_crawls WHERE state_key = ? AND fingerprint = ?", (state_key, fingerprint)
        )

    def pending_count(self, collection_id: str, *, materials_only: bool = False) -> int:
        row = self._one(
            "SELECT SUM(value) FROM frontier_status_counts WHERE collection_id = ? AND status = 'pending' "
            "AND (? = 0 OR kind = 'material')",
            (collection_id, int(materials_only)),
        )
        return int(row[0] or 0) if row else 0

    def frontier_size_for_state_key(self, state_key: str) -> int:
        row = self._one(
            "SELECT SUM(f.value) FROM collections c JOIN frontier_status_counts f "
            "ON f.collection_id = c.collection_id "
            "WHERE c.state_key = ? AND ((c.status IN ('queued', 'running', 'cancelling') "
            "AND f.status IN ('pending', 'inflight')) OR (c.status = 'succeeded' "
            "AND (f.status = 'deferred' OR (f.status IN ('pending', 'inflight') "
            "AND EXISTS (SELECT 1 FROM deferred_crawls d WHERE d.collection_id = c.collection_id)))))",
            (state_key,),
        )
        overflow = self._one(
            "SELECT SUM(o.value) FROM collections c JOIN counters o ON o.name = 'overflow:' || c.collection_id "
            "WHERE c.state_key = ? AND c.status IN ('queued', 'running', 'cancelling', 'succeeded')",
            (state_key,),
        )
        return (int(row[0] or 0) if row else 0) + (int(overflow[0] or 0) if overflow else 0)

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
            db.execute(
                "UPDATE counters SET value = 0 WHERE name IN (SELECT 'overflow:' || collection_id FROM deferred_crawls WHERE state_key = ?)",
                (state_key,),
            )
            db.execute(
                "DELETE FROM frontier_loans WHERE donor_id IN (SELECT collection_id FROM deferred_crawls WHERE state_key = ?)",
                (state_key,),
            )
            for table in ("seed_navigation", "frontier", "frontier_overflow"):
                db.execute(
                    f"DELETE FROM {table} WHERE collection_id IN (SELECT collection_id FROM deferred_crawls WHERE state_key = ?)",  # noqa: S608
                    (state_key,),
                )
            db.execute("DELETE FROM deferred_crawls WHERE state_key = ?", (state_key,))

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

    # ------------------------------------------------------------------ jobs (jane-kit shared stores, R17)
    @contextmanager
    def read(self) -> Iterator[sqlite3.Connection]:
        """The connection for single-statement reads (no write lock; ``jane_kit.stores.sqlite``)."""
        with self._lock:
            yield self._db

    def get_job(self, job_id: str) -> str | None:
        row = self._one("SELECT body FROM jobs WHERE job_id = ?", (job_id,))
        return str(row[0]) if row else None

    def work_row(self, db: sqlite3.Connection, job_id: str) -> tuple[str | None, str] | None:
        """``(owner, status)`` of the collection of a job (``jane_kit.stores.sqlite.WorkRows``)."""
        row = db.execute(
            "SELECT owner, status FROM collections WHERE collection_id = ?", (job_id,)
        ).fetchone()
        return (row[0], str(row[1])) if row else None

    def cancel_unstarted(self, db: sqlite3.Connection, job_id: str, owner: str) -> bool:
        """A collection cancelled before its run started ends ``cancelled`` (only its lease holder)."""
        now = time.time()
        cur = db.execute(
            "UPDATE collections SET status = 'cancelled', finished_at = ?, finished_ts = ?, lease_until = 0 "
            "WHERE collection_id = ? AND status = 'queued' AND owner = ?",
            (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), now, job_id, owner),
        )
        return cur.rowcount == 1

    # ------------------------------------------------------------------ per-host schedule of all instances (R15)
    def host_take_slot(
        self, host: str, instance_id: str, token: str, *, interval: float, parallel: int, ttl: float
    ) -> tuple[bool, float]:
        """One attempt of request ``token`` to start on ``host`` for the whole platform (R15), in one transaction.

        Registers (renews) the limits of ``instance_id`` on the host and queues the request in arrival order
        (``host_waiters``). The request takes a slot only when it may start **now**: it is first in line (starts go
        strictly in arrival order: a younger request never takes the start the first one waits for), fewer requests
        than the smallest registered parallelism are in flight, and the schedule allows a start - the largest registered interval after the previous start of any instance has
        passed, and so has a ``Retry-After``. A slot is thus never held while waiting (review 1 of WP-16).

        Returns ``(True, 0.0)`` when the slot is taken (the start is recorded as now), ``(False, seconds)`` when the
        request is first in line but the schedule allows a start only in ``seconds``, ``(False, 0.0)`` when it waits
        for a slot or an older waiter (try again after the poll interval). Expired registrations, slots and waiters
        (instances that died: nothing renews them) are dropped first."""
        now = time.time()
        with self.tx() as db:
            db.execute("DELETE FROM host_slots WHERE host = ? AND expires_at <= ?", (host, now))
            db.execute("DELETE FROM host_users WHERE host = ? AND expires_at <= ?", (host, now))
            db.execute("DELETE FROM host_waiters WHERE host = ? AND expires_at <= ?", (host, now))
            db.execute(
                "INSERT INTO host_users(host, instance_id, interval_s, parallel, expires_at) VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT(host, instance_id) DO UPDATE SET interval_s = excluded.interval_s, "
                "parallel = excluded.parallel, expires_at = excluded.expires_at",
                (host, instance_id, interval, parallel, now + ttl),
            )
            db.execute(
                "INSERT INTO host_waiters(host, token, since, expires_at) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(host, token) DO UPDATE SET expires_at = excluded.expires_at",
                (host, token, now, now + ttl),
            )
            since = float(
                db.execute(
                    "SELECT since FROM host_waiters WHERE host = ? AND token = ?", (host, token)
                ).fetchone()[0]
            )
            ahead = int(
                db.execute(
                    "SELECT COUNT(*) FROM host_waiters WHERE host = ? AND (since < ? OR (since = ? AND token < ?))",
                    (host, since, since, token),
                ).fetchone()[0]
            )
            allowed = int(
                db.execute("SELECT MIN(parallel) FROM host_users WHERE host = ?", (host,)).fetchone()[0]
            )
            busy = int(db.execute("SELECT COUNT(*) FROM host_slots WHERE host = ?", (host,)).fetchone()[0])
            if (
                ahead or busy >= allowed
            ):  # strictly first come, first served: no younger request takes a start
                return False, 0.0
            interval_s = float(
                db.execute("SELECT MAX(interval_s) FROM host_users WHERE host = ?", (host,)).fetchone()[0]
            )
            row = db.execute(
                "SELECT last_start, not_before FROM host_schedule WHERE host = ?", (host,)
            ).fetchone()
            last, not_before = (float(row[0]), float(row[1])) if row else (0.0, 0.0)
            due = max(last + interval_s, not_before)
            if due > now:
                return False, due - now  # first in line: keep the place, start when the schedule allows
            db.execute("DELETE FROM host_waiters WHERE host = ? AND token = ?", (host, token))
            db.execute(
                "INSERT INTO host_slots(host, token, instance_id, expires_at) VALUES (?, ?, ?, ?)",
                (host, token, instance_id, now + ttl),
            )
            db.execute(
                "INSERT INTO host_schedule(host, last_start, not_before) VALUES (?, ?, ?) "
                "ON CONFLICT(host) DO UPDATE SET last_start = excluded.last_start",
                (host, now, not_before),
            )
            return True, 0.0

    def host_renew(
        self,
        instance_id: str,
        registrations: Mapping[str, tuple[float, int]],
        tokens: Sequence[str],
        ttl: float,
    ) -> None:
        """Keep alive what a live instance holds (R15): its registrations on hosts (``host -> (interval, parallel)``,
        re-created if they expired meanwhile), and the slots and places in line of ``tokens``. A killed instance
        renews nothing, so its rows expire ``ttl`` seconds after its last renewal."""
        expires = time.time() + ttl
        with self.tx() as db:
            for host, (interval, parallel) in registrations.items():
                db.execute(
                    "INSERT INTO host_users(host, instance_id, interval_s, parallel, expires_at) "
                    "VALUES (?, ?, ?, ?, ?) ON CONFLICT(host, instance_id) DO UPDATE SET "
                    "interval_s = excluded.interval_s, parallel = excluded.parallel, expires_at = excluded.expires_at",
                    (host, instance_id, interval, parallel, expires),
                )
            for token in tokens:
                db.execute("UPDATE host_slots SET expires_at = ? WHERE token = ?", (expires, token))
                db.execute("UPDATE host_waiters SET expires_at = ? WHERE token = ?", (expires, token))

    def host_release_slot(self, host: str, token: str) -> None:
        """Give back the slot of ``token`` (or its place in line, if it never got one)."""
        with self.tx() as db:
            db.execute("DELETE FROM host_slots WHERE host = ? AND token = ?", (host, token))
            db.execute("DELETE FROM host_waiters WHERE host = ? AND token = ?", (host, token))

    def host_push_back(self, host: str, until: float) -> None:
        with self.tx() as db:
            db.execute(
                "INSERT INTO host_schedule(host, last_start, not_before) VALUES (?, 0, ?) "
                "ON CONFLICT(host) DO UPDATE SET not_before = MAX(host_schedule.not_before, excluded.not_before)",
                (host, until),
            )

    def host_leave(self, host: str, instance_id: str) -> None:
        with self.tx() as db:
            db.execute("DELETE FROM host_users WHERE host = ? AND instance_id = ?", (host, instance_id))

    def host_rows(self, host: str) -> dict[str, Any]:
        """Shared state of one host (diagnostics, tests)."""
        users = self._all("SELECT instance_id, interval_s, parallel FROM host_users WHERE host = ?", (host,))
        slots = self._one("SELECT COUNT(*) FROM host_slots WHERE host = ?", (host,))
        return {"users": [dict(r) for r in users], "slots": int(slots[0]) if slots else 0}

    def host_prune(self) -> int:
        """Drop expired registrations, slots and schedules of hosts nobody uses (housekeeping)."""
        now = time.time()
        with self.tx() as db:
            removed = db.execute("DELETE FROM host_slots WHERE expires_at <= ?", (now,)).rowcount
            removed += db.execute("DELETE FROM host_users WHERE expires_at <= ?", (now,)).rowcount
            removed += db.execute("DELETE FROM host_waiters WHERE expires_at <= ?", (now,)).rowcount
            removed += db.execute(
                "DELETE FROM host_schedule WHERE last_start < ? AND not_before < ? "
                "AND host NOT IN (SELECT host FROM host_users) AND host NOT IN (SELECT host FROM host_slots)",
                (now, now),
            ).rowcount
            return removed
