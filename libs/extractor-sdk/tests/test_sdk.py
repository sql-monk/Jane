from __future__ import annotations

import base64
import io
import json
import stat
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from jane_extractor_sdk import Context, empty, entity, success, unrecognized
from jane_extractor_sdk.compare import compare_output
from jane_extractor_sdk.entities import build_key, to_entity_record
from jane_extractor_sdk.package import (
    PackageError,
    UnpackLimits,
    build_archive,
    case_input,
    digest_of,
    load_manifest,
    material_from_bytes,
    safe_unpack,
)
from jane_extractor_sdk.runner import execute
from jane_extractor_sdk.testing import apply_param_defaults, run_local, run_package_tests

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "testsite-product-extractor"
LIMITS = UnpackLimits(max_archive_bytes=1_000_000, max_unpacked_bytes=1_000_000, max_files=100)


def write_package(root: Path, code: str, module: str = "probe_pkg") -> Path:
    (root / "src" / module).mkdir(parents=True)
    (root / "src" / module / "__init__.py").write_text("", encoding="utf-8")
    (root / "src" / module / "main.py").write_text(code, encoding="utf-8")
    manifest = {
        "schema_version": "1",
        "package_id": "test.probe",
        "version": "0.1.0",
        "kind": "extractor",
        "title": "probe",
        "entry": {"runtime": "python", "module": f"{module}.main", "callable": "extract"},
        "output": {
            "entities": [{"entity_type": "thing", "schema": "schemas/thing.json", "key_fields": ["id"]}]
        },
        "dependencies": {"runtime_profile": "python-extractor@1"},
        "provenance": {"created_by": "human"},
    }
    (root / "jane-package.json").write_text(json.dumps(manifest), encoding="utf-8")
    return root


def request_for(package_dir: Path, material: dict[str, object]) -> dict[str, object]:
    manifest = load_manifest(package_dir)
    return {
        "protocol": 1,
        "entry": manifest["entry"],
        "package_dir": str(package_dir),
        "params": {},
        "inputs": [{"input": {"kind": "material", "material": material}, "content_file": None}],
    }


# ---------------------------------------------------------------- result helpers and context


def test_result_helpers_cover_the_three_returned_states() -> None:
    e = entity("product", {"sku": "A-1", "title": None, "price": 1}, cleared=["old", "old"])
    assert e == {"entity_type": "product", "fields": {"sku": "A-1", "price": 1}, "cleared": ["old"]}
    assert success([e])["status"] == "success"
    assert empty() == {"status": "empty", "entities": []}
    partial = unrecognized("no price", signature="missing-selector:.price", entities=[e])
    assert partial["unrecognized"] == {
        "partial": True,
        "reason": "no price",
        "signature": "missing-selector:.price",
    }
    assert unrecognized("unknown layout")["unrecognized"]["partial"] is False


def test_context_text_and_bytes() -> None:
    m = material_from_bytes("Привіт".encode("cp1251"), media_type="text/html", charset="cp1251")
    ctx = Context(m)
    assert ctx.text() == "Привіт"
    binary = material_from_bytes(b"\x00\x01\xff", media_type="application/octet-stream")
    assert binary["content"]["encoding"] == "base64"
    assert Context(binary).bytes() == b"\x00\x01\xff"
    loaded = Context({"content": {"kind": "blob"}}, content_loader=lambda: b"abc")
    assert loaded.text() == "abc"
    ctx.log.warning("w", code="x.y", selector=".price")
    assert ctx.log.messages[0]["material_id"] == m["material_id"]


def test_material_ids_follow_collector_rules() -> None:
    m = material_from_bytes(b"<html/>", media_type="text/html", url="https://a.test/x")
    assert m["material_id"].startswith("web:") and len(m["material_id"]) == 36
    assert material_from_bytes(b"x", media_type="text/plain")["material_id"].startswith("file:")


# ---------------------------------------------------------------- compare


