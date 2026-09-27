"""Test package that probes the sandbox; behaviour is chosen by ``params.mode``."""

from __future__ import annotations

import os
import socket
import time
from pathlib import Path
from typing import Any


def _try_write(path: str) -> str:
    try:
        Path(path).write_text("x", encoding="utf-8")
    except OSError as exc:
        return f"denied: {exc.strerror or exc}"
    return "written"


def extract(material: dict[str, Any], params: dict[str, Any], ctx: Any) -> dict[str, Any]:
    mode = params.get("mode", "ok")
    if mode == "ok":
        return {"status": "success", "data": {"text": ctx.text()[:100]}}
    if mode == "hang":
        while True:  # busy loop: never returns
            pass
    if mode == "sleep":
        time.sleep(3600)
    if mode == "network":
        sock = socket.create_connection((params["host"], int(params["port"])), timeout=5)
        sock.close()
        return {"status": "success", "data": {"connected": True}}
    if mode == "memory":
        blocks = []
        for _ in range(int(params.get("mb", 1024))):
            blocks.append(b"x" * 2**20)  # touched pages: really committed
        return {"status": "success", "data": {"allocated_mb": len(blocks)}}
    if mode == "environment":
        return {
            "status": "success",
            "data": {
                "uid": getattr(os, "getuid", lambda: None)(),
                "env": sorted(os.environ),
                "write_root": _try_write("/probe.txt"),
                "write_package": _try_write("/work/package/probe.txt"),
                "write_work": _try_write("/work/probe.txt"),
                "write_tmp": _try_write("/tmp/probe.txt"),
                "interfaces": sorted(name for _, name in socket.if_nameindex()),
            },
        }
    if mode == "output":
        return {"status": "success", "data": {"blob": "x" * int(params["bytes"])}}
    if mode == "raise":
        raise RuntimeError("probe failure")
    if mode == "bad_entity":
        return {"status": "success", "entities": [{"entity_type": "thing", "fields": {"id": None}}]}
    raise ValueError(f"unknown mode {mode}")
