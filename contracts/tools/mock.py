# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml>=6"]
# ///
"""Example-driven mock server for a Jane API (no Node.js required).

    uv run contracts/tools/mock.py <api> [--port 4010] [--host 127.0.0.1] [--list]

<api>: collector | handler | storage | registry | orchestrator | llm | assistant

Behaviour (compatible with Prism's `Prefer` header):
  * route = path template + method from contracts/openapi/<api>.v1.yaml;
  * response = the first example of the lowest 2xx status; choose another with
    `Prefer: code=404` and/or `Prefer: example=<name>`;
  * required headers (e.g. Idempotency-Key) and a JSON body (when required) are checked;
    violations return 422 problem+json; unknown path 404, wrong method 405;
  * 202 responses get `Location: /v1/jobs/<job_id>` from the example Job;
  * CORS is open for local admin development.
Request bodies are NOT validated against schemas: use Prism for that
(npx --yes @stoplight/prism-cli@5.16.0 mock contracts/openapi/<api>.v1.yaml -p 4010).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import API_NAMES, OPENAPI_DIR, deref, iter_operations, load_file  # noqa: E402


class Route:
    def __init__(self, template: str, method: str, op: dict, op_uri: str, item: dict) -> None:
        self.template = template
        self.method = method.upper()
        self.operation_id = op.get("operationId", "")
        pattern = re.sub(r"\\\{[^/]+?\\\}", "[^/]+", re.escape(template))
        self.regex = re.compile(f"^{pattern}$")
        params = [deref(p, op_uri)[0] for p in (item.get("parameters") or []) + (op.get("parameters") or [])]
        self.required_headers = [p["name"] for p in params if p.get("in") == "header" and p.get("required")]
        body = deref(op["requestBody"], op_uri)[0] if op.get("requestBody") else None
        self.body_required = bool(body and body.get("required"))
        self.responses: list[tuple[int, str, list[tuple[str, str, Any]]]] = []
        for code, resp in (op.get("responses") or {}).items():
            if not str(code).isdigit():
                continue
            resp_node, resp_uri = deref(resp, op_uri)
            examples: list[tuple[str, str, Any]] = []
            for mt, media in (resp_node.get("content") or {}).items():
                if "example" in media:
                    examples.append(("example", mt, media["example"]))
                for name, ex in (media.get("examples") or {}).items():
                    ex_node, _ = deref(ex, resp_uri)
                    if isinstance(ex_node, dict) and "value" in ex_node:
                        examples.append((name, mt, ex_node["value"]))
            self.responses.append((int(code), resp_node.get("description", ""), examples))
        self.responses.sort(key=lambda r: r[0])

    def choose(self, prefer: dict[str, str]) -> tuple[int, str | None, Any]:
        wanted_code = int(prefer["code"]) if prefer.get("code", "").isdigit() else None
        wanted_example = prefer.get("example")
        candidates = [r for r in self.responses if (wanted_code is None and 200 <= r[0] < 300) or r[0] == wanted_code]
        if not candidates:
            raise LookupError(f"no response {wanted_code or '2xx'} for {self.operation_id}")
        for code, _desc, examples in candidates:
            for name, mt, value in examples:
                if wanted_example in (None, name):
                    return code, mt, value
        code = candidates[0][0]
        if wanted_example:
            raise LookupError(f"example '{wanted_example}' not found for {self.operation_id} {code}")
        return code, None, None


def load_routes(api: str) -> list[Route]:
    path = OPENAPI_DIR / f"{api}.v1.yaml"
    doc = load_file(path)
    routes = []
    for template, method, op, item_uri, item in iter_operations(doc, path.as_uri()):
        op_uri = item_uri
        routes.append(Route(template, method, op, op_uri, item))
    # literal segments before templated ones (e.g. /v1/jobs/x/cancel vs /v1/jobs/{id})
    routes.sort(key=lambda r: (r.template.count("{"), -len(r.template)))
    return routes


def problem(status: int, code: str, detail: str) -> dict:
    return {"type": f"urn:jane:problem:{code}", "title": code.replace("_", " ").capitalize(),
            "status": status, "code": code, "detail": detail, "retryable": False}


def parse_prefer(header: str | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for part in (header or "").split(","):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip().lower()] = v.strip().strip('"')
    return out


def make_handler(routes: list[Route], api: str):
    class Handler(BaseHTTPRequestHandler):
        server_version = f"jane-mock-{api}/1.0"

        def log_message(self, fmt: str, *args: Any) -> None:  # concise access log
            sys.stderr.write(f"[mock {api}] {self.command} {self.path} -> {fmt % args}\n")

        def _send(self, status: int, body: Any, media_type: str | None, extra: dict[str, str] | None = None) -> None:
            if body is None:
                payload = b""
            elif isinstance(body, (dict, list)) or (media_type or "").endswith("json"):
                payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
            else:
                payload = str(body).encode("utf-8")
            self.send_response(status)
            if payload:
                self.send_header("Content-Type", media_type or "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Expose-Headers", "Location, ETag, Retry-After, Idempotency-Replayed")
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers()
            if payload and self.command != "HEAD":
                self.wfile.write(payload)

        def _problem(self, status: int, code: str, detail: str) -> None:
            self._send(status, problem(status, code, detail), "application/problem+json")

        def do_OPTIONS(self) -> None:  # noqa: N802
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "*")
            self.end_headers()

        def _dispatch(self) -> None:
            path = urlsplit(self.path).path
            matching = [r for r in routes if r.regex.match(path)]
            if not matching:
                return self._problem(404, "not_found", f"no route {path} in {api}.v1.yaml")
            route = next((r for r in matching if r.method == self.command), None)
            if route is None:
                return self._problem(405, "method_not_allowed", f"{self.command} not allowed on {path}")
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length else b""
            missing = [h for h in route.required_headers if not self.headers.get(h)]
            if missing:
                return self._problem(422, "validation_failed", f"missing required header(s): {', '.join(missing)}")
            if route.body_required and not raw:
                return self._problem(422, "validation_failed", "request body is required")
            if raw and "json" in (self.headers.get("Content-Type") or "application/json"):
                try:
                    json.loads(raw)
                except ValueError:
                    return self._problem(400, "bad_request", "request body is not valid JSON")
            try:
                status, media_type, body = route.choose(parse_prefer(self.headers.get("Prefer")))
            except LookupError as exc:
                return self._problem(422, "validation_failed", str(exc))
            extra: dict[str, str] = {}
            if status == 202 and isinstance(body, dict) and body.get("job_id"):
                extra["Location"] = (body.get("links") or {}).get("self") or f"/v1/jobs/{body['job_id']}"
            self._send(status, body, media_type, extra)

        do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = do_HEAD = _dispatch  # noqa: N815

    return Handler


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("api", choices=API_NAMES)
    ap.add_argument("--port", type=int, default=4010)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--list", action="store_true", help="print routes and exit")
    args = ap.parse_args()
    routes = load_routes(args.api)
    if args.list:
        for r in sorted(routes, key=lambda r: (r.template, r.method)):
            codes = ",".join(str(c) for c, _, _ in r.responses)
            print(f"{r.method:7} {r.template:60} {r.operation_id} [{codes}]")
        return 0
    server = ThreadingHTTPServer((args.host, args.port), make_handler(routes, args.api))
    print(f"jane mock '{args.api}' on http://{args.host}:{args.port} ({len(routes)} operations)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
