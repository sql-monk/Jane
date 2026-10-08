"""Deterministic "work still running" windows for R-04 (``tests/e2e/test_r04_active_replays.py``).

* :class:`Gate` - a material download held open by the ``package-host`` stand-in (``/e2e/gates``, see
  ``package_host.py``): the content of a material is a blob whose ``download_url`` points at the gate, so a
  service that reads it is provably inside its work until the test releases the gate. SUBSTITUTE (З) of the
  blob store behind ``download_url`` (ADR-0004); the services read it through their real code path.
* :func:`package_ref` - pinned ref and inline archive of a local fixture package (``tests/e2e/packages``), for
  direct ``handler.v1`` calls that carry ``package_archive``; the archive is the registry's canonical one, so
  the same ref also pins the version published to the real registry (``E2EStack.publish_local_package``).
* :func:`wait_for` - poll a condition instead of sleeping.
"""

from __future__ import annotations

import base64
import hashlib
import json
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import httpx

from jane_e2e.stack import E2EStack
from jane_registry.archive import canonical_archive, files_from_dir

__all__ = ["PACKAGE_HOST", "Gate", "gate", "package_ref", "wait_for"]

PACKAGE_HOST = "http://package-host:8080"  # the stand-in as seen by the services inside the compose network
POLL_S = 0.1


def wait_for[T](
    what: str, probe: Callable[[], T | None], timeout_s: float = 120.0, poll_s: float = POLL_S
) -> T:
    """Poll ``probe`` until it returns a value other than ``None``."""
    deadline = time.monotonic() + timeout_s
    while True:
        value = probe()
        if value is not None:
            return value
        if time.monotonic() > deadline:
            raise TimeoutError(f"{what}: not reached in {timeout_s:.0f}s")
        time.sleep(poll_s)


class Gate:
    """One gate of the ``package-host`` stand-in: ``content`` served at :attr:`download_url` once released."""

    def __init__(self, stack: E2EStack, name: str, content: bytes, media_type: str) -> None:
        self.name = name
        self.content = content
        self.media_type = media_type
        self.base_url = stack.url("package-host")
        r = self._call("PUT", "", content=content, headers={"Content-Type": media_type})
        assert r.status_code == 201, r.text

    def _call(self, method: str, suffix: str, **kwargs: Any) -> httpx.Response:
        """One request on its own connection: the gate stays usable after the scenario released it."""
        return httpx.request(method, f"{self.base_url}/e2e/gates/{self.name}{suffix}", timeout=30.0, **kwargs)

    @property
    def download_url(self) -> str:
        return f"{PACKAGE_HOST}/e2e/gates/{self.name}/content"

    def content_ref(self, charset: str | None = None) -> dict[str, Any]:
        """``ContentRef`` (``kind: blob``) of the gated content: an ``s3://`` address that no reader of this
        stack can open directly (no transit store is configured), so every reader uses ``download_url``."""
        ref: dict[str, Any] = {
            "kind": "blob",
            "uri": f"s3://e2e-gates/{self.name}",
            "download_url": self.download_url,
            "media_type": self.media_type,
            "size_bytes": len(self.content),
            "sha256": hashlib.sha256(self.content).hexdigest(),
            "store": "transit",
        }
        if charset:
            ref["charset"] = charset
        return ref

    def status(self) -> dict[str, Any]:
        r = self._call("GET", "")
        assert r.status_code == 200, r.text
        return dict(r.json())

    def wait_held(self, count: int = 1, timeout_s: float = 120.0) -> dict[str, Any]:
        """Wait until ``count`` downloads are held by the gate (the readers are inside their work)."""

        def held() -> dict[str, Any] | None:
            status = self.status()
            return status if status["waiting"] >= count else None

        return wait_for(f"{count} download(s) held by gate {self.name}", held, timeout_s)

    def release(self) -> dict[str, Any]:
        r = self._call("POST", "/release")
        assert r.status_code == 200, r.text
        return dict(r.json())


@contextmanager
def gate(stack: E2EStack, name: str, content: bytes, media_type: str) -> Iterator[Gate]:
    """A :class:`Gate` that is always released at the end, so a failed scenario leaves no reader blocked."""
    g = Gate(stack, name, content, media_type)
    try:
        yield g
    finally:
        g.release()


def package_ref(package_dir: Path) -> tuple[dict[str, str], dict[str, Any]]:
    """Pinned ``PackageRef`` (id, version, digest of the registry's canonical archive) and the archive as inline
    ``ContentRef`` (``package_archive`` of a direct call). The registry stores this canonical form of the same
    files, so the digest also matches the version published there."""
    manifest = json.loads((package_dir / "jane-package.json").read_text(encoding="utf-8"))
    archive = canonical_archive(files_from_dir(package_dir))
    sha = hashlib.sha256(archive).hexdigest()
    ref = {
        "package_id": str(manifest["package_id"]),
        "version": str(manifest["version"]),
        "digest": f"sha256:{sha}",
    }
    content = {
        "kind": "inline",
        "media_type": "application/zip",
        "encoding": "base64",
        "data": base64.b64encode(archive).decode("ascii"),
        "size_bytes": len(archive),
        "sha256": sha,
    }
    return ref, content
