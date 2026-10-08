"""STAND-IN (Т) for the handler registry (WP-05) until it is merged: serves archives of LOCAL packages.

Only one operation of registry.v1 is implemented - ``GET /v1/packages/{id}/versions/{v}/archive``
(``application/zip``, ``ETag: "sha256:…"``) - because the orchestrator does not send ``package_archive`` and
handler-runtime otherwise takes the package from the registry (``JANE_HANDLER_RUNTIME_REGISTRY_URL``).
Plan.md §6 defines M1 with extraction by a *local* package, so this host is how the local archive reaches
the runtime in orchestrated scenarios. It is NOT evidence for criteria 7/9 (registry); those wait for WP-05.

Layout: ``<root>/<package_id>/<version>.zip`` (written by the e2e harness).

Second role, SUBSTITUTE (З) of a blob store's ``download_url`` (ContentRef ``kind: blob``, ADR-0004) for R-04
"replay while the work is still running" (``tests/e2e/test_r04_active_replays.py``). A *gate* holds a
download open until the test releases it, so a service that reads material content is provably inside its
work while the test replays the request - no timing guesses:

* ``PUT  /e2e/gates/{gate}``          body = content (``Content-Type`` kept); creates or resets the gate;
* ``GET  /e2e/gates/{gate}/content``  the download: waits until the gate is released, then serves the content
  (``504`` if not released within ``?max_wait_s=``, default :data:`MAX_WAIT_S`);
* ``POST /e2e/gates/{gate}/release``  lets every waiting and later download through;
* ``GET  /e2e/gates/{gate}``          JSON ``{"requests", "waiting", "served", "released"}`` - how many downloads
  started, are held now and were served (a second execution of the same work would download again).

Standard library only:

    python package_host.py <root> [port]
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import threading
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ARCHIVE = re.compile(
    r"^/v1/packages/(?P<pid>[a-z0-9][a-z0-9._-]*)/versions/(?P<ver>[A-Za-z0-9.+_-]+)/archive$"
)
GATE = re.compile(r"^/e2e/gates/(?P<gate>[A-Za-z0-9._-]{1,128})(?P<action>/content|/release)?$")
MAX_WAIT_S = 300.0  # upper bound of one held download; a scenario releases its gate long before
NOT_FOUND = b'{"type":"urn:jane:problem:not_found","title":"Not found","status":404,"code":"not_found"}'


@dataclass
class Gate:
    content: bytes
    media_type: str
    released: threading.Event = field(default_factory=threading.Event)
    requests: int = 0
    waiting: int = 0
    served: int = 0

    def status(self) -> dict[str, object]:
        return {
            "requests": self.requests,
            "waiting": self.waiting,
            "served": self.served,
            "released": self.released.is_set(),
        }


def make_handler(root: Path) -> type[BaseHTTPRequestHandler]:
    gates: dict[str, Gate] = {}
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            url = urlsplit(self.path)
            if url.path == "/v1/health":
                self._send(200, b'{"status":"ok"}', "application/json")
                return
            if g := GATE.match(url.path):
                self._gate_get(g["gate"], g["action"], parse_qs(url.query))
                return
            m = ARCHIVE.match(url.path)
            file = root / m["pid"] / f"{m['ver']}.zip" if m else None
            if file is None or not file.is_file():
                self._send(404, NOT_FOUND, "application/problem+json")
                return
            data = file.read_bytes()
            etag = '"sha256:' + hashlib.sha256(data).hexdigest() + '"'
            self._send(200, data, "application/zip", {"ETag": etag})

        def do_PUT(self) -> None:
            g = GATE.match(urlsplit(self.path).path)
            if g is None or g["action"]:
                self._send(404, NOT_FOUND, "application/problem+json")
                return
            length = int(self.headers.get("Content-Length") or 0)
            gate = Gate(
                self.rfile.read(length), self.headers.get("Content-Type") or "application/octet-stream"
            )
            with lock:
                gates[g["gate"]] = gate
                status = gate.status()
            self._json(201, status)

        def do_POST(self) -> None:
            g = GATE.match(urlsplit(self.path).path)
            gate = gates.get(g["gate"]) if g and g["action"] == "/release" else None
            if gate is None:
                self._send(404, NOT_FOUND, "application/problem+json")
                return
            gate.released.set()
            with lock:
                status = gate.status()
            self._json(200, status)

        def _gate_get(self, name: str, action: str | None, query: dict[str, list[str]]) -> None:
            gate = gates.get(name)
            if gate is None:
                self._send(404, NOT_FOUND, "application/problem+json")
                return
            if action is None:
                with lock:
                    status = gate.status()
                self._json(200, status)
                return
            if action != "/content":
                self._send(404, NOT_FOUND, "application/problem+json")
                return
            max_wait = float((query.get("max_wait_s") or [str(MAX_WAIT_S)])[0])
            with lock:
                gate.requests += 1
                gate.waiting += 1
            released = gate.released.wait(max_wait)
            with lock:
                gate.waiting -= 1
                if released:
                    gate.served += 1
            if not released:
                self._send(504, b"gate was not released", "text/plain")
                return
            self._send(200, gate.content, gate.media_type)

        def _json(self, status: int, doc: dict[str, object]) -> None:
            self._send(status, json.dumps(doc).encode(), "application/json")

        def _send(self, status: int, body: bytes, ctype: str, headers: dict[str, str] | None = None) -> None:
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            for k, v in (headers or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

    return Handler


def main() -> None:
    root = Path(sys.argv[1])
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    ThreadingHTTPServer(("0.0.0.0", port), make_handler(root)).serve_forever()


if __name__ == "__main__":
    main()
