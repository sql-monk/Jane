"""Unit tests of the parsers and helpers: sitemap/feed formats, gzip bombs and hostile XML, JSONPath, URL
templates, API pagination, registration in the core registry."""

from __future__ import annotations

import gzip
import time
import zlib
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

from jane_contracts.discovery import DiscoveryStrategy
from jane_web_collector.discovery import Registry

PACKAGE_DIR = Path(__file__).resolve().parents[1]
MiB = 1024 * 1024
SM = 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'


# ------------------------------------------------------------------------------------------ registration
def test_package_registers_every_wp03_strategy(discovery: ModuleType) -> None:
    reg = Registry.default(PACKAGE_DIR, use_entry_points=False)
    assert reg.load_errors == []
    assert set(reg.types()) == {
        "seed_list",
        "recursive",
        "sitemap",
        "feed",
        "listing",
        "url_template",
        "api_feed",
    }
    for name in ("sitemap", "feed", "listing", "url_template", "api_feed"):
        assert reg.origins[name].startswith("package:"), reg.origins
    assert not reg.supported("llm_explore")  # ADR-0010: not executed by the collector
    configs: dict[str, dict[str, Any]] = {
        "sitemap": {},
        "feed": {},
        "listing": {"start_urls": ["https://x.test/c/"]},
        "url_template": {"template": "https://x.test/{n}", "variables": {"n": {"values": [1]}}},
        "api_feed": {"url": "https://x.test/api", "items_path": "$.items", "url_path": "$.url"},
    }
    for cls in discovery.STRATEGIES:
        instance = cls({"type": cls.type_name, **configs[cls.type_name]}, "s")
        assert isinstance(instance, DiscoveryStrategy)
        assert instance.snapshot() == {}
        instance.restore({})


# ------------------------------------------------------------------------------------------ gzip
def test_gzip_is_decoded_and_multi_member_files_are_joined(discovery: ModuleType) -> None:
    common = discovery._common
    body = gzip.compress(b"<urlset>", mtime=0) + gzip.compress(b"</urlset>", mtime=0)
    out = common.maybe_gunzip(body, MiB)
    assert (out.data, out.compressed, out.truncated) == (b"<urlset></urlset>", True, False)
    plain = common.maybe_gunzip(b"<urlset/>", 10)
    assert (plain.data, plain.compressed) == (b"<urlset/>", False)


def test_gzip_bomb_is_cut_at_the_limit(discovery: ModuleType) -> None:
    common = discovery._common
    bomb = gzip.compress(b"\0" * (200 * MiB), compresslevel=9, mtime=0)  # ~200 KiB on the wire
    assert len(bomb) < MiB
    started = time.monotonic()
    out = common.maybe_gunzip(bomb, MiB)
    assert out.truncated and len(out.data) == MiB
    assert time.monotonic() - started < 5