def test_compare_exact_and_subset() -> None:
    expected = {"entities": [{"entity_type": "p", "fields": {"sku": "A", "price": 1}}]}
    actual = {
        "entities": [
            {"entity_type": "p", "fields": {"sku": "A", "price": 1.0, "extra": True}, "observation": {"x": 1}}
        ]
    }
    assert compare_output(expected, actual, "subset") == []
    diffs = compare_output(expected, actual, "exact")
    assert diffs == [{"pointer": "/entities/0/fields/extra", "expected": None, "actual": True}]
    assert compare_output({"entities": [{"fields": {"ok": True}}]}, {"entities": [{"fields": {"ok": 1}}]})
    two = {"entities": [{"fields": {"sku": "B"}}, {"fields": {"sku": "A"}}]}
    assert compare_output({"entities": [{"fields": {"sku": "A"}}]}, two, "subset") == []
    assert compare_output({"entities": [{"fields": {"sku": "C"}}]}, two, "subset")


# ---------------------------------------------------------------- package utilities


def test_canonical_archive_is_deterministic_and_unpacks(tmp_path: Path) -> None:
    first = build_archive(EXAMPLE)
    assert build_archive(EXAMPLE) == first
    assert digest_of(first).startswith("sha256:") and len(digest_of(first)) == 71
    names = zipfile.ZipFile(io.BytesIO(first)).namelist()
    assert names == sorted(names) and "jane-package.json" in names
    safe_unpack(first, tmp_path / "out", LIMITS)
    assert load_manifest(tmp_path / "out")["package_id"] == "testsite.product-extractor"


def _zip(entries: dict[str, bytes], symlink: str | None = None) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in entries.items():
            zf.writestr(name, data)
        if symlink:
            info = zipfile.ZipInfo(symlink)
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            zf.writestr(info, "/etc/passwd")
    return buf.getvalue()


@pytest.mark.parametrize(
    ("archive", "message"),
    [
        (_zip({"jane-package.json": b"{}", "../evil.py": b""}), "invalid package path"),
        (_zip({"jane-package.json": b"{}", "/abs.py": b""}), "invalid package path"),
        (_zip({"jane-package.json": b"{}"}, symlink="link"), "symlinks"),
        (_zip({"src/a.py": b""}), "no jane-package.json"),
        (b"not a zip", "not a zip"),
        (_zip({"jane-package.json": b"{}", "big.bin": b"x" * 2_000_000}), "max_unpacked_bytes"),
    ],
    ids=["dotdot", "absolute", "symlink", "no-manifest", "not-zip", "too-big"],
)
def test_unsafe_archives_are_rejected(tmp_path: Path, archive: bytes, message: str) -> None:
    with pytest.raises(PackageError, match=message):
        safe_unpack(archive, tmp_path / "out", LIMITS)


def test_archive_limits(tmp_path: Path) -> None:
    many = _zip({"jane-package.json": b"{}", **{f"f{i}.txt": b"" for i in range(5)}})
    with pytest.raises(PackageError, match="max_files"):
        safe_unpack(many, tmp_path / "a", UnpackLimits(10_000, 10_000, 3))
    with pytest.raises(PackageError, match="max_archive_bytes"):
        safe_unpack(many, tmp_path / "b", UnpackLimits(10, 10_000, 100))


def test_case_inputs(tmp_path: Path) -> None:
    manifest = load_manifest(EXAMPLE)
    by_name = {c["name"]: c for c in manifest["tests"]}
    file_input = case_input(EXAMPLE, by_name["product-phone-alpha"])
    assert file_input["material"]["locator"]["url"].endswith("/product/phone-alpha")
    material_input = case_input(EXAMPLE, by_name["unknown-page-empty"])
    content = material_input["material"]["content"]
    assert "careers" in content["data"].lower()
    assert material_input["material"]["revision"]["content_sha256"] == content["sha256"]
    with pytest.raises(PackageError):
        case_input(EXAMPLE, {"name": "x", "input": {"file": "../secret"}})


