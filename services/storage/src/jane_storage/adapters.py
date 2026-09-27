"""Adapter registry: adapters are separate distributions discovered through entry points.

An adapter package (``services/storage/adapters/<name>/``, distribution ``jane-storage-<name>``)
declares in its ``pyproject.toml``::

    [project.entry-points."jane.storage.adapters"]
    filesystem = "jane_storage_files:FilesystemAdapter"      # name == Adapter.kind == Connection.kind

    [project.entry-points."jane.storage.packages"]
    "jane.storage-files" = "jane_storage_files:package_dir"  # () -> Path of the storage package directory

The core never imports adapters directly: installing the distribution is enough (``uv sync
--all-packages`` in development, the Dockerfile installs every ``services/storage/adapters/*``).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from importlib.metadata import entry_points
from pathlib import Path
from typing import Any, cast

from jane_contracts.storage_adapter import StorageAdapter

__all__ = [
    "ADAPTER_GROUP",
    "PACKAGE_GROUP",
    "REQUIRED_CAPABILITIES",
    "UnknownAdapter",
    "adapter_class",
    "available_adapters",
    "create_adapter",
    "package_dirs",
]

ADAPTER_GROUP = "jane.storage.adapters"
PACKAGE_GROUP = "jane.storage.packages"
REQUIRED_CAPABILITIES = frozenset({"objects", "entities", "history"})


class UnknownAdapter(LookupError):
    pass


def available_adapters() -> dict[str, type[StorageAdapter]]:
    """``kind`` → adapter class for every installed adapter distribution."""
    out: dict[str, type[StorageAdapter]] = {}
    for ep in entry_points(group=ADAPTER_GROUP):
        cls = cast(type[StorageAdapter], ep.load())
        kind = getattr(cls, "kind", None)
        if kind != ep.name:
            raise TypeError(f"entry point {ep.name!r} -> {ep.value}: class kind is {kind!r}")
        caps = frozenset(getattr(cls, "capabilities", ()))
        if caps != REQUIRED_CAPABILITIES:
            raise TypeError(f"adapter {kind!r}: capabilities must be {sorted(REQUIRED_CAPABILITIES)}")
        out[ep.name] = cls
    return out


def adapter_class(kind: str) -> type[StorageAdapter]:
    adapters = available_adapters()
    try:
        return adapters[kind]
    except KeyError:
        raise UnknownAdapter(
            f"storage adapter {kind!r} is not installed (installed: {sorted(adapters)})"
        ) from None


def create_adapter(kind: str, **kwargs: Any) -> StorageAdapter:
    """New, not yet opened adapter instance of ``kind``."""
    factory = cast(Callable[..., StorageAdapter], adapter_class(kind))
    return factory(**kwargs)


def package_dirs() -> Mapping[str, Path]:
    """``package_id`` → directory with ``jane-package.json`` for every installed storage package."""
    out: dict[str, Path] = {}
    for ep in entry_points(group=PACKAGE_GROUP):
        provider = ep.load()
        path = Path(provider() if callable(provider) else provider)
        if not (path / "jane-package.json").is_file():
            raise FileNotFoundError(f"storage package {ep.name!r}: {path}/jane-package.json not found")
        out[ep.name] = path
    return out