def test_cut_or_corrupt_gzip_yields_what_was_decoded(discovery: ModuleType) -> None:
    common = discovery._common
    full = gzip.compress(
        b"<urlset>" + b"<url><loc>https://x.test/a</loc></url>" * 200 + b"</urlset>", mtime=0
    )
    cut = common.maybe_gunzip(full[: len(full) // 2], MiB)
    assert cut.truncated and cut.data.startswith(b"<urlset><url>")
    corrupt = common.maybe_gunzip(full[:10] + b"\xff" * 50, MiB)
    assert corrupt.truncated


# ------------------------------------------------------------------------------------------ XML safety
BILLION_LAUGHS = b"""<?xml version="1.0"?>
<!DOCTYPE lolz [
 <!ENTITY lol "lol">
 <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
 <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
 <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
 <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
 <!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
 <!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
 <!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">
 <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
]>
<urlset><url><loc>https://x.test/&lol9;</loc></url></urlset>"""

XXE = b"""<?xml version="1.0"?>
<!DOCTYPE urlset [<!ENTITY secret SYSTEM "file:///etc/passwd">]>
<urlset><url><loc>https://x.test/&secret;</loc></url></urlset>"""


@pytest.mark.parametrize(
    "body", [BILLION_LAUGHS, XXE, gzip.compress(XXE, mtime=0)], ids=["laughs", "xxe", "xxe-gz"]
)
def test_documents_with_dtd_entities_are_refused(discovery: ModuleType, body: bytes) -> None:
    sitemap = discovery.sitemap
    started = time.monotonic()
    with pytest.raises(discovery._common.UnsafeDocument):
        sitemap.parse_sitemap(body, "https://x.test/sitemap.xml", max_bytes=MiB, max_entries=100)
    assert time.monotonic() - started < 2


def test_non_xml_and_broken_xml(discovery: ModuleType) -> None:
    common = discovery._common
    assert common.parse_xml(b"") is None
    assert common.parse_xml(b'{"items": []}') is None
    root = common.parse_xml(
        b"\xef\xbb\xbf  <urlset><url><loc>https://x.test/a</loc></url><url><loc>https://x"
    )
    assert root is not None and common.localname(root) == "urlset"  # recover: the complete entry survives


# ------------------------------------------------------------------------------------------ sitemaps
def test_sitemap_formats(discovery: ModuleType) -> None:
    parse = discovery.sitemap.parse_sitemap
    urlset = f"""<?xml version="1.0" encoding="UTF-8"?><urlset {SM}>
      <url><loc> https://x.test/a </loc><lastmod>2026-09-01</lastmod></url>
      <url><loc>https://x.test/b</loc><lastmod>2026-09-02T10:00:00+03:00</lastmod></url>
      <url><lastmod>2026-09-02</lastmod></url></urlset>""".encode()
    doc = parse(urlset, "https://x.test/sitemap.xml", max_bytes=MiB, max_entries=100)
    assert doc.kind == "urlset" and [e.loc for e in doc.urls] == ["https://x.test/a", "https://x.test/b"]
    assert doc.urls[0].lastmod == datetime(2026, 9, 1, tzinfo=UTC)
    assert doc.urls[1].lastmod == datetime(2026, 9, 2, 7, tzinfo=UTC)

    index = b"<sitemapindex><sitemap><loc>/s1.xml.gz</loc></sitemap><sitemap><loc>https://x.test/s2</loc></sitemap></sitemapindex>"
    doc = parse(gzip.compress(index), "https://x.test/sitemap.xml", max_bytes=MiB, max_entries=100)
    assert doc.kind == "sitemapindex" and doc.compressed
    assert [e.loc for e in doc.sitemaps] == ["https://x.test/s1.xml.gz", "https://x.test/s2"]

    text = b"https://x.test/one\n\n# comment\nhttps://x.test/two\r\nftp://x.test/no\n"
    doc = parse(text, "https://x.test/sitemap.txt", max_bytes=MiB, max_entries=100)
    assert doc.kind == "text" and [e.loc for e in doc.urls] == ["https://x.test/one", "https://x.test/two"]

    many = (
        f"<urlset {SM}>"
        + "".join(f"<url><loc>https://x.test/{i}</loc></url>" for i in range(10))
        + "</urlset>"
    )
    doc = parse(many.encode(), "https://x.test/s.xml", max_bytes=MiB, max_entries=4)
    assert len(doc.urls) == 4 and doc.dropped == 6

    html = parse(
        b"<!doctype html><html><body>soft 404</body></html>", "https://x.test/s", max_bytes=MiB, max_entries=4
    )
    assert html.kind == "unknown" and html.urls == []


def test_robots_sitemap_lines(discovery: ModuleType) -> None:
    text = "User-agent: *\nDisallow: /x\nSITEMAP: https://x.test/a.xml\n  sitemap:/b.xml # c\nSitemap: https://x.test/a.xml\n"
    assert discovery.sitemap.parse_robots_sitemaps(text, "https://x.test/robots.txt") == [
        "https://x.test/a.xml",
        "https://x.test/b.xml",
    ]


# ------------------------------------------------------------------------------------------ feeds
def test_feed_formats(discovery: ModuleType) -> None:
    parse = discovery.feed.parse_feed_bytes
    rss = b"""<rss version="2.0"><channel><title>t</title>
      <item><link>https://x.test/1</link><pubDate>Tue, 01 Sep 2026 09:00:00 GMT</pubDate></item>
      <item><guid isPermaLink="true">https://x.test/2</guid></item>
      <item><guid isPermaLink="false">tag:x.test,2026:3</guid></item>
    </channel></rss>"""
    entries, dropped = parse(rss, "https://x.test/rss", max_bytes=MiB, max_entries=10)
    assert [e.link for e in entries] == ["https://x.test/1", "https://x.test/2"] and dropped == 0
    assert entries[0].lastmod == datetime(2026, 9, 1, 9, tzinfo=UTC)

    atom = b"""<feed xmlns="http://www.w3.org/2005/Atom" xml:base="https://x.test/news/">
      <entry><link rel="self" href="/api/1"/><link href="one"/><updated>2026-09-03T00:00:00Z</updated></entry>
      <entry><link rel="alternate" type="text/html" href="https://x.test/two"/></entry>
      <entry><title>no link</title></entry></feed>"""
    entries, _ = parse(atom, "https://x.test/atom", max_bytes=MiB, max_entries=10)
    assert [e.link for e in entries] == ["https://x.test/news/one", "https://x.test/two"]
    assert entries[0].lastmod == datetime(2026, 9, 3, tzinfo=UTC)

    rdf = b"""<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/"
      xmlns:dc="http://purl.org/dc/elements/1.1/"><channel rdf:about="https://x.test/"><title>t</title></channel>
      <item rdf:about="https://x.test/r1"><link>https://x.test/r1</link><dc:date>2026-09-04</dc:date></item>
      <item rdf:about="https://x.test/r2"/></rdf:RDF>"""
    entries, _ = parse(rdf, "https://x.test/rdf", max_bytes=MiB, max_entries=1)
    assert [e.link for e in entries] == ["https://x.test/r1"]


def test_autodiscovery_xpath_matches_only_feed_links(discovery: ModuleType) -> None:
    from lxml import html as lxml_html  # type: ignore[import-untyped]

    doc = lxml_html.fromstring(
        b"""<html><head>
        <link rel="Alternate" type="application/RSS+xml" href="/rss">
        <link rel="alternate" type="application/atom+xml; charset=utf-8" href="/atom">
        <link rel="alternate" hreflang="uk" href="/uk/">
        <link rel="stylesheet" type="application/rss+xml" href="/not-a-feed">
        </head><body><a rel="alternate" type="application/rss+xml" href="/a-tag"></a></body></html>"""
    )
    assert doc.xpath(discovery.feed.FEED_AUTODISCOVERY_XPATH) == ["/rss", "/atom"]


# ------------------------------------------------------------------------------------------ dates
@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2026", datetime(2026, 1, 1, tzinfo=UTC)),
        ("2026-09", datetime(2026, 9, 1, tzinfo=UTC)),
        ("2026-09-05", datetime(2026, 9, 5, tzinfo=UTC)),
        ("2026-09-05T10:30+02:00", datetime(2026, 9, 5, 8, 30, tzinfo=UTC)),
        ("2026-09-05T10:30:00Z", datetime(2026, 9, 5, 10, 30, tzinfo=UTC)),
        ("Sat, 05 Sep 2026 10:30:00 +0000", datetime(2026, 9, 5, 10, 30, tzinfo=UTC)),
        (1788604200, datetime(2026, 9, 5, 10, 30, tzinfo=UTC)),
        ("yesterday", None),
        ("", None),
        (None, None),
        (True, None),
    ],
)
def test_parse_datetime(discovery: ModuleType, value: Any, expected: datetime | None) -> None:
    assert discovery._common.parse_datetime(value) == expected


