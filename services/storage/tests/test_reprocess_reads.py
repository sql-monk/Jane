"""Reads for reprocessing and the storage limits of WP-17 (R06, R01 format.raw, R19, R14, R21).

Real filesystem adapter, real core and HTTP app; no external services.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from jane_contracts.storage_adapter import CommitOutcome, CommitResult
from jane_kit.clients import RetryPolicy
from jane_kit.contracts import OpenAPISpec
from jane_storage import connections as connections_module
from jane_storage.app import build_app
from jane_storage.connections import AdapterPool, ConnectionRegistry
from jane_storage.engine import ConflictRetriesExhausted, StorageEngine
from jane_storage.settings import ConflictRetries, Settings, resolve_service_limits

CONTRACTS = Path(__file__).resolve().parents[3] / "contracts"
STORAGE_SPEC = OpenAPISpec.load(CONTRACTS / "openapi" / "storage.v1.yaml")


def _store(client: TestClient, h: SimpleNamespace, material: dict[str, Any], key: str) -> dict[str, Any]:
    result = h.post(client, h.invocation([{"kind": "material", "material": material}], key)).json()
    assert result["status"] == "success", result
    ack: dict[str, Any] = result["output"]["writes"][0]
    return ack


def _all_pages(client: TestClient, params: Mapping[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    cursor = None
    for _ in range(50):
        query = dict(params)
        if cursor:
            query["cursor"] = cursor
        r = client.get("/v1/objects", params=query)
        assert r.status_code == 200, r.text
        STORAGE_SPEC.validate_response("get", "/v1/objects", 200, r.json(), "application/json")
        items += r.json()["items"]
        cursor = r.json()["next_cursor"]
        if cursor is None:
            return items
    raise AssertionError("pagination did not end")


# ------------------------------------------------------------------ R06: several material_id values
def test_objects_filter_by_several_material_ids_pages_without_gaps(
    client: TestClient, h: SimpleNamespace
) -> None:
    stored: dict[str, list[str]] = {}
    for n in range(5):
        mid = f"web:{n:032x}"
        for obs in range(2 if n == 2 else 1):  # material 2 has two stored observations
            page = h.PAGE.replace(b"1299", f"{n}{obs}".encode())
            ack = _store(
                client, h, h.material(page, material_id=mid, observation_id=f"obs_{n}_{obs}"), f"dk-{n}-{obs}"
            )
            stored.setdefault(mid, []).append(ack["object"]["object_id"])
    wanted = [f"web:{n:032x}" for n in (4, 2, 0)]
    params: dict[str, Any] = {"connection_id": "raw-files", "material_ids": wanted[1:], "limit": 1}
    params["material_id"] = wanted[0]  # the single-value filter joins the list (union)
    items = _all_pages(client, params)
    ids = [i["object"]["object_id"] for i in items]
    assert sorted(ids) == sorted(oid for mid in wanted for oid in stored[mid])
    assert len(ids) == len(set(ids)) == 4  # every object once, also across pages of one material
    assert {i["material"]["material_id"] for i in items} == set(wanted)
    # one id via material_ids behaves like material_id
    one = _all_pages(client, {"connection_id": "raw-files", "material_ids": [wanted[1]]})
    assert sorted(i["object"]["object_id"] for i in one) == sorted(stored[wanted[1]])
    # filters still apply to every id
    other = _all_pages(client, {"connection_id": "raw-files", "material_ids": wanted, "source_id": "other"})
    assert other == []


def test_material_ids_filter_has_a_configured_cap_and_a_strict_cursor(
    settings: Settings, h: SimpleNamespace, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("JANE_STORAGE_LIMITS__OBJECTS__MAX_FILTER_MATERIAL_IDS", "2")
    with TestClient(build_app(settings)) as c:
        r = c.get("/v1/objects", params={"connection_id": "raw-files", "material_ids": ["a", "b", "c"]})
        assert r.status_code == 422 and r.json()["code"] == "limit_exceeded", r.text
        ok = c.get("/v1/objects", params={"connection_id": "raw-files", "material_ids": ["a", "b"]})
        assert ok.status_code == 200 and ok.json() == {"items": [], "next_cursor": None}
        bad = c.get(
            "/v1/objects", params={"connection_id": "raw-files", "material_ids": ["a", "b"], "cursor": "nope"}
        )
        assert bad.status_code == 422 and bad.json()["code"] == "validation_failed", bad.text


# ------------------------------------------------------------------ R01: RAW stored as a JSON document
def test_json_format_raw_is_restored_with_its_original_content(
    client: TestClient, h: SimpleNamespace
) -> None:
    """TZ §5 default stores a non-page RAW as the JSON document of the Material; reprocessing must get the
    original content back, not the wrapper document."""
    material = json.loads(
        (CONTRACTS / "examples" / "schemas" / "material" / "telegram-message-edit.json").read_text(
            encoding="utf-8"
        )
    )
    ack = _store(client, h, material, "dk-tg-restore")
    assert ack["object"]["media_type"] == "application/json"
    detail = client.get(f"/v1/objects/{ack['object']['object_id']}", params={"connection_id": "raw-files"})
    assert detail.status_code == 200
    body = detail.json()
    STORAGE_SPEC.validate_response("get", "/v1/objects/{object_id}", 200, body, "application/json")
    restored = body["material"]
    original = material["content"]["data"].encode("utf-8")
    assert restored["content"]["kind"] == "inline"
    assert restored["content"]["data"] == material["content"]["data"]
    assert restored["content"]["media_type"] == material["content"]["media_type"]
    assert restored["content"]["sha256"] == hashlib.sha256(original).hexdigest()
    assert restored["content"]["size_bytes"] == len(original)
    assert restored["format"] == material["format"]
    assert {k: v for k, v in restored.items() if k != "content"} == {
        k: v for k, v in material.items() if k != "content"
    }


def test_json_format_raw_larger_than_inline_is_not_offered_for_reprocessing(
    settings: Settings, h: SimpleNamespace, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("JANE_STORAGE_LIMITS__TRANSFER__INLINE_MAX_BYTES", "16")
    with TestClient(build_app(settings)) as c:
        mat = h.material(b'{"long": "' + b"x" * 64 + b'"}', media_type="application/json")
        ack = _store(c, h, mat, "dk-json-big")
        body = c.get(
            f"/v1/objects/{ack['object']['object_id']}", params={"connection_id": "raw-files"}
        ).json()
        assert "material" not in body  # no persistent URI of the original bytes, and too big to inline
        assert body["object"]["object_id"] == ack["object"]["object_id"]


# ------------------------------------------------------------------ R19: from_stage -> storage
def _two_files_settings(tmp_path: Path, storage_dir: Path, content_dir: Path | None) -> Settings:
    conn_file = tmp_path / "connections-r19.json"
    conn_file.write_text(
        json.dumps(
            {
                "connections": [
                    {
                        "connection_id": "raw-files",
                        "kind": "filesystem",
                        "params": {"base_path": str(storage_dir)},
                    },
                    {
                        "connection_id": "copy-files",
                        "kind": "filesystem",
                        "params": {"base_path": str(tmp_path / "copy")},
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    return Settings(log_format="console", connections_file=conn_file, content_files_dir=content_dir)


def test_stored_raw_with_persistent_file_uri_can_be_stored_again(
    tmp_path: Path, storage_dir: Path, h: SimpleNamespace
) -> None:
    """Reprocessing with ``from_stage`` = a storage stage hands storage the restored Material as is (ADR-0004
    §6). With ``JANE_STORAGE_CONTENT_FILES_DIR`` = the files adapter's ``objects`` root (the base stack's
    setting) storage reads its own persistent RAW; nothing outside that root."""
    settings = _two_files_settings(tmp_path, storage_dir, storage_dir / "objects")
    with TestClient(build_app(settings)) as c:
        ack = _store(c, h, h.material(), "dk-r19-first")
        restored = c.get(f"/v1/objects/{ack['object']['object_id']}", params={"connection_id": "raw-files"})
        material = restored.json()["material"]
        assert material["content"]["uri"].startswith("file://")
        assert material["content"]["store"] == "persistent"
        again = h.post(
            c, h.invocation([{"kind": "material", "material": material}], "dk-r19-again", target="copy-files")
        ).json()
        assert again["status"] == "success", again
        copy = again["output"]["writes"][0]
        assert (tmp_path / "copy" / copy["object"]["locator"]["path"]).read_bytes() == h.PAGE
        assert copy["object"]["sha256"] == ack["object"]["sha256"]
        # the same connection again: the object key and bytes are equal, nothing is duplicated
        same = h.post(c, h.invocation([{"kind": "material", "material": material}], "dk-r19-same")).json()
        assert same["status"] == "success" and same["output"]["writes"][0]["object"] == ack["object"]
        # a file:// outside the objects root is still refused (e.g. the adapter's own delivery records)
        outside = {
            **material,
            "content": {**material["content"], "uri": (storage_dir / "deliveries").as_uri() + "/x.json"},
        }
        refused = h.post(c, h.invocation([{"kind": "material", "material": outside}], "dk-r19-out")).json()
        assert refused["status"] == "failed" and refused["failure"]["retryable"] is False


def test_without_content_files_dir_persistent_file_raw_is_refused(
    tmp_path: Path, storage_dir: Path, h: SimpleNamespace
) -> None:
    settings = _two_files_settings(tmp_path, storage_dir, None)
    with TestClient(build_app(settings)) as c:
        ack = _store(c, h, h.material(), "dk-r19-off")
        material = c.get(
            f"/v1/objects/{ack['object']['object_id']}", params={"connection_id": "raw-files"}
        ).json()["material"]
        result = h.post(
            c, h.invocation([{"kind": "material", "material": material}], "dk-r19-off2", target="copy-files")
        ).json()
        assert result["status"] == "failed"
        assert "local blob reading is disabled" in result["failure"]["message"]


# ------------------------------------------------------------------ R14: CONFLICT backoff from configuration
def test_conflict_retries_come_only_from_the_service_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    assert resolve_service_limits(Settings(log_format="console")).limits.conflict_retries == ConflictRetries()
    assert ConflictRetries() == ConflictRetries.model_validate(RetryPolicy().model_dump())  # same as before
    monkeypatch.setenv("JANE_STORAGE_LIMITS__CONFLICT_RETRIES__MAX_ATTEMPTS", "7")
    monkeypatch.setenv("JANE_STORAGE_LIMITS__CONFLICT_RETRIES__INITIAL_BACKOFF_MS", "5")
    monkeypatch.setenv("JANE_STORAGE_LIMITS__CONFLICT_RETRIES__MAX_BACKOFF_MS", "40")
    settings = Settings(log_format="console")
    lim = resolve_service_limits(settings).limits.conflict_retries
    assert (lim.max_attempts, lim.initial_backoff_ms, lim.max_backoff_ms) == (7, 5, 40)
    # the stage's retries in HandlerInvocation.limits never reach the core
    with TestClient(build_app(settings)) as c:
        assert c.app.state.limits.limits.conflict_retries == lim  # type: ignore[attr-defined]


class _AlwaysConflict:
    """Adapter whose commits always lose the race (a hot entity under concurrent writers)."""

    kind = "fake"

    def __init__(self) -> None:
        self.commits = 0

    async def get_delivery(self, delivery_key: str) -> None:
        return None

    async def read_entity(self, entity_type: str, key: str) -> None:
        return None

    async def commit_entity(self, **_: Any) -> CommitResult:
        self.commits += 1
        return CommitResult(CommitOutcome.CONFLICT, None)


async def test_core_retries_conflicts_with_the_configured_backoff(h: SimpleNamespace) -> None:
    policy = ConflictRetries(max_attempts=5, initial_backoff_ms=10, max_backoff_ms=25, jitter=False)
    adapter = _AlwaysConflict()
    sleeps: list[float] = []

    async def sleep(seconds: float) -> None:
        sleeps.append(seconds)

    engine = StorageEngine(adapter, retries=policy, sleep=sleep)  # type: ignore[arg-type]
    with pytest.raises(ConflictRetriesExhausted) as err:
        await engine.store_entity(h.entity(), "dk-hot#0")
    assert err.value.retryable is True
    assert adapter.commits == 5
    assert sleeps == [0.01, 0.02, 0.025, 0.025]  # initial * 2^n, capped by max_backoff_ms


# ------------------------------------------------------------------ R21: adapters.chunk_bytes / retry_max_attempts
def test_service_wide_adapter_defaults_yield_to_connection_params(
    settings: Settings, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    opened: list[dict[str, Any]] = []

    class Recording:
        kind = "filesystem"

        async def open(self, connection: Any, options: Mapping[str, Any]) -> None:
            opened.append(dict(options))

        async def ensure_schema(self, entity_types: Any) -> None:
            return None

        async def close(self) -> None:
            return None

    monkeypatch.setattr(connections_module, "create_adapter", lambda kind: Recording())
    monkeypatch.setenv("JANE_STORAGE_LIMITS__ADAPTERS__CHUNK_BYTES", "2048")
    monkeypatch.setenv("JANE_STORAGE_LIMITS__ADAPTERS__RETRY_MAX_ATTEMPTS", "6")
    lim = resolve_service_limits(Settings(log_format="console")).limits.adapters
    assert (lim.chunk_bytes, lim.retry_max_attempts) == (2048, 6)

    registry = ConnectionRegistry()
    registry.put(
        {"connection_id": "plain", "kind": "filesystem", "params": {"base_path": str(tmp_path / "a")}}
    )
    registry.put(
        {
            "connection_id": "own",
            "kind": "filesystem",
            "params": {"base_path": str(tmp_path / "b"), "chunk_bytes": 512},
        }
    )
    from jane_storage.settings import CONNECTION_FIRST_OPTIONS

    pool = AdapterPool(registry, lim.model_dump(exclude_none=True), connection_first=CONNECTION_FIRST_OPTIONS)

    import asyncio

    async def open_both() -> None:
        await pool.adapter_for("plain", "filesystem", {})
        await pool.adapter_for("own", "filesystem", {"prefix": "p"})

    asyncio.run(open_both())
    plain, own = opened
    assert plain["chunk_bytes"] == 2048 and plain["retry_max_attempts"] == 6
    assert "chunk_bytes" not in own  # the connection's params.chunk_bytes (512) applies in the adapter
    assert own["retry_max_attempts"] == 6 and own["prefix"] == "p"
    assert plain["lock_timeout_ms"] == own["lock_timeout_ms"] == 30_000  # other options unchanged
    # without the settings the adapters keep their own defaults (no None leaks into open())
    monkeypatch.delenv("JANE_STORAGE_LIMITS__ADAPTERS__CHUNK_BYTES")
    monkeypatch.delenv("JANE_STORAGE_LIMITS__ADAPTERS__RETRY_MAX_ATTEMPTS")
    default = resolve_service_limits(Settings(log_format="console")).limits.adapters
    assert {"chunk_bytes", "retry_max_attempts"}.isdisjoint(default.model_dump(exclude_none=True))
