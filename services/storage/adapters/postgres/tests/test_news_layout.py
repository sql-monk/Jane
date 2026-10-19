"""Relational layout ``news`` against the dev stack: projection, child replacement, extra, rollback, rebuild.

Needs `just up --project <name> postgres`, then `just integration --project <name> services/storage/adapters/postgres`.
Every test gets its own schema, dropped afterwards.
"""

from __future__ import annotations

import asyncio
import copy
import json
import os
import subprocess
import sys
import uuid
from collections.abc import AsyncIterator
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import asyncpg  # type: ignore[import-untyped]
import pytest

from jane_contracts.storage_adapter import (
    AdapterError,
    CommitOutcome,
    HistoryEvent,
    ResolvedConnection,
)
from jane_kit.devstack import load_stack
from jane_storage.engine import StorageEngine
from jane_storage.keys import canonical_key
from jane_storage.merge import merge
from jane_storage_postgres import PostgresAdapter

pytestmark = pytest.mark.integration

SAMPLES: dict[str, Any] = json.loads(
    (Path(__file__).parent / "data" / "news_samples.json").read_text(encoding="utf-8")
)
T0 = datetime(2026, 10, 12, 10, 0, tzinfo=UTC)
ADAPTER_OPTIONS = {"connect_timeout_ms": 60_000, "pool_max_size": 4}
"""Generous connect timeout: the concurrency test opens several pool connections at once on a slow dev host."""


def record(
    entity_type: str,
    *,
    at: float = 0,
    fields: dict[str, Any] | None = None,
    cleared: list[str] | None = None,
    natural: dict[str, Any] | None = None,
    scope: str | None = None,
    **changes: Any,
) -> dict[str, Any]:
    """An EntityRecord from a sample; ``changes`` update the sample fields, ``fields`` replaces them."""
    sample = SAMPLES[entity_type]
    body = copy.deepcopy(sample["fields"]) if fields is None else fields
    body.update(changes)
    rec: dict[str, Any] = {
        "entity_type": entity_type,
        "key": {
            "scope": scope or sample["key"]["scope"],
            "natural": natural or copy.deepcopy(sample["key"]["natural"]),
        },
        "fields": body,
        "observation": {
            "observation_id": f"obs_{entity_type}_{int(at * 60):06d}",
            "observed_at": (T0 + timedelta(minutes=at)).isoformat().replace("+00:00", "Z"),
        },
    }
    if cleared:
        rec["cleared"] = cleared
    return rec


class NewsEnv:
    def __init__(self, pg: dict[str, Any]) -> None:
        self.pg = pg
        self.schema = f"news_{uuid.uuid4().hex[:12]}"
        self._opened: list[PostgresAdapter] = []
        self._con: asyncpg.Connection | None = None
        self._clock = T0

    def connection(self, **params: Any) -> ResolvedConnection:
        return ResolvedConnection(
            connection_id="news-layout",
            kind="postgresql",
            params={
                "host": self.pg["host"],
                "port": int(self.pg["port"]),
                "database": self.pg["database"],
                "schema": self.schema,
                "sslmode": "disable",
                "layout": "news",
                **params,
            },
            secrets={"username": self.pg["user"], "password": self.pg["password"]},
        )

    async def adapter(self, **params: Any) -> PostgresAdapter:
        adapter = PostgresAdapter()
        await adapter.open(self.connection(**params), ADAPTER_OPTIONS)
        self._opened.append(adapter)
        await adapter.ensure_schema([])
        return adapter

    def tick(self) -> datetime:
        self._clock += timedelta(seconds=1)
        return self._clock

    def engine(self, adapter: PostgresAdapter) -> StorageEngine:
        """Engine with a deterministic clock (``updated_at`` / ``received_at``)."""
        return StorageEngine(adapter, connection_id="news-layout", clock=self.tick)

    async def con(self) -> asyncpg.Connection:
        if self._con is None:
            self._con = await asyncpg.connect(self.pg["dsn"])
            await self._con.set_type_codec(
                "jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
            )
        return self._con

    async def rows(self, query: str, *args: Any) -> list[dict[str, Any]]:
        con = await self.con()
        return [dict(r) for r in await con.fetch(query.replace("{s}", f'"{self.schema}"'), *args)]

    async def close(self) -> None:
        for adapter in self._opened:
            await adapter.close()
        con = await self.con()
        try:
            await con.execute(f'DROP SCHEMA IF EXISTS "{self.schema}" CASCADE')
        finally:
            await con.close()


