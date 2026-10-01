"""Unit tests of the building blocks: canonical archive, secret scan, profiles, merge, diff, SemVer."""

from __future__ import annotations

import base64
import hashlib
import io
import itertools
import json
import os
import random
import re
import time
import warnings
import zipfile
from typing import Any

import pytest

from jane_registry.archive import (
    ArchiveError,
    ArchiveLimits,
    canonical_archive,
    digest_of,
    is_canonical,
    manifest_bytes,
    read_archive,
)
from jane_registry.diffing import diff_files, diff_manifest
from jane_registry.merge import merge3_lines, merge_packages
from jane_registry.profiles import check_dependencies, parse_profiles
from jane_registry.secrets import scan_files
from jane_registry.semver import SemVer, max_version, sort_versions
from jane_registry.settings import SecretScanLimits
from jane_registry.testing import TEST_PROFILE, extractor_files, extractor_manifest, zip_of

LIMITS = ArchiveLimits(max_archive_bytes=10_000_000, max_unpacked_bytes=10_000_000, max_files=100)


# ------------------------------------------------------------------------------------ archive
def test_canonical_archive_golden_digest() -> None:
    """Locks the canonical algorithm (stored, sorted, 1980-01-01, 0644, Unix). Changing any of these
    changes every digest in every registry: do not update this value casually."""
    files = {"jane-package.json": b'{"a": 1}\n', "src/m.py": b"print('x')\n", "B.txt": b"upper"}
    archive = canonical_archive(files)
    assert digest_of(archive) == "sha256:e80692e640c2cb1a1976caaad1ba67460a0af0926012748f85748d15c6a404a0"
    with zipfile.ZipFile(io.BytesIO(archive)) as zf:
        infos = zf.infolist()
    assert [i.filename for i in infos] == ["B.txt", "jane-package.json", "src/m.py"]  # byte order
    for info in infos:
        assert info.compress_type == zipfile.ZIP_STORED
        assert info.date_time == (1980, 1, 1, 0, 0, 0)
        assert info.external_attr >> 16 == 0o100644
        assert info.create_system == 3
        assert info.extra == b"" and info.comment == b""


def test_canonical_archive_ignores_insertion_order_and_source_format() -> None:
    manifest = extractor_manifest("order.test")
    files = extractor_files()
    a = canonical_archive({**files, "jane-package.json": manifest_bytes(manifest)})
    b = canonical_archive(
        dict(reversed(list({**files, "jane-package.json": manifest_bytes(manifest)}.items())))
    )
    assert a == b
    repacked = canonical_archive(read_archive(zip_of(manifest, files), LIMITS))
    assert repacked == a
    assert is_canonical(a, LIMITS) and not is_canonical(zip_of(manifest, files), LIMITS)


@pytest.mark.parametrize(
    ("name", "reason"),
    [
        ("../x.py", "invalid package path"),
        ("/abs.py", "invalid package path"),
        ("a/../../b", "invalid package path"),
    ],
)
def test_read_archive_rejects_bad_paths(name: str, reason: str) -> None:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(name, b"x")
    with pytest.raises(ArchiveError, match=reason):
        read_archive(buf.getvalue(), LIMITS)


def test_read_archive_rejects_symlinks_duplicates_and_limits() -> None:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        info = zipfile.ZipInfo("link")
        info.external_attr = 0o120777 << 16
        zf.writestr(info, "target")
    with pytest.raises(ArchiveError, match="symlinks"):
        read_archive(buf.getvalue(), LIMITS)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf, warnings.catch_warnings():
        warnings.simplefilter("ignore")  # zipfile warns about the duplicate name we create on purpose
        zf.writestr("a.txt", b"1")
        zf.writestr("a.txt", b"2")
    with pytest.raises(ArchiveError, match="duplicate"):
        read_archive(buf.getvalue(), LIMITS)
    big = canonical_archive({f"f{i}.txt": b"x" * 10 for i in range(5)})
    with pytest.raises(ArchiveError) as exc:
        read_archive(big, ArchiveLimits(10_000, 10_000, 4))
    assert exc.value.limit == "packages.max_files"
    with pytest.raises(ArchiveError) as exc:
        read_archive(big, ArchiveLimits(10_000, 20, 100))
    assert exc.value.limit == "packages.max_unpacked_bytes"
    with pytest.raises(ArchiveError) as exc:
        read_archive(big, ArchiveLimits(100, 10_000, 100))
    assert exc.value.limit == "packages.max_archive_bytes"
    with pytest.raises(ArchiveError, match="not a zip"):
        read_archive(b"not a zip", LIMITS)


