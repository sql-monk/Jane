"""Helpers for tests of the registry and of its clients: sample packages and a test runtime profile.

The sample extractor has no dependency on the extractor SDK, so an exported archive can be executed by
a plain Python interpreter (``run_extractor_from_archive``) without the registry or other Jane services.
"""

from __future__ import annotations

import base64
import io
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from .archive import MANIFEST_NAME, manifest_bytes

__all__ = [
    "TEST_PROFILE",
    "extractor_files",
    "extractor_manifest",
    "publish_body",
    "run_extractor_from_archive",
    "zip_of",
]

TEST_PROFILE: dict[str, Any] = {
    "profile": "python-extractor@1",
    "description": "Test copy of the profile format published by handler-runtime (WP-06).",
    "python": "3.12",
    "libraries": {"lxml": "6.1.3", "selectolax": "0.3.34", "beautifulsoup4": "4.15.0"},
    "stdlib": True,
    "network": "none",
}

MAIN_PY = '''"""Sample extractor: finds <h1 data-sku="..."> and <span class="price">."""

import re


def extract(material, params, ctx=None):
    html = material["content"]["data"]
    m = re.search(r'<h1 data-sku="([^"]+)">([^<]*)</h1>', html)
    if not m:
        return {"status": "empty", "entities": []}
    fields = {"sku": m.group(1), "title": m.group(2).strip()}
    price = re.search(r'<span class="price">([0-9.]+)</span>', html)
    if price:
        fields["price"] = float(price.group(1))
    return {"status": "success", "entities": [{"entity_type": "product", "fields": fields}]}
'''

PRODUCT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["sku"],
    "properties": {"sku": {"type": "string"}, "title": {"type": "string"}, "price": {"type": "number"}},
}


def extractor_manifest(package_id: str, version: str = "1.0.0", **overrides: Any) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema_version": "1",
        "package_id": package_id,
        "version": version,
        "kind": "extractor",
        "title": "Demo product cards",
        "tags": ["demo", "products"],
        "entry": {"runtime": "python", "module": "demo_extractor.main", "callable": "extract"},
        "input": {"accepts": ["material"], "media_types": ["text/html"]},
        "output": {
            "entities": [
                {"entity_type": "product", "schema": "schemas/product.schema.json", "key_fields": ["sku"]}
            ]
        },
        "dependencies": {"runtime_profile": "python-extractor@1", "python": ["lxml>=6"]},
        "access": {"network": "none"},
        "tests": [
            {
                "name": "product-a100",
                "input": {"file": "tests/product/page.html", "media_type": "text/html"},
                "expected_status": "success",
                "expected": "tests/product/expected.json",
            },
            {
                "name": "category-empty",
                "input": {"file": "tests/category/page.html", "media_type": "text/html"},
                "expected_status": "empty",
            },
        ],
        "provenance": {"created_by": "human", "authors": ["tests"]},
        "bindings_hint": {"source_kinds": ["web"], "domains": ["shop.example.test"]},
    }
    manifest.update(overrides)
    return manifest


def extractor_files(main_py: str = MAIN_PY, extra: dict[str, bytes] | None = None) -> dict[str, bytes]:
    files = {
        "src/demo_extractor/__init__.py": b"",
        "src/demo_extractor/main.py": main_py.encode("utf-8"),
        "schemas/product.schema.json": json.dumps(PRODUCT_SCHEMA, indent=2).encode("utf-8"),
        "tests/product/page.html": b'<html><h1 data-sku="A-100">Kettle A-100</h1><span class="price">1299.0</span></html>',
        "tests/product/expected.json": json.dumps(
            {
                "entities": [
                    {
                        "entity_type": "product",
                        "fields": {"sku": "A-100", "title": "Kettle A-100", "price": 1299.0},
                    }
                ]
            }
        ).encode("utf-8"),
        "tests/category/page.html": b"<html><h2>Kettles</h2></html>",
    }
    files.update(extra or {})
    return files


def publish_body(manifest: dict[str, Any], files: dict[str, bytes]) -> dict[str, Any]:
    """``PublishRequest`` (registry.v1) from a manifest and files."""
    out: dict[str, Any] = {}
    for path, data in files.items():
        try:
            out[path] = {"encoding": "utf-8", "data": data.decode("utf-8")}
        except UnicodeDecodeError:
            out[path] = {"encoding": "base64", "data": base64.b64encode(data).decode("ascii")}
    return {"manifest": manifest, "files": out}


def zip_of(manifest: dict[str, Any], files: dict[str, bytes], *, deflate: bool = True) -> bytes:
    """A non-canonical zip as an author might build it (deflated, directory entries, current time)."""
    buf = io.BytesIO()
    method = zipfile.ZIP_DEFLATED if deflate else zipfile.ZIP_STORED
    with zipfile.ZipFile(buf, "w", compression=method) as zf:
        zf.writestr("src/", b"")
        for path in reversed(sorted(files)):
            zf.writestr(path, files[path])
        zf.writestr(MANIFEST_NAME, manifest_bytes(manifest))
    return buf.getvalue()


RUNNER = r"""
import importlib, json, sys, zipfile, pathlib
archive, workdir, html = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3]
with zipfile.ZipFile(archive) as zf:
    zf.extractall(workdir)
manifest = json.loads((workdir / "jane-package.json").read_text(encoding="utf-8"))
sys.path.insert(0, str(workdir / "src"))
entry = manifest["entry"]
fn = getattr(importlib.import_module(entry["module"]), entry["callable"])
material = {"content": {"kind": "inline", "encoding": "utf-8", "data": html}}
print(json.dumps({"package": manifest["package_id"] + "@" + manifest["version"], "result": fn(material, {}, None)}))
"""


def run_extractor_from_archive(archive: Path, html: str, timeout_s: float = 60.0) -> dict[str, Any]:
    """Unpack an exported archive and call its entry point in an isolated interpreter (``python -I``):
    no registry, no Jane packages on ``sys.path`` - only the archive itself."""
    with tempfile.TemporaryDirectory(prefix="jane-export-run-") as tmp:
        proc = subprocess.run(  # noqa: S603 - fixed interpreter and script, test helper
            [sys.executable, "-I", "-c", RUNNER, str(archive), tmp, html],
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
    if proc.returncode != 0:
        raise RuntimeError(f"extractor failed: {proc.stderr}")
    result: dict[str, Any] = json.loads(proc.stdout)
    return result
