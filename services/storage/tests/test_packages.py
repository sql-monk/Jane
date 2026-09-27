"""Storage packages: discovery through entry points, canonical archive, publication to a registry mock.

WP-05 (registry) is not ready: publication is checked against a mock built from registry.v1.yaml
(``jane_kit.contracts.build_mock_app`` validates request bodies against the contract).
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jane_kit.contracts import OpenAPISpec, build_mock_app, contracts_dir
from jane_storage.adapters import available_adapters, package_dirs
from jane_storage.packages import PackageCatalog, load_package, main, package_from_archive, publish

CONTRACTS = contracts_dir(Path(__file__).parent)


def test_adapters_and_packages_are_discovered() -> None:
    adapters = available_adapters()
    assert adapters["filesystem"].kind == "filesystem"
    assert adapters["postgresql"].kind == "postgresql"
    dirs = package_dirs()
    assert {"jane.storage-files", "jane.storage-postgresql"} <= set(dirs)


def test_archive_is_deterministic_and_round_trips() -> None:
    root = package_dirs()["jane.storage-files"]
    a, b = load_package(root), load_package(root)
    assert a.archive == b.archive
    assert a.digest == b.digest
    names = zipfile.ZipFile(io.BytesIO(a.archive)).namelist()
    assert names == sorted(names)
    assert "jane-package.json" in names
    again = package_from_archive(a.archive)
    assert again.digest == a.digest
    assert again.manifest == a.manifest


def test_publish_to_registry_mock() -> None:
    if CONTRACTS is None:
        pytest.skip("contracts not available")
    mock = build_mock_app(OpenAPISpec.load(CONTRACTS / "openapi" / "registry.v1.yaml"))
    packages = PackageCatalog.discover().all()
    with TestClient(mock) as registry:
        outcomes = publish(registry, packages)
    assert {o.package_id for o in outcomes} >= {"jane.storage-files", "jane.storage-postgresql"}
    assert all(o.ok for o in outcomes), outcomes
    assert all(o.digest.startswith("sha256:") for o in outcomes)


def test_cli_lists_packages(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["list"]) == 0
    out = capsys.readouterr().out
    assert "jane.storage-files@1.0.0  adapter=filesystem" in out
    assert "jane.storage-postgresql@1.0.0  adapter=postgresql" in out
