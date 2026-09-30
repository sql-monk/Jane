"""Compatibility with handler-runtime and the extractor SDK (WP-06) as merged in ``main``.

The registry does not depend on them at run time; these tests import them only when they are installed
in the workspace (skipped otherwise):

* the dependency check gives the same verdicts as the runtime's on the real ``python-extractor@1`` profile;
* the SDK example package published to the registry and exported runs through ``jane-handler-runtime test``
  without the registry (``subprocess`` backend - trusted example package; the docker sandbox run is shown in
  the WP-05 report);
* the canonical archive of the registry contains exactly the files the SDK packs (the SDK still deflates,
  so its digest differs - request to WP-06 in the report).
"""

from __future__ import annotations

import io
import json
import zipfile
from importlib import resources
from pathlib import Path
from typing import Any

import pytest

from jane_kit.contracts import contracts_dir
from jane_registry.__main__ import main as registry_main
from jane_registry.archive import canonical_archive, digest_of, files_from_dir
from jane_registry.export import export_package
from jane_registry.profiles import check_dependencies, parse_profiles

runtime_profiles = pytest.importorskip("jane_handler_runtime.profiles")
sdk_package = pytest.importorskip("jane_extractor_sdk.package")

CONTRACTS = contracts_dir(Path(__file__).parent)
EXAMPLE = (
    CONTRACTS.parent if CONTRACTS else Path()
) / "libs/extractor-sdk/examples/testsite-product-extractor"


def _runtime_profile_file() -> Path:
    item = resources.files("jane_handler_runtime.profiles") / "python-extractor-1.json"
    return Path(str(item))


def test_dependency_check_matches_runtime() -> None:
    doc = json.loads(_runtime_profile_file().read_text(encoding="utf-8"))
    ours = parse_profiles(doc)["python-extractor@1"]
    theirs = runtime_profiles.load_profiles()["python-extractor@1"]
    requirements = [
        "lxml>=6",
        "selectolax>=0.3,<0.4",
        "beautifulsoup4==4.15.0",
        "lxml<5",
        "requests>=2",
        "numpy",
        "pywin32; sys_platform == 'win32'",
        "parsel; python_version < '3.0'",
        "lxml @ https://example.test/lxml.whl",
        "not a requirement !!",
        "Python-Dateutil>=2.9",
    ]
    our_bad = {p.requirement for p in check_dependencies(ours, requirements)}
    their_bad = {p.requirement for p in runtime_profiles.check_dependencies(theirs, requirements)}
    assert our_bad == their_bad
    assert our_bad == {
        "lxml<5",
        "requests>=2",
        "numpy",
        "lxml @ https://example.test/lxml.whl",
        "not a requirement !!",
    }


def test_registry_archive_has_the_files_the_sdk_packs() -> None:
    if not EXAMPLE.is_dir():
        pytest.skip("SDK example package not in this checkout")
    ours = canonical_archive(files_from_dir(EXAMPLE))
    theirs = sdk_package.build_archive(EXAMPLE)
    with zipfile.ZipFile(io.BytesIO(ours)) as a, zipfile.ZipFile(io.BytesIO(theirs)) as b:
        assert [i.filename for i in a.infolist()] == [i.filename for i in b.infolist()]
        assert all(a.read(n) == b.read(n) for n in a.namelist())
        assert all(
            i.date_time == (1980, 1, 1, 0, 0, 0) and i.external_attr >> 16 == 0o100644 for i in b.infolist()
        )
        compression = {i.compress_type for i in b.infolist()}
    # the only difference left is the compression method of the SDK (WP-06 request in the WP-05 report)
    if compression == {zipfile.ZIP_STORED}:
        assert digest_of(theirs) == digest_of(ours)
    else:
        assert digest_of(theirs) != digest_of(ours)


def test_exported_sdk_example_runs_in_runtime_cli(backend: Any, tmp_path: Path, capsys: Any) -> None:
    if not EXAMPLE.is_dir():
        pytest.skip("SDK example package not in this checkout")
    runtime_cli = pytest.importorskip("jane_handler_runtime.cli")
    files = files_from_dir(EXAMPLE)
    manifest = json.loads(files["jane-package.json"])
    pid, version = manifest["package_id"], manifest["version"]
    out = tmp_path / "export"
    with backend.client(runtime_profiles=[str(_runtime_profile_file())]) as c:
        body = {"package_id": pid, "kind": "extractor", "title": manifest["title"]}
        assert c.post("/v1/packages", json=body, headers={"Idempotency-Key": f"c-{pid}"}).status_code == 201
        r = c.post(
            f"/v1/packages/{pid}/versions",
            content=canonical_archive(files),
            headers={"Content-Type": "application/zip", "Idempotency-Key": f"p-{pid}"},
        )
        assert r.status_code == 201, r.text
        export_package(c, pid, version, out, max_packages=10)
    # ---- no registry from here on
    archive = out / f"{pid}-{version}.zip"
    assert digest_of(archive.read_bytes()) == r.json()["digest"]
    assert registry_main(["verify", str(archive)]) == 0
    capsys.readouterr()
    result = tmp_path / "report.json"
    code = runtime_cli.main(
        ["test", str(archive), "--backend", "subprocess", "--unsafe-no-sandbox", "--json", "-o", str(result)]
    )
    report = json.loads(result.read_text(encoding="utf-8"))
    assert code == 0, report
    assert report["failed"] == 0 and report["passed"] == len(manifest["tests"])
    assert report["package"]["digest"] == r.json()["digest"]
