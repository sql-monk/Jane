"""Tests of scripts/migrate_news_to_pg.py.

Unit tests run the script's logic with filesystem storage adapters (a real implementation of the adapter protocol)
in place of both sources and the target. The integration test (marker ``integration``) runs the script's CLI against
a dev stack with PostgreSQL and MongoDB, each run in its own schemas and database:

    just up --project news-b postgres mongodb
    just integration --project news-b scripts/tests/test_migrate_news_to_pg.py
    just down --project news-b -v
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import uuid
from collections import Counter
from collections.abc import AsyncIterator, Mapping
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from jane_contracts.storage_adapter import (
    AdapterError,
    CommitResult,
    EntitySnapshot,
    HistoryEvent,
    OrderKey,
    ResolvedConnection,
)
from jane_kit.devstack import find_repo_root, load_stack
from jane_storage.engine import StorageEngine
from jane_storage.keys import canonical_key
from jane_storage_files import FilesystemAdapter

SPEC = importlib.util.spec_from_file_location(
    "jane_migrate_news_to_pg", Path(__file__).parents[1] / "migrate_news_to_pg.py"
)
assert SPEC and SPEC.loader
mig = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mig
SPEC.loader.exec_module(mig)

T0 = datetime(2026, 10, 1, 8, 0, tzinfo=UTC)


def natural_key(entity_type: str, n: int) -> dict[str, Any]:
    """Natural key of the n-th test entity of a type (shaped like the live ones)."""
    if entity_type == "post":
        return {"channel": "chan", "message_id": 1000 + n}
    if entity_type == "news_event":
        return {"event_id": f"news-event-{n}"}
    return {"url": f"https://{entity_type}.example/{n}"}


def at(minutes: float) -> datetime:
    return T0 + timedelta(minutes=minutes)


def news(
    entity_type: str,
    n: int,
    *,
    fields: dict[str, Any] | None = None,
    observed: float,
    obs: str,
    cleared: tuple[str, ...] = (),
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "entity_type": entity_type,
        "key": {"scope": f"scope-{entity_type}", "natural": natural_key(entity_type, n)},
        "fields": dict(fields or {}),
        "observation": {
            "observation_id": obs,
            "observed_at": at(observed).isoformat().replace("+00:00", "Z"),
        },
    }
    if cleared:
        record["cleared"] = list(cleared)
    return record


def key_of(record: dict[str, Any]) -> str:
    return canonical_key(record["key"])


async def store(adapter: Any, record: dict[str, Any], delivery_key: str, received: float) -> str:
    engine = StorageEngine(adapter, clock=mig.fixed_clock(at(received)))
    return str((await engine.store_entity(record, delivery_key))["status"])


async def open_files(path: Path, cls: type[FilesystemAdapter] = FilesystemAdapter) -> FilesystemAdapter:
    adapter = cls()
    await adapter.open(
        ResolvedConnection(connection_id=path.name, kind="filesystem", params={"base_path": str(path)}), {}
    )
    return adapter


@pytest.fixture
async def stores(tmp_path: Path) -> AsyncIterator[dict[str, FilesystemAdapter]]:
    out = {name: await open_files(tmp_path / name) for name in ("legacy-pg", "mongo", "target")}
    yield out
    for adapter in out.values():
        await adapter.close()


# K1 article: legacy only; K2 post: mongo only, a stale event; K3 news_article: both sources interleaved, a clear and
# a stale event; K4 news_event: both, one delivery key in both; K5 article: both, same received_at.
K1 = news("article", 1, fields={"title": "A1"}, observed=9, obs="o-k1a")
K2 = news("post", 2, fields={"text": "p", "views": 5}, observed=29, obs="o-k2a")
K3 = news("news_article", 3, fields={"headline": "old", "region": "kyiv"}, observed=10, obs="o-k3a")
K4 = news("news_event", 4, fields={"summary": "s1"}, observed=10, obs="o-k4a")
K5 = news("article", 5, fields={"title": "legacy"}, observed=80, obs="o-k5-l")


async def seed(s: dict[str, FilesystemAdapter]) -> None:
    legacy, mongo = s["legacy-pg"], s["mongo"]
    await store(legacy, K1, "L1#0", 10)
    await store(legacy, news("article", 1, fields={"title": "A1 v2"}, observed=19, obs="o-k1b"), "L2#0", 20)
    await store(mongo, K2, "M1#0", 30)
    await store(mongo, news("post", 2, fields={"views": 7}, observed=39, obs="o-k2b"), "M2#0", 40)
    assert (
        await store(mongo, news("post", 2, fields={"views": 6}, observed=35, obs="o-k2c"), "M3#0", 50)
        == "stale"
    )
    await store(legacy, K3, "L3#0", 10)
    await store(
        mongo,
        news("news_article", 3, fields={"headline": "new", "sentiment": "neg"}, observed=30, obs="o-k3b"),
        "M4#0",
        30,
    )
    await store(legacy, news("news_article", 3, cleared=("region",), observed=60, obs="o-k3c"), "L4#0", 60)
    await store(
        mongo, news("news_article", 3, fields={"headline": "older"}, observed=20, obs="o-k3d"), "M5#0", 70
    )
    await store(legacy, K4, "E1#0", 10)
    await store(mongo, K4, "E1#0", 10)
    await store(mongo, news("news_event", 4, fields={"summary": "s2"}, observed=20, obs="o-k4b"), "E2#0", 20)
    await store(legacy, K5, "T1#0", 80)
    await store(mongo, news("article", 5, fields={"title": "mongo"}, observed=80, obs="o-k5-m"), "T2#0", 80)


async def run_migrate(
    s: dict[str, FilesystemAdapter], types: tuple[str, ...] = mig.NEWS_TYPES, **kwargs: Any
) -> Any:
    sources = {"legacy-pg": s["legacy-pg"], "mongo": s["mongo"]}
    return await mig.migrate(sources, s["target"], types=types, out=lambda _: None, **kwargs)


async def run_verify(s: dict[str, FilesystemAdapter], **kwargs: Any) -> Any:
    sources = {"legacy-pg": s["legacy-pg"], "mongo": s["mongo"]}
    return await mig.verify(sources, s["target"], types=mig.NEWS_TYPES, **kwargs)


def ev(delivery_key: str, minutes: float) -> HistoryEvent:
    return HistoryEvent(
        entity_type="article",
        canonical_key="k",
        record={"delivery": delivery_key},
        delivery_key=delivery_key,
        received_at=at(minutes),
        applied_fields=[],
        stale_fields=[],
    )


def snap(
    fields: dict[str, Any], orders: dict[str, float], cleared: tuple[str, ...] = (), version: int = 1
) -> EntitySnapshot:
    return EntitySnapshot(
        entity_type="article",
        canonical_key="k",
        key={"scope": "s", "natural": {"url": "u"}},
        fields=fields,
        field_orders={n: OrderKey(observed_at=at(m), observation_id=f"o{m}") for n, m in orders.items()},
        cleared_fields=frozenset(cleared),
        version=version,
        updated_at=T0,
    )


# ----------------------------------------------------------------------------- pure logic
def test_replay_order_interleaves_sources_by_received_at_then_source_then_version() -> None:
    streams = {
        "mongo": [ev("m1", 5), ev("m2", 10), ev("m3", 10)],
        "legacy-pg": [ev("l1", 1), ev("l2", 10), ev("l3", 20)],
    }
    order = [(e.source, e.event.delivery_key) for e in mig.replay_order(streams)]
    assert order == [
        ("legacy-pg", "l1"),
        ("mongo", "m1"),
        ("legacy-pg", "l2"),  # same received_at: legacy-pg before mongo
        ("mongo", "m2"),  # same source and time: version order
        ("mongo", "m3"),
        ("legacy-pg", "l3"),
    ]


def test_repeated_deliveries_counts_keys_seen_in_both_sources() -> None:
    differing = replace(ev("k2", 2), record={"x": 1})
    events = mig.replay_order({"legacy-pg": [ev("k1", 1), ev("k2", 2)], "mongo": [ev("k1", 1), differing]})
    assert mig.repeated_deliveries(events) == (2, 1)


def test_plan_keys_groups_sources_by_target_key() -> None:
    a = snap({"title": "x"}, {"title": 1})
    b = replace(a, key={"scope": "s", "natural": {"url": "v"}})
    plans = mig.plan_keys("article", {"mongo": [a, b], "legacy-pg": [a]})
    assert {p.origin for p in plans.values()} == {"both", "mongo"}
    both = plans[canonical_key(a.key)]
    assert list(both.sources) == ["legacy-pg", "mongo"]
    with pytest.raises(ValueError, match="unknown sources"):
        mig.plan_keys("article", {"sqlserver": [a]})


def test_state_differences_takes_the_newest_order_of_every_field() -> None:
    legacy = snap({"title": "new", "region": "kyiv"}, {"title": 30, "region": 10})
    mongo = snap({"title": "old", "lead": "l"}, {"title": 20, "lead": 5, "region": 40}, cleared=("region",))
    merged = snap({"title": "new", "lead": "l"}, {"title": 30, "lead": 5, "region": 40}, cleared=("region",))
    assert mig.state_differences([legacy, mongo], merged) == []
    assert mig.state_differences([legacy], legacy) == []
    wrong_value = snap(
        {"title": "old", "lead": "l"}, {"title": 30, "lead": 5, "region": 40}, cleared=("region",)
    )
    assert mig.state_differences([legacy, mongo], wrong_value) == ["fields: title"]
    wrong_order = snap(
        {"title": "new", "lead": "l"}, {"title": 31, "lead": 5, "region": 40}, cleared=("region",)
    )
    assert mig.state_differences([legacy, mongo], wrong_order) == ["field_orders: title"]
    not_cleared = snap(
        {"title": "new", "lead": "l", "region": "kyiv"}, {"title": 30, "lead": 5, "region": 40}
    )
    extra = snap(
        {"title": "new", "lead": "l", "x": 1}, {"title": 30, "lead": 5, "region": 40, "x": 1}, ("region",)
    )
    assert mig.state_differences([legacy, mongo], not_cleared) == ["fields: region"]
    assert mig.state_differences([legacy, mongo], extra) == ["fields: x"]


# ----------------------------------------------------------------------------- migration
async def test_migrate_replays_history_with_the_original_clock_and_is_idempotent(
    stores: dict[str, FilesystemAdapter],
) -> None:
    await seed(stores)
    target = stores["target"]
    first = await run_migrate(stores)
    assert first.ok
    totals = sum((r.statuses for r in first.types.values()), start=Counter[str]())
    assert dict(totals) == {"written": 11, "stale": 2, "duplicate": 1}
    assert first.types["news_event"].repeated_deliveries == 1
    assert first.types["news_event"].differing_repeats == 0
    assert dict(first.types["article"].keys) == {"legacy-pg": 1, "both": 1}

    k1 = await target.read_entity("article", key_of(K1))
    assert k1 is not None and k1.version == 2 and dict(k1.fields) == {"title": "A1 v2"}
    assert k1.updated_at == at(20)
    history, _ = await target.list_history("article", key_of(K1), limit=10)
    assert [(e.delivery_key, e.received_at) for e in history] == [("L2#0", at(20)), ("L1#0", at(10))]
    delivery = await target.get_delivery("L1#0")
    assert delivery is not None and delivery.recorded_at == at(10)

    k2 = await target.read_entity("post", key_of(K2))
    assert k2 is not None and k2.version == 3 and dict(k2.fields) == {"text": "p", "views": 7}
    k3 = await target.read_entity("news_article", key_of(K3))
    assert k3 is not None and k3.version == 4
    assert dict(k3.fields) == {"headline": "new", "sentiment": "neg"} and k3.cleared_fields == {"region"}
    history, _ = await target.list_history("news_article", key_of(K3), limit=10)
    assert [e.delivery_key for e in reversed(history)] == ["L3#0", "M4#0", "L4#0", "M5#0"]
    assert history[0].stale_fields == ["headline"]
    k4 = await target.read_entity("news_event", key_of(K4))
    assert k4 is not None and k4.version == 2 and dict(k4.fields) == {"summary": "s2"}
    history, _ = await target.list_history("article", key_of(K5), limit=10)
    assert [e.delivery_key for e in reversed(history)] == ["T1#0", "T2#0"]

    second = await run_migrate(stores, concurrency=1)
    assert second.ok
    totals = sum((r.statuses for r in second.types.values()), start=Counter[str]())
    assert dict(totals) == {"duplicate": 14}
    again = await target.read_entity("news_article", key_of(K3))
    assert again is not None and again.version == 4
    assert "result: OK" in mig.format_migration(second)


class FailingTarget(FilesystemAdapter):
    async def commit_entity(
        self, *, new: EntitySnapshot, expected_version: int | None, event: HistoryEvent
    ) -> CommitResult:
        if new.entity_type == "post":
            raise AdapterError("postgresql: connection refused", retryable=True)
        return await super().commit_entity(new=new, expected_version=expected_version, event=event)


async def test_migrate_reports_failed_keys_and_stops_after_max_failures(
    stores: dict[str, FilesystemAdapter], tmp_path: Path
) -> None:
    await seed(stores)
    stores["target"] = await open_files(tmp_path / "failing", FailingTarget)
    report = await run_migrate(stores)
    assert not report.ok and report.types["post"].failed_keys == 1
    assert report.failures == [f"post {key_of(K2)}: AdapterError: postgresql: connection refused"]
    assert report.types["article"].statuses["written"] == 4
    assert "failed keys: 1" in mig.format_migration(report)
    stopped = await run_migrate(stores, concurrency=1, max_failures=1, types=("post", "article"))
    assert stopped.stopped and not stopped.ok
    assert stopped.types["article"].events == 0


# ----------------------------------------------------------------------------- verification
async def test_verify_compares_states_and_finds_the_tail_missing_keys_and_live_writes(
    stores: dict[str, FilesystemAdapter],
) -> None:
    await seed(stores)
    await run_migrate(stores)

    async def projection(entity_type: str) -> Any:
        n = len((await stores["target"].list_entities(entity_type, limit=100))[0])
        return mig.ProjectionCheck(states=n, rows=n)

    report = await run_verify(stores, projection=projection)
    assert report.ok, mig.format_verify(report)
    assert report.rows[("news_event", "both")]["ok"] == 1  # version 2 = 1 + 2 - one shared delivery key
    assert report.rows[("article", "legacy-pg")]["ok"] == 1
    text = mig.format_verify(report)
    assert "result: OK" in text and "projection (canonical_key, version):" in text

    # the tail: events and keys that reached the sources after the migration
    await store(stores["mongo"], news("post", 2, fields={"views": 9}, observed=90, obs="o-k2d"), "M6#0", 90)
    await store(
        stores["legacy-pg"], news("article", 6, fields={"title": "late"}, observed=95, obs="o-k6"), "L9#0", 95
    )
    report = await run_verify(stores)
    assert not report.ok
    assert report.rows[("post", "mongo")]["mismatch"] == 1
    assert report.rows[("article", "legacy-pg")]["missing"] == 1
    assert any("version 3 != 4" in p and "fields: views" in p for p in report.problems)
    tail = await run_migrate(stores)
    totals = sum((r.statuses for r in tail.types.values()), start=Counter[str]())
    assert totals["written"] == 2 and totals["duplicate"] == 14
    assert (await run_verify(stores)).ok

    # a live write to the target after the switch is reported, not an error
    await store(
        stores["target"],
        news("article", 1, fields={"title": "live"}, observed=99, obs="o-live"),
        "LIVE#0",
        99,
    )
    await store(
        stores["target"], news("article", 7, fields={"title": "new"}, observed=99, obs="o-new"), "LIVE#1", 99
    )
    report = await run_verify(stores)
    assert report.ok
    assert report.rows[("article", "legacy-pg")]["changed_after"] == 1
    assert report.target_only["article"] == 1
    text = mig.format_verify(report)
    assert "changed after the migration" in text and "target-only keys" in text
    assert "projection: not checked" in text


async def test_verify_reports_projection_mismatch_and_missing_layout(
    stores: dict[str, FilesystemAdapter],
) -> None:
    await seed(stores)
    await run_migrate(stores)

    async def unavailable(entity_type: str) -> None:
        return None

    async def stale_row(entity_type: str) -> Any:
        if entity_type != "article":
            return mig.ProjectionCheck(states=1, rows=1)
        # same number of rows, but one of them carries an older version than its state
        return mig.ProjectionCheck(
            states=2, rows=2, only_state=1, only_rows=1, state_examples=("k1 v2",), row_examples=("k1 v1",)
        )

    missing = await run_verify(stores, projection=unavailable)
    assert not missing.ok and missing.rows[("article", "legacy-pg")]["ok"] == 1
    assert "layout unavailable" in mig.format_verify(missing)
    behind = await run_verify(stores, projection=stale_row)
    assert not behind.ok and not behind.projection["article"].ok and behind.projection["post"].ok
    text = mig.format_verify(behind, 5)
    assert "MISMATCH" in text and "result: FAILED" in text
    assert "article: state without such projection row: k1 v2" in text
    assert "article: projection row without such state: k1 v1" in text


class RecordingAdapter(FilesystemAdapter):
    """Stands in for PostgresAdapter / MongoAdapter in ``run()``: records the connection, stores in a directory."""

    base: Path
    opened: list[ResolvedConnection]

    async def open(self, connection: ResolvedConnection, options: Mapping[str, Any]) -> None:
        RecordingAdapter.opened.append(connection)
        folder = RecordingAdapter.base / connection.connection_id
        await super().open(
            ResolvedConnection(connection.connection_id, "filesystem", {"base_path": str(folder)}), {}
        )


async def test_run_opens_the_target_with_the_news_layout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    RecordingAdapter.base, RecordingAdapter.opened = tmp_path, []
    monkeypatch.setattr(mig, "PostgresAdapter", RecordingAdapter)
    monkeypatch.setattr(mig, "MongoAdapter", RecordingAdapter)
    argv = [
        "--stack-file",
        str(stack_file(tmp_path)),
        "--verify",
        "--skip-projection",
        "--target-schema",
        "news_x",
    ]
    assert await mig.amain(argv) == 0
    opened = {c.connection_id: c for c in RecordingAdapter.opened}
    assert set(opened) == {"results-pg", "results-mongo", "results-news"}
    target = opened["results-news"]
    assert (target.kind, target.params["schema"], target.params["layout"]) == ("postgresql", "news_x", "news")
    assert (target.params["database"], target.secrets["username"]) == (
        "jane_storage_results",
        "jane_storage_results",
    )
    assert opened["results-pg"].params["schema"] == "public" and "layout" not in opened["results-pg"].params


async def test_survey_counts_entities_events_and_shared_keys(stores: dict[str, FilesystemAdapter]) -> None:
    await seed(stores)
    rows = await mig.survey({"legacy-pg": stores["legacy-pg"], "mongo": stores["mongo"]}, mig.NEWS_TYPES, 2)
    by_type = {r.entity_type: r for r in rows}
    assert by_type["article"].entities == {"legacy-pg": 2, "mongo": 1}
    assert by_type["article"].events == {"legacy-pg": 3, "mongo": 1}
    assert (by_type["article"].keys, by_type["article"].both) == (2, 1)
    assert by_type["news_event"].events == {"legacy-pg": 1, "mongo": 2}
    text = mig.format_survey(rows, ["legacy-pg", "mongo"])
    assert "legacy-pg entities" in text and "in both" in text
    assert not (await stores["target"].list_entities("article", limit=10))[0]


# ----------------------------------------------------------------------------- settings
def stack_file(tmp_path: Path) -> Path:
    path = tmp_path / "stack.json"
    path.write_text(
        json.dumps(
            {
                "project": "t",
                "env": {
                    "JANE_PG_STORAGE_RESULTS_PASSWORD": "pg-from-file",
                    "JANE_MONGO_PASSWORD": "mongo-from-file",
                },
                "services": {
                    "postgres": {"host": "127.0.0.1", "port": 5501, "user": "jane"},
                    "mongodb": {"host": "127.0.0.1", "port": 5502, "user": "root-user"},
                },
            }
        ),
        encoding="utf-8",
    )
    return path


def test_settings_take_addresses_from_the_stack_file_and_passwords_from_env_or_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("JANE_PG_STORAGE_RESULTS_PASSWORD", raising=False)
    monkeypatch.setenv("JANE_MONGO_PASSWORD", "mongo-from-env")
    args = mig.build_parser().parse_args(["--stack-file", str(stack_file(tmp_path)), "--mongo-port", "6000"])
    cfg = mig.resolve_settings(args)
    assert (cfg.pg.host, cfg.pg.port, cfg.pg.user, cfg.pg.database) == (
        "127.0.0.1",
        5501,
        "jane_storage_results",
        "jane_storage_results",
    )
    assert cfg.pg.password == "pg-from-file" and cfg.mongo.password == "mongo-from-env"
    assert (cfg.mongo.port, cfg.mongo.user, cfg.mongo.database) == (6000, "root-user", "jane_results")
    assert cfg.sources == ("legacy-pg", "mongo") and cfg.types == mig.NEWS_TYPES
    assert "from-file" not in repr(cfg) and "from-env" not in repr(cfg)
    secrets = mig.pg_connection(
        cfg.pg, "news", connection_id="results-news", sslmode="disable", layout="news"
    )
    assert secrets.params["layout"] == "news" and "pg-from-file" not in repr(secrets)


def test_settings_never_take_a_password_from_argv_and_fail_without_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    parser = mig.build_parser()
    options = [o for action in parser._actions for o in action.option_strings]
    assert [o for o in options if "password" in o] == ["--pg-password-env", "--mongo-password-env"]
    monkeypatch.delenv("JANE_TEST_NO_SUCH_PASSWORD", raising=False)
    args = parser.parse_args(
        ["--stack-file", str(stack_file(tmp_path)), "--pg-password-env", "JANE_TEST_NO_SUCH_PASSWORD"]
    )
    with pytest.raises(mig.ConfigError, match="JANE_TEST_NO_SUCH_PASSWORD"):
        mig.resolve_settings(args)
    same = parser.parse_args(["--stack-file", str(stack_file(tmp_path)), "--target-schema", "public"])
    with pytest.raises(mig.ConfigError, match="must differ"):
        mig.resolve_settings(same)
    mongo_only = parser.parse_args(
        ["--stack-file", str(stack_file(tmp_path)), "--source", "mongo", "--dry-run"]
    )
    cfg = mig.resolve_settings(mongo_only)
    assert cfg.pg is None and cfg.sources == ("mongo",)
    with pytest.raises(SystemExit):
        parser.parse_args(["--types", "article,product"])
    assert mig.main(["--stack-file", str(tmp_path / "absent.json")]) == 2


# ----------------------------------------------------------------------------- integration
def _stack_file_path(project: str) -> Path:
    env_file = os.environ.get("JANE_STACK_FILE")
    return Path(env_file) if env_file else find_repo_root() / ".jane" / f"stack-{project}.json"


SEED_FIELDS: dict[str, list[dict[str, Any]]] = {
    "article": [
        {"url": "{url}", "title": "Title", "text": "Body", "site": "site.example", "tags": ["a", "b"],
         "published_at": "2026-10-12T10:00:00+03:00"},
        {"title": "Title 2", "lead": "Lead"},
        {"title": "Title 3"},
    ],
    "post": [
        {"channel": "chan", "message_id": 0, "text": "Post", "views": 10, "links": ["https://x.example/1"],
         "published_at": "2026-10-12T10:00:00Z", "has_media": False},
        {"views": 20, "edited": True},
        {"views": 15},
    ],
    "news_article": [
        {"url": "{url}", "headline": "Headline", "summary": "Summary", "region": "kyiv",
         "source_name": "Site", "source_kind": "web", "published_at": "2026-10-12T10:00:00+03:00"},
        {"headline": "Headline 2", "sentiment": {"label": "neutral", "confidence": 0.5}},
        {"summary": "Summary 3"},
    ],
    "news_event": [
        {"event_id": "{event_id}", "summary": "Event", "identity_kind": "specific", "identity_confidence": 0.9},
        {"summary": "Event 2"},
        {"summary": "Event 3"},
    ],
}  # fmt: skip


def seed_record(entity_type: str, n: int, step: int, *, observed: float) -> dict[str, Any]:
    natural = natural_key(entity_type, n)
    fields = {
        k: (v.format(**natural) if isinstance(v, str) else v)
        for k, v in SEED_FIELDS[entity_type][step].items()
    }
    if entity_type == "post" and "message_id" in fields:
        fields["message_id"] = natural["message_id"]
    return news(entity_type, n, fields=fields, observed=observed, obs=f"o-{entity_type}-{n}-{step}")


def show(capsys: pytest.CaptureFixture[str], text: str) -> None:
    """The CLI output on the terminal too (pytest -s), for the delivery report."""
    with capsys.disabled():
        print(text, flush=True)


@pytest.mark.integration
async def test_cli_migrates_twice_and_verifies_against_the_dev_stack(
    capsys: pytest.CaptureFixture[str],
) -> None:
    import asyncpg  # type: ignore[import-untyped]
    from pymongo import AsyncMongoClient

    from jane_storage_mongodb import MongoAdapter
    from jane_storage_postgres import PostgresAdapter

    stack = load_stack()
    if stack is None or not {"postgres", "mongodb"} <= set(stack.services):
        pytest.skip("dev stack with postgres and mongodb is not running (just up postgres mongodb)")
    path = _stack_file_path(stack.project)
    env = json.loads(path.read_text(encoding="utf-8"))["env"]
    pg, mongo_info = stack.services["postgres"], stack.services["mongodb"]
    suffix = uuid.uuid4().hex[:10]
    mongo_db, legacy_schema, target_schema = f"news_mig_{suffix}", f"legacy_{suffix}", f"news_{suffix}"
    pg_ep = mig.Endpoint(
        pg["host"],
        int(pg["port"]),
        "jane_storage_results",
        "jane_storage_results",
        env["JANE_PG_STORAGE_RESULTS_PASSWORD"],
    )
    mongo_ep = mig.Endpoint(
        mongo_info["host"], int(mongo_info["port"]), mongo_db, mongo_info["user"], mongo_info["password"]
    )
    legacy = PostgresAdapter()
    await legacy.open(
        mig.pg_connection(pg_ep, legacy_schema, connection_id="results-pg", sslmode="disable"), {}
    )
    mongo = MongoAdapter()
    await mongo.open(mig.mongo_connection(mongo_ep), {})
    try:
        await legacy.ensure_schema(list(mig.NEWS_TYPES))
        await mongo.ensure_schema(list(mig.NEWS_TYPES))
        for t_index, entity_type in enumerate(mig.NEWS_TYPES):
            base = 100 * t_index
            # legacy only (2 versions), mongo only (3 versions, the last one stale), both (interleaved)
            await store(
                legacy, seed_record(entity_type, 1, 0, observed=base + 1), f"{entity_type}-L1#0", base + 1
            )
            await store(
                legacy, seed_record(entity_type, 1, 1, observed=base + 2), f"{entity_type}-L2#0", base + 2
            )
            await store(
                mongo, seed_record(entity_type, 2, 0, observed=base + 3), f"{entity_type}-M1#0", base + 3
            )
            await store(
                mongo, seed_record(entity_type, 2, 1, observed=base + 5), f"{entity_type}-M2#0", base + 5
            )
            await store(
                mongo, seed_record(entity_type, 2, 2, observed=base + 4), f"{entity_type}-M3#0", base + 6
            )
            await store(
                legacy, seed_record(entity_type, 3, 0, observed=base + 1), f"{entity_type}-L3#0", base + 1
            )
            await store(
                mongo, seed_record(entity_type, 3, 1, observed=base + 7), f"{entity_type}-M4#0", base + 7
            )
            await store(
                legacy, seed_record(entity_type, 3, 2, observed=base + 8), f"{entity_type}-L4#0", base + 8
            )
        shared = seed_record("news_event", 4, 0, observed=400)
        await store(legacy, shared, "news_event-shared#0", 400)
        await store(mongo, shared, "news_event-shared#0", 400)
    finally:
        await legacy.close()
        await mongo.close()

    common = [
        "--stack-file",
        str(path),
        "--mongo-database",
        mongo_db,
        "--source-schema",
        legacy_schema,
        "--target-schema",
        target_schema,
        "--concurrency",
        "3",
        "--batch-size",
        "2",
    ]
    try:
        assert await mig.amain([*common, "--dry-run"]) == 0
        dry = capsys.readouterr().out
        show(capsys, dry)
        assert "nothing is written" in dry

        assert await mig.amain(common) == 0
        first = capsys.readouterr().out
        show(capsys, first)
        assert "result: OK" in first
        # 4 types x (2 + 3 + 3) events + 2 shared events (one of them a duplicate)
        total_row = next(line for line in first.splitlines() if line.startswith("total"))
        # keys legacy-pg/mongo/both, events, written, partially_stale, stale, duplicate
        assert total_row.split()[1:9] == ["4", "4", "5", "34", "30", "0", "3", "1"]
        assert await mig.amain(common) == 0
        second = capsys.readouterr().out
        show(capsys, second)
        total_row = next(line for line in second.splitlines() if line.startswith("total"))
        assert total_row.split()[1:9] == ["4", "4", "5", "34", "0", "0", "0", "34"]

        con = await asyncpg.connect(
            host=pg_ep.host,
            port=pg_ep.port,
            user=pg_ep.user,
            password=pg_ep.password,
            database=pg_ep.database,
        )
        try:
            owner = await con.fetchval(
                "SELECT pg_get_userbyid(nspowner) FROM pg_namespace WHERE nspname = $1", target_schema
            )
            assert owner == "jane_storage_results"
            # the script opened the target with layout "news": the projection tables exist
            for table_name in mig.PROJECTION_TABLES.values():
                exists = await con.fetchval(
                    "SELECT to_regclass($1) IS NOT NULL", f'"{target_schema}"."{table_name}"'
                )
                assert exists, f"projection table {target_schema}.{table_name} is missing"

            assert await mig.amain([*common, "--verify"]) == 0
            verified = capsys.readouterr().out
            show(capsys, verified)
            assert "result: OK" in verified and "layout unavailable" not in verified
            projection = verified.split("projection (canonical_key, version):", 1)[1]
            for entity_type in mig.NEWS_TYPES:
                assert any(
                    line.startswith(entity_type) and line.endswith(" ok") for line in projection.splitlines()
                )

            # a projection row with another version than its state is a discrepancy, with the key as example
            article_key = canonical_key({"scope": "scope-article", "natural": natural_key("article", 1)})
            await con.execute(
                f'UPDATE "{target_schema}"."article" SET version = version + 1 WHERE canonical_key = $1',
                article_key,
            )
            assert await mig.amain([*common, "--verify", "--examples", "5"]) == 1
            tampered = capsys.readouterr().out
            show(capsys, tampered)
            assert "MISMATCH" in tampered and "result: FAILED" in tampered
            assert f"state without such projection row: {article_key} v2" in tampered
            assert f"projection row without such state: {article_key} v3" in tampered
        finally:
            await con.close()
    finally:
        con = await asyncpg.connect(
            host=pg_ep.host,
            port=pg_ep.port,
            user=pg_ep.user,
            password=pg_ep.password,
            database=pg_ep.database,
        )
        try:
            for schema in (legacy_schema, target_schema):
                await con.execute(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE')
        finally:
            await con.close()
        client: AsyncMongoClient[dict[str, Any]] = AsyncMongoClient(mongo_info["uri"])
        try:
            await client.drop_database(mongo_db)
        finally:
            await client.close()
