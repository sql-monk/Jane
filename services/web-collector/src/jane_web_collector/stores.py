"""jane-kit's shared SQLite ``JobStore`` / ``IdempotencyStore`` on the collector's own state file (R17).

* jobs mirror their collections (``jane_kit.stores.sqlite.SqliteWorkJobStore``): only the instance holding a
  collection's lease writes its job, others may only request ``cancelling``; a terminal job status is stored
  only when the collection already has it (written by the run's final lease-fenced transaction or by the owner
  on failure/cancellation), so a run that stopped without finishing (lease lost, graceful shutdown) never makes
  the job look finished; a job cancelled before its run started ends the collection too;
* ``Idempotency-Key`` claims carry this instance, a token and a lease (``JANE_WEB_COLLECTOR_IDEMPOTENCY_LEASE_MS``)
  renewed by the resume loop: a claim of a killed instance can be taken over after the lease instead of the
  key's whole TTL.
"""

from __future__ import annotations

from jane_kit.stores.sqlite import SqliteIdempotencyStore as _KitIdempotency
from jane_kit.stores.sqlite import SqliteWorkJobStore

from .state import StateStore

__all__ = ["SqliteIdempotencyStore", "SqliteJobStore"]


class SqliteJobStore(SqliteWorkJobStore):
    """Jobs of collections, shared by all instances on the state file."""

    def __init__(self, state: StateStore, instance_id: str) -> None:
        super().__init__(state, state, owner=instance_id, table="jobs", doc_column="body")
        self.state = state
        self.instance_id = instance_id
        self.migrate()


class SqliteIdempotencyStore(_KitIdempotency):
    def __init__(self, state: StateStore, instance_id: str, in_progress_lease_s: float) -> None:
        super().__init__(
            state, owner=instance_id, in_progress_lease_s=in_progress_lease_s, table="idempotency"
        )
        self.state = state
        self.migrate()
