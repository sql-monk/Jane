"""In-sandbox runner: ``python -I -m jane_extractor_sdk.runner <workdir>``.

Protocol (version 1) between handler-runtime and the sandbox, all files inside ``<workdir>`` (read-only):

``request.json``::

    {"protocol": 1,
     "entry": {"module": "product_extractor.main", "callable": "extract"},
     "package_dir": "package",                  # unpacked package; <package_dir>/src is put on sys.path
     "params": {...}, "test_mode": false,
     "inputs": [{"input": <HandlerInput>, "content_file": "inputs/0.bin" | null}]}

The runner writes exactly one JSON document to the original stdout (user ``print`` goes to stderr)::

    {"protocol": 1,
     "results": [<ExtractResult> | {"error": {"type", "message", "traceback", "stage"}}],   # one per input
     "violations": [{"kind": "network" | "process", "event": "...", "detail": "...", "input": 0}],
     "metrics": {"cpu_ms": 12, "peak_memory_mb": 31.5}}

Violations are *recorded* through an audit hook for diagnostics only; the boundary itself is the sandbox
(no network namespace, read-only FS, limits). The runner never raises for extractor errors: the runtime
decides the final status (``failed`` with ``execution_error`` / ``sandbox_violation`` / ``schema_mismatch``).
"""

from __future__ import annotations

import functools
import importlib
import json
import os
import sys
import time
import traceback
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from .context import Context

__all__ = ["PROTOCOL_VERSION", "execute", "main"]

PROTOCOL_VERSION = 1
STATUSES = ("success", "empty", "unrecognized")
NETWORK_EVENTS = frozenset(
    {"socket.connect", "socket.getaddrinfo", "socket.gethostbyname", "socket.sendto", "socket.bind"}
)
PROCESS_EVENTS = frozenset(
    {"subprocess.Popen", "os.system", "os.posix_spawn", "os.exec", "os.fork", "os.spawn"}
)
MAX_TRACEBACK_CHARS = 8000
MAX_VIOLATIONS = 50


class _Recorder:
    def __init__(self) -> None:
        self.current_input: int | None = None
        self.violations: list[dict[str, Any]] = []

    def hook(self, event: str, args: tuple[Any, ...]) -> None:
        if event in NETWORK_EVENTS:
            kind = "network"
        elif event in PROCESS_EVENTS:
            kind = "process"
        else:
            return
        if len(self.violations) < MAX_VIOLATIONS:
            self.violations.append(
                {"kind": kind, "event": event, "detail": repr(args)[:300], "input": self.current_input}
            )


def _error(stage: str, exc: BaseException) -> dict[str, Any]:
    tb = "".join(traceback.format_exception(exc))
    return {
        "error": {
            "stage": stage,
            "type": type(exc).__name__,
            "message": str(exc)[:4000],
            "traceback": tb[-MAX_TRACEBACK_CHARS:],
        }
    }


def _normalize(value: Any, log_messages: list[Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"extractor must return a mapping (ExtractResult), got {type(value).__name__}")
    status = value.get("status")
    if status not in STATUSES:
        raise ValueError(
            f"invalid status {status!r}; expected one of {STATUSES} (raise an exception to fail)"
        )
    out = dict(value)
    diags = list(out.get("diagnostics") or [])
    if log_messages:
        diags = [*log_messages, *diags]
    if diags:
        out["diagnostics"] = diags
    json.dumps(out, allow_nan=False)  # must be plain JSON
    return out


def _metrics() -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    try:
        resource: Any = importlib.import_module("resource")  # Unix only
        usage = resource.getrusage(resource.RUSAGE_SELF)
        metrics["cpu_ms"] = int((usage.ru_utime + usage.ru_stime) * 1000)
        metrics["peak_memory_mb"] = round(usage.ru_maxrss / 1024, 1)  # KiB on Linux
    except (ImportError, OSError):
        pass
    for name in ("memory.peak", "memory.max_usage_in_bytes"):  # cgroup v2 / v1 of the sandbox container
        try:
            metrics["peak_memory_mb"] = round(int(Path("/sys/fs/cgroup", name).read_text()) / 2**20, 1)
            break
        except (OSError, ValueError):
            continue
    return metrics


def execute(
    request: Mapping[str, Any],
    workdir: Path,
    *,
    recorder: _Recorder | None = None,
) -> dict[str, Any]:
    """Run the entry callable for every input of ``request``; return the protocol response."""
    recorder = recorder or _Recorder()
    package_dir = (workdir / str(request.get("package_dir", "package"))).resolve()
    src = package_dir / "src"
    for path in (str(src), str(package_dir)):
        if path not in sys.path:
            sys.path.insert(0, path)
    entry = request["entry"]
    params = dict(request.get("params") or {})
    inputs = list(request.get("inputs") or [])
    results: list[dict[str, Any]] = []
    fn: Callable[..., Any] | None = None
    try:
        module = importlib.import_module(str(entry["module"]))
        fn = getattr(module, str(entry["callable"]))
        if not callable(fn):
            raise TypeError(f"{entry['module']}.{entry['callable']} is not callable")
    except BaseException as exc:
        if isinstance(exc, KeyboardInterrupt):
            raise
        results = [_error("import", exc) for _ in inputs]
    if fn is not None:
        for index, item in enumerate(inputs):
            recorder.current_input = index
            handler_input = item.get("input") or {}
            material = (
                handler_input.get("material") if handler_input.get("kind") == "material" else handler_input
            )
            content_file = item.get("content_file")
            loader: Callable[[], bytes] | None = None
            if content_file:
                loader = functools.partial(Path.read_bytes, workdir / str(content_file))

            ctx = Context(
                material or {}, params, content_loader=loader, test_mode=bool(request.get("test_mode"))
            )
            try:
                value = fn(material, params, ctx)
                results.append(_normalize(value, ctx.log.messages))
            except BaseException as exc:
                if isinstance(exc, KeyboardInterrupt):
                    raise
                results.append(_error("extract", exc))
        recorder.current_input = None
    return {
        "protocol": PROTOCOL_VERSION,
        "results": results,
        "violations": recorder.violations,
        "metrics": _metrics(),
    }


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: python -I -m jane_extractor_sdk.runner <workdir>", file=sys.stderr)
        return 2
    workdir = Path(args[0])
    sys.dont_write_bytecode = True
    # Keep the protocol channel clean: anything the extractor prints goes to stderr.
    sys.stdout.flush()
    out_fd = os.dup(1)
    os.dup2(2, 1)
    try:
        request = json.loads((workdir / "request.json").read_text(encoding="utf-8"))
        if request.get("protocol") != PROTOCOL_VERSION:
            raise ValueError(f"unsupported runner protocol {request.get('protocol')!r}")
    except (OSError, ValueError) as exc:
        print(f"runner: invalid request: {exc}", file=sys.stderr)
        return 3
    recorder = _Recorder()
    sys.addaudithook(recorder.hook)
    started = time.monotonic()
    response = execute(request, workdir, recorder=recorder)
    response["metrics"].setdefault("duration_ms", int((time.monotonic() - started) * 1000))
    payload = json.dumps(response, ensure_ascii=False, allow_nan=False).encode("utf-8")
    sys.stdout.flush()
    sys.stderr.flush()
    view = memoryview(payload)
    while view:
        written = os.write(out_fd, view)
        view = view[written:]
    os.close(out_fd)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
