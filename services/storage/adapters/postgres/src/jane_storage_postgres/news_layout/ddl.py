"""DDL of the ``news`` layout: numbered migrations over ``<schema>``.

Every migration is applied once, in order, in the transaction of ``ensure_schema`` and recorded in
``<schema>.jane_layout_migrations``. A released migration is never edited: a change of the layout is a new
migration (plus ``rebuild`` when existing rows have to be laid out again).

Statements are templates with one placeholder, ``{s}`` — the quoted schema (validated by the adapter).
"""

# ruff: noqa: S608 - only the validated schema identifier is formatted into the statements

from __future__ import annotations

__all__ = [
    "MIGRATIONS",
    "MIGRATIONS_TABLE",
    "PROJECTION_TABLES",
    "VIEWS",
    "migrations_table_sql",
]

MIGRATIONS_TABLE = "jane_layout_migrations"

PROJECTION_TABLES: tuple[str, ...] = (
    "source",
    "tag",
    "topic",
    "named_entity",
    "article",
    "article_tag",
    "post",
    "post_link",
    "news_event",
    "news_article",
    "news_article_event",
    "news_article_topic",
    "news_article_location",
    "news_article_mention",
    "evidence",
)
"""Tables of the projection (cleared together by ``rebuild``); dictionaries first."""

VIEWS: tuple[str, ...] = ("news_article_with_event", "article_analysis")

_ENTITY_TAIL = """
    version integer NOT NULL,
    updated_at timestamptz NOT NULL,
    extra jsonb NOT NULL DEFAULT '{{}}'::jsonb"""