@pytest.fixture
async def env() -> AsyncIterator[NewsEnv]:
    stack = load_stack()
    if stack is None or "postgres" not in stack.services:
        pytest.skip("dev stack with postgres is not running (just up postgres)")
    news = NewsEnv(stack.services["postgres"])
    try:
        yield news
    finally:
        await news.close()


def _without(rows: list[dict[str, Any]], *columns: str) -> list[dict[str, Any]]:
    return [{k: v for k, v in r.items() if k not in columns} for r in rows]


async def dump(env: NewsEnv) -> dict[str, Any]:
    """The whole projection by natural keys (surrogate ids left out)."""
    return {
        "source": await env.rows("SELECT * FROM {s}.source ORDER BY source_id"),
        "article": _without(await env.rows("SELECT * FROM {s}.article ORDER BY canonical_key"), "article_id"),
        "article_tag": await env.rows(
            """SELECT a.canonical_key, x.position, t.name FROM {s}.article_tag AS x
               JOIN {s}.article AS a USING (article_id) JOIN {s}.tag AS t USING (tag_id) ORDER BY 1, 2"""
        ),
        "post": _without(await env.rows("SELECT * FROM {s}.post ORDER BY canonical_key"), "post_id"),
        "post_link": await env.rows(
            """SELECT p.canonical_key, x.position, x.url FROM {s}.post_link AS x
               JOIN {s}.post AS p USING (post_id) ORDER BY 1, 2"""
        ),
        "news_event": _without(
            await env.rows("SELECT * FROM {s}.news_event ORDER BY canonical_key"), "news_event_id"
        ),
        "news_article": _without(
            await env.rows("SELECT * FROM {s}.news_article ORDER BY canonical_key"), "news_article_id"
        ),
        "news_article_event": _without(
            await env.rows(
                """SELECT na.canonical_key, x.* FROM {s}.news_article_event AS x
                   JOIN {s}.news_article AS na USING (news_article_id) ORDER BY 1"""
            ),
            "news_article_id",
        ),
        "news_article_topic": await env.rows(
            """SELECT na.canonical_key, x.position, t.name FROM {s}.news_article_topic AS x
               JOIN {s}.news_article AS na USING (news_article_id) JOIN {s}.topic AS t USING (topic_id)
               ORDER BY 1, 2"""
        ),
        "news_article_location": await env.rows(
            """SELECT na.canonical_key, x.position, x.name FROM {s}.news_article_location AS x
               JOIN {s}.news_article AS na USING (news_article_id) ORDER BY 1, 2"""
        ),
        "news_article_mention": await env.rows(
            """SELECT na.canonical_key, m.position, ne.canonical_name, ne.entity_kind, m.name, m.role, m.attitude,
                      m.attitude_confidence, m.factual_impact
               FROM {s}.news_article_mention AS m JOIN {s}.news_article AS na USING (news_article_id)
               LEFT JOIN {s}.named_entity AS ne USING (named_entity_id) ORDER BY 1, 2"""
        ),
        "evidence": await env.rows(
            """SELECT na.canonical_key, e.subject, m.position AS mention_position, e.position, e.quote, e.reason,
                      e.attribution
               FROM {s}.evidence AS e JOIN {s}.news_article AS na ON na.news_article_id = e.news_article_id
               LEFT JOIN {s}.news_article_mention AS m ON m.mention_id = e.mention_id
               ORDER BY 1, 2, 3 NULLS FIRST, 4"""
        ),
    }


