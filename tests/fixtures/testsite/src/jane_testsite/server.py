"""HTTP server of the test site (stdlib only, so it runs anywhere: tests, CLI, container).

Absolute URLs (sitemaps, feeds, API) are built from the ``Host`` header; ``X-Forwarded-Prefix``
(set by the dev reverse proxy) prefixes every generated link.
"""

from __future__ import annotations

import gzip
import hashlib
import html
import json
import threading
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from email.utils import format_datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlsplit

from . import site

__all__ = ["TestSiteHandler", "make_server", "serve_in_thread"]

XML = "application/xml; charset=utf-8"
HTML = "text/html; charset=utf-8"


def _esc(s: str) -> str:
    return html.escape(s, quote=True)


class TestSiteHandler(BaseHTTPRequestHandler):
    server_version = "JaneTestSite/1.0"
    protocol_version = "HTTP/1.1"
    quiet = True

    # ------------------------------------------------------------------ helpers
    @property
    def prefix(self) -> str:
        return (self.headers.get("X-Forwarded-Prefix") or "").rstrip("/")

    @property
    def base(self) -> str:
        proto = self.headers.get("X-Forwarded-Proto") or "http"
        host = self.headers.get("X-Forwarded-Host") or self.headers.get("Host") or "localhost"
        return f"{proto}://{host}{self.prefix}"

    def link(self, path: str) -> str:
        return f"{self.prefix}{path}" if path.startswith("/") else path

    def log_message(self, format: str, *args: Any) -> None:
        if not self.quiet:
            super().log_message(format, *args)

    def send(self, status: int, body: bytes, ctype: str, headers: dict[str, str] | None = None) -> None:
        etag = '"' + hashlib.sha256(body).hexdigest()[:16] + '"'
        if status == 200 and self.headers.get("If-None-Match") == etag:
            self.send_response(HTTPStatus.NOT_MODIFIED)
            self.send_header("ETag", etag)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        if status == 200:
            self.send_header("ETag", etag)
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def page(
        self,
        title: str,
        page_type: str,
        body: str,
        *,
        status: int = 200,
        head: str = "",
        headers: dict[str, str] | None = None,
    ) -> None:
        doc = (
            '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            f"<title>{_esc(title)} | Jane Test Shop</title>"
            f'<meta name="jane:page-type" content="{page_type}">'
            f'<link rel="alternate" type="application/rss+xml" href="{self.link("/feeds/news.rss")}">'
            f'<link rel="alternate" type="application/atom+xml" href="{self.link("/feeds/news.atom")}">'
            f"{head}</head><body>"
            f'<nav><a href="{self.link("/")}">Home</a> <a href="{self.link("/catalog/")}">Catalog</a> '
            f'<a href="{self.link("/news/")}">News</a> <a href="{self.link("/about")}">About</a></nav>'
            f"<main><h1>{_esc(title)}</h1>{body}</main></body></html>\n"
        )
        self.send(status, doc.encode("utf-8"), HTML, headers)

    def links(self, items: list[tuple[str, str]], rel: str | None = None) -> str:
        r = f' rel="{rel}"' if rel else ""
        return (
            "<ul>"
            + "".join(f'<li><a href="{self.link(h)}"{r}>{_esc(t)}</a></li>' for h, t in items)
            + "</ul>"
        )

    def pager(self, page: int, total: int, path_for: Any) -> str:
        out = []
        if page > 1:
            out.append(f'<a rel="prev" href="{self.link(path_for(page - 1))}">Previous</a>')
        if page < total:
            out.append(f'<a rel="next" href="{self.link(path_for(page + 1))}">Next</a>')
        return f'<nav class="pagination">{" ".join(out)}</nav>'

    def not_found(self) -> None:
        self.page("Not found", "error", "<p>No such page.</p>", status=404)

    # ------------------------------------------------------------------ routing
    def do_HEAD(self) -> None:
        self.do_GET()

    def do_GET(self) -> None:
        url = urlsplit(self.path)
        path, query = url.path, parse_qs(url.query)
        page_no = self._int(query.get("page", ["1"])[0])
        if path in site.REDIRECTS:
            self.send(301, b"", HTML, {"Location": self.link(site.REDIRECTS[path])})
            return
        routes: dict[str, Callable[[], None]] = {
            "/": self.home,
            "/about": self.about,
            "/robots.txt": self.robots,
            "/sitemap.xml": self.sitemap_index,
            "/sitemaps/products.xml": self.sitemap_products,
            "/sitemaps/pages.xml": self.sitemap_pages,
            "/sitemaps/news.xml.gz": self.sitemap_news_gz,
            "/feeds/news.rss": self.rss,
            "/feeds/news.atom": self.atom,
            "/catalog/": self.catalog,
            "/news/": lambda: self.news_list(1),
            "/api/v1/products": lambda: self.api_list(page_no),
            "/search": lambda: self.search(query.get("q", [""])[0], page_no),
        }
        if path in routes:
            routes[path]()
            return
        parts = [p for p in path.split("/") if p]
        try:
            self._dynamic(path, parts, page_no)
        except LookupError:
            self.not_found()

    @staticmethod
    def _int(v: str) -> int:
        try:
            return max(1, int(v))
        except ValueError:
            return 1

    def _dynamic(self, path: str, parts: list[str], page_no: int) -> None:
        if len(parts) == 2 and parts[0] == "catalog" and parts[1] in site.CATEGORIES and path.endswith("/"):
            return self.category(parts[1], page_no)
        if len(parts) == 2 and parts[0] == "product" and (p := site.product_by_slug(parts[1])):
            return self.product(p)
        if len(parts) == 3 and parts[:2] == ["news", "page"] and path.endswith("/"):
            return self.news_list(self._int(parts[2]))
        if len(parts) == 3 and parts[:2] == ["news", "2026"] and (a := site.article_by_slug(parts[2])):
            return self.article(a)
        if len(parts) == 2 and parts[0] == "pages":
            u = next((u for u in site.UNKNOWN_PAGES if u.slug == parts[1]), None)
            if u:
                return self.page(u.title, "unknown", f"<p>{_esc(u.body)}</p>")
        if path in site.LOOP_PAGES:
            return self.loop(path)
        if path in site.PRIVATE_PAGES:
            return self.page("Private", "private", "<p>Robots must not fetch this page.</p>")
        if path in site.FILES:
            return self.send(200, site.FILES[path], "application/pdf")
        if (
            len(parts) == 2
            and parts[0] == "archive"
            and parts[1].isdigit()
            and 1 <= int(parts[1]) <= site.ARCHIVE_PAGES
        ):
            return self.page(f"Archive notice {parts[1]}", "archive", f"<p>Old notice #{parts[1]}.</p>")
        if len(parts) == 4 and parts[:3] == ["api", "v1", "products"]:
            p = site.product_by_slug(parts[3])
            if p and p.in_api:
                return self.api_detail(p)
        if len(parts) == 2 and parts[0] == "calendar":
            return self.calendar(parts[1])
        raise LookupError(path)

    # ------------------------------------------------------------------ pages
    def home(self) -> None:
        body = (
            "<p>Welcome to the Jane test shop.</p>"
            + self.links([("/catalog/", "Catalog"), ("/news/", "News"), ("/about", "About us")])
            + f'<form action="{self.link("/search")}" method="get"><input name="q"><button>Search</button></form>'
            + self.links([(site.search_page_path(site.POPULAR_SEARCH, 1), f"Popular: {site.POPULAR_SEARCH}")])
            + self.links(
                [
                    ("/loop/a", "Loop start"),
                    ("/loop/a?utm_source=home&utm_medium=link", "Loop (tracking)"),
                    ("/loop/a#top", "Loop (fragment)"),
                ]
            )
            + self.links([(site.TRAP_START, "Event calendar")])
            + self.links([("/private/admin", "Admin"), ("/private/reports", "Reports")])
            + self.links([(u, "Partner") for u in site.EXTERNAL_LINKS])
            + self.links([(u, "Contact") for u in site.NON_HTTP_LINKS])
        )
        self.page("Home", "home", body)

    def about(self) -> None:
        body = (
            "<p>About the shop.</p>"
            + self.links([(u.path, u.title) for u in site.UNKNOWN_PAGES])
            + self.links(
                [
                    ("/old/catalog", "Old catalog link"),
                    ("/missing-page", "Broken link"),
                    ("/about/", "About (trailing slash)"),
                ]
            )
        )
        self.page("About", "about", body)

    def robots(self) -> None:
        text = (
            "# Jane testsite robots.txt\n"
            "User-agent: *\n"
            "Disallow: /private/\n"
            "Allow: /\n\n"
            "User-agent: BadBot\n"
            "Disallow: /\n\n"
            f"Sitemap: {self.base}/sitemap.xml\n"
        )
        self.send(200, text.encode(), "text/plain; charset=utf-8")

    def catalog(self) -> None:
        items = [(site.category_page_path(c, 1), name) for c, name in site.CATEGORIES.items()]
        self.page(
            "Catalog",
            "catalog",
            self.links(items) + self.links([("/files/price-list.pdf", "Price list (PDF)")]),
        )

    def category(self, category: str, page_no: int) -> None:
        products = site.listed_products(category)
        total = site.pages(len(products), site.CATEGORY_PAGE_SIZE)
        if page_no > total:
            return self.not_found()
        chunk = products[(page_no - 1) * site.CATEGORY_PAGE_SIZE : page_no * site.CATEGORY_PAGE_SIZE]
        body = self.links([(p.path, p.name) for p in chunk]) + self.pager(
            page_no, total, lambda n: site.category_page_path(category, n)
        )
        self.page(f"{site.CATEGORIES[category]} - page {page_no}", "category", body)

    def product(self, p: site.Product) -> None:
        same = site.listed_products(p.category)
        related = []
        if p in same:
            related = [same[(same.index(p) + 1) % len(same)]]
        ld = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": p.name,
            "sku": p.slug,
            "offers": {
                "@type": "Offer",
                "price": p.price,
                "priceCurrency": "UAH",
                "availability": f"https://schema.org/{p.availability}",
            },
        }
        head = f'<script type="application/ld+json">{json.dumps(ld)}</script>'
        body = (
            f'<div itemscope itemtype="https://schema.org/Product"><span itemprop="name">{_esc(p.name)}</span>'
            f'<span class="price" itemprop="price" content="{p.price}">{p.price} UAH</span>'
            f'<span class="availability">{p.availability}</span></div>'
            + self.links([(site.category_page_path(p.category, 1), "Back to category")])
            + self.links([(r.path, f"Related: {r.name}") for r in related])
        )
        self.page(p.name, "product", body, head=head)

    def news_list(self, page_no: int) -> None:
        arts = site.listed_articles()
        total = site.pages(len(arts), site.NEWS_PAGE_SIZE)
        if page_no > total:
            return self.not_found()
        chunk = arts[(page_no - 1) * site.NEWS_PAGE_SIZE : page_no * site.NEWS_PAGE_SIZE]
        body = self.links([(a.path, a.title) for a in chunk]) + self.pager(
            page_no, total, site.news_page_path
        )
        self.page(f"News - page {page_no}", "news-list", body)

    def article(self, a: site.Article) -> None:
        arts = site.listed_articles()
        nav = []
        if a in arts:
            i = arts.index(a)
            if i > 0:
                nav.append((arts[i - 1].path, "Newer"))
            if i < len(arts) - 1:
                nav.append((arts[i + 1].path, "Older"))
        head = (
            f'<meta property="article:published_time" content="{a.published.isoformat()}">'
            f'<meta property="article:modified_time" content="{a.modified.isoformat()}">'
        )
        body = (
            f'<article><time class="published" datetime="{a.published.isoformat()}">'
            f"{a.published:%Y-%m-%d}</time><p>{_esc(a.title)}. Body text.</p></article>"
            + self.links([("/news/", "All news"), *nav])
        )
        self.page(
            a.title,
            "news",
            body,
            head=head,
            headers={"Last-Modified": format_datetime(a.modified, usegmt=True)},
        )

    def loop(self, path: str) -> None:
        i = site.LOOP_PAGES.index(path)
        nxt = site.LOOP_PAGES[(i + 1) % len(site.LOOP_PAGES)]
        items = [(nxt, "Next in loop"), (path, "Self"), (f"{nxt}/" if nxt == "/loop/b" else nxt, "Variant")]
        self.page(f"Loop {path[-1]}", "loop", self.links(items))

    def calendar(self, ym: str) -> None:
        try:
            year, month = (int(x) for x in ym.split("-"))
            if not 1 <= month <= 12:
                raise ValueError
        except ValueError:
            return self.not_found()
        prev = f"{year - (month == 1)}-{(month - 2) % 12 + 1:02d}"
        nxt = f"{year + (month == 12)}-{month % 12 + 1:02d}"
        body = self.links([(f"/calendar/{prev}", "Previous month"), (f"/calendar/{nxt}", "Next month")])
        self.page(f"Calendar {ym}", "trap", "<p>Infinite calendar (crawler trap).</p>" + body)

    def search(self, term: str, page_no: int) -> None:
        results = site.search_results(term)
        total = site.pages(len(results), site.SEARCH_PAGE_SIZE)
        chunk = results[(page_no - 1) * site.SEARCH_PAGE_SIZE : page_no * site.SEARCH_PAGE_SIZE]
        body = f"<p>{len(results)} result(s) for {_esc(term)!s}</p>" + self.links(
            [(p.path, p.name) for p in chunk]
        )
        if results:
            body += self.pager(page_no, total, lambda n: site.search_page_path(term, n))
        self.page(f"Search: {term}", "search", body)

    # ------------------------------------------------------------------ machine formats
    def _urlset(self, entries: list[tuple[str, str | None]]) -> bytes:
        rows = "".join(
            f"<url><loc>{_esc(self.base + p)}</loc>" + (f"<lastmod>{lm}</lastmod>" if lm else "") + "</url>"
            for p, lm in entries
        )
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{rows}</urlset>\n'
        ).encode()

    def sitemap_index(self) -> None:
        rows = "".join(
            f"<sitemap><loc>{_esc(self.base + s)}</loc></sitemap>"
            for s in ["/sitemaps/products.xml", "/sitemaps/news.xml.gz", "/sitemaps/pages.xml"]
        )
        body = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{rows}</sitemapindex>\n'
        )
        self.send(200, body.encode(), XML)

    def sitemap_products(self) -> None:
        lm = site.BASE_TIME.date().isoformat()
        self.send(200, self._urlset([(p.path, lm) for p in site.PRODUCTS if p.in_sitemap]), XML)

    def sitemap_pages(self) -> None:
        paths = site.STATIC_PAGES + [u.path for u in site.UNKNOWN_PAGES]
        self.send(200, self._urlset([(p, None) for p in paths]), XML)

    def sitemap_news_gz(self) -> None:
        xml = self._urlset([(a.path, a.modified.isoformat()) for a in site.ARTICLES if a.in_sitemap])
        self.send(200, gzip.compress(xml, mtime=0), "application/gzip")

    def rss(self) -> None:
        items = "".join(
            f"<item><title>{_esc(a.title)}</title><link>{_esc(self.base + a.path)}</link>"
            f'<guid isPermaLink="true">{_esc(self.base + a.path)}</guid>'
            f"<pubDate>{format_datetime(a.published, usegmt=True)}</pubDate></item>"
            for a in site.feed_articles()
        )
        body = (
            '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
            f"<title>Jane Test Shop news</title><link>{_esc(self.base)}/</link>"
            f"<description>News</description>{items}</channel></rss>\n"
        )
        self.send(200, body.encode(), "application/rss+xml; charset=utf-8")

    def atom(self) -> None:
        entries = "".join(
            f'<entry><title>{_esc(a.title)}</title><link href="{_esc(self.base + a.path)}"/>'
            f"<id>{_esc(self.base + a.path)}</id><published>{a.published.isoformat()}</published>"
            f"<updated>{a.modified.isoformat()}</updated></entry>"
            for a in site.feed_articles()
        )
        updated = max(a.modified for a in site.ARTICLES).isoformat()
        body = (
            '<?xml version="1.0" encoding="UTF-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom">'
            f"<title>Jane Test Shop news</title><id>{_esc(self.base)}/</id><updated>{updated}</updated>"
            f"{entries}</feed>\n"
        )
        self.send(200, body.encode(), "application/atom+xml; charset=utf-8")

    def _api_item(self, p: site.Product) -> dict[str, Any]:
        return {
            "id": p.slug,
            "url": self.base + p.path,
            "name": p.name,
            "price": p.price,
            "currency": "UAH",
            "availability": p.availability,
            "category": p.category,
        }

    def api_list(self, page_no: int) -> None:
        items = site.api_products()
        total = site.pages(len(items), site.API_PAGE_SIZE)
        chunk = items[(page_no - 1) * site.API_PAGE_SIZE : page_no * site.API_PAGE_SIZE]
        nxt = f"{self.base}/api/v1/products?page={page_no + 1}" if page_no < total else None
        body = {"items": [self._api_item(p) for p in chunk], "page": page_no, "pages": total, "next": nxt}
        self.send(200, json.dumps(body).encode(), "application/json")

    def api_detail(self, p: site.Product) -> None:
        self.send(200, json.dumps(self._api_item(p)).encode(), "application/json")


def make_server(host: str = "127.0.0.1", port: int = 0, *, quiet: bool = True) -> ThreadingHTTPServer:
    handler = type("Handler", (TestSiteHandler,), {"quiet": quiet})
    server = ThreadingHTTPServer((host, port), handler)
    server.daemon_threads = True
    return server


@contextmanager
def serve_in_thread(host: str = "127.0.0.1", port: int = 0) -> Iterator[str]:
    """Run the site in a background thread; yields the base URL (``http://127.0.0.1:<port>``)."""
    server = make_server(host, port)
    thread = threading.Thread(target=server.serve_forever, name="jane-testsite", daemon=True)
    thread.start()
    try:
        yield f"http://{host}:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
