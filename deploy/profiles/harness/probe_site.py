"""Instrumented HTTP site of the WP-14 limits harness (stdlib only; runs in a python:3.12-slim container).

Every request under ``/s/<ns>/...`` is logged with its server-side start and end time, so request rate,
per-host parallelism, timeouts and retries of a collector are measured *outside* the collector::

    GET /s/<ns>/p/<i>                          small HTML page
    GET /s/<ns>/slow/<i>?ms=<n>                answers after n ms (timeouts, parallelism)
    GET /s/<ns>/flaky/<i>?fail=<n>&status=503  first n requests of this path fail with status, then 200
    GET /s/<ns>/limited/<i>?fail=<n>&retry_after=<s>   first n requests -> 429 + Retry-After
    GET /robots.txt                            allow everything
    GET /_probe/health                         200
    GET /_probe/log?ns=<ns>&after=<seq>        JSON {"events": [...], "last": seq}; times are server epoch seconds
    POST /_probe/reset?ns=<ns>                 forget the events (and failure counters) of a namespace

``python probe_site.py --host 0.0.0.0 --port 8080``. The harness reads the log through the published port.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlsplit

PATH = re.compile(r"^/s/(?P<ns>[a-z0-9-]{1,40})/(?P<kind>p|slow|flaky|limited)/(?P<item>[a-z0-9-]{1,40})$")
MAX_EVENTS = 200_000
MAX_SLOW_MS = 600_000
_EPOCH0, _PERF0 = time.time(), time.perf_counter()


def now() -> float:
    """Epoch seconds with the resolution of ``perf_counter`` (``time.time`` ticks every 15.6 ms on Windows)."""
    return _EPOCH0 + (time.perf_counter() - _PERF0)


class ProbeLog:
    """Thread-safe request log with per-path failure counters."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._events: list[dict[str, Any]] = []
        self._seq = 0
        self._hits: dict[str, int] = {}

    def start(self, ns: str, path: str, query: str, user_agent: str) -> dict[str, Any]:
        with self._lock:
            self._seq += 1
            event = {
                "seq": self._seq,
                "ns": ns,
                "path": path,
                "query": query,
                "start": now(),
                "end": None,
                "status": None,
                "ua": user_agent[:120],
            }
            self._events.append(event)
            del self._events[:-MAX_EVENTS]
            return event

    def hit(self, path: str) -> int:
        """1 for the first request of ``path``, 2 for the second, ..."""
        with self._lock:
            self._hits[path] = self._hits.get(path, 0) + 1
            return self._hits[path]

    def finish(self, event: dict[str, Any], status: int | None) -> None:
        with self._lock:
            event["end"] = now()
            event["status"] = status

    def read(self, ns: str | None, after: int) -> dict[str, Any]:
        with self._lock:
            events = [dict(e) for e in self._events if e["seq"] > after and (ns is None or e["ns"] == ns)]
            return {"events": events, "last": self._seq}

    def reset(self, ns: str | None) -> None:
        with self._lock:
            self._events = [e for e in self._events if ns is not None and e["ns"] != ns]
            prefix = f"/s/{ns}/" if ns else "/"
            self._hits = {k: v for k, v in self._hits.items() if not k.startswith(prefix)}


LOG = ProbeLog()


def _first(query: dict[str, list[str]], name: str) -> str | None:
    values = query.get(name)
    return values[0] if values else None


class Handler(BaseHTTPRequestHandler):
    server_version = "JaneProbe/1"
    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args: Any) -> None:  # quiet: the JSON log is the record
        return

    def _send(self, status: int, body: bytes, ctype: str, headers: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        url = urlsplit(self.path)
        if url.path == "/_probe/reset":
            LOG.reset(_first(parse_qs(url.query), "ns"))
            self._send(200, b'{"ok": true}', "application/json")
        else:
            self._send(404, b"not found", "text/plain")

    def do_GET(self) -> None:
        url = urlsplit(self.path)
        query = parse_qs(url.query)
        if url.path == "/_probe/health":
            self._send(200, b"ok", "text/plain")
        elif url.path == "/_probe/log":
            ns = _first(query, "ns")
            after = int((query.get("after") or ["0"])[0])
            self._send(200, json.dumps(LOG.read(ns, after)).encode(), "application/json")
        elif url.path == "/robots.txt":
            self._send(200, b"User-agent: *\nAllow: /\n", "text/plain")
        elif match := PATH.match(url.path):
            with self._logged(match["ns"], url.path, url.query) as event:
                event["status"] = self._probe(match["kind"], url.path, query)
        else:
            self._send(404, b"not found", "text/plain")

    @contextmanager
    def _logged(self, ns: str, path: str, query: str) -> Iterator[dict[str, Any]]:
        event = LOG.start(ns, path, query, self.headers.get("User-Agent", ""))
        try:
            yield event
        finally:
            LOG.finish(event, event.get("status"))

    def _probe(self, kind: str, path: str, query: dict[str, list[str]]) -> int | None:
        def arg(name: str, default: int) -> int:
            return int((query.get(name) or [str(default)])[0])

        page = f"<!doctype html><html><head><title>{path}</title></head><body><p>{path}</p></body></html>"
        try:
            if kind == "slow":
                time.sleep(min(arg("ms", 1000), MAX_SLOW_MS) / 1000)
            elif kind in {"flaky", "limited"} and LOG.hit(path) <= arg("fail", 1):
                if kind == "limited":
                    headers = {"Retry-After": str(arg("retry_after", 1))}
                    self._send(429, b"slow down", "text/plain", headers)
                    return 429
                status = arg("status", 503)
                self._send(status, b"unavailable", "text/plain")
                return status
            self._send(200, page.encode(), "text/html; charset=utf-8")
            return 200
        except (BrokenPipeError, ConnectionResetError):
            return None  # the client gave up (timeout) - recorded as status None


class ProbeServer(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request: Any, client_address: Any) -> None:
        """A client that closes a keep-alive connection or gives up (timeout) is normal here."""
        if isinstance(sys.exc_info()[1], ConnectionError):
            return
        super().handle_error(request, client_address)


def make_server(host: str = "127.0.0.1", port: int = 0) -> ThreadingHTTPServer:
    return ProbeServer((host, port), Handler)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8080)
    ns = ap.parse_args()
    make_server(ns.host, ns.port).serve_forever()


if __name__ == "__main__":
    main()