# ------------------------------------------------------------------------------------ secrets
def _codes(files: dict[str, bytes]) -> list[str]:
    return [f.code for f in scan_files(files, SecretScanLimits())]


def test_secret_patterns() -> None:
    # every value is assembled at run time so that no secret-looking literal is committed
    cases = {
        "private_key": "-----BEGIN RSA " + "PRIVATE KEY-----\nMIIE\n",
        "aws_access_key": "key = 'AKIA" + "ABCDEFGHIJKLMNOP" + "'",
        "github_token": "t = 'ghp_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8" + "'",
        "slack_token": "xoxb-" + "123456789012-abcdefghij",
        "google_api_key": "AIza" + "SyA1234567890abcdefghijklmnopqrstuv",
        "llm_api_key": "OPENAI = 'sk-" + "proj-" + "abcdefghijklmnopqrstuvwxyz0123" + "'",
        "jwt": "eyJ"
        + "hbGciOiJIUzI1NiJ9"
        + ".eyJ"
        + "zdWIiOiIxMjM0NTY3ODkwIn0"
        + "."
        + "dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U",
        "url_credentials": "DSN = 'postgresql://jane:" + "s3cr3tPassw0rd" + "@db:5432/x'",
        "secret_assignment": 'password = "' + "Zx9!kQ2@wL7#" + '"',
        "telegram_bot_token": "1234567890:AA" + "Hk3jd9fKd93kfJd93kfJd93kfJd93kfJd",
    }
    for code, text in cases.items():
        assert code in _codes({"src/x.py": text.encode()}), code


def test_secret_high_entropy_only_in_code_and_config() -> None:
    # derived at run time (not a literal): 40 characters of base64 with upper, lower case and digits
    token = base64.b64encode(hashlib.sha256(b"jane-registry-entropy-test").digest()).decode()[:40]
    assert re.search(r"[A-Z]", token) and re.search(r"[a-z]", token) and re.search(r"[0-9]", token)
    assert _codes({"config.json": f'{{"value": "{token}"}}'.encode()}) == ["high_entropy_string"]
    assert _codes({"tests/page.html": f'<div data-x="{token}"></div>'.encode()}) == []


def test_secret_scan_has_no_false_positives_on_normal_packages() -> None:
    files = extractor_files(
        extra={
            "tests/x/expected.json": json.dumps(
                {
                    "digest": "sha256:" + "0f4c1c8f3e0f6a7d9b2c4e6f8a0b2c4d6e8f0a1b3c5d7e9f1a3b5c7d9e1f3a5b",
                    "id": "0b7d5c1e-3f7e-4a53-9d0e-5a0f5c0a9b11",
                }
            ).encode(),
            "tests/x/page.html": b'<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==">'
            b'<script integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/uxy9rx7HNQlGYl1kPzQho1wx4JwY8wC"></script>'
            b'<a href="https://example.test/path">x</a>',
            "src/demo_extractor/config.py": b'TOKEN_ENV = "JANE_TOKEN"\npassword = "${DB_PASSWORD}"\napi_key = "<your-api-key>"\n',
            ".env.example": b"DB_PASSWORD=changeme\n",
        }
    )
    files["jane-package.json"] = manifest_bytes(extractor_manifest("clean.pkg"))
    assert scan_files(files, SecretScanLimits()) == []


def test_secret_file_names() -> None:
    for name in [".env", "conf/.env.production", "keys/server.pem", "id_rsa", ".netrc", "a/b.p12"]:
        assert _codes({name: b"x"}) == ["secret_file"], name
    assert _codes({".env.sample": b"A=b"}) == []


