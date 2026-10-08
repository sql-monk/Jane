"""``file:`` secret references: the read uses the path that was checked, not the raw reference (TOCTOU)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest

from jane_llm.connections import ConnectionPolicy, resolve_ref


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
    assert resolve_ref(f"file:{link}", policy) == "inside-secret"


def test_symlink_swapped_after_the_check_is_not_followed(layout: tuple[Path, Path, Path]) -> None:
    secrets_dir, outside, link = layout

    class SwapAfterCheck(ConnectionPolicy):
        """The reference passes the check, then the link is pointed outside before the secret is read."""

        def ref_error(self, ref: str) -> str | None:
            error = super().ref_error(ref)
            link.unlink()
            link.symlink_to(outside)
            return error

    assert resolve_ref(f"file:{link}", SwapAfterCheck(files_dir=secrets_dir)) is None


def test_read_uses_the_resolved_path(layout: tuple[Path, Path, Path]) -> None:
    secrets_dir, outside, link = layout

    class SwapAfterResolve(ConnectionPolicy):
        def secret_file(self, ref: str) -> Path | None:
            path = super().secret_file(ref)
            link.unlink()
            link.symlink_to(outside)
            return path

    assert resolve_ref(f"file:{link}", SwapAfterResolve(files_dir=secrets_dir)) == "inside-secret"


@pytest.mark.parametrize("swap", ["target", "parent"])
def test_resolved_target_or_parent_swapped_before_open_is_not_read(tmp_path: Path, swap: str) -> None:
    secrets_dir = tmp_path / "secrets"
    parent = secrets_dir / "sub"
    parent.mkdir(parents=True)
    target = parent / "secret"
    target.write_text("inside-secret", encoding="utf-8")
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret").write_text("outside-secret", encoding="utf-8")

    class SwapAfterResolvedTarget(ConnectionPolicy):
        def secret_file(self, ref: str) -> Path | None:
            path = super().secret_file(ref)
            if swap == "target":
                target.unlink()
                target.symlink_to(outside / "secret")
            else:
                parent.rename(secrets_dir / "original-sub")
                parent.symlink_to(outside, target_is_directory=True)
            return path

    assert resolve_ref(f"file:{target}", SwapAfterResolvedTarget(files_dir=secrets_dir)) is None


def test_malformed_file_references_do_not_raise(tmp_path: Path) -> None:
    secrets_dir = tmp_path / "secrets"
    secrets_dir.mkdir()
    (secrets_dir / "binary").write_bytes(b"\xff\xfe\x00not-utf8")
    policy = ConnectionPolicy(files_dir=secrets_dir)
    nul = f"file:{secrets_dir}/a\x00b"
    assert policy.ref_error(nul) is not None and resolve_ref(nul, policy) is None
    assert resolve_ref(f"file:{secrets_dir / 'binary'}", policy) is None
    assert resolve_ref(f"file:{secrets_dir}", policy) is None  # the directory itself is not a secret


@pytest.mark.parametrize("swap", ["target", "parent"])
def test_swap_after_open_cannot_redirect_the_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, swap: str
) -> None:
    secrets_dir = tmp_path / "secrets"
    parent = secrets_dir / "sub"
    parent.mkdir(parents=True)
    target = parent / "secret"
    target.write_text("inside-secret", encoding="utf-8")
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret").write_text("outside-secret", encoding="utf-8")
    real_fdopen = os.fdopen
    attempted = False

    def before_bytes(fd: int, *args: Any, **kwargs: Any) -> Any:
        nonlocal attempted
        attempted = True
        try:
            if swap == "target":
                target.unlink()
                target.symlink_to(outside / "secret")
            else:
                parent.rename(secrets_dir / "original-sub")
                parent.symlink_to(outside, target_is_directory=True)
        except PermissionError:
            # Windows handles prohibit deletion/rename; POSIX reads the already pinned descriptors.
            assert os.name == "nt"
        return real_fdopen(fd, *args, **kwargs)

    # Replace the OS stream wrapper at the boundary, after verification and before the first byte.
    monkeypatch.setattr(os, "fdopen", before_bytes)
    assert resolve_ref(f"file:{target}", ConnectionPolicy(files_dir=secrets_dir)) == "inside-secret"
    assert attempted