def test_key_and_record() -> None:
    assert build_key({"sku": "A", "n": 1}, ["sku", "n"], "s") == {
        "scope": "s",
        "natural": {"sku": "A", "n": 1},
    }
    assert build_key({"sku": {"x": 1}}, ["sku"], "s") is None
    m = material_from_bytes(b"x", media_type="text/plain")
    rec = to_entity_record(
        {"entity_type": "t", "fields": {"id": "1"}}, key_fields=["id"], material=m, schema_ref="p@1#t"
    )
    assert rec["key"] == {"scope": "local", "natural": {"id": "1"}}
    assert rec["observation"]["observation_id"] == m["observation_id"]
    assert rec["schema"] == "p@1#t"


# ---------------------------------------------------------------- runner


def test_runner_reports_errors_per_input(tmp_path: Path) -> None:
    pkg = write_package(
        tmp_path / "pkg",
        "def extract(material, params, ctx):\n"
        "    mode = material['metadata']['mode']\n"
        "    if mode == 'raise': raise ValueError('boom')\n"
        "    if mode == 'bad': return {'status': 'failed'}\n"
        "    if mode == 'nonjson': return {'status': 'success', 'entities': [{'x': object()}]}\n"
        "    ctx.log.info('hello', code='t.hello')\n"
        "    return {'status': 'success', 'entities': [{'entity_type': 'thing', 'fields': {'id': 'a'}}]}\n",
    )
    req = request_for(pkg, {})
    req["inputs"] = [
        {"input": {"kind": "material", "material": {"metadata": {"mode": m}}}, "content_file": None}
        for m in ("ok", "raise", "bad", "nonjson")
    ]
    out = execute(req, pkg)
    ok, raised, bad, nonjson = out["results"]
    assert ok["status"] == "success" and ok["diagnostics"][0]["code"] == "t.hello"
    assert raised["error"]["type"] == "ValueError" and "boom" in raised["error"]["traceback"]
    assert "invalid status" in bad["error"]["message"]
    assert nonjson["error"]["type"] == "TypeError"


def test_runner_import_error(tmp_path: Path) -> None:
    pkg = write_package(tmp_path / "pkg", "import does_not_exist_anywhere\n", module="broken_pkg")
    out = execute(request_for(pkg, {}), pkg)
    assert out["results"][0]["error"]["stage"] == "import"


def test_runner_main_protocol_and_violations(tmp_path: Path) -> None:
    pkg = write_package(
        tmp_path / "work" / "package",
        "import socket\n"
        "def extract(material, params, ctx):\n"
        "    print('noise on stdout')\n"
        "    try:\n"
        "        socket.getaddrinfo('localhost', 80)\n"
        "    except OSError:\n"
        "        pass\n"
        "    return {'status': 'empty'}\n",
    )
    work = pkg.parent
    content = base64.b64encode(b"data").decode()
    material: dict[str, object] = {"content": {"kind": "inline", "encoding": "base64", "data": content}}
    req = request_for(pkg, material)
    req["package_dir"] = "package"
    (work / "request.json").write_text(json.dumps(req), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, "-I", "-m", "jane_extractor_sdk.runner", str(work)],
        capture_output=True,
        timeout=60,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout)
    assert out["results"][0]["status"] == "empty"
    assert out["violations"][0]["kind"] == "network"
    assert out["violations"][0]["event"] == "socket.getaddrinfo"
    assert b"noise on stdout" in proc.stderr


# ---------------------------------------------------------------- testing utilities on the example package


def test_example_package_tests_pass_in_process() -> None:
    results = run_package_tests(EXAMPLE)
    assert [r.name for r in results if not r.passed] == []
    assert {r.actual_status for r in results} == {"success", "empty", "unrecognized"}


def test_run_local_on_a_file() -> None:
    result = run_local(
        EXAMPLE,
        file=EXAMPLE / "tests" / "product-phone-gamma" / "page.html",
        media_type="text/html",
        params={"include_url": False},
    )
    assert result["status"] == "success"
    assert "url" not in result["output"]["entities"][0]["fields"]


def test_param_defaults() -> None:
    schema = {"properties": {"a": {"default": 1}, "b": {"type": "string"}}}
    assert apply_param_defaults(schema, {"b": "x"}) == {"a": 1, "b": "x"}