# ------------------------------------------------------------------------------------------ JSONPath
def test_jsonpath_subset(discovery: ModuleType) -> None:
    jp = discovery.jsonpath.JsonPath
    doc: dict[str, Any] = {
        "data": {"items": [{"url": "/a", "meta": {"url": "/deep"}}, {"url": "/b"}], "next": None},
        "n": 1,
    }
    assert jp("$.data.items").find(doc) == [doc["data"]["items"]]
    assert jp("data.items[*].url").find(doc) == ["/a", "/b"]
    assert jp("$['data']['items'][-1].url").find(doc) == ["/b"]
    assert jp("$.data.items[0].*").first(doc) == "/a"
    assert jp("$..url").find(doc) == ["/a", "/deep", "/b"]
    assert jp("$.data.next").find(doc) == [None]
    assert jp("$.missing").first(doc) is None
    assert jp("$").find([1, 2]) == [[1, 2]]
    deep: Any = {"url": "/x"}
    for _ in range(50_000):  # far beyond Python's recursion limit
        deep = {"child": deep}
    assert jp("$..url").find(deep) == ["/x"]
    for bad in ("", "$.items[?(@.x)]", "$.items[0:2]", "$[1,2]", "$.a b", "$..[0]"):
        with pytest.raises(ValueError, match="JSONPath"):
            jp(bad)