# review 1: every value below is assembled at run time so that no secret-looking literal is committed
RND = (
    base64.b64encode(hashlib.sha256(b"wp05-review-1").digest())
    .decode()[:36]
    .replace("/", "x")
    .replace("+", "y")
)


@pytest.mark.parametrize(
    ("name", "text", "code"),
    [
        ("src/h.py", 'HEADERS = {"Authorization": "Bearer ' + RND + '"}\n', "authorization_value"),
        ("src/b.py", "curl -H 'Authorization: Basic " + RND + "'\n", "authorization_value"),
        ("conf/db.yaml", "db:\n  password: " + "Sup3r" + "S3cretPwd2024\n", "secret_assignment"),
        ("conf/db.ini", "[db]\npassword = " + "Sup3r" + "S3cretPwd2024\n", "secret_assignment"),
        ("conf/app.properties", "api.key=" + "k9" + "Qw7Zx2Lm\n", "secret_assignment"),
        (
            "src/odbc.py",
            'CONN = "Server=db;User Id=sa;Password=' + "MyS3cret" + 'Pwd9;"\n',
            "connection_string_password",
        ),
        ("src/low.py", 'PASSWORD = "' + "hunter2" * 2 + '"\n', "secret_assignment"),
        ("src/sg.py", 'K = "SG.' + RND[:22] + "." + RND + RND[:7] + '"\n', "sendgrid_key"),
        ("src/hf.py", 'T = "hf_' + RND.replace("=", "a") + '"\n', "huggingface_token"),
        (
            "src/az.py",
            'C = "AccountName=x;AccountKey=' + "Zm9vYmFyYmF6cXV4" * 5 + 'Ab1=="\n',
            "azure_storage_key",
        ),
        (
            "src/sas.py",
            'U = "https://a.blob.core.windows.net/c/f?sv=2022-11-02&sig=' + RND + '"\n',
            "azure_sas",
        ),
        ("src/pk.py", 'KEY = "-----BEGIN " + "RSA PRIVATE KEY' + '-----\\nMIIE"\n', "private_key"),
        (
            "src/slack.py",
            "U = 'https://hooks.slack.com/services/T0" + "ABCDEF/B0ABCDEF/" + RND + "'\n",
            "slack_webhook",
        ),
        ("src/c.py", 'COOKIES = {"sessionid": "' + RND[:28] + '"}\n', "secret_assignment"),
    ],
)
def test_secret_formats_from_review(name: str, text: str, code: str) -> None:
    assert code in _codes({name: text.encode()})


def test_secret_hidden_by_encoding_is_found() -> None:
    aws = "AKIA" + "QX7Z" * 4
    assert "aws_access_key" in _codes({"data/blob.txt": b"\0" + f"key={aws}\n".encode()})
    assert "aws_access_key" in _codes({"cfg.json": ('{"k": "' + aws + '"}').encode("utf-16")})  # with BOM
    assert "aws_access_key" in _codes({"cfg.json": ('{"k": "' + aws + '"}').encode("utf-16-le")})  # no BOM
    assert "aws_access_key" in _codes({"img.png": b"\x89PNG\0\0" + aws.encode() + b"\0\xff"})


def test_oversized_files_are_reported_not_skipped() -> None:
    from jane_registry.secrets import oversized_files

    limits = SecretScanLimits(max_scan_bytes_per_file=1024)
    files = {"small.py": b"x" * 1024, "src/pad.py": b"#" * 1025}
    assert oversized_files(files, limits) == ["src/pad.py"]


def test_secret_scan_stops_after_max_findings() -> None:
    limits = SecretScanLimits(max_findings_per_file=3)
    text = "".join(f"password = Zq{i:06d}x\n" for i in range(100)).encode()
    assert len(scan_files({"a.ini": text}, limits)) == 3


def test_package_paths_reject_dot_segments_and_case_duplicates() -> None:
    from jane_registry.archive import check_package_path, check_unique_paths

    for bad in ["src/./main.py", "./a.py", "a/."]:
        with pytest.raises(ArchiveError):
            check_package_path(bad)
    check_package_path("src/.hidden/x.py")  # dot files and directories stay valid
    with pytest.raises(ArchiveError, match="letter case"):
        check_unique_paths(["tests/Readme.txt", "tests/README.txt"])
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("tests/Readme.txt", b"1")
        zf.writestr("tests/README.txt", b"2")
    with pytest.raises(ArchiveError, match="letter case"):
        read_archive(buf.getvalue(), LIMITS)