async def store_samples(env: NewsEnv, adapter: PostgresAdapter) -> dict[str, dict[str, Any]]:
    engine = env.engine(adapter)
    acks = {}
    for entity_type in ("article", "post", "news_article", "news_event"):
        acks[entity_type] = await engine.store_entity(record(entity_type), f"{entity_type}-dk#0")
        assert acks[entity_type]["status"] == "written"
    return acks


# ---------------------------------------------------------------------------------------------- tests
async def test_each_type_is_laid_out_in_its_tables(env: NewsEnv) -> None:
    adapter = await env.adapter()
    await store_samples(env, adapter)
    await env.engine(adapter).store_entity(
        {
            "entity_type": "product",
            "key": {"scope": "shop", "natural": {"sku": "A-1"}},
            "fields": {"title": "Kettle"},
            "observation": {"observation_id": "obs_p", "observed_at": "2026-10-12T10:00:00Z"},
        },
        "product-dk#0",
    )
    d = await dump(env)
    art = SAMPLES["article"]["fields"]
    assert len(d["article"]) == 1
    article = d["article"][0]
    assert article["canonical_key"] == canonical_key(SAMPLES["article"]["key"])
    assert (article["source_id"], article["url"], article["title"], article["body"]) == (
        "news-suspilne",
        art["url"],
        art["title"],
        art["text"],
    )
    assert article["published_at"] == datetime(2026, 10, 12, 10, 22, 42, tzinfo=UTC)
    assert (article["version"], article["extra"]) == (1, {})
    assert [(r["position"], r["name"]) for r in d["article_tag"]] == list(enumerate(art["tags"]))

    post = d["post"][0]
    assert (post["channel"], post["message_id"], post["views"], post["edited"], post["has_media"]) == (
        "hromadske_ua",
        89322,
        17100,
        True,
        False,
    )
    assert [r["url"] for r in d["post_link"]] == SAMPLES["post"]["fields"]["links"]

    event = d["news_event"][0]
    assert (event["scope"], event["event_date"], event["event_time"], event["action"]) == (
        "news-events",
        date(2026, 10, 12),
        None,
        "crash",
    )

    na = d["news_article"][0]
    assert na["published_at"] == datetime(2026, 10, 12, 10, 25, tzinfo=UTC)
    assert (na["sentiment_label"], na["sentiment_confidence"], na["grouping_status"]) == (
        "neutral",
        0.85,
        "ungrouped",
    )
    assert [r["name"] for r in d["news_article_topic"]] == SAMPLES["news_article"]["fields"]["topics"]
    assert [r["name"] for r in d["news_article_location"]] == SAMPLES["news_article"]["fields"]["locations"]
    assert [(r["canonical_name"], r["entity_kind"], r["role"]) for r in d["news_article_mention"]] == [
        ("Vitali Klitschko", "person", "mentioned"),
        ("Kyiv", "place", "object"),
        ("Russia", "country", "mentioned"),
    ]
    assert [(r["subject"], r["mention_position"]) for r in d["evidence"]] == [
        ("event", None),
        ("mention", 0),
        ("mention", 1),
        ("mention", 2),
        ("sentiment", None),
    ]
    (na_event,) = d["news_article_event"]
    assert (na_event["identity_specificity"], na_event["location"], na_event["country"]) == (
        "broad",
        "Kyiv",
        "Ukraine",
    )

    sources = {r["source_id"]: r for r in d["source"]}
    assert set(sources) == {"news-suspilne", "tgweb-hromadske-ua", "news-web-pravda"}
    assert (sources["news-suspilne"]["kind"], sources["news-suspilne"]["site"]) == ("web", "suspilne.media")
    assert (sources["tgweb-hromadske-ua"]["kind"], sources["tgweb-hromadske-ua"]["channel"]) == (
        "telegram",
        "hromadske_ua",
    )
    assert (sources["news-web-pravda"]["kind"], sources["news-web-pravda"]["name"]) == (
        "web",
        "Українська правда",
    )
    assert (
        sources["news-suspilne"]["first_seen_at"]
        == sources["news-suspilne"]["last_seen_at"]
        == article["updated_at"]
    )
    # the product of the compatibility suite stays in the engine tables only
    assert await adapter.read_entity("product", 'shop|{"sku":"A-1"}') is not None
    assert len(d["article"]) + len(d["post"]) + len(d["news_article"]) + len(d["news_event"]) == 4


