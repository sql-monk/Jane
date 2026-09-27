from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from jane_extractor_sdk.package import build_archive, material_from_file
from jane_handler_runtime.settings import Settings

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
EXAMPLE = REPO / "libs" / "extractor-sdk" / "examples" / "testsite-product-extractor"
PROBE = HERE / "packages" / "probe"


def archive_ref(package_dir: Path) -> dict[str, Any]:
    data = build_archive(package_dir)
    return {
        "kind": "inline",
        "media_type": "application/zip",
        "encoding": "base64",
        "data": base64.b64encode(data).decode("ascii"),
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def digest(package_dir: Path) -> str:
    return "sha256:" + hashlib.sha256(build_archive(package_dir)).hexdigest()


def product_material(name: str = "product-phone-alpha", source_id: str | None = "testsite") -> dict[str, Any]:
    return material_from_file(
        EXAMPLE / "tests" / name / "page.html",
        media_type="text/html",
        url=f"https://testsite.example.test/product/{name.removeprefix('product-')}",
        source_id=source_id,
    )


def invocation(
    package_dir: Path,
    material: dict[str, Any],
    *,
    key: str = "dk-1",
    params: dict[str, Any] | None = None,
    **extra: Any,
) -> dict[str, Any]:

    manifest = json.loads((package_dir / "jane-package.json").read_text(encoding="utf-8"))
    body: dict[str, Any] = {
        "handler": {"package_id": manifest["package_id"], "version": manifest["version"]},
        "package_archive": archive_ref(package_dir),
        "inputs": [{"kind": "material", "material": material}],
        "delivery": {"delivery_key": key},
    }
    if params is not None:
        body["params"] = params
    body.update(extra)
    return body


class Helpers:
    """Shared helpers as a fixture (``--import-mode=importlib``: test modules cannot import conftest)."""

    example = EXAMPLE
    probe = PROBE
    repo = REPO
    archive_ref = staticmethod(archive_ref)
    digest = staticmethod(digest)
    product_material = staticmethod(product_material)
    invocation = staticmethod(invocation)


@pytest.fixture
def h() -> type[Helpers]:
    return Helpers


@pytest.fixture
def subprocess_settings(tmp_path: Path) -> Settings:
    """Settings for API/unit tests: the unsafe subprocess backend (the docker backend is covered by the
    isolation tests on a real container engine)."""
    return Settings(
        log_format="console",
        sandbox_backend="subprocess",
        allow_unsafe_subprocess=True,
        package_cache_dir=tmp_path / "cache",
    )