# ------------------------------------------------------------------------------------ profiles
def test_parse_profiles_accepts_all_documented_shapes() -> None:
    assert set(parse_profiles(TEST_PROFILE)) == {"python-extractor@1"}
    assert set(parse_profiles([TEST_PROFILE, {**TEST_PROFILE, "profile": "python-extractor@2"}])) == {
        "python-extractor@1",
        "python-extractor@2",
    }
    info = {
        "service": "handler-runtime",
        "capabilities": {"runtime_profiles": {"python-extractor@1": TEST_PROFILE}},
    }
    assert set(parse_profiles(info)) == {"python-extractor@1"}
    assert set(parse_profiles({"runtime_profiles": {"python-extractor@1": TEST_PROFILE}})) == {
        "python-extractor@1"
    }


def test_check_dependencies_rules() -> None:
    profile = parse_profiles(TEST_PROFILE)["python-extractor@1"]
    ok = [
        "lxml>=6",
        "LXML==6.1.3",
        "beautifulsoup4~=4.15",
        "pywin32; sys_platform == 'win32'",
        "selectolax<1",
    ]
    assert check_dependencies(profile, ok) == []
    problems = check_dependencies(
        profile, ["requests", "lxml<6", "not a requirement !!", "lxml @ https://example.test/lxml.whl"]
    )
    assert [p.index for p in problems] == [0, 1, 2, 3]
    assert "not available" in problems[0].message
    assert "does not satisfy" in problems[1].message
    assert "invalid requirement" in problems[2].message
    assert "direct URL" in problems[3].message


# ------------------------------------------------------------------------------------ merge and diff
def test_merge3_lines() -> None:
    base = ["a\n", "b\n", "c\n", "d\n"]
    ours = ["a\n", "B\n", "c\n", "d\n"]
    theirs = ["a\n", "b\n", "c\n", "D\n"]
    assert merge3_lines(base, ours, theirs) == (["a\n", "B\n", "c\n", "D\n"], 0)
    assert merge3_lines(base, ours, ours) == (ours, 0)
    assert merge3_lines(base, ["a\n", "X\n", "c\n", "d\n"], ["a\n", "Y\n", "c\n", "d\n"])[1] == 1


def _pkg(manifest: dict[str, Any], **files: bytes) -> dict[str, bytes]:
    return {
        "jane-package.json": json.dumps(manifest).encode(),
        **{k.replace("__", "/"): v for k, v in files.items()},
    }


def test_merge_packages_files_and_manifest() -> None:
    m = {
        "package_id": "p",
        "version": "1.0.0",
        "title": "T",
        "tags": ["a"],
        "provenance": {"created_by": "human"},
    }
    base = _pkg(m, src__a=b"1\n", src__gone=b"x", src__bin=b"\0\1")
    ours = _pkg(
        {**m, "package_id": "f", "tags": ["a", "fork"], "fork_of": {"package_id": "p"}},
        src__a=b"1\n",
        src__gone=b"x",
        src__bin=b"\0\1",
        src__mine=b"m",
    )
    theirs = _pkg({**m, "version": "1.1.0", "title": "T2"}, src__a=b"2\n", src__bin=b"\0\1", src__new=b"n")
    r = merge_packages(base, ours, theirs, max_merge_file_bytes=1000)
    assert r.conflicts == []
    assert r.files == {"src/a": b"2\n", "src/bin": b"\0\1", "src/mine": b"m", "src/new": b"n"}
    assert r.manifest["title"] == "T2" and r.manifest["tags"] == ["a", "fork"]
    assert r.manifest["package_id"] == "f" and r.manifest["version"] == "1.0.0" and "fork_of" in r.manifest
    conflict = merge_packages(
        base,
        _pkg(m, src__a=b"3\n", src__bin=b"\0\2", src__gone=b"changed"),
        _pkg({**m, "title": "X"}, src__a=b"4\n", src__bin=b"\0\3"),
        max_merge_file_bytes=1000,
    )
    assert {c.path for c in conflict.conflicts} == {"src/a", "src/bin", "src/gone"}
    assert all(c.pointer is None for c in conflict.conflicts)


