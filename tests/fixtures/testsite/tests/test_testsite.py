"""The test site serves exactly what ``expected()`` promises (reference crawler over real HTTP)."""

from __future__ import annotations

import gzip
import json
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections import deque
from collections.abc import Iterator
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser

import pytest

from jane_testsite import expected, serve_in_thread
from jane_testsite.__main__ import expected_json

EXP = expected()
SM = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args: object, **kwargs: object) -> None:
        return None


OPENER = urllib.request.build_opener(_NoRedirect)


def fetch(url: str, headers: dict[str, str] | None = None) -> tuple[int, dict[str, str], bytes]:
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with OPENER.open(req, timeout=5) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.hrefs.append(href)


def normalize(url: str) -> str:
    parts = urlsplit(url)
    query = urlencode([(k, v) for k, v in parse_qsl(parts.query) if not k.startswith("utm_")])
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, ""))


def rel(url: str) -> str:
    p = urlsplit(url)
    return p.path + (f"?{p.query}" if p.query else "")


@pytest.fixture(scope="module")
def base() -> Iterator[str]:
    with serve_in_thread() as url:
        yield url


def crawl(base: str) -> tuple[set[str], set[str], set[str]]:
    """BFS within the host, robots.txt respected, trap prefix excluded. Returns (ok, broken, disallowed)."""
    robots = RobotFileParser(base + "/robots.txt")
    robots.read()
    host = urlsplit(base).netloc
    queue, seen = deque([base + "/"]), {base + "/"}
    ok: set[str] = set()
    broken: set[str] = set()
    disallowed: set[str] = set()
    while queue:
        url = queue.popleft()
        if not robots.can_fetch("JaneBot", url):
            disallowed.add(rel(url))
            continue
        status, headers, body = fetch(url)
        if status in (301, 302):
            target = normalize(urljoin(url, headers["Location"]))
            if target not in seen:
                seen.add(target)
                queue.append(target)
            continue
        if status != 200:
            broken.add(rel(url))
            continue
        ok.add(rel(url))
        if not headers.get("Content-Type", "").startswith("text/html"):
            continue
        parser = Links()
        parser.feed(body.decode())
        for href in parser.hrefs:
            target = normalize(urljoin(url, href))
            p = urlsplit(target)
            if p.scheme not in ("http", "https") or p.netloc != host:
                continue
            if p.path.startswith(EXP.info["trap_prefix"]):
                continue
            if target not in seen:
                seen.add(target)
                queue.append(target)
    return ok, broken, disallowed


def test_recursive_crawl_matches_expected(base: str) -> None:
    ok, broken, disallowed = crawl(base)
    assert ok == set(EXP.sets["recursive"])
    assert broken == set(EXP.sets["broken"])
    assert disallowed == set(EXP.sets["robots_disallowed"])
    for only in ("only:sitemap", "only:api", "only:search", "only:feeds", "only:template"):
        assert not (ok & set(EXP.sets[only])), only


def _sitemap_locs(base: str, url: str) -> set[str]:
    status, headers, body = fetch(url)
    assert status == 200
    if url.endswith(".gz"):
        assert headers["Content-Type"] == "application/gzip"
        body = gzip.decompress(body)
    root = ET.fromstring(body)
    if root.tag == f"{SM}sitemapindex":
        out: set[str] = set()
        for loc in root.iter(f"{SM}loc"):
            out |= _sitemap_locs(base, loc.text or "")
        return out
    return {rel(loc.text or "") for loc in root.iter(f"{SM}loc")}


def test_robots_declares_sitemap_index(base: str) -> None:
    status, _, body = fetch(base + "/robots.txt")
    assert status == 200
    assert f"Sitemap: {base}/sitemap.xml" in body.decode()


def test_sitemap_index_with_gz_matches_expected(base: str) -> None:
    assert _sitemap_locs(base, base + "/sitemap.xml") == set(EXP.sets["sitemap"])


def test_feeds_match_expected(base: str) -> None:
    _, _, rss = fetch(base + "/feeds/news.rss")
    rss_links = {rel(e.text or "") for e in ET.fromstring(rss).iter("link")} - {"/"}
    _, _, atom = fetch(base + "/feeds/news.atom")
    ns = "{http://www.w3.org/2005/Atom}"
    atom_links = {rel(e.get("href", "")) for e in ET.fromstring(atom).iter(f"{ns}link")}
    assert rss_links == atom_links == set(EXP.sets["feeds"])


