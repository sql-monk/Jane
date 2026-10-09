"""Instrument the REAL testsite HTTP handler for L2 / R15; never emulate the collector.

Only requests with a ``JaneHostProbe/`` User-Agent are measured. Product pages and robots.txt are served by
``jane_testsite.server.TestSiteHandler``; delays and a releasable gate make concurrent requests and a killed
download observable. Control requests and Docker health checks are excluded from the measurements.
"""

from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass, field
from http.server import ThreadingHTTPServer
from typing import Any
from urllib.parse import urlsplit

from jane_testsite.server import TestSiteHandler

CONTROL = "/_e2e/host-probe"
PREFIX = "JaneHostProbe/"
GATE_TIMEOUT_S = float(os.environ.get("JANE_E2E_HOST_PROBE_GATE_TIMEOUT_S", "120"))


@dataclass
class Probe:
    lock: threading.Lock = field(default_factory=threading.Lock)
    events: list[dict[str, Any]] = field(default_factory=list)
    marks: dict[str, float] = field(default_factory=dict)
    delays: dict[str, float] = field(default_factory=dict)
    gates: dict[str, threading.Event] = field(default_factory=dict)

    def snapshot(self) -> dict[str, Any]:
        with self.lock:
            return {"events": [dict(event) for event in self.events], "marks": dict(self.marks)}


PROBE = Probe()


class HostProbeHandler(TestSiteHandler):
    def do_PUT(self) -> None:
        if urlsplit(self.path).path != CONTROL:
            return super().do_PUT()
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        with PROBE.lock:
            if "marker" in body:
                marker = str(body["marker"])
                PROBE.delays[marker] = float(body.get("delay_s", 0))
                if body.get("gate"):
                    PROBE.gates[marker] = threading.Event()
            if "release" in body:
                PROBE.gates[str(body["release"])].set()
            if "mark" in body:
                PROBE.marks[str(body["mark"])] = time.monotonic()
        self.send(200, json.dumps(PROBE.snapshot()).encode(), "application/json")

    def do_GET(self) -> None:
        if urlsplit(self.path).path == CONTROL:
            return self.send(200, json.dumps(PROBE.snapshot()).encode(), "application/json")
        marker = self.headers.get("User-Agent", "")
        if not marker.startswith(PREFIX):
            return super().do_GET()
        with PROBE.lock:
            event = {"marker": marker, "path": self.path, "started": time.monotonic(), "ended": None}
            PROBE.events.append(event)
            # Keep robots.txt unblocked: the gate must hold the actual product download.
            page = urlsplit(self.path).path != "/robots.txt"
            delay = PROBE.delays.get(marker, 0) if page else 0
            gate = PROBE.gates.get(marker) if page else None
        try:
            if gate is not None and not gate.wait(timeout=GATE_TIMEOUT_S):
                return self.send(504, b"probe gate timed out", "text/plain")
            if delay:
                time.sleep(delay)
            super().do_GET()
        except (BrokenPipeError, ConnectionResetError):
            pass  # The kill scenario deliberately disconnects a download.
        finally:
            with PROBE.lock:
                event["ended"] = time.monotonic()


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 8080), HostProbeHandler)
    server.daemon_threads = True
    server.serve_forever()
