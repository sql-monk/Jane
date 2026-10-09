"""``Idempotency-Key`` storage in the orchestrator DB, so several API instances share it.

jane-kit's shared :class:`jane_kit.stores.postgres.PgIdempotencyStore` (R17) on the table ``idempotency_keys``
(migration 7 added the claim ``owner``/``token``/``lease_until``): a claim of a stopped instance is taken over after
``limits.claims.in_progress_lease_ms``; a live instance renews its claims (``heartbeat_interval_ms``); a request
whose claim was taken over cannot overwrite the new one.
"""

from __future__ import annotations

from jane_kit.stores import ClaimLimits
from jane_kit.stores.postgres import PgIdempotencyStore
from jane_orchestrator.db import Database

__all__ = ["idempotency_store"]


def idempotency_store(db: Database, owner: str, claims: ClaimLimits) -> PgIdempotencyStore:
    # the table and its columns come from the orchestrator's own migrations (db.MIGRATIONS), not from ddl()
    return PgIdempotencyStore(
        db.tx, owner=owner, in_progress_lease_s=claims.in_progress_lease_ms / 1000, table="idempotency_keys"
    )