def test_diff_manifest_and_files() -> None:
    changes = diff_manifest({"a": 1, "b": {"c": [1]}, "x/y": 1}, {"a": 2, "b": {"c": [1, 2]}, "d": True})
    assert changes == [
        {"pointer": "/a", "op": "replace", "old": 1, "new": 2},
        {"pointer": "/b/c", "op": "replace", "old": [1], "new": [1, 2]},
        {"pointer": "/d", "op": "add", "new": True},
        {"pointer": "/x~1y", "op": "remove", "old": 1},
    ]
    files = diff_files(
        {"a.txt": b"1\n2\n", "gone": b"g", "img.png": b"\0\1", "jane-package.json": b"{}"},
        {"a.txt": b"1\n3\n", "new": b"n", "img.png": b"\0\2", "jane-package.json": b"{ }"},
        context_lines=1,
        max_file_bytes=1000,
        old_label="p@1",
        new_label="p@2",
    )
    by_path = {f["path"]: f for f in files}
    assert set(by_path) == {"a.txt", "gone", "img.png", "new"}
    assert by_path["a.txt"]["status"] == "modified" and "-2\n+3\n" in by_path["a.txt"]["unified_diff"]
    assert by_path["img.png"] == {"path": "img.png", "status": "modified", "binary": True}
    assert by_path["gone"]["status"] == "removed" and by_path["new"]["status"] == "added"


def test_semver_ordering() -> None:
    versions = [
        "1.0.0",
        "1.0.0-rc.1",
        "1.0.0-alpha",
        "1.0.0-alpha.1",
        "1.0.0-beta.2",
        "1.0.0-beta.11",
        "0.9.9",
        "1.10.0",
        "1.2.0+build",
    ]
    assert sort_versions(versions) == [
        "0.9.9",
        "1.0.0-alpha",
        "1.0.0-alpha.1",
        "1.0.0-beta.2",
        "1.0.0-beta.11",
        "1.0.0-rc.1",
        "1.0.0",
        "1.2.0+build",
        "1.10.0",
    ]
    assert max_version(["1.2.0", "1.10.0", "1.9.9"]) == "1.10.0"
    assert SemVer("1.0.0+a") == SemVer("1.0.0+b")
    with pytest.raises(ValueError, match="not a semantic version"):
        SemVer("latest")


# ------------------------------------------------------------------------------------ review 2: no ReDoS
def _best_scan_time(path: str, data: bytes, runs: int = 3) -> float:
    limits = SecretScanLimits()
    best = float("inf")
    for _ in range(runs):
        t0 = time.perf_counter()
        scan_files({path: data}, limits)
        best = min(best, time.perf_counter() - t0)
    return best