async def test_views_link_article_analysis_and_event(env: NewsEnv) -> None:
    adapter = await env.adapter()
    await store_samples(env, adapter)
    engine = env.engine(adapter)
    url = SAMPLES["news_article"]["fields"]["url"]
    site_article = record("article", scope="news-pravda", natural={"url": url}, url=url, site="pravda.com.ua")
    await engine.store_entity(site_article, "pravda-article#0")
    event_id = SAMPLES["news_event"]["fields"]["event_id"]
    await engine.store_entity(record("news_article", at=1, fields={"event_id": event_id}), "na-event#0")
    (joined,) = await env.rows("SELECT * FROM {s}.news_article_with_event")
    assert joined["event_id"] == event_id
    assert joined["event_summary"] == SAMPLES["news_event"]["fields"]["summary"]
    assert joined["event_date"] == date(2026, 10, 12)
    assert joined["headline"] == SAMPLES["news_article"]["fields"]["headline"]
    (analysis,) = await env.rows("SELECT * FROM {s}.article_analysis")
    assert (analysis["url"], analysis["article_source_id"], analysis["news_article_source_id"]) == (
        url,
        "news-pravda",
        "news-web-pravda",
    )
    assert analysis["sentiment_label"] == "neutral"
    assert analysis["event_id"] == event_id


async def test_recommit_replaces_child_rows(env: NewsEnv) -> None:
    adapter = await env.adapter()
    engine = env.engine(adapter)
    await engine.store_entity(record("article", tags=["A", "B"]), "a#0")
    (first,) = await env.rows("SELECT article_id FROM {s}.article")
    await engine.store_entity(record("article", at=1, fields={"tags": ["C", "A", "D"]}), "a#1")
    d = await dump(env)
    assert [(r["position"], r["name"]) for r in d["article_tag"]] == [(0, "C"), (1, "A"), (2, "D")]
    assert d["article"][0]["version"] == 2
    assert await env.rows("SELECT article_id FROM {s}.article") == [first], "the parent row is upserted"
    assert [r["name"] for r in await env.rows("SELECT name FROM {s}.tag ORDER BY name")] == [
        "A",
        "B",
        "C",
        "D",
    ]

    await engine.store_entity(record("post"), "p#0")
    await engine.store_entity(record("post", at=1, fields={"links": ["https://x.example/1"]}), "p#1")
    assert [r["url"] for r in (await dump(env))["post_link"]] == ["https://x.example/1"]

    await engine.store_entity(record("news_article"), "na#0")
    entities = [
        {
            "name": "Харків",
            "canonical_name": "Kharkiv",
            "type": "place",
            "role": "object",
            "attitude": "neutral",
            "attitude_confidence": 0.7,
            "evidence": [
                {"quote": "у Харкові", "reason": "місце", "attribution": "author"},
                {"quote": "харків'яни", "reason": "мешканці", "attribution": "quoted_source"},
            ],
        }
    ]
    await engine.store_entity(
        record(
            "news_article",
            at=1,
            fields={"entities": entities, "topics": ["Харків"], "locations": []},
            cleared=["event"],
        ),
        "na#1",
    )
    d = await dump(env)
    assert [(r["canonical_name"], r["name"]) for r in d["news_article_mention"]] == [("Kharkiv", "Харків")]
    assert [(r["subject"], r["mention_position"], r["position"]) for r in d["evidence"]] == [
        ("mention", 0, 0),
        ("mention", 0, 1),
        ("sentiment", None, 0),
    ]
    assert [r["name"] for r in d["news_article_topic"]] == ["Харків"]
    assert d["news_article_location"] == []
    assert d["news_article_event"] == [], "cleared event removes the 1:1 row"
    mentions = await env.rows("SELECT count(*) AS n FROM {s}.news_article_mention")
    assert mentions == [{"n": 1}]


