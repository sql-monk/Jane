"""STAND-IN (Т) for a controllable price change on the test site (requested from WP-01) - S-M2-04 only.

The test site (``tests/fixtures/testsite``) renders a fixed product model, so a shop that changes a price
between the catalog and the price check cannot be reproduced with it. This launcher runs the UNCHANGED
``jane_testsite`` server inside the testsite container of one isolated e2e stack (``compose.prices.yaml``) and
adds a control path that the crawler never sees (nothing links to it):

* ``PUT /_e2e/products/{slug}`` - JSON with any of ``price`` (``"279.00"``), ``availability``
  (``InStock`` / ``OutOfStock`` / ``PreOrder``) and ``name``; replaces that product in the in-memory model,
  so product pages, JSON-LD, microdata and the JSON API show the new values (and a new ``ETag``);
* ``GET /_e2e/products/{slug}`` - the product as the model holds it now.

Every other request is served by ``jane_testsite.server.TestSiteHandler`` as usual. Standard library only:

    python testsite_prices.py [--host H] [--port P]
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import re
import threading
from http.server import ThreadingHTTPServer
from typing import Any

from jane_testsite import site  # type: ignore[import-untyped]
from jane_testsite.server import TestSiteHandler  # type: ignore[import-untyped]

CONTROL = re.compile(r"^/_e2e/products/(?P<slug>[a-z0-9-]+)$")
FIELDS = frozenset({"price", "availability", "name"})
AVAILABILITY = frozenset({"InStock", "OutOfStock", "PreOrder"})
PRICE = re.compile(r"^\d+\.\d{2}$")
_lock = threading.Lock()


def product_json(product: Any) -> bytes:
    keys = ("slug", "name", "category", "price", "availability")
    return json.dumps({k: getattr(product, k) for k in keys}).encode()


def change_product(slug: str, changes: dict[str, Any]) -> Any:
    """Replace one product of ``site.PRODUCTS`` in place (the server looks products up on every request)."""
    unknown = sorted(set(changes) - FIELDS)
    if unknown or not changes:
        raise ValueError(f"only {sorted(FIELDS)} can be changed, got {sorted(changes)}")
    if "price" in changes and not PRICE.match(str(changes["price"])):
        raise ValueError(f"price must look like 279.00, got {changes['price']!r}")
    if "availability" in changes and changes["availability"] not in AVAILABILITY:
        raise ValueError(f"availability must be one of {sorted(AVAILABILITY)}")
    with _lock:
        for i, product in enumerate(site.PRODUCTS):
            if product.slug == slug:
                site.PRODUCTS[i] = dataclasses.replace(product, **{k: str(v) for k, v in changes.items()})
                return site.PRODUCTS[i]
    raise LookupError(slug)


class PricesHandler(TestSiteHandler):  # type: ignore[misc]
    def _control(self) -> str | None:
        match = CONTROL.match(self.path.split("?", 1)[0])
        return match["slug"] if match else None

    def _json(self, status: int, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        slug = self._control()
        if slug is None:
            super().do_GET()
            return
        product = site.product_by_slug(slug)
        if product is None:
            self._json(404, b'{"error": "unknown product"}')
        else:
            self._json(200, product_json(product))

    def do_PUT(self) -> None:
        slug = self._control()
        if slug is None:
            self._json(404, b'{"error": "not a control path"}')
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
            changes = json.loads(self.rfile.read(length) or b"{}")
            if not isinstance(changes, dict):
                raise ValueError("body must be a JSON object")
            product = change_product(slug, changes)
        except LookupError:
            self._json(404, b'{"error": "unknown product"}')
        except ValueError as exc:
            self._json(422, json.dumps({"error": str(exc)}).encode())
        else:
            print(f"e2e price switch: {product_json(product).decode()}", flush=True)
            self._json(200, product_json(product))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8080)
    ns = ap.parse_args()
    server = ThreadingHTTPServer((ns.host, ns.port), PricesHandler)
    server.daemon_threads = True
    print(f"Jane testsite with the e2e price switch on http://{ns.host}:{ns.port}/", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
