"""STAND-IN (Т) for the handler registry (WP-05) until it is merged: serves archives of LOCAL packages.

Only one operation of registry.v1 is implemented - ``GET /v1/packages/{id}/versions/{v}/archive``
(``application/zip``, ``ETag: "sha256:…"``) - because the orchestrator does not send ``package_archive`` and
handler-runtime otherwise takes the package from the registry (``JANE_HANDLER_RUNTIME_REGISTRY_URL``).
Plan.md §6 defines M1 with extraction by a *local* package, so this host is how the local archive reaches
the runtime in orchestrated scenarios. It is NOT evidence for criteria 7/9 (registry); those wait for WP-05.

Layout: ``<root>/<package_id>/<version>.zip`` (written by the e2e harness). Standard library only:

    python package_host.py <root> [port]
"""

from __future__ import annotations

import hashlib
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ARCHIVE = re.compile(
    r"^/v1/packages/(?P<pid>[a-z0-9][a-z0-9._-]*)/versions/(?P<ver>[A-Za-z0-9.+_-]+)/archive$"
)


def make_handler(root: Path) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            path = self.path.split("?", 1)[0]
            if path == "/v1/health":
                self._send(200, b'{"status":"ok"}', "application/json")
                return
            m = ARCHIVE.match(path)
            file = root / m["pid"] / f"{m['ver']}.zip" if m else None
            if file is None or not file.is_file():
                body = b'{"type":"urn:jane:problem:not_found","title":"Not found","status":404,"code":"not_found"}'
                self._send(404, body, "application/problem+json")
                return
            data = file.read_bytes()
            etag = '"sha256:' + hashlib.sha256(data).hexdigest() + '"'
            self._send(200, data, "application/zip", {"ETag": etag})

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
