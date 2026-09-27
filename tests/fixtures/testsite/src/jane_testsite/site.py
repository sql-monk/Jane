"""Deterministic content model of the test site and the expected URL sets derived from it.

Everything the server renders comes from here, so the expected sets (``expected()``) cannot drift
from what is served. Paths are root-relative; absolute URLs are built from the request host.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from math import ceil
from typing import Any

CATEGORY_PAGE_SIZE = 3
NEWS_PAGE_SIZE = 3
SEARCH_PAGE_SIZE = 3
API_PAGE_SIZE = 5
ARCHIVE_PAGES = 5
BASE_TIME = datetime(2026, 9, 1, 9, 0, tzinfo=UTC)


@dataclass(frozen=True)
class Product:
    slug: str
    name: str
    category: str
    price: str
    availability: str = "InStock"
    listed: bool = True  # linked from category pages (and therefore reachable by recursion)
    in_sitemap: bool = True
    in_api: bool = True
    searchable: bool = True

    @property
    def path(self) -> str:
        return f"/product/{self.slug}"


@dataclass(frozen=True)
class Article:
    slug: str
    title: str
    day: int
    edited_day: int | None = None
    listed: bool = True  # on /news/ listing pages
    in_sitemap: bool = True
    in_feed: bool = True

    @property
    def path(self) -> str:
        return f"/news/2026/{self.slug}"

    @property
    def published(self) -> datetime:
        return BASE_TIME + timedelta(days=self.day)

    @property
    def modified(self) -> datetime:
        return BASE_TIME + timedelta(days=self.edited_day if self.edited_day is not None else self.day)


@dataclass(frozen=True)
class UnknownPage:
    slug: str
    title: str
    body: str

    @property
    def path(self) -> str:
        return f"/pages/{self.slug}"


CATEGORIES: dict[str, str] = {"phones": "Phones", "laptops": "Laptops", "accessories": "Accessories"}

PRODUCTS: list[Product] = [
    Product("phone-alpha", "Phone Alpha", "phones", "299.00"),
    Product("phone-beta", "Phone Beta", "phones", "349.00"),
    Product("phone-gamma", "Phone Gamma", "phones", "399.00", "OutOfStock"),
    Product("phone-delta", "Phone Delta", "phones", "449.00"),
    Product("phone-epsilon", "Phone Epsilon", "phones", "499.00"),
    Product("phone-zeta", "Phone Zeta", "phones", "549.00", "PreOrder"),
    Product("phone-eta", "Phone Eta", "phones", "599.00"),
    Product("laptop-one", "Laptop One", "laptops", "899.00"),
    Product("laptop-two", "Laptop Two", "laptops", "999.00"),
    Product("laptop-three", "Laptop Three", "laptops", "1099.00"),
    Product("laptop-four", "Laptop Four", "laptops", "1199.00", "OutOfStock"),
    Product("laptop-five", "Laptop Five", "laptops", "1299.00"),
    Product("case-red", "Phone Case Red", "accessories", "19.00"),
    Product("charger-fast", "Fast Charger", "accessories", "29.00"),
    Product("headphones-pro", "Headphones Pro", "accessories", "149.00"),
    Product("stand-desk", "Desk Stand", "accessories", "39.00"),
    # Discoverable by exactly one non-recursive strategy:
    Product(
        "sitemap-only-widget",
        "Sitemap Widget",
        "accessories",
        "9.00",
        listed=False,
        in_api=False,
        searchable=False,
    ),
    Product(
        "api-only-gadget",
        "API Gadget",
        "accessories",
        "59.00",
        listed=False,
        in_sitemap=False,
        searchable=False,
    ),
    Product(
        "search-only-cable",
        "Hidden Cable",
        "accessories",
        "5.00",
        listed=False,
        in_sitemap=False,
        in_api=False,
    ),
]

ARTICLES: list[Article] = [
    Article("launch-alpha", "Phone Alpha launched", 1),
    Article("price-drop-laptops", "Price drop on laptops", 2, edited_day=5),
    Article("store-opening", "New store opening", 3),
    Article("holiday-hours", "Holiday opening hours", 4),
    Article("review-headphones", "Headphones Pro review", 5, edited_day=6),
    Article("warranty-update", "Warranty terms updated", 6),
    Article("recycling-program", "Recycling program", 7),
    Article("autumn-sale", "Autumn sale starts", 8),
    # Only in RSS/Atom feeds:
    Article("feed-only-announcement", "Feed-only announcement", 9, listed=False, in_sitemap=False),
]

UNKNOWN_PAGES: list[UnknownPage] = [
    UnknownPage("event-spring-meetup", "Spring meetup", "Event: 2026-10-10 18:00, Kyiv, free entrance."),
    UnknownPage("careers", "Careers", "Job posting: Warehouse operator, full time."),
    UnknownPage("faq", "FAQ", "Questions and answers about delivery and returns."),
]

STATIC_PAGES = ["/", "/about", "/catalog/", "/news/"]
LOOP_PAGES = ["/loop/a", "/loop/b", "/loop/c"]
PRIVATE_PAGES = ["/private/admin", "/private/reports"]
REDIRECTS = {"/old/catalog": "/catalog/", "/loop/b/": "/loop/b", "/about/": "/about"}
BROKEN_LINKS = ["/missing-page"]
FILES = {"/files/price-list.pdf": b"%PDF-1.4\n% Jane testsite fixture\n%%EOF\n"}
EXTERNAL_LINKS = [
    "https://external.example.org/partner",
    "https://external.example.org/catalog/phones/",
    "http://cdn.external.example.net/banner.png",
]
NON_HTTP_LINKS = ["mailto:info@example.org", "tel:+380000000000", "javascript:void(0)"]
POPULAR_SEARCH = "phone"
TRAP_PREFIX = "/calendar/"
TRAP_START = "/calendar/2026-09"


def listed_products(category: str | None = None) -> list[Product]:
    return [p for p in PRODUCTS if p.listed and (category is None or p.category == category)]


def pages(total: int, size: int) -> int:
    return max(1, ceil(total / size))


def category_page_path(category: str, page: int) -> str:
    return f"/catalog/{category}/" if page == 1 else f"/catalog/{category}/?page={page}"


def news_page_path(page: int) -> str:
    return "/news/" if page == 1 else f"/news/page/{page}/"


def search_results(term: str) -> list[Product]:
    t = term.strip().lower()
    return [p for p in PRODUCTS if p.searchable and t and (t in p.name.lower() or t in p.slug)]


def search_page_path(term: str, page: int) -> str:
    return f"/search?q={term}" if page == 1 else f"/search?q={term}&page={page}"


def api_products() -> list[Product]:
    return [p for p in PRODUCTS if p.in_api]


def listed_articles() -> list[Article]:
    return sorted((a for a in ARTICLES if a.listed), key=lambda a: a.day, reverse=True)


def feed_articles() -> list[Article]:
    return sorted((a for a in ARTICLES if a.in_feed), key=lambda a: a.day, reverse=True)


def product_by_slug(slug: str) -> Product | None:
    return next((p for p in PRODUCTS if p.slug == slug), None)


def article_by_slug(slug: str) -> Article | None:
    return next((a for a in ARTICLES if a.slug == slug), None)


@dataclass
class Expected:
    """Expected URL sets per discovery strategy (root-relative paths, sorted in ``as_dict``)."""

    sets: dict[str, set[str]] = field(default_factory=dict)
    info: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {"sets": {k: sorted(v) for k, v in sorted(self.sets.items())}, **self.info}


def expected() -> Expected:
    cat_pages = {
        category_page_path(c, n)
        for c in CATEGORIES
        for n in range(1, pages(len(listed_products(c)), CATEGORY_PAGE_SIZE) + 1)
    }
    listed = {p.path for p in listed_products()}
    news_pages = {news_page_path(n) for n in range(1, pages(len(listed_articles()), NEWS_PAGE_SIZE) + 1)}
    articles = {a.path for a in listed_articles()}
    popular = search_results(POPULAR_SEARCH)
    popular_pages = {
        search_page_path(POPULAR_SEARCH, n) for n in range(1, pages(len(popular), SEARCH_PAGE_SIZE) + 1)
    }
    unknown = {u.path for u in UNKNOWN_PAGES}

    recursive = (
        set(STATIC_PAGES)
        | cat_pages
        | listed
        | news_pages
        | articles
        | popular_pages
        | {p.path for p in popular}
        | unknown
        | set(LOOP_PAGES)
        | set(FILES)
    )
    sitemap = (
        {p.path for p in PRODUCTS if p.in_sitemap}
        | {a.path for a in ARTICLES if a.in_sitemap}
        | set(STATIC_PAGES)
        | unknown
    )
    feeds = {a.path for a in feed_articles()}
    categories = cat_pages | listed
    api = {p.path for p in api_products()}
    cable = search_results("cable")
    search_cable = {search_page_path("cable", n) for n in range(1, pages(len(cable), SEARCH_PAGE_SIZE) + 1)}
    archive = {f"/archive/{n}" for n in range(1, ARCHIVE_PAGES + 1)}

    page_types: dict[str, str] = {}
    page_types.update({p.path: "product" for p in PRODUCTS})
    page_types.update({a.path: "news" for a in ARTICLES})
    page_types.update({u: "unknown" for u in unknown})
    page_types.update({c: "category" for c in cat_pages})
    page_types.update({n: "news-list" for n in news_pages})

    return Expected(
        sets={
            "recursive": recursive,
            "sitemap": sitemap,
            "feeds": feeds,
            "categories": categories,
            "api": api,
            "search:cable": search_cable | {p.path for p in cable},
            "search:phone": popular_pages | {p.path for p in popular},
            "template:/archive/{n}": archive,
            "robots_disallowed": set(PRIVATE_PAGES),
            "broken": set(BROKEN_LINKS),
            "only:sitemap": {"/product/sitemap-only-widget"},
            "only:api": {"/product/api-only-gadget"},
            "only:search": {"/product/search-only-cable"},
            "only:feeds": {"/news/2026/feed-only-announcement"},
            "only:template": archive,
        },
        info={
            "entry": "/",
            "robots": "/robots.txt",
            "sitemap_index": "/sitemap.xml",
            "sitemaps": ["/sitemaps/products.xml", "/sitemaps/news.xml.gz", "/sitemaps/pages.xml"],
            "feeds": {"rss": "/feeds/news.rss", "atom": "/feeds/news.atom"},
            "api": {"list": "/api/v1/products?page={n}", "detail": "/api/v1/products/{slug}"},
            "search": "/search?q={term}&page={n}",
            "url_template": "/archive/{n}",
            "trap_prefix": TRAP_PREFIX,
            "redirects": REDIRECTS,
            "external_links": EXTERNAL_LINKS,
            "non_http_links": NON_HTTP_LINKS,
            "tracking_params": ["utm_source", "utm_medium"],
            "page_types": dict(sorted(page_types.items())),
        },
    )
