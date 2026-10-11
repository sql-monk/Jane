"""POST body pagination must reach the final page without reusing or mutating request bodies."""

from __future__ import annotations

import importlib
import json
import threading
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

import pytest

from jane_web_collector.testing import FAST_LIMITS, Site, drain, start, wait_done, web_rules


@pytest.fixture
def classes(discovery):
    module = importlib.import_module(discovery.__name__ + ".api_feed")
    return module.ApiFeedStrategy, module.UnsupportedConfig


def config(**overrides):
    return {
        "type": "api_feed",
        "url": "https://shop.example.test/api/graphql",
        "method": "POST",
        "body": {"query": "query Products", "variables": {"page": 3, "pageSize": 48}},
        "items_path": "$.items",
        "url_path": "$.url",
        "pagination": {"type": "page", "page_param": "page", "body_page_path": "$.variables.page"},
        **overrides,
    }


def test_distinct_body_pages_keep_initial_config_and_prior_request_unchanged(classes):
    strategy_type, _ = classes
    settings = config()
    original = deepcopy(settings)
    strategy = strategy_type(settings, "products")
    url = strategy.url
    requests = []
    for _ in range(3):
        requests.append(strategy.page_body(url))
        url = strategy.next_page({}, url, 48, set())
    assert [r["variables"]["page"] for r in requests] == [3, 4, 5]
    assert all(r["variables"]["pageSize"] == 48 for r in requests)
    assert settings == original
    assert strategy.next_page({}, url, 0, set()) is None


@pytest.mark.parametrize(("method", "pagination"), [("GET", "page"), ("POST", "none")])
def test_body_page_path_rejects_inapplicable_pagination(classes, method, pagination):
    strategy_type, unsupported_error = classes
    settings = config(method=method)
    settings["pagination"]["type"] = pagination
    with pytest.raises(unsupported_error):
        strategy_type(settings, "products")


@pytest.mark.parametrize("value", [0, -1, True, "1", None])
def test_body_page_path_rejects_invalid_initial_page(classes, value):
    strategy_type, _ = classes
    settings = config()
    settings["body"]["variables"]["page"] = value
    with pytest.raises(ValueError, match="positive integer"):
        strategy_type(settings, "products")


def test_missing_body_page_path_is_rejected(classes):
    strategy_type, _ = classes
    settings = config(body={"variables": {}})
    with pytest.raises(ValueError, match="existing field"):
        strategy_type(settings, "products")


def test_initial_url_page_overrides_body_without_mutation(classes):
    strategy_type, _ = classes
    settings = config(url="https://shop.example.test/api/graphql?page=5")
    strategy = strategy_type(settings, "products")
    assert strategy.page_body(strategy.url)["variables"]["page"] == 5
    assert settings["body"]["variables"]["page"] == 3


@pytest.mark.parametrize("page", ["0", "-1", "text"])
def test_invalid_url_page_is_rejected(classes, page):
    strategy_type, _ = classes
    with pytest.raises(ValueError, match="URL page number"):
        strategy_type(config(url=f"https://shop.example.test/api/graphql?page={page}"), "products")


@pytest.mark.parametrize("pagination", ["page", "cursor"])
def test_partitions_and_body_paging_reach_children_and_clamped_tail_over_real_http(client, pagination):
    requests = []
    data = {
        ("root", 1): (["shared"], ["branch", "root"]),
        ("root", 2): ([], []),
        ("branch", 1): (["shared", "b1"], ["empty"]),
        ("branch", 2): (["b2"], []),
        ("branch", 3): (["b2"], []),
        ("empty", 1): ([], ["leaf"]),
        ("leaf", 1): (["leaf1"], []),
        ("leaf", 2): ([], []),
    }

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            self.send_response(200 if self.path == "/robots.txt" else 404)
            self.end_headers()
            self.wfile.write(b"User-agent: *\nAllow: /\n")

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            category = body["variables"]["id"]
            page = (
                body["variables"]["page"]
                if pagination == "page"
                else int(parse_qs(urlsplit(self.path).query).get("after", ["1"])[0])
            )
            requests.append((category, page, self.path, body))
            products, children = data[(category, page)]
            payload = {
                "category": {
                    "children": [{"id": c} for c in children],
                    "products": {
                        "items": [{"url": f"p/{p}", "price": 12.5} for p in products],
                        "cursor": str(page + 1) if products else None,
                    },
                }
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode())

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    site = Site(base=f"http://127.0.0.1:{server.server_address[1]}")
    body = {"variables": {"id": "root", "page": 1}}
    strategy = {
        "type": "api_feed",
        "url": site.url("/api/graphql"),
        "item_url_base": site.url("/"),
        "method": "POST",
        "body": body,
        "items_path": "$.category.products.items[*]",
        "url_path": "$.url",
        "emit_items_as_materials": True,
        "pagination": {"type": "page", "page_param": "page", "body_page_path": "$.variables.page"},
        "partitions": {
            "items_path": "$.category.children[*].id",
            "body_path": "$.variables.id",
            "url_param": "category",
        },
    }
    if pagination == "cursor":
        strategy["pagination"] = {
            "type": "cursor",
            "cursor_param": "after",
            "cursor_path": "$.category.products.cursor",
        }
    try:
        rules = web_rules(site, strategies=[strategy])
        cid = start(
            client, {"source_kind": "web", "source_id": "partitioned", "rules": rules, "limits": FAST_LIMITS}
        )
        records = drain(client, cid)
        assert wait_done(client, cid)["status"] == "succeeded"
        assert {urlsplit(m["locator"]["url"]).path for m in records} == {
            "/p/shared",
            "/p/b1",
            "/p/b2",
            "/p/leaf1",
        }
        assert len(records) == 4
        assert [(c, p) for c, p, _, _ in requests] == list(data)
        assert all(parse_qs(urlsplit(url).query)["category"] == [c] for c, _, url, _ in requests)
        parameter = "page" if pagination == "page" else "after"
        assert all(
            parse_qs(urlsplit(url).query).get(parameter, ["1"]) == [str(p)] for _, p, url, _ in requests
        )
        assert body == {"variables": {"id": "root", "page": 1}}
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