async def test_cleared_field_is_null_and_unknown_field_goes_to_extra(env: NewsEnv) -> None:
    adapter = await env.adapter()
    engine = env.engine(adapter)
    await engine.store_entity(record("article"), "a#0")
    await engine.store_entity(record("article", at=1, fields={}, cleared=["lead", "tags"]), "a#1")
    d = await dump(env)
    assert d["article"][0]["lead"] is None
    assert d["article"][0]["title"] == SAMPLES["article"]["fields"]["title"]
    assert d["article_tag"] == []
    await engine.store_entity(
        record(
            "article", at=2, fields={"source_name": "Суспільне", "modified_at": "вчора", "paywall": False}
        ),
        "a#2",
    )
    (article,) = (await dump(env))["article"]
    assert article["extra"] == {"source_name": "Суспільне", "modified_at": "вчора", "paywall": False}
    assert article["modified_at"] is None
    snap = await adapter.read_entity("article", article["canonical_key"])
    assert snap is not None and snap.fields["modified_at"] == "вчора", "the state keeps the original value"


async def test_duplicate_and_conflict_do_not_touch_the_projection(env: NewsEnv) -> None:
    adapter = await env.adapter()
    await store_samples(env, adapter)
    before = await dump(env)
    rec = record("article", at=5, fields={"title": "Інший заголовок", "tags": ["Z"]})
    key = canonical_key(rec["key"])
    current = await adapter.read_entity("article", key)
    assert current is not None
    merged = merge(current, rec, now=env.tick())

    def event(delivery_key: str) -> HistoryEvent:
        return HistoryEvent(
            entity_type="article",
            canonical_key=key,
            record=rec,
            delivery_key=delivery_key,
            received_at=merged.snapshot.updated_at,
            applied_fields=merged.applied,
            stale_fields=merged.stale,
        )

    duplicate = await adapter.commit_entity(
        new=merged.snapshot, expected_version=current.version, event=event("article-dk#0")
    )
    assert duplicate.outcome is CommitOutcome.DUPLICATE
    conflict = await adapter.commit_entity(
        new=merged.snapshot, expected_version=current.version + 7, event=event("article-new#0")
    )
    assert conflict.outcome is CommitOutcome.CONFLICT
    assert await dump(env) == before
    assert await adapter.get_delivery("article-new#0") is None


async def test_projection_failure_rolls_the_whole_commit_back(env: NewsEnv) -> None:
    """Two articles of one source with the same ``url`` field break ``UNIQUE (source_id, url)``."""
    adapter = await env.adapter()
    engine = env.engine(adapter)
    await engine.store_entity(record("article"), "a#0")
    before = await dump(env)
    other = record("article", natural={"url": "https://suspilne.media/other/"})
    with pytest.raises(AdapterError) as err:
        await engine.store_entity(other, "other#0")
    assert err.value.retryable is False
    assert "article" in str(err.value)
    assert await adapter.read_entity("article", canonical_key(other["key"])) is None
    assert await adapter.get_delivery("other#0") is None
    history = await env.rows('SELECT count(*) AS n FROM {s}."jane_entity_history"')
    assert history == [{"n": 1}]
    assert await dump(env) == before