# ------------------------------------------------------------------------------------------ URL templates
def test_url_template_expansion(discovery: ModuleType) -> None:
    ut = discovery.url_template
    assert ut.expand("https://x.test/{a}/{b}", {"a": "x y/ž", "b": 7}) == "https://x.test/x%20y%2F%C5%BE/7"
    assert list(ut.variable_values({"range": {"start": 5, "end": 1, "step": 2}})) == [5, 3, 1]
    assert list(ut.variable_values({"range": {"start": 1, "end": 3}})) == [1, 2, 3]
    huge = ut.variable_values({"range": {"start": 1, "end": 10**15}})
    assert next(huge) == 1  # lazily generated, never materialized
    strategy = ut.UrlTemplateStrategy(
        {
            "template": "https://x.test/{year}/{page}",
            "variables": {"page": {"range": {"start": 1, "end": 2}}, "year": {"values": [2025, 2026]}},
        },
        "t",
    )
    assert [ut.expand(strategy.template, c) for c in strategy.combinations()] == [
        "https://x.test/2025/1",
        "https://x.test/2025/2",
        "https://x.test/2026/1",
        "https://x.test/2026/2",
    ]
    with pytest.raises(ValueError, match="no values for page"):
        ut.UrlTemplateStrategy(
            {"template": "https://x.test/{page}", "variables": {"n": {"values": [1]}}}, "t"
        )


# ------------------------------------------------------------------------------------------ API pagination
def _api(discovery: ModuleType, **pagination: Any) -> Any:
    config = {"url": "https://x.test/api?limit=5", "items_path": "$.items", "url_path": "$.url"}
    return discovery.api_feed.ApiFeedStrategy({**config, "pagination": pagination}, "api")


