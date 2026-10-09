"""The orchestrator's own PostgreSQL database: connection pool and schema migrations.

The work queue uses ``SELECT … FOR UPDATE SKIP LOCKED`` (plan.md §2); no other broker. Migrations are
idempotent and serialized with an advisory lock, so several instances may start at once.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from psycopg_pool import ConnectionPool

__all__ = ["Database", "Jsonb"]

log = logging.getLogger(__name__)

MIGRATION_LOCK = 0x6A616E65  # "jane"

MIGRATIONS: list[str] = [
    # 1 — initial schema
    """
    CREATE TABLE sources (
        source_id   text PRIMARY KEY,
        doc         jsonb NOT NULL,
        version     integer NOT NULL DEFAULT 1,
        created_at  timestamptz NOT NULL DEFAULT now(),
        updated_at  timestamptz NOT NULL DEFAULT now()
    );

    CREATE TABLE tasks (
        task_id            text PRIMARY KEY,
        source_id          text NOT NULL REFERENCES sources(source_id),
        doc                jsonb NOT NULL,
        version            integer NOT NULL DEFAULT 1,
        next_run_at        timestamptz,
        last_scheduled_at  timestamptz,
        created_at         timestamptz NOT NULL DEFAULT now(),
        updated_at         timestamptz NOT NULL DEFAULT now()
    );
    CREATE INDEX tasks_next_run ON tasks (next_run_at) WHERE next_run_at IS NOT NULL;

    CREATE TABLE runs (
        run_id                text PRIMARY KEY,
        seq                   bigserial,
        task_id               text NOT NULL,
        source_id             text NOT NULL,
        task_etag             text NOT NULL,
        config                jsonb NOT NULL,
        source_doc            jsonb NOT NULL,
        limits                jsonb NOT NULL,
        input                 jsonb NOT NULL,
        status                text NOT NULL,
        trigger               text NOT NULL,
        test_mode             boolean NOT NULL DEFAULT false,
        reason                text,
        requested_by          text,
        idempotency_key       text,
        trace_id              text NOT NULL,
        overlap               text NOT NULL DEFAULT 'skip',
        created_at            timestamptz NOT NULL DEFAULT now(),
        started_at            timestamptz,
        finished_at           timestamptz,
        updated_at            timestamptz NOT NULL DEFAULT now(),
        collection_id         text,
        feed_cursor           text,
        feed_done             boolean NOT NULL DEFAULT false,
        feed_error            jsonb,
        feed_lease_owner      text,
        feed_lease_expires_at timestamptz,
        feed_available_at     timestamptz NOT NULL DEFAULT now(),
        backpressure          boolean NOT NULL DEFAULT false,
        cancel_requested_at   timestamptz,
        cancel_requested_by   text,
        cancel_reason         text,
        collector_cancelled   boolean NOT NULL DEFAULT false,
        error                 jsonb
    );
    CREATE INDEX runs_task ON runs (task_id, seq DESC);
    CREATE INDEX runs_feed ON runs (feed_available_at)
        WHERE status IN ('queued', 'running', 'cancelling') AND NOT feed_done;

    CREATE TABLE items (
        item_id           text PRIMARY KEY,
        seq               bigserial,
        run_id            text NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
        task_id           text NOT NULL,
        stage_id          text NOT NULL,
        item_key          text NOT NULL,
        status            text NOT NULL,
        payload           jsonb,
        material_id       text,
        observation_id    text,
        source_id         text,
        url               text,
        fetched_at        timestamptz,
        content_sha256    text,
        upstream_item_id  text,
        attempts          integer NOT NULL DEFAULT 0,
        max_attempts      integer NOT NULL DEFAULT 1,
        parallel_limit    integer NOT NULL DEFAULT 1,
        available_at      timestamptz NOT NULL DEFAULT now(),
        lease_owner       text,
        lease_expires_at  timestamptz,
        delivery_key      text,
        handler           jsonb,
        invocation_id     text,
        executor_job      text,
        result_status     text,
        outputs           jsonb,
        error             jsonb,
        llm_cost          numeric,
        llm_currency      text,
        created_at        timestamptz NOT NULL DEFAULT now(),
        started_at        timestamptz,
        finished_at       timestamptz,
        updated_at        timestamptz NOT NULL DEFAULT now(),
        UNIQUE (run_id, stage_id, item_key)
    );
    CREATE INDEX items_claim ON items (available_at) WHERE status IN ('queued', 'retrying');
    CREATE INDEX items_lease ON items (lease_expires_at) WHERE status = 'running';
    CREATE INDEX items_run_stage ON items (run_id, stage_id, status);
    CREATE INDEX items_material ON items (material_id, seq);
    CREATE INDEX items_task_active ON items (task_id)
        WHERE status IN ('queued', 'retrying', 'leased', 'running');

    CREATE TABLE activations (
        activation_id  text PRIMARY KEY,
        seq            bigserial,
        task_id        text NOT NULL,
        stage_id       text NOT NULL,
        package        jsonb NOT NULL,
        previous       jsonb,
        kind           text NOT NULL,
        reason         text,
        activated_by   text,
        activated_at   timestamptz NOT NULL DEFAULT now()
    );
    CREATE INDEX activations_stage ON activations (task_id, stage_id, seq DESC);

    CREATE TABLE audit_events (
        event_id      text PRIMARY KEY,
        seq           bigserial,
        at            timestamptz NOT NULL DEFAULT now(),
        actor         text NOT NULL,
        action        text NOT NULL,
        subject_type  text NOT NULL,
        subject_id    text NOT NULL,
        details       jsonb
    );
    CREATE INDEX audit_subject ON audit_events (subject_type, subject_id, seq DESC);

    CREATE TABLE connections (
        connection_id  text PRIMARY KEY,
        doc            jsonb NOT NULL,
        version        integer NOT NULL DEFAULT 1,
        created_at     timestamptz NOT NULL DEFAULT now(),
        updated_at     timestamptz NOT NULL DEFAULT now()
    );

    CREATE TABLE connection_sync (
        connection_id     text NOT NULL,
        executor          text NOT NULL,
        op                text NOT NULL,
        status            text NOT NULL,
        message           text,
        synced_at         timestamptz,
        attempts          integer NOT NULL DEFAULT 0,
        available_at      timestamptz NOT NULL DEFAULT now(),
        lease_owner       text,
        lease_expires_at  timestamptz,
        PRIMARY KEY (connection_id, executor)
    );

    CREATE TABLE platform_limits (
        id          integer PRIMARY KEY CHECK (id = 1),
        doc         jsonb NOT NULL,
        version     integer NOT NULL DEFAULT 1,
        updated_at  timestamptz NOT NULL DEFAULT now()
    );

    CREATE TABLE problem_groups (
        group_id          text PRIMARY KEY,
        seq               bigserial,
        source_id         text NOT NULL,
        package_id        text NOT NULL,
        package_version   text NOT NULL,
        package           jsonb NOT NULL,
        problem           text NOT NULL,
        failure_kind      text,
        signature         text NOT NULL,
        count             integer NOT NULL DEFAULT 0,
        first_seen_at     timestamptz NOT NULL DEFAULT now(),
        last_seen_at      timestamptz NOT NULL DEFAULT now(),
        status            text NOT NULL DEFAULT 'open',
        assistant_job_id  text,
        samples           jsonb NOT NULL DEFAULT '[]'::jsonb,
        UNIQUE (source_id, package_id, package_version, problem, signature)
    );

    CREATE TABLE unknown_materials (
        id                bigserial PRIMARY KEY,
        material_id       text NOT NULL,
        observation_id    text NOT NULL,
        source_id         text NOT NULL,
        run_id            text NOT NULL,
        url               text,
        registered_at     timestamptz NOT NULL DEFAULT now(),
        forwarded_to_llm  boolean NOT NULL,
        reason            text,
        UNIQUE (run_id, observation_id)
    );

    CREATE TABLE idempotency_keys (
        key          text PRIMARY KEY,
        fingerprint  text NOT NULL,
        state        text NOT NULL,
        status_code  integer,
        body         jsonb,
        headers      jsonb,
        expires_at   timestamptz NOT NULL
    );
    """,
    # 2 — lease take-overs counted apart from retry attempts; LLM budget sync (source/task levels)
    """
    ALTER TABLE items ADD COLUMN lease_reclaims integer NOT NULL DEFAULT 0;

    CREATE TABLE budget_sync (
        scope_type        text NOT NULL,
        scope_id          text NOT NULL,
        op                text NOT NULL,
        doc               jsonb,
        status            text NOT NULL,
        message           text,
        synced_at         timestamptz,
        attempts          integer NOT NULL DEFAULT 0,
        available_at      timestamptz NOT NULL DEFAULT now(),
        lease_owner       text,
        lease_expires_at  timestamptz,
        PRIMARY KEY (scope_type, scope_id)
    );
    """,
    # 3 — restart of a rate-limited collection (collector job failed with rate_limited, retryable)
    """
    ALTER TABLE runs ADD COLUMN collection_restarts integer NOT NULL DEFAULT 0;
    """,
    # 4 — durable RAW reference for problem samples, including storage-fed reprocessing
    """
    ALTER TABLE items ADD COLUMN stored_object_id text;
    CREATE INDEX items_stored_raw ON items (source_id, observation_id)
        WHERE stored_object_id IS NOT NULL;
    """,
    # 5 — remember conflicting storage-read copies across pages and process restarts
    """
    ALTER TABLE items ADD COLUMN stored_object_ambiguous boolean NOT NULL DEFAULT false;
    CREATE INDEX items_stored_raw_ambiguous ON items (source_id, observation_id)
        WHERE stored_object_ambiguous;
    """,
    # 6 — diagnostics of claims and retries per item (R25); note of a problem group (R05)
    """
    ALTER TABLE items ADD COLUMN attempt_history jsonb NOT NULL DEFAULT '[]'::jsonb;
    ALTER TABLE problem_groups ADD COLUMN note text;
    """,
]


class Database:
    """Connection pool over the orchestrator's DSN; rows are dicts."""

    def __init__(self, dsn: str, *, max_size: int = 10, min_size: int = 1) -> None:
        self.dsn = dsn
        self.pool = ConnectionPool(
            dsn,
            min_size=min_size,
            max_size=max_size,
            kwargs={"row_factory": dict_row, "autocommit": True},
            open=False,
        )

    def open(self) -> None:
        self.pool.open(wait=True)

    def close(self) -> None:
        self.pool.close()

    @contextmanager
    def tx(self) -> Iterator[Any]:
        """A connection inside one transaction (commit on success, rollback on error)."""
        with self.pool.connection() as conn, conn.transaction():
            yield conn

    @contextmanager
    def conn(self) -> Iterator[Any]:
        with self.pool.connection() as conn:
            yield conn

    def migrate(self) -> int:
        """Apply pending migrations; returns the schema version."""
        with self.tx() as conn:
            conn.execute("SELECT pg_advisory_xact_lock(%s)", (MIGRATION_LOCK,))
            conn.execute(
                "CREATE TABLE IF NOT EXISTS schema_migrations ("
                " version integer PRIMARY KEY, applied_at timestamptz NOT NULL DEFAULT now())"
            )
            row = conn.execute("SELECT coalesce(max(version), 0) AS v FROM schema_migrations").fetchone()
            current = int(row["v"]) if row else 0
            for version, sql in enumerate(MIGRATIONS, start=1):
                if version <= current:
                    continue
                conn.execute(sql)
                conn.execute("INSERT INTO schema_migrations (version) VALUES (%s)", (version,))
                log.info("schema migrated", extra={"version": version})
            return len(MIGRATIONS)

    def ping(self) -> bool:
        with self.conn() as conn:
            conn.execute("SELECT 1")
        return True
