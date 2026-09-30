"""Export for autonomous use (WP-05 "done when": an exported package runs without the registry).

The registry runs as a real HTTP server (uvicorn) - with the ``real`` backend on PostgreSQL + MinIO.
``jane-registry export`` downloads the package and its package dependencies, the server is stopped,
and then, **without any registry**: ``jane-registry verify`` checks integrity and structure, and the
extractor is executed from the exported archive in an isolated interpreter (``python -I``).
"""

from __future__ import annotations

import json
import socket
import threading
import time
import zipfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import httpx
import pytest
import uvicorn

from jane_kit.contracts import contracts_dir
from jane_registry.__main__ import main
from jane_registry.app import build_app
from jane_registry.archive import digest_of
from jane_registry.export import INDEX_NAME
from jane_registry.testing import (
    extractor_files,
    extractor_manifest,
    publish_body,
    run_extractor_from_archive,
)


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


class LiveRegistry:
    def __init__(self, backend: Any) -> None:
        self.port = _free_port()
        self.url = f"http://127.0.0.1:{self.port}"
        config = uvicorn.Config(
            build_app(backend.settings()), host="127.0.0.1", port=self.port, log_config=None, lifespan="on"
        )
        self.server = uvicorn.Server(config)
        self.thread = threading.Thread(target=self.server.run, daemon=True)

    def __enter__(self) -> LiveRegistry:
        self.thread.start()
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            try:
                if httpx.get(f"{self.url}/v1/health", timeout=1).status_code == 200:
                    return self
            except httpx.HTTPError:
                time.sleep(0.1)
        raise AssertionError("registry did not start")

    def __exit__(self, *exc: object) -> None:
        self.server.should_exit = True
        self.thread.join(timeout=30)


@pytest.fixture
def live(backend: Any) -> Iterator[LiveRegistry]:
    with LiveRegistry(backend) as registry:
        yield registry


def _publish_demo(url: str, pid: str, rules_id: str) -> dict[str, Any]:
    with httpx.Client(base_url=url, timeout=30) as c:
        for package_id, kind in [(rules_id, "collector-rules"), (pid, "extractor")]:
            body = {"package_id": package_id, "kind": kind, "title": package_id}
            assert (
                c.post("/v1/packages", json=body, headers={"Idempotency-Key": f"c-{package_id}"}).status_code
                == 201
            )
        rules_manifest = {
            "schema_version": "1",
            "package_id": rules_id,
            "version": "1.0.0",
            "kind": "collector-rules",
            "title": "Demo rules",
            "entry": {"collector": "web", "rules": "rules.json"},
            "provenance": {"created_by": "human"},
        }
        contracts = contracts_dir()
        assert contracts is not None
        rules = json.loads(
            (contracts / "examples/schemas/collector-rules/web-shop.json").read_text(encoding="utf-8")
        )
        r = c.post(
            f"/v1/packages/{rules_id}/versions",
            json=publish_body(rules_manifest, {"rules.json": json.dumps(rules).encode()}),
            headers={"Idempotency-Key": f"p-{rules_id}"},
        )
        assert r.status_code == 201, r.text
        manifest = extractor_manifest(
            pid,
            "1.0.0",
            dependencies={
                "runtime_profile": "python-extractor@1",
                "python": ["lxml>=6"],
                "packages": [{"package_id": rules_id, "version": "1.0.0", "digest": r.json()["digest"]}],
            },
        )
        v = c.post(
            f"/v1/packages/{pid}/versions",
            json=publish_body(manifest, extractor_files()),
            headers={"Idempotency-Key": f"p-{pid}"},
        )
        assert v.status_code == 201, v.text
        return dict(v.json())


def test_exported_package_runs_without_registry(backend: Any, uid: Any, tmp_path: Path, capsys: Any) -> None:
    pid, rules_id = uid("export"), uid("export-rules")
    out = tmp_path / "exported"
    with LiveRegistry(backend) as live:
        version = _publish_demo(live.url, pid, rules_id)
        assert main(["export", f"{pid}@1.0.0", "--registry", live.url, "--out", str(out)]) == 0
    # ---- the registry is gone from here on
    with pytest.raises(httpx.HTTPError):
        httpx.get(f"{live.url}/v1/health", timeout=1)
    capsys.readouterr()

    index = json.loads((out / INDEX_NAME).read_text(encoding="utf-8"))
    assert [(p["package_id"], p["version"]) for p in index["packages"]] == [
        (pid, "1.0.0"),
        (rules_id, "1.0.0"),
    ]
    archive = out / f"{pid}-1.0.0.zip"
    assert digest_of(archive.read_bytes()) == version["digest"] == index["packages"][0]["digest"]

    assert main(["verify", str(archive)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["ok"] and report["checks"] == {
        "digest": True,
        "canonical": True,
        "manifest": True,
        "scan_limit": True,
        "secrets": True,
    }
    assert main(["verify", str(out / f"{rules_id}-1.0.0.zip")]) == 0
    capsys.readouterr()

    page = '<html><h1 data-sku="B-7">Blender B-7</h1><span class="price">499.5</span></html>'
    ran = run_extractor_from_archive(archive, page)
    assert ran["package"] == f"{pid}@1.0.0"
    assert ran["result"] == {
        "status": "success",
        "entities": [
            {"entity_type": "product", "fields": {"sku": "B-7", "title": "Blender B-7", "price": 499.5}}
        ],
    }
    assert run_extractor_from_archive(archive, "<html>nothing</html>")["result"]["status"] == "empty"

    # a tampered archive is detected offline
    tampered = tmp_path / archive.name
    with zipfile.ZipFile(archive) as src, zipfile.ZipFile(tampered, "w") as dst:
        for info in src.infolist():
            data = src.read(info)
            if info.filename.endswith("main.py"):
                data += b"\n# tampered\n"
            dst.writestr(info, data)
    (tmp_path / INDEX_NAME).write_text((out / INDEX_NAME).read_text(encoding="utf-8"), encoding="utf-8")
    assert main(["verify", str(tampered)]) == 1
    bad = json.loads(capsys.readouterr().out)
    assert bad["checks"]["digest"] is False


def test_export_errors_and_local_archive(live: LiveRegistry, tmp_path: Path, capsys: Any) -> None:
    assert main(["export", "missing@1.0.0", "--registry", live.url, "--out", str(tmp_path)]) == 2
    pkg = tmp_path / "pkg"
    for path, data in {
        **extractor_files(),
        "jane-package.json": json.dumps(extractor_manifest("local.pkg")).encode(),
    }.items():
        (pkg / path).parent.mkdir(parents=True, exist_ok=True)
        (pkg / path).write_bytes(data)
    (pkg / "src" / "demo_extractor" / "__pycache__").mkdir()
    (pkg / "src" / "demo_extractor" / "__pycache__" / "main.cpython-312.pyc").write_bytes(b"junk")
    zip1, zip2 = tmp_path / "a.zip", tmp_path / "b.zip"
    assert main(["archive", str(pkg), "--out", str(zip1)]) == 0
    assert main(["archive", str(pkg), "--out", str(zip2)]) == 0
    assert zip1.read_bytes() == zip2.read_bytes()
    with zipfile.ZipFile(zip1) as zf:
        assert not any("__pycache__" in n for n in zf.namelist())
    capsys.readouterr()
    assert main(["verify", str(zip1)]) == 0
