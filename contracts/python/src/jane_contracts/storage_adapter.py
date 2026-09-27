"""Storage adapter contract for the storage handler.

Owners: WP-07 implements the storage core (handler protocol, merge semantics, ordering, delivery
dedup, test mode, default formats) plus the ``filesystem`` and ``postgresql`` adapters and the
**compatibility suite**; WP-08 implements ``sqlserver``, ``mongodb``, ``minio`` and ``s3``.

Principle: the *core* owns all semantics of EntityRecord application (partial update, explicit
clear, observation ordering, stale detection) as a pure function; an adapter only provides durable
primitives with two guarantees:

1. :meth:`StorageAdapter.commit_entity` is atomic: delivery-key uniqueness, compare-and-swap on the
   snapshot ``version`` and the history append succeed or fail together.
2. :meth:`StorageAdapter.put_object` is idempotent by ``object_key``.

Scenarios every adapter must pass are listed in contracts/docs/storage-adapter.md (C-01…C-16).
Adapters never read environment variables or secret stores: the core resolves ``secret_refs`` and
passes a :class:`ResolvedConnection`.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar, Literal, Protocol, runtime_checkable

RawFormat = Literal["original", "html", "json"]


@dataclass(frozen=True, slots=True)
class ResolvedConnection:
    connection_id: str
    kind: str
    params: Mapping[str, Any]
    secrets: Mapping[str, str] = field(repr=False, default_factory=dict)


@dataclass(frozen=True, slots=True)
class OrderKey:
    """Observation order (entity.schema.json#/$defs/ObservationOrder). Compare with :func:`order_tuple`."""

    observed_at: datetime
    observation_id: str
    sequence: int | None = None


def order_tuple(key: OrderKey) -> tuple[datetime, int, str]:
    """Total order used by the core: observed_at, then sequence (missing = -1), then observation_id."""
    return (key.observed_at, -1 if key.sequence is None else key.sequence, key.observation_id)


@dataclass(frozen=True, slots=True)
class RawObject:
    """A material (RAW) or result document to persist as an object."""

    object_key: str
    """Deterministic key built by the core: ``<source_id>/<yyyy>/<mm>/<dd>/<material_id>/<observation_id>.<ext>``
    (filesystem-safe: ':' replaced by '_'). Same key + same sha256 = same object."""
    material_id: str
    observation_id: str
    source_id: str | None
    media_type: str
    format: RawFormat
    content: bytes
    sha256: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
    """Material without content (JSON-compatible), stored next to the object for reprocessing."""


@dataclass(frozen=True, slots=True)
class ObjectRecord:
    object_id: str
    object_key: str
    locator: Mapping[str, str | int]
    media_type: str
    size_bytes: int
    sha256: str
    stored_at: datetime
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class EntitySnapshot:
    """Current state of one entity (entity.schema.json#/$defs/EntityState)."""

    entity_type: str
    canonical_key: str
    key: Mapping[str, Any]
    fields: Mapping[str, Any]
    field_orders: Mapping[str, OrderKey]
    cleared_fields: frozenset[str]
    version: int
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class HistoryEvent:
    """One accepted update (also stale ones) — entity.schema.json#/$defs/EntityHistoryEntry."""

    entity_type: str
    canonical_key: str
    record: Mapping[str, Any]
    delivery_key: str
    received_at: datetime
    applied_fields: Sequence[str]
    stale_fields: Sequence[str]


@dataclass(frozen=True, slots=True)
class DeliveryRecord:
    """What was acknowledged for a delivery key (serialized WriteAck list)."""

    delivery_key: str
    recorded_at: datetime
    acks: Sequence[Mapping[str, Any]]


class CommitOutcome(Enum):
    COMMITTED = "committed"
    CONFLICT = "conflict"
    """``expected_version`` did not match: the core re-reads, re-merges and retries (bounded)."""
    DUPLICATE = "duplicate"
    """The delivery key (for this entity) was already committed: nothing written."""


@dataclass(frozen=True, slots=True)
class CommitResult:
    outcome: CommitOutcome
    snapshot: EntitySnapshot | None
    """Snapshot after the commit (COMMITTED) or the current one (CONFLICT/DUPLICATE), if known."""


class AdapterError(Exception):
    """Adapter failure. ``retryable`` maps to Problem.retryable / HandlerResult.failure.retryable."""

    def __init__(self, message: str, *, retryable: bool) -> None:
        super().__init__(message)
        self.retryable = retryable


@runtime_checkable
class StorageAdapter(Protocol):
    kind: ClassVar[str]
    """``filesystem``, ``postgresql``, ``sqlserver``, ``mongodb``, ``minio``, ``s3``."""
    capabilities: ClassVar[frozenset[str]]
    """Subset of {"objects", "entities", "history"}. Object stores (minio, s3) may support entities via
    conditional writes; if not, they declare only {"objects"} and the core rejects entity writes."""

    async def open(self, connection: ResolvedConnection, options: Mapping[str, Any]) -> None: ...

    async def close(self) -> None: ...

    async def health(self) -> bool: ...

    async def ensure_schema(self, entity_types: Sequence[str]) -> None:
        """Idempotently create tables/collections/buckets/directories."""
        ...

    # Objects (RAW, result documents) ------------------------------------------------------------

    async def put_object(self, obj: RawObject) -> ObjectRecord:
        """Idempotent by ``object_key``: an existing object with the same sha256 is returned as is;
        a different sha256 raises ``AdapterError(retryable=False)``."""
        ...

    async def get_object(self, object_id: str) -> ObjectRecord | None: ...

    async def read_object_content(self, object_id: str) -> bytes: ...

    async def list_objects(
        self,
        *,
        source_id: str | None = None,
        material_id: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        cursor: str | None = None,
        limit: int,
    ) -> tuple[Sequence[ObjectRecord], str | None]: ...

    # Entities ---------------------------------------------------------------------------------

    async def read_entity(self, entity_type: str, canonical_key: str) -> EntitySnapshot | None: ...

    async def commit_entity(self, *, new: EntitySnapshot, expected_version: int | None, event: HistoryEvent) -> CommitResult:
        """Atomically: if (event.delivery_key, entity) already recorded → DUPLICATE; else if the stored
        version != expected_version (None = must not exist) → CONFLICT; else write ``new`` (whose
        version = expected_version + 1, or 1) and append ``event`` → COMMITTED. A stale-only update
        is committed with ``new`` equal to the current snapshot fields and the same version + 1."""
        ...

    async def list_entities(
        self,
        entity_type: str,
        *,
        scope: str | None = None,
        updated_since: datetime | None = None,
        cursor: str | None = None,
        limit: int,
    ) -> tuple[Sequence[EntitySnapshot], str | None]: ...

    async def list_history(
        self, entity_type: str, canonical_key: str, *, cursor: str | None = None, limit: int
    ) -> tuple[Sequence[HistoryEvent], str | None]: ...

    # Deliveries -------------------------------------------------------------------------------

    async def get_delivery(self, delivery_key: str) -> DeliveryRecord | None: ...

    async def record_delivery(self, record: DeliveryRecord) -> bool:
        """Insert-if-absent. Returns False if the key already exists (used for object-only writes)."""
        ...