async def test_rebuild_reproduces_the_projection(env: NewsEnv) -> None:
    adapter = await env.adapter()
    engine = env.engine(adapter)
    await store_samples(env, adapter)
    await engine.store_entity(record("article", at=3, fields={"tags": ["Радіодиктант"]}), "a#1")  # orphan tag
    await engine.store_entity(record("article", at=-1, fields={"lead": "старе"}), "a#late")  # stale
    await engine.store_entity(record("post", at=2, fields={"views": 20000}), "p#1")
    await engine.store_entity(
        record("post", natural={"channel": "hromadske_ua", "message_id": 89323}, message_id=89323), "p2#0"
    )
    await engine.store_entity(record("news_article", at=2, fields={"source_name": "УП"}), "na#1")
    # the source is renamed by a newer snapshot of another entity whose canonical_key sorts first
    renamed = "https://www.pravda.com.ua/news/2026/10/12/8000000/"
    await engine.store_entity(
        record("news_article", at=3, natural={"url": renamed}, url=renamed, source_name="Українська правда"),
        "na2#0",
    )
    # a commit whose snapshot is older than the source's last_seen_at (clock behind) only fills gaps
    old = "https://www.pravda.com.ua/news/2026/10/11/7999999/"
    behind = StorageEngine(adapter, connection_id="news-layout", clock=lambda: T0)
    await behind.store_entity(
        record("news_article", natural={"url": old}, url=old, source_name="Правда (стара назва)"), "na3#0"
    )
    await engine.store_entity(record("news_event", at=1, fields={"identity_confidence": 0.9}), "ev#1")
    before = await dump(env)
    pravda = next(r for r in before["source"] if r["source_id"] == "news-web-pravda")
    assert pravda["name"] == "Українська правда"
    assert pravda["first_seen_at"] == T0
    assert len(await env.rows("SELECT * FROM {s}.tag")) == 2

    await (await env.con()).execute(f'DELETE FROM "{env.schema}".article_tag')  # damage it
    counts = await adapter.rebuild_layout(batch_size=2)
    assert counts == {"article": 1, "news_article": 3, "news_event": 1, "post": 2}
    assert await dump(env) == before
    assert [r["name"] for r in await env.rows("SELECT name FROM {s}.tag")] == ["Радіодиктант"], (
        "rebuild drops dictionary rows nothing refers to"
    )
    # commits go on after a rebuild
    await engine.store_entity(record("article", at=4, fields={"tags": ["Нове"]}), "a#2")
    assert [r["name"] for r in (await dump(env))["article_tag"]] == ["Нове"]


async def test_rebuild_cli(env: NewsEnv) -> None:
    adapter = await env.adapter()
    await store_samples(env, adapter)
    before = await dump(env)
    await (await env.con()).execute(f'TRUNCATE "{env.schema}".source CASCADE')
    argv = [
        sys.executable,
        "-m",
        "jane_storage_postgres.news_layout",
        "rebuild",
        "--host",
        str(env.pg["host"]),
        "--port",
        str(env.pg["port"]),
        "--database",
        str(env.pg["database"]),
        "--user",
        str(env.pg["user"]),
        "--schema",
        env.schema,
        "--sslmode",
        "disable",
        "--batch-size",
        "3",
    ]
    environ = {**os.environ, "JANE_TEST_PG_PASSWORD": str(env.pg["password"]), "PYTHONIOENCODING": "utf-8"}
    environ.pop("PGPASSWORD", None)
    done = await asyncio.to_thread(
        subprocess.run,
        [*argv, "--password-env", "JANE_TEST_PG_PASSWORD"],
        env=environ,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        check=False,
    )
    assert done.returncode == 0, done.stderr
    assert "RuntimeWarning" not in done.stderr
    summary = json.loads(done.stdout)
    assert summary["rebuilt"] == {"article": 1, "news_article": 1, "news_event": 1, "post": 1}
    assert summary["schema"] == env.schema
    assert await dump(env) == before
    wrong = await asyncio.to_thread(
        subprocess.run,
        [*argv, "--password-env", "JANE_TEST_NO_SUCH_VARIABLE"],
        env=environ,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        check=False,
    )
    assert wrong.returncode == 1
    assert str(env.pg["password"]) not in wrong.stderr + wrong.stdout


