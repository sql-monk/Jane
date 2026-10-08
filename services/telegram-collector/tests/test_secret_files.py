"""``file:`` secret references: the read uses the path that was checked, not the raw reference (TOCTOU)."""

from __future__ import annotations

from pathlib import Path

import pytest

from jane_telegram_collector.connections import ConnectionPolicy


@pytest.fixture
def layout(tmp_path: Path) -> tuple[Path, Path, Path]:
    secrets_dir = tmp_path / "secrets"
    secrets_dir.mkdir()
    (secrets_dir / "real").write_text("inside-secret\n", encoding="utf-8")
    outside = tmp_path / "outside"
    outside.write_text("outside-secret\n", encoding="utf-8")
    link = secrets_dir / "link"
    try:
        link.symlink_to(secrets_dir / "real")
    except (OSError, NotImplementedError):
        pytest.skip("symlinks require extra privileges on this platform")
    return secrets_dir, outside, link


def test_symlink_inside_the_directory_is_read(layout: tuple[Path, Path, Path]) -> None:
    secrets_dir, _, link = layout
    policy = ConnectionPolicy(files_dir=secrets_dir)
    assert policy.ref_error(f"file:{link}") is None
    assert policy.resolve(f"file:{link}") == "inside-secret"


def test_symlink_swapped_after_the_check_is_not_followed(layout: tuple[Path, Path, Path]) -> None:
    secrets_dir, outside, link = layout

    class SwapAfterCheck(ConnectionPolicy):
        """The reference passes the check, then the link is pointed outside before the secret is read."""

        def ref_error(self, ref: str) -> str | None:
            error = super().ref_error(ref)
            link.unlink()
            link.symlink_to(outside)
            return error

    assert SwapAfterCheck(files_dir=secrets_dir).resolve(f"file:{link}") is None


def test_read_uses_the_resolved_path(layout: tuple[Path, Path, Path]) -> None:
    secrets_dir, outside, link = layout

    class SwapAfterResolve(ConnectionPolicy):
        def secret_file(self, ref: str) -> Path | None:
            path = super().secret_file(ref)
            link.unlink()
            link.symlink_to(outside)
            return path

    assert SwapAfterResolve(files_dir=secrets_dir).resolve(f"file:{link}") == "inside-secret"


def test_malformed_file_references_do_not_raise(tmp_path: Path) -> None:
    secrets_dir = tmp_path / "secrets"
    secrets_dir.mkdir()
    (secrets_dir / "binary").write_bytes(b"\xff\xfe\x00not-utf8")
    policy = ConnectionPolicy(files_dir=secrets_dir)
    nul = f"file:{secrets_dir}/a\x00b"
    assert policy.ref_error(nul) is not None and policy.resolve(nul) is None
    assert policy.resolve(f"file:{secrets_dir / 'binary'}") is None
    assert policy.resolve(f"file:{secrets_dir}") is None  # the directory itself is not a secret