def test_api_pagination_rules(discovery: ModuleType) -> None:
    cursor = _api(discovery, type="cursor", cursor_path="$.meta.cursor", cursor_param="after")
    seen: set[str] = set()
    assert cursor.next_page({"meta": {"cursor": "c1"}}, "https://x.test/api?limit=5", 5, seen) == (
        "https://x.test/api?limit=5&after=c1"
    )
    assert (
        cursor.next_page({"meta": {"cursor": "c1"}}, "https://x.test/api?after=c1&limit=5", 5, seen) is None
    )
    assert cursor.next_page({"meta": {"cursor": None}}, "https://x.test/api", 5, seen) is None
    assert cursor.next_page({"meta": {"cursor": ""}}, "https://x.test/api", 5, seen) is None

    page = _api(discovery, type="page", page_param="p")
    assert page.next_page({}, "https://x.test/api?limit=5", 5, set()) == "https://x.test/api?limit=5&p=2"
    assert page.next_page({}, "https://x.test/api?p=7&limit=5", 5, set()) == "https://x.test/api?limit=5&p=8"
    assert page.next_page({}, "https://x.test/api?p=7", 0, set()) is None  # empty page ends the pagination

    nxt = _api(discovery, type="next_url", next_url_path="$.links.next")
    assert nxt.next_page({"links": {"next": "/api?page=2"}}, "https://x.test/api", 5, set()) == "/api?page=2"
    assert nxt.next_page({"links": {"next": None}}, "https://x.test/api", 5, set()) is None
    assert _api(discovery).next_page({"next": "/x"}, "https://x.test/api", 5, set()) is None  # type none

    items = _api(discovery).items
    assert items({"items": [{"url": "/a"}]}) == [{"url": "/a"}]
    assert items({"other": 1}) == []


def test_api_feed_configs_the_core_cannot_execute(discovery: ModuleType) -> None:
    unsupported = discovery.api_feed.UnsupportedConfig
    base = {"url": "https://x.test/api", "items_path": "$.items", "url_path": "$.url"}
    with pytest.raises(unsupported, match="POST"):
        discovery.api_feed.ApiFeedStrategy({**base, "method": "POST", "body": {"q": 1}}, "api")
    with pytest.raises(unsupported, match="emit_items_as_materials"):
        discovery.api_feed.ApiFeedStrategy({**base, "emit_items_as_materials": True}, "api")
    with pytest.raises(ValueError, match="cursor_param"):
        discovery.api_feed.ApiFeedStrategy(
            {**base, "pagination": {"type": "cursor", "cursor_path": "$.c"}}, "api"
        )


# ------------------------------------------------------------------------------------------ helpers
def test_rule_origins(discovery: ModuleType) -> None:
    origins = discovery._common.rule_origins
    rules = {
        "scope": {"allowed_domains": ["x.test"]},
        "strategies": [
            {"type": "sitemap"},
            {"type": "seed_list", "urls": ["http://x.test:8080/a", "http://x.test:8080/b"]},
            {"type": "url_template", "template": "https://{sub}.x.test/{n}", "variables": {}},
            {
                "type": "listing",
                "start_urls": ["https://x.test/c"],
                "search": {"url_template": "https://s.x.test/?q={query}"},
            },
        ],
    }
    assert origins(rules) == ["http://x.test:8080", "https://x.test", "https://s.x.test"]
    no_urls = {
        "scope": {"allowed_domains": ["x.test", "y.test"], "allowed_schemes": ["http"]},
        "strategies": [{"type": "sitemap"}],
    }
    assert origins(no_urls) == ["http://x.test", "http://y.test"]


def test_limits_fallback_only_without_a_value(discovery: ModuleType) -> None:
    common = discovery._common
    ctx = SimpleNamespace(limits={"crawl": {"max_depth": 9, "max_links_per_page": True}})
    assert common.limit(ctx, "crawl.max_depth") == 9
    assert common.limit(ctx, "crawl.max_links_per_page") == common.FALLBACK_LIMITS["crawl.max_links_per_page"]
    assert common.limit(ctx, "crawl.max_material_bytes") == 10 * MiB


def test_zlib_stream_without_gzip_header_is_not_touched(discovery: ModuleType) -> None:
    raw = zlib.compress(b"<urlset/>")
    assert discovery._common.maybe_gunzip(raw, MiB).data == raw


def test_package_dir_is_the_production_path() -> None:
    assert Path(__file__).resolve().parents[1] == PACKAGE_DIR
    assert PACKAGE_DIR.parts[-3:] == ("web-collector", "strategies", "discovery")