async def test_migrations_are_idempotent(env: NewsEnv) -> None:
    adapter = await env.adapter()
    await adapter.ensure_schema([])
    other = await env.adapter()  # another instance, as another worker would have
    await other.ensure_schema(["article"])
    migrations = await env.rows("SELECT layout, version FROM {s}.jane_layout_migrations")
    assert migrations == [{"layout": "news", "version": 1}]
    tables = await env.rows(
        "SELECT table_name, table_type FROM information_schema.tables WHERE table_schema = $1 ORDER BY 1",
        env.schema,
    )
    names = {r["table_name"]: r["table_type"] for r in tables}
    assert names["news_article_with_event"] == names["article_analysis"] == "VIEW"
    assert names["article"] == names["evidence"] == names["jane_entities"] == "BASE TABLE"

    con = await env.con()
    await con.execute(f"INSERT INTO \"{env.schema}\".jane_layout_migrations VALUES ('news', 99, now())")
    with pytest.raises(AdapterError) as err:
        await other.ensure_schema([])
    assert err.value.retryable is False
    assert "99" in str(err.value)


async def test_without_layout_no_projection_tables(env: NewsEnv) -> None:
    adapter = PostgresAdapter()
    params = dict(env.connection().params)
    del params["layout"]
    await adapter.open(
        ResolvedConnection(
            connection_id="plain", kind="postgresql", params=params, secrets=env.connection().secrets
        ),
        {},
    )
    try:
        assert adapter.layout is None
        await adapter.ensure_schema([])
        await env.engine(adapter).store_entity(record("article"), "a#0")
    finally:
        await adapter.close()
    tables = await env.rows(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = $1 ORDER BY 1", env.schema
    )
    assert sorted(r["table_name"] for r in tables) == [
        "jane_deliveries",
        "jane_entities",
        "jane_entity_history",
        "jane_objects",
    ]


async def test_concurrent_commits_share_dictionaries(env: NewsEnv) -> None:
    first, second = await env.adapter(), await env.adapter()
    tags = ["війна", "Київ", "економіка", "спорт", "культура"]
    names = ["Kyiv", "Russia", "Ukraine", "Kharkiv"]
    writes = []
    for i in range(16):
        engine = env.engine(first if i % 2 else second)
        picked = tags[i % 5 :] + tags[: i % 5]
        url = f"https://example.test/{i}"
        if i % 2:
            picked.reverse()
        writes.append(
            engine.store_entity(
                record(
                    "article",
                    scope=f"news-site-{i % 2}",
                    natural={"url": url},
                    url=url,
                    tags=picked[:3],
                ),
                f"art-{i}#0",
            )
        )
        entities = [
            {
                "name": n,
                "canonical_name": n,
                "type": "place",
                "role": "mentioned",
                "attitude": "neutral",
                "attitude_confidence": 0.5,
                "evidence": [{"quote": n, "reason": "r", "attribution": "author"}],
            }
            for n in (names if i % 2 else list(reversed(names)))
        ]
        writes.append(
            engine.store_entity(
                record(
                    "news_article",
                    natural={"url": url},
                    url=url,
                    topics=picked,
                    entities=entities,
                ),
                f"na-{i}#0",
            )
        )
    acks = await asyncio.gather(*writes)
    assert {a["status"] for a in acks} == {"written"}
    assert sorted(r["name"] for r in await env.rows("SELECT name FROM {s}.tag")) == sorted(tags)
    assert len(await env.rows("SELECT * FROM {s}.topic")) == len(tags)
    assert len(await env.rows("SELECT * FROM {s}.named_entity")) == len(names)
    d = await dump(env)
    assert len(d["article"]) == len(d["news_article"]) == 16
    assert len(d["article_tag"]) == 16 * 3
    assert len(d["news_article_mention"]) == 16 * len(names)
    assert len(d["evidence"]) == 16 * (len(names) + 2)  # + sentiment and event evidence of the sample