def test_api_pagination_matches_expected(base: str) -> None:
    url: str | None = base + "/api/v1/products?page=1"
    found: set[str] = set()
    while url:
        status, _, body = fetch(url)
        assert status == 200
        data = json.loads(body)
        found |= {rel(i["url"]) for i in data["items"]}
        url = data["next"]
    assert found == set(EXP.sets["api"])
    status, _, body = fetch(base + "/api/v1/products/api-only-gadget")
    assert status == 200 and json.loads(body)["price"] == "59.00"


@pytest.mark.parametrize("term", ["cable", "phone"])
def test_search_matches_expected(base: str, term: str) -> None:
    found: set[str] = set()
    n = 1
    while True:
        path = f"/search?q={term}" if n == 1 else f"/search?q={term}&page={n}"
        _, _, body = fetch(base + path)
        parser = Links()
        parser.feed(body.decode())
        products = {h for h in parser.hrefs if h.startswith("/product/")}
        if not products:
            break
        found |= {path, *products}
        n += 1
    assert found == set(EXP.sets[f"search:{term}"])


def test_url_template_stops_at_first_404(base: str) -> None:
    found = set()
    n = 1
    while fetch(f"{base}/archive/{n}")[0] == 200:
        found.add(f"/archive/{n}")
        n += 1
    assert found == set(EXP.sets["template:/archive/{n}"])


def test_categories_with_pagination(base: str) -> None:
    ok, _, _ = crawl(base)
    assert set(EXP.sets["categories"]) <= ok
    status, _, _ = fetch(base + "/catalog/phones/?page=99")
    assert status == 404


def test_redirects_and_trap(base: str) -> None:
    for src, dst in EXP.info["redirects"].items():
        status, headers, _ = fetch(base + src)
        assert status == 301 and headers["Location"] == dst
    status, _, body = fetch(base + "/calendar/2031-12")
    assert status == 200 and b"/calendar/2032-01" in body


def test_page_types_and_conditional_get(base: str) -> None:
    for path, kind in EXP.info["page_types"].items():
        status, headers, body = fetch(base + path)
        assert status == 200, path
        assert f'<meta name="jane:page-type" content="{kind}">'.encode() in body, path
    status, headers, _ = fetch(base + "/news/2026/launch-alpha")
    assert "Last-Modified" in headers
    status, _, _ = fetch(base + "/news/2026/launch-alpha", {"If-None-Match": headers["ETag"]})
    assert status == 304


def test_forwarded_prefix_rewrites_links(base: str) -> None:
    status, _, body = fetch(base + "/", {"X-Forwarded-Prefix": "/testsite"})
    assert status == 200 and b'href="/testsite/catalog/"' in body


def test_controlled_price_change_updates_the_same_product_url(base: str) -> None:
    path = "/product/phone-alpha"
    control = base + "/_e2e/products/phone-alpha"
    original = json.loads(fetch(control)[2])
    before = fetch(base + path)

    def put(changes: dict[str, str]) -> tuple[int, bytes]:
        request = urllib.request.Request(
            control,
            data=json.dumps(changes).encode(),
            headers={"Content-Type": "application/json"},
            method="PUT",
        )
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as error:
            return error.code, error.read()

    try:
        status, changed = put({"price": "279.00", "name": "Phone Alpha 2027"})
        assert status == 200
        assert json.loads(changed)["price"] == "279.00"
        after = fetch(base + path)
        assert after[0] == 200 and after[1]["ETag"] != before[1]["ETag"]
        assert b"279.00" in after[2] and b"Phone Alpha 2027" in after[2]
        assert json.loads(fetch(base + "/api/v1/products/phone-alpha")[2])["price"] == "279.00"
        assert put({"category": "laptops"})[0] == 422
        assert json.loads(fetch(control)[2])["category"] == original["category"]
    finally:
        assert put({"price": original["price"], "name": original["name"]})[0] == 200


def test_expected_json_is_up_to_date() -> None:
    committed = Path(__file__).resolve().parents[1] / "expected_urls.json"
    assert committed.read_text(encoding="utf-8") == expected_json(), (
        "regenerate: uv run python -m jane_testsite --write-expected tests/fixtures/testsite/expected_urls.json"
    )
