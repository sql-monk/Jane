"""Secret references and destination allowlists of managed connections (ADR-0006, R17)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from jane_kit.secrets import HostAllowlist, OriginAllowlist, SecretPolicy, parse_host_port, read_secret_file


def test_env_references_need_the_prefix_and_a_plain_name() -> None:
    policy = SecretPolicy(env_prefix="JANE_SECRET_", files_dir=None)
    assert policy.ref_error("env:JANE_SECRET_PG_PASSWORD") is None
    for ref in (
        "env:PGPASSWORD",
        "env:JANE_SECRET_",  # only the prefix
        "env:JANE_SECRET_lower",
        "env:JANE_SECRET_X-Y",
        "env:JANE_SECRET_X\nY",
        "env:",
    ):
        assert policy.ref_error(ref) is not None, ref
    assert SecretPolicy(env_prefix="", files_dir=None).ref_error("env:JANE_SECRET_X") is not None
    assert policy.ref_error("vault:kv/x#y") == "vault: references are not configured in this service"
    assert policy.ref_error("http://x") == "unknown secret reference scheme"


def test_env_resolution(monkeypatch: pytest.MonkeyPatch) -> None:
    policy = SecretPolicy(files_dir=None)
    monkeypatch.setenv("JANE_SECRET_TOKEN", "t0k")
    monkeypatch.setenv("PGPASSWORD", "nope")
    assert policy.resolve("env:JANE_SECRET_TOKEN") == "t0k"
    assert policy.resolve("env:PGPASSWORD") is None
    assert policy.resolve("env:JANE_SECRET_MISSING") is None
    assert policy.resolve("env:JANE_SECRET_X", environ={"JANE_SECRET_X": "v"}) == "v"


def test_file_references_stay_inside_the_directory(tmp_path: Path) -> None:
    secrets_dir = tmp_path / "secrets"
    secrets_dir.mkdir()
    (secrets_dir / "pg").write_text("s3cret\n", encoding="utf-8")
    (secrets_dir / "empty").write_text("\n", encoding="utf-8")
    (tmp_path / "other").write_text("outside", encoding="utf-8")
    policy = SecretPolicy(files_dir=secrets_dir)
    assert policy.resolve(f"file:{secrets_dir / 'pg'}") == "s3cret"
    assert policy.resolve(f"file:{secrets_dir / 'empty'}") is None
    for ref in (f"file:{tmp_path / 'other'}", f"file:{secrets_dir}/../other", f"file:{secrets_dir}", "file:"):
        assert policy.ref_error(ref) is not None, ref
        assert policy.resolve(ref) is None
    assert (
        SecretPolicy(files_dir=None).ref_error(f"file:{secrets_dir / 'pg'}")
        == "file: references are disabled"
    )
    errors = policy.violations({"a": f"file:{secrets_dir / 'pg'}", "b": "env:PATH"})
    assert [(e.pointer, e.code) for e in errors] == [("/secret_refs/b", "secret_ref_not_allowed")]
    assert [e.pointer for e in policy.violations(["x"])] == ["/secret_refs"]


def test_symlink_out_of_the_directory_is_not_followed(tmp_path: Path) -> None:
    secrets_dir = tmp_path / "secrets"
    secrets_dir.mkdir()
    target = tmp_path / "outside.txt"
    target.write_text("leak", encoding="utf-8")
    link = secrets_dir / "link"
    try:
        os.symlink(target, link)
    except OSError:
        pytest.skip("symlinks are not available")
    policy = SecretPolicy(files_dir=secrets_dir)
    assert policy.ref_error(f"file:{link}") is not None  # resolves outside
    assert read_secret_file(link) is None  # the pinned reader refuses a symlinked leaf as well


def test_host_parsing_and_allowlist() -> None:
    assert parse_host_port("Postgres:5432") == ("postgres", 5432)
    assert parse_host_port("minio") == ("minio", None)
    for bad in ("evil.test\\@ok", "user@ok", "ok:0", "ok:65536", "ok.", "[::1]", "ok/path", "ok ", ""):
        assert parse_host_port(bad) is None, bad
    allow = HostAllowlist.of(["postgres:5432", "minio"])
    assert allow.allows("postgres", 5432) and allow.allows("MINIO", 9000) and allow.allows("minio", None)
    assert not allow.allows("postgres", 5433) and not allow.allows("postgres", None)
    with pytest.raises(ValueError, match="hostname"):
        HostAllowlist.of(["http://x"])


def test_origin_allowlist() -> None:
    allow = OriginAllowlist.of(["https://api.anthropic.com", "http://fake-llm:8080/"])
    assert allow.allows("https://api.anthropic.com/v1/messages")
    assert allow.allows("https://api.anthropic.com:443")
    assert allow.allows("http://fake-llm:8080")
    for url in (
        "https://api.anthropic.com.attacker.example",
        "http://api.anthropic.com",
        "https://user@api.anthropic.com",
        "https://api.anthropic.com\\@evil.example",
        "https://api.anthropic.com:99999",
        "https://api.anthropic.com :443",
        None,
    ):
        assert not allow.allows(url), url
    with pytest.raises(ValueError, match="exact"):
        OriginAllowlist.of(["https://api.openai.com/v1"])