ADVERSARIAL = [
    ("c.yaml", lambda n: b"\n" * n),
    ("LICENSE", lambda n: b"\n" * n),
    ("c.yaml", lambda n: b" \n" * (n // 2)),
    ("c.ini", lambda n: b"\t\r\n" * (n // 3)),
    ("c.yaml", lambda n: b"\0 " * (n // 2)),
    ("m.bin", lambda n: random.Random(1).randbytes(n)),
    ("blob", lambda n: random.Random(2).randbytes(n)),
    ("c.yaml", lambda n: random.Random(3).randbytes(n)),
    ("c.py", lambda n: b"eyJ-" * (n // 4)),
    ("c.py", lambda n: b"bearer" + b"\n" * n + b"!"),
    ("c.py", lambda n: b"=" + b"\n" * n + b"!"),
    # a keyword and "=" open the pre-filters of the line-anchored assignment detector, then a newline run: the
    # review-2 ReDoS (^\s* crossing lines) again behind them is caught only with an input like this
    ("c.yaml", lambda n: b"password=x\n" + b"\n" * n),
    ("c.yaml", lambda n: b"a." * (n // 2)),
    ("c.yaml", lambda n: b"password" * (n // 8)),  # keyword-dense line without newline
    ("LICENSE", lambda n: b"password" * (n // 8)),
    ("c.py", lambda n: b"secret" * (n // 6)),
    ("c.yaml", lambda n: b"password=a" * (n // 10)),
    ("c.yaml", lambda n: b"token " * (n // 6)),
]


@pytest.mark.parametrize(("path", "gen"), ADVERSARIAL)
def test_scanner_is_linear_on_adversarial_input(path: str, gen: Any) -> None:
    """Doubling the input must not quadruple the time (the old ``(?m)^\\s*`` pattern was O(N^2): 20 000 newlines
    took 20 s). The 2N input is the N input twice, so the keyword pre-filter behaves the same on both. Minimum of
    5 runs per size; the 5 ms floor absorbs timer noise on tiny timings. A loaded machine can push one pair over
    the bound, so up to 3 pairs are measured: a quadratic scanner fails all of them (ratio about 4)."""
    data = gen(256 * 1024)
    pairs = []
    for _ in range(3):
        t1 = _best_scan_time(path, data, runs=5)
        t2 = _best_scan_time(path, data + data, runs=5)
        pairs.append(f"t(N)={t1:.4f}s t(2N)={t2:.4f}s ratio={t2 / max(t1, 1e-9):.2f}")
        if t2 <= 2.5 * max(t1, 0.005):
            return
    pytest.fail(f"{path}: not linear: " + "; ".join(pairs))


SCAN_GROWTH = 16
"""Each rung of the size ladder below is this many times larger than the previous one."""
SCAN_RUNGS = 3
"""Rungs below ``max_scan_bytes_per_file``: 2 MiB / 16**3 = 512 B, so a catastrophic pattern fails within seconds."""
SCAN_GROWTH_BOUND = float(os.environ.get("JANE_REGISTRY_TEST_SCAN_GROWTH_BOUND", "6"))
"""Allowed CPU time of one scan of the larger input over ``SCAN_GROWTH`` scans of the smaller one (the same number
of bytes): about 1 for a linear scanner - up to about 3.3 on random bytes, where the larger input passes the
keyword pre-filter of more detectors - and ``SCAN_GROWTH`` (16) for a quadratic one."""
MAX_FILE_SCAN_UNITS = float(os.environ.get("JANE_REGISTRY_TEST_MAX_FILE_SCAN_UNITS", "16"))
"""CPU time allowed for one scan of a ``max_scan_bytes_per_file`` file, in units of :func:`_reference_cpu`
measured next to it. 16 units are the former bound of 2 s on an idle development laptop (a unit is 0.11-0.125 s
there); the slowest adversarial input takes 3-4.5 units on an idle and on a loaded machine alike."""
SCAN_CPU_FLOOR_S = 0.05
"""Smaller CPU times are compared as this value (the thread clock of Windows advances in 15.6 ms ticks)."""
SCAN_ATTEMPTS = 3
"""Measurements per rung before the test fails (one can be taken while the machine changes speed)."""
SCAN_WALL_BUDGET_MS = 3_600_000
"""``scan_time_budget_ms`` of the measured scans (see :func:`_scan_cpu`)."""
_REFERENCE_LINE = "def handler(item, limits):\n    value = item.get('price') or 0  # 42 units\n"
_REFERENCE_WORD = re.compile(r"[a-z_][a-z0-9_]*")


def _scan_cpu(path: str, inputs: list[bytes]) -> float:
    """CPU time of this thread for scanning ``inputs`` one after another. Unlike wall time it does not grow
    while other processes hold the CPU. The wall-time budget of a scan (``scan_time_budget_ms``, 20 s; covered by
    ``test_scan_time_budget_is_enforced``) is lifted: a loaded machine stretched one 2 MiB scan to 13 s of wall
    time for 2.8 s of CPU time."""
    limits = SecretScanLimits(scan_time_budget_ms=SCAN_WALL_BUDGET_MS)
    t0 = time.thread_time()
    for data in inputs:
        scan_files({path: data}, limits)
    return time.thread_time() - t0


def _reference_cpu(size: int) -> float:
    """CPU time of a fixed workload of the scanner's kind (lower-casing and a regular expression over ``size``
    characters of code, 4 times). CPU time itself is not enough: on a loaded laptop (hybrid cores, lower clock)
    the same work takes up to 5 times more of it, so the bound on the largest file is relative to this unit."""
    text = (_REFERENCE_LINE * (size // len(_REFERENCE_LINE) + 1))[:size]
    t0 = time.thread_time()
    for _ in range(4):
        _REFERENCE_WORD.findall(text.lower())
    return time.thread_time() - t0


@pytest.mark.parametrize(("path", "gen"), ADVERSARIAL)
def test_scanner_handles_the_largest_scannable_file_fast(path: str, gen: Any) -> None:
    """A file of ``max_scan_bytes_per_file`` (2 MiB) of adversarial content is scanned fast, and the scan cost
    grows linearly up to that size (review 2: no ReDoS, no quadratic work).

    No wall-clock seconds (the former bound of 2 s failed at 2.8-7.8 s on a loaded machine): CPU time of the test
    thread, compared with CPU time measured next to it.

    * growth: sizes go up by ``SCAN_GROWTH`` (512 B ... 2 MiB); on every rung one scan of the larger input may
      cost at most ``SCAN_GROWTH_BOUND`` times ``SCAN_GROWTH`` scans of the smaller one (the same bytes). A
      quadratic scanner (ratio 16) fails on the small rungs already, before a catastrophic pattern runs for hours
      on 2 MiB;
    * constant factor: the 2 MiB scan may cost at most ``MAX_FILE_SCAN_UNITS`` reference units (a linear pattern
      that backtracks a long way at every position is linear, but slow).

    Each rung is measured up to ``SCAN_ATTEMPTS`` times (the CPU time of the same work changed fivefold within
    seconds on a loaded laptop with hybrid cores). The bounds can be changed through
    ``JANE_REGISTRY_TEST_SCAN_GROWTH_BOUND`` and ``JANE_REGISTRY_TEST_MAX_FILE_SCAN_UNITS``."""
    largest = SecretScanLimits().max_scan_bytes_per_file
    sizes = [largest // SCAN_GROWTH**k for k in range(SCAN_RUNGS, -1, -1)]
    for small, big in itertools.pairwise(sizes):
        small_data, big_data = gen(small), gen(big)
        top = big == largest
        tried = []
        for _ in range(SCAN_ATTEMPTS):
            unit = _reference_cpu(largest) if top else 0.0
            t_small = _scan_cpu(path, [small_data] * SCAN_GROWTH)
            t_big = _scan_cpu(path, [big_data])
            if top:
                unit = max(unit, _reference_cpu(largest))  # the slower of the two units around the scan
            if t_big > SCAN_GROWTH_BOUND * max(t_small, SCAN_CPU_FLOOR_S):
                # the machine may have slowed down during the larger scan: the smaller side once more, after it
                t_small = max(t_small, _scan_cpu(path, [small_data] * SCAN_GROWTH))
            growth = t_big / max(t_small, SCAN_CPU_FLOOR_S)
            units = t_big / max(unit, SCAN_CPU_FLOOR_S)
            tried.append(
                f"{SCAN_GROWTH}x{len(small_data)} B: {t_small:.3f} s, 1x{len(big_data)} B: {t_big:.3f} s, "
                f"growth {growth:.2f}" + (f", {units:.1f} units of {unit:.3f} s" if top else "")
            )
            if growth <= SCAN_GROWTH_BOUND and (not top or units <= MAX_FILE_SCAN_UNITS):
                break
        else:
            pytest.fail(
                f"{path}: scan cost grows faster than linearly (growth > {SCAN_GROWTH_BOUND}) or the largest file "
                f"takes more than {MAX_FILE_SCAN_UNITS} units: " + "; ".join(tried)
            )


def test_scan_time_budget_is_enforced() -> None:
    from jane_registry.secrets import ScanBudgetExceeded

    limits = SecretScanLimits(scan_time_budget_ms=1)
    files = {f"f{i}.py": b"x = 1\n" * 20_000 for i in range(50)}
    with pytest.raises(ScanBudgetExceeded):
        scan_files(files, limits)
