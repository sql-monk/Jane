"""Crash recovery and races of the S3 commit protocol (shared by the MinIO adapter).

Runs against both S3 servers of the dev stack: SeaweedFS (``s3``) and MinIO (``minio``). The risky points
are driven deterministically through hooks on the adapter's primitive ``_put`` (the other instance runs
between two steps of a commit), not by timing:

* a delivery claim left by a crashed writer (fresh → CONFLICT, stale → removed, lost race → dead at once);
* a snapshot whose ``pending`` history event was never rolled forward;
* an ambiguous response: the conditional PUT (claim or snapshot CAS) took effect, the response was lost
  and botocore's retry got 412 against our own write;
* two instances with the same delivery key, the second one running inside the first one's commit;
* compensation removes only the claim this call wrote.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator, Callable
from datetime import UTC, datetime, timedelta
from typing import Any

import boto3  # type: ignore[import-untyped]
import pytest
from botocore.config import Config  # type: ignore[import-untyped]

from jane_contracts.storage_adapter import CommitOutcome, CommitResult, HistoryEvent, ResolvedConnection
from jane_kit.devstack import load_stack
from jane_storage.adapters import adapter_class
from jane_storage.codec import dumps, format_ts
from jane_storage.compat.suite import COMPAT_RETRIES, record
from jane_storage.engine import StorageEngine
from jane_storage.keys import canonical_key, key_digest
from jane_storage.merge import merge
from jane_storage_s3 import S3Adapter

pytestmark = pytest.mark.integration

PREFIX = "recovery"
KEY = canonical_key(record()["key"])
DIGEST = key_digest(KEY)
SNAP = f"entities/product/{DIGEST}.json"


def hist(version: int) -> str:
    return f"history/product/{DIGEST}/{version:012d}.json"


def claim_key(delivery_key: str) -> str:
    return f"deliveries/{key_digest(delivery_key)}.json"


class Env:
    def __init__(self, kind: str, info: dict[str, Any]) -> None:
        self.kind = kind
        self.info = info
        self.bucket = f"recovery-{uuid.uuid4().hex[:12]}"
        self.client = boto3.client(
            "s3",
            endpoint_url=info["endpoint"],
            region_name=info.get("region", "us-east-1"),
            aws_access_key_id=info["access_key"],
            aws_secret_access_key=info["secret_key"],
            config=Config(s3={"addressing_style": "path"}),
        )
        self.opened: list[S3Adapter] = []

    async def adapter(self, cls: type[S3Adapter] | None = None, **options: Any) -> S3Adapter:
        base = adapter_class(self.kind)
        assert issubclass(base, S3Adapter)
        adapter = (cls or base)()
        params = {
            "endpoint": self.info["endpoint"],
            "bucket": self.bucket,
            "addressing_style": "path",
            "create_bucket": True,
        }
        secrets = {"access_key": self.info["access_key"], "secret_key": self.info["secret_key"]}
        await adapter.open(
            ResolvedConnection(f"recovery-{self.kind}", self.kind, params, secrets),
            {"prefix": PREFIX, **options},
        )
        await adapter.ensure_schema(["product"])
        self.opened.append(adapter)
        return adapter

    def engine(self, adapter: S3Adapter) -> StorageEngine:
        return StorageEngine(adapter, connection_id=f"recovery-{self.kind}", retries=COMPAT_RETRIES)

    def get(self, key: str) -> Any:
        return json.loads(self.client.get_object(Bucket=self.bucket, Key=f"{PREFIX}/{key}")["Body"].read())

    def exists(self, key: str) -> bool:
        resp = self.client.list_objects_v2(Bucket=self.bucket, Prefix=f"{PREFIX}/{key}")
        return bool(resp.get("Contents"))

    def put(self, key: str, doc: Any) -> None:
        self.client.put_object(Bucket=self.bucket, Key=f"{PREFIX}/{key}", Body=dumps(doc))

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=f"{PREFIX}/{key}")

    async def history(self, adapter: S3Adapter) -> list[str]:
        events, _ = await adapter.list_history("product", KEY, limit=100)
        return [e.delivery_key for e in events]

    async def close(self) -> None:
        for adapter in self.opened:
            await adapter.close()
        resp = self.client.list_objects_v2(Bucket=self.bucket)
        for obj in resp.get("Contents", []):
            self.client.delete_object(Bucket=self.bucket, Key=obj["Key"])
        self.client.delete_bucket(Bucket=self.bucket)


@pytest.fixture(params=["s3", "minio"])
async def env(request: pytest.FixtureRequest) -> AsyncIterator[Env]:
    kind = str(request.param)
    stack = load_stack()
    if stack is None or kind not in stack.services:
        pytest.skip(f"dev stack with {kind} is not running (just up {kind})")
    e = Env(kind, stack.services[kind])
    try:
        yield e
    finally:
        await e.close()


def event_for(rec: dict[str, Any], delivery_key: str, applied: list[str]) -> HistoryEvent:
    return HistoryEvent("product", KEY, rec, delivery_key, datetime.now(UTC), applied, [])


def claim(delivery_key: str, version: int, claimed_at: datetime) -> dict[str, Any]:
    return {
        "delivery_key": delivery_key,
        "recorded_at": format_ts(claimed_at),
        "claimed_at": format_ts(claimed_at),
        "claim_id": uuid.uuid4().hex,
        "acks": [{"entity": {"entity_type": "product", "canonical_key": KEY, "version": version}}],
    }


class Hooked(S3Adapter):
    """``S3Adapter`` whose ``_put`` calls ``hook(key, kwargs, real_put)`` — the hook decides what happens."""

    hook: Callable[[str, dict[str, Any], Callable[[], str | None]], str | None] | None = None

    def _put(self, key: str, body: bytes, **kwargs: Any) -> str | None:
        def real() -> str | None:
            return S3Adapter._put(self, key, body, **kwargs)

        hook = type(self).hook
        return real() if hook is None else hook(key, kwargs, real)


def hooked(
    kind: str, hook: Callable[[str, dict[str, Any], Callable[[], str | None]], str | None]
) -> type[S3Adapter]:
    base = adapter_class(kind)
    return type("HookedAdapter", (Hooked, base), {"hook": staticmethod(hook), "kind": kind})


# ---------------------------------------------------------------------------------- crash leftovers
async def test_claim_of_a_commit_in_flight_conflicts_and_a_stale_one_is_removed(env: Env) -> None:
    adapter = await env.adapter(lock_stale_ms=60_000)
    rec = record(at=0)
    env.put(claim_key("crash-dk#0"), claim("crash-dk#0", 1, datetime.now(UTC)))
    merged = merge(None, rec, now=datetime.now(UTC))
    # a fresh claim: its writer may still be committing → CONFLICT, nothing touched
    result = await adapter.commit_entity(
        new=merged.snapshot, expected_version=None, event=event_for(rec, "crash-dk#0", merged.applied)
    )
    assert result.outcome is CommitOutcome.CONFLICT
    assert env.exists(claim_key("crash-dk#0"))
    assert await adapter.get_delivery("crash-dk#0") is None
    assert await adapter.read_entity("product", KEY) is None
    # the same claim older than lock_stale_ms: a crashed writer → removed, the delivery is written
    env.put(claim_key("crash-dk#0"), claim("crash-dk#0", 1, datetime.now(UTC) - timedelta(minutes=5)))
    ack = await env.engine(adapter).store_entity(rec, "crash-dk#0")
    assert ack["status"] == "written"
    assert (await adapter.get_delivery("crash-dk#0")) is not None


async def test_claim_that_lost_the_race_is_dead_at_once(env: Env) -> None:
    adapter = await env.adapter()
    engine = env.engine(adapter)
    await engine.store_entity(record(at=0), "winner#0")
    # a claim for version 1 by another key: the snapshot is at version 1 by "winner" → the claim is dead
    env.put(claim_key("loser#0"), claim("loser#0", 1, datetime.now(UTC)))
    assert await adapter.get_delivery("loser#0") is None
    ack = await engine.store_entity(record(fields={"price": 1.0}, at=1), "loser#0")
    assert ack["status"] == "written"
    assert ack["entity"]["version"] == 2


async def test_pending_history_event_is_rolled_forward(env: Env) -> None:
    adapter = await env.adapter()
    engine = env.engine(adapter)
    await engine.store_entity(record(at=0), "p-a#0")
    await engine.store_entity(record(fields={"price": 2.0}, at=1), "p-b#0")
    # state after a crash between the snapshot CAS and the roll-forward of version 2
    snap = env.get(SNAP)
    snap["pending"] = env.get(hist(2))
    env.put(SNAP, snap)
    env.delete(hist(2))
    assert (await adapter.get_delivery("p-b#0")) is not None  # complete: the event is in the snapshot
    assert await env.history(adapter) == ["p-b#0", "p-a#0"]
    assert env.get(hist(2))["delivery_key"] == "p-b#0"  # rolled forward by the reader
    assert "pending" not in env.get(SNAP)
    ack = await engine.store_entity(record(fields={"price": 3.0}, at=2), "p-c#0")
    assert ack["entity"]["version"] == 3


# ---------------------------------------------------------------------------------- ambiguous responses
def retried_after_success(
    target: str,
) -> Callable[[str, dict[str, Any], Callable[[], str | None]], str | None]:
    """The first conditional PUT of ``target`` is applied, its response 'lost' and the request repeated
    (what botocore's ``standard`` retry does after a read timeout / 5xx): the caller sees the retry's result."""
    done: list[bool] = []

    def hook(key: str, kwargs: dict[str, Any], real: Callable[[], str | None]) -> str | None:
        conditional = kwargs.get("create") or kwargs.get("if_match") is not None
        if key.endswith(target) and conditional and not done:
            done.append(True)
            assert real() is not None  # applied on the server
            return real()  # the retry: 412 against our own write → None
        return real()

    return hook


@pytest.mark.parametrize("version", [1, 2])
async def test_snapshot_cas_applied_but_answered_412_is_committed_once(env: Env, version: int) -> None:
    plain = await env.adapter()
    if version == 2:
        await env.engine(plain).store_entity(record(at=0), "base#0")
    adapter = await env.adapter(hooked(env.kind, retried_after_success(SNAP)))
    rec = record(fields={"price": 5.0}, at=5)
    ack = await env.engine(adapter).store_entity(rec, "K#0")
    assert ack["status"] == "written"
    assert ack["entity"]["version"] == version
    assert env.exists(claim_key("K#0"))  # the claim is kept: the delivery is committed
    assert (await plain.get_delivery("K#0")) is not None
    expected = ["K#0"] if version == 1 else ["K#0", "base#0"]
    assert await env.history(plain) == expected
    again = await env.engine(plain).store_entity(rec, "K#0")
    assert again["status"] == "duplicate"
    assert await env.history(plain) == expected


async def test_ambiguous_cas_recovery_never_rolls_back_a_newer_snapshot(env: Env) -> None:
    """Review 2: A's CAS of version 2 (K#0) is applied, the response lost; before botocore's retry
    answers 412, instance B commits version 3 (OTHER#0) and does not roll it forward (crash / still
    running). A's recovery finds its event in the history of version 2 — and must not write anything
    over version 3: final version 3, history OTHER#0, K#0, base#0, OTHER#0 delivered."""
    plain = await env.adapter()
    await env.engine(plain).store_entity(record(at=0), "base#0")
    other = record(fields={"title": "other"}, at=6, obs="obs_other")

    def no_own_roll_forward(self: S3Adapter, doc: Any, etag: str) -> str | None:
        pending = doc.get("pending")
        if isinstance(pending, dict) and pending.get("delivery_key") == "OTHER#0":
            return None  # B's own commit stays pending (B crashed right after its CAS)
        return S3Adapter._roll_forward(self, doc, etag)

    b_cls = type("NoRollForwardB", (adapter_class(env.kind),), {"_roll_forward": no_own_roll_forward})
    b = await env.adapter(b_cls)
    b_results: list[CommitResult] = []

    def b_commits() -> None:
        current = b._read_entity("product", KEY)
        assert current is not None and current.version == 2
        merged = merge(current, other, now=datetime.now(UTC))
        b_results.append(b._commit(merged.snapshot, 2, event_for(other, "OTHER#0", merged.applied)))

    done: list[bool] = []

    def hook(key: str, kwargs: dict[str, Any], real: Callable[[], str | None]) -> str | None:
        if key.endswith(SNAP) and kwargs.get("if_match") is not None and not done:
            done.append(True)
            assert real() is not None  # A's CAS of version 2 is applied on the server
            b_commits()  # B commits version 3 between the lost response and the retry
            return real()  # the retry: 412
        return real()

    a = await env.adapter(hooked(env.kind, hook))
    ack = await env.engine(a).store_entity(record(fields={"price": 5.0}, at=5), "K#0")
    assert ack["status"] == "written"
    assert ack["entity"]["version"] == 2
    assert [r.outcome for r in b_results] == [CommitOutcome.COMMITTED]
    snap = await plain.read_entity("product", KEY)
    assert snap is not None and snap.version == 3
    assert snap.fields["title"] == "other" and snap.fields["price"] == 5.0
    assert await env.history(plain) == ["OTHER#0", "K#0", "base#0"]
    assert (await plain.get_delivery("OTHER#0")) is not None
    assert (await plain.get_delivery("K#0")) is not None


async def test_claim_applied_but_answered_412_is_ours(env: Env) -> None:
    adapter = await env.adapter(hooked(env.kind, retried_after_success(claim_key("K#0"))))
    ack = await env.engine(adapter).store_entity(record(at=0), "K#0")
    assert ack["status"] == "written"
    assert await env.history(adapter) == ["K#0"]


async def test_object_delivery_applied_but_answered_412_is_recorded(env: Env) -> None:
    from jane_contracts.storage_adapter import DeliveryRecord

    adapter = await env.adapter(hooked(env.kind, retried_after_success(claim_key("obj-dk"))))
    rec = DeliveryRecord("obj-dk", datetime.now(UTC), [{"note": "no object ack"}])
    assert await adapter.record_delivery(rec) is True
    assert await adapter.record_delivery(rec) is False


# ---------------------------------------------------------------------------------- same key, two instances
async def test_same_key_second_instance_inside_the_first_commit(env: Env) -> None:
    """B commits the same delivery key while A is between its claim and its CAS, then after A's CAS
    before A's roll-forward: B never applies the delivery a second time and never removes A's claim."""
    b = await env.adapter()
    base = await env.engine(b).store_entity(record(at=0), "base#0")
    assert base["status"] == "written"
    current = await b.read_entity("product", KEY)
    assert current is not None
    rec = record(fields={"price": 7.0}, at=5)
    merged = merge(current, rec, now=datetime.now(UTC))
    outcomes: dict[str, CommitResult] = {}

    def b_commit(label: str) -> None:
        outcomes[label] = b._commit(merged.snapshot, 1, event_for(rec, "K#0", merged.applied))

    def hook(key: str, kwargs: dict[str, Any], real: Callable[[], str | None]) -> str | None:
        if key.endswith(SNAP) and kwargs.get("if_match") is not None and "before_cas" not in outcomes:
            b_commit("before_cas")  # A has claimed K#0, its CAS has not happened yet
            result = real()
            b_commit("after_cas")  # A's CAS is done, the roll-forward has not happened yet
            return result
        return real()

    a = await env.adapter(hooked(env.kind, hook))
    result = await a.commit_entity(
        new=merged.snapshot, expected_version=1, event=event_for(rec, "K#0", merged.applied)
    )
    assert result.outcome is CommitOutcome.COMMITTED
    assert outcomes["before_cas"].outcome is CommitOutcome.CONFLICT  # A's claim is in flight
    assert outcomes["after_cas"].outcome is CommitOutcome.DUPLICATE  # found in A's pending
    assert env.exists(claim_key("K#0"))
    assert await env.history(b) == ["K#0", "base#0"]
    again = await env.engine(b).store_entity(rec, "K#0")  # the core's retry of B
    assert again["status"] == "duplicate"
    assert await env.history(b) == ["K#0", "base#0"]


async def test_compensation_removes_only_its_own_claim(env: Env) -> None:
    """A loses the CAS; before A compensates, its claim was replaced by another writer's claim (e.g. the
    stale-claim cleanup of a third instance followed by a new claim): A must not delete it."""
    plain = await env.adapter()
    await env.engine(plain).store_entity(record(at=0), "base#0")
    current = await plain.read_entity("product", KEY)
    assert current is not None
    rec = record(fields={"price": 9.0}, at=9)
    merged = merge(current, rec, now=datetime.now(UTC))
    foreign = claim("K#0", 2, datetime.now(UTC))

    def hook(key: str, kwargs: dict[str, Any], real: Callable[[], str | None]) -> str | None:
        if key.endswith(SNAP) and kwargs.get("if_match") is not None:
            # another writer moved the snapshot on (A will get 412) and re-claimed K#0 meanwhile
            snap = env.get(SNAP)
            snap["version"] = int(snap["version"]) + 1
            env.put(SNAP, snap)
            env.put(claim_key("K#0"), foreign)
        return real()

    a = await env.adapter(hooked(env.kind, hook))
    result = await a.commit_entity(
        new=merged.snapshot, expected_version=1, event=event_for(rec, "K#0", merged.applied)
    )
    assert result.outcome is CommitOutcome.CONFLICT
    assert env.get(claim_key("K#0"))["claim_id"] == foreign["claim_id"]  # not deleted by A