_V1 = f"""
CREATE TABLE {{s}}.source (
    source_id text PRIMARY KEY,
    kind text,
    name text,
    site text,
    channel text,
    first_seen_at timestamptz,
    last_seen_at timestamptz
);
CREATE TABLE {{s}}.tag (
    tag_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL UNIQUE
);
CREATE TABLE {{s}}.topic (
    topic_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL UNIQUE
);
CREATE TABLE {{s}}.named_entity (
    named_entity_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    canonical_name text NOT NULL,
    entity_kind text,
    CONSTRAINT named_entity_canonical_name_entity_kind_key
        UNIQUE NULLS NOT DISTINCT (canonical_name, entity_kind)
);

CREATE TABLE {{s}}.article (
    article_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    canonical_key text NOT NULL UNIQUE,
    source_id text NOT NULL REFERENCES {{s}}.source (source_id),
    url text,
    site text,
    title text,
    lead text,
    body text,
    author text,
    section text,
    language text,
    image text,
    published_at timestamptz,
    modified_at timestamptz,{_ENTITY_TAIL},
    CONSTRAINT article_source_id_url_key UNIQUE (source_id, url)
);
CREATE INDEX article_published_at_idx ON {{s}}.article (published_at);
CREATE INDEX article_source_id_published_at_idx ON {{s}}.article (source_id, published_at);
CREATE INDEX article_url_idx ON {{s}}.article (url);
CREATE TABLE {{s}}.article_tag (
    article_id bigint NOT NULL REFERENCES {{s}}.article (article_id) ON DELETE CASCADE,
    position integer NOT NULL,
    tag_id bigint NOT NULL REFERENCES {{s}}.tag (tag_id),
    PRIMARY KEY (article_id, position)
);
CREATE INDEX article_tag_tag_id_idx ON {{s}}.article_tag (tag_id);

CREATE TABLE {{s}}.post (
    post_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    canonical_key text NOT NULL UNIQUE,
    source_id text NOT NULL REFERENCES {{s}}.source (source_id),
    channel text,
    message_id bigint,
    url text,
    title text,
    body text,
    views bigint,
    forwarded_from text,
    has_media boolean,
    edited boolean,
    published_at timestamptz,{_ENTITY_TAIL},
    CONSTRAINT post_source_id_channel_message_id_key UNIQUE (source_id, channel, message_id)
);
CREATE INDEX post_published_at_idx ON {{s}}.post (published_at);
CREATE INDEX post_source_id_published_at_idx ON {{s}}.post (source_id, published_at);
CREATE INDEX post_url_idx ON {{s}}.post (url);
CREATE TABLE {{s}}.post_link (
    post_id bigint NOT NULL REFERENCES {{s}}.post (post_id) ON DELETE CASCADE,
    position integer NOT NULL,
    url text NOT NULL,
    PRIMARY KEY (post_id, position)
);
CREATE INDEX post_link_url_idx ON {{s}}.post_link (url);

CREATE TABLE {{s}}.news_event (
    news_event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    canonical_key text NOT NULL UNIQUE,
    scope text NOT NULL,
    event_id text,
    summary text,
    identity_kind text,
    grouping_method text,
    identity_confidence double precision,
    event_date date,
    event_time time,
    primary_actor text,
    action text,
    object text,
    location text,
    country text,{_ENTITY_TAIL},
    CONSTRAINT news_event_scope_event_id_key UNIQUE (scope, event_id)
);
CREATE INDEX news_event_event_id_idx ON {{s}}.news_event (event_id);
CREATE INDEX news_event_event_date_idx ON {{s}}.news_event (event_date);

CREATE TABLE {{s}}.news_article (
    news_article_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    canonical_key text NOT NULL UNIQUE,
    source_id text NOT NULL REFERENCES {{s}}.source (source_id),
    url text,
    material_id text,
    content_sha256 text,
    headline text,
    headline_ukrainian text,
    summary text,
    source_language text,
    analysis_language text,
    reporting_kind text,
    region text,
    transport text,
    published_at timestamptz,
    fetched_at timestamptz,
    edited_at timestamptz,
    evidence_validation text,
    event_id text,
    grouping_status text,
    grouping_method text,
    grouping_reason text,
    sentiment_label text,
    sentiment_confidence double precision,
    sentiment_explanation text,{_ENTITY_TAIL},
    CONSTRAINT news_article_source_id_url_key UNIQUE (source_id, url)
);
CREATE INDEX news_article_published_at_idx ON {{s}}.news_article (published_at);
CREATE INDEX news_article_source_id_published_at_idx ON {{s}}.news_article (source_id, published_at);
CREATE INDEX news_article_url_idx ON {{s}}.news_article (url);
CREATE INDEX news_article_event_id_idx ON {{s}}.news_article (event_id);
CREATE TABLE {{s}}.news_article_event (
    news_article_id bigint PRIMARY KEY REFERENCES {{s}}.news_article (news_article_id) ON DELETE CASCADE,
    summary text,
    identity_confidence double precision,
    identity_specificity text,
    identity_kind text,
    event_date date,
    event_time time,
    primary_actor text,
    action text,
    object text,
    location text,
    country text,
    date_resolution_method text,
    date_resolution_quote text,
    date_resolution_reference_published_at timestamptz
);
CREATE TABLE {{s}}.news_article_topic (
    news_article_id bigint NOT NULL REFERENCES {{s}}.news_article (news_article_id) ON DELETE CASCADE,
    position integer NOT NULL,
    topic_id bigint NOT NULL REFERENCES {{s}}.topic (topic_id),
    PRIMARY KEY (news_article_id, position)
);
CREATE INDEX news_article_topic_topic_id_idx ON {{s}}.news_article_topic (topic_id);
CREATE TABLE {{s}}.news_article_location (
    news_article_id bigint NOT NULL REFERENCES {{s}}.news_article (news_article_id) ON DELETE CASCADE,
    position integer NOT NULL,
    name text NOT NULL,
    PRIMARY KEY (news_article_id, position)
);
CREATE INDEX news_article_location_name_idx ON {{s}}.news_article_location (name);
CREATE TABLE {{s}}.news_article_mention (
    mention_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    news_article_id bigint NOT NULL REFERENCES {{s}}.news_article (news_article_id) ON DELETE CASCADE,
    position integer NOT NULL,
    named_entity_id bigint REFERENCES {{s}}.named_entity (named_entity_id),
    name text,
    role text,
    attitude text,
    attitude_confidence double precision,
    factual_impact text,
    CONSTRAINT news_article_mention_news_article_id_position_key UNIQUE (news_article_id, position)
);
CREATE INDEX news_article_mention_named_entity_id_idx ON {{s}}.news_article_mention (named_entity_id);
CREATE TABLE {{s}}.evidence (
    evidence_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    news_article_id bigint NOT NULL REFERENCES {{s}}.news_article (news_article_id) ON DELETE CASCADE,
    subject text NOT NULL,
    mention_id bigint REFERENCES {{s}}.news_article_mention (mention_id) ON DELETE CASCADE,
    position integer NOT NULL,
    quote text,
    reason text,
    attribution text
);
CREATE INDEX evidence_news_article_id_idx ON {{s}}.evidence (news_article_id);
CREATE INDEX evidence_mention_id_idx ON {{s}}.evidence (mention_id);

CREATE VIEW {{s}}.news_article_with_event AS
SELECT na.*,
       ev.news_event_id,
       ev.canonical_key AS event_canonical_key,
       ev.scope AS event_scope,
       ev.summary AS event_summary,
       ev.identity_kind AS event_identity_kind,
       ev.grouping_method AS event_grouping_method,
       ev.identity_confidence AS event_identity_confidence,
       ev.event_date,
       ev.event_time,
       ev.primary_actor AS event_primary_actor,
       ev.action AS event_action,
       ev.object AS event_object,
       ev.location AS event_location,
       ev.country AS event_country
FROM {{s}}.news_article AS na
LEFT JOIN {{s}}.news_event AS ev ON ev.event_id = na.event_id;

CREATE VIEW {{s}}.article_analysis AS
SELECT a.article_id,
       a.canonical_key AS article_canonical_key,
       a.source_id AS article_source_id,
       a.url,
       a.site,
       a.title,
       a.lead,
       a.body,
       a.author,
       a.section,
       a.language,
       a.published_at AS article_published_at,
       na.news_article_id,
       na.canonical_key AS news_article_canonical_key,
       na.source_id AS news_article_source_id,
       na.headline,
       na.headline_ukrainian,
       na.summary,
       na.source_language,
       na.reporting_kind,
       na.region,
       na.published_at AS news_article_published_at,
       na.event_id,
       na.grouping_status,
       na.grouping_reason,
       na.sentiment_label,
       na.sentiment_confidence,
       na.sentiment_explanation
FROM {{s}}.article AS a
JOIN {{s}}.news_article AS na ON na.url = a.url;
"""

MIGRATIONS: tuple[tuple[int, str], ...] = ((1, _V1),)
"""``(version, statements)`` in application order; versions start at 1 and grow by one."""


def migrations_table_sql(schema: str) -> str:
    return f"""CREATE TABLE IF NOT EXISTS "{schema}".{MIGRATIONS_TABLE} (
        layout text NOT NULL,
        version integer NOT NULL,
        applied_at timestamptz NOT NULL,
        PRIMARY KEY (layout, version)
    )"""
