"""Sandbox probe of the WP-14 limits harness: ``sleep_ms`` (wall time) and ``alloc_mb`` (memory limit).

Not an extractor of real data: it always returns ``empty`` so that only the sandbox behaviour is measured.
"""

from __future__ import annotations

import time
from typing import Any

from jane_extractor_sdk import Context, ExtractResult, Material, empty


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    block = bytearray(int(params["alloc_mb"]) * 1024 * 1024)
    for i in range(0, len(block), 4096):  # touch every page so the memory is really used
        block[i] = 1
    time.sleep(int(params["sleep_ms"]) / 1000)
    ctx.log.info(f"probe done: {len(block)} bytes allocated", code="harness.probe")
    return empty()
