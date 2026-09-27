"""Strategy registry (``jane_contracts.discovery.StrategyRegistry``) and the plug-in points for WP-03.

Sources, in this order (a later source may not redefine an existing ``type_name``):

1. built-ins of the core: ``seed_list``, ``recursive``;
2. the WP-03 package directory ``services/web-collector/strategies/discovery/`` (override:
   ``JANE_WEB_COLLECTOR_DISCOVERY_PATH``): imported as the package ``jane_web_collector_discovery``
   (relative imports inside it work) and its ``STRATEGIES: list[type[DiscoveryStrategy]]`` is registered;
3. entry points of the group ``jane.web_collector.strategies`` (a class or a list of classes) for strategy
   packages installed next to the service.

``llm_explore`` is reserved and never supported by the collector (ADR-0010).
"""

from __future__ import annotations

import importlib.util
import logging
import sys
from collections.abc import Iterable, Sequence
from importlib.metadata import entry_points
from pathlib import Path
from types import ModuleType
from typing import Any

from jane_contracts.discovery import DiscoveryStrategy

from .builtin import RecursiveStrategy, SeedListStrategy

__all__ = [
    "DISCOVERY_MODULE",
    "ENTRY_POINT_GROUP",
    "RESERVED_TYPES",
    "Registry",
    "default_discovery_path",
    "load_discovery_package",
]

log = logging.getLogger(__name__)

ENTRY_POINT_GROUP = "jane.web_collector.strategies"
DISCOVERY_MODULE = "jane_web_collector_discovery"
RESERVED_TYPES = frozenset({"llm_explore"})
"""Valid in CollectorRules but not executed by the collector in v1 (ADR-0010)."""


def default_discovery_path() -> Path:
    """``services/web-collector/strategies/discovery`` next to ``src/`` (editable/dev checkout)."""
    return Path(__file__).resolve().parents[3] / "strategies" / "discovery"


def load_discovery_package(path: Path) -> ModuleType | None:
    """Import the WP-03 package at ``path`` (a directory with ``__init__.py``) as ``jane_web_collector_discovery``."""
    init = path / "__init__.py"
    if not init.is_file():
        return None
    if DISCOVERY_MODULE in sys.modules:
        module = sys.modules[DISCOVERY_MODULE]
        if Path(getattr(module, "__file__", "") or "").resolve() == init.resolve():
            return module
    spec = importlib.util.spec_from_file_location(
        DISCOVERY_MODULE, init, submodule_search_locations=[str(path)]
    )
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[DISCOVERY_MODULE] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(DISCOVERY_MODULE, None)
        raise
    return module


class Registry:
    """``StrategyRegistry`` owned by WP-02."""

    def __init__(self) -> None:
        self._types: dict[str, type[DiscoveryStrategy]] = {}
        self.origins: dict[str, str] = {}
        self.load_errors: list[str] = []

    def register(self, strategy: type[DiscoveryStrategy], origin: str = "code") -> None:
        name = getattr(strategy, "type_name", None)
        if not isinstance(name, str) or not name:
            raise TypeError(f"{strategy!r} has no type_name")
        if name in RESERVED_TYPES:
            raise ValueError(
                f"strategy type {name!r} is reserved and not executed by the collector (ADR-0010)"
            )
        if name in self._types and self._types[name] is not strategy:
            raise ValueError(f"strategy type {name!r} already registered from {self.origins[name]}")
        for method in ("seeds", "on_fetched", "snapshot", "restore"):
            if not callable(getattr(strategy, method, None)):
                raise TypeError(f"{strategy!r} does not implement DiscoveryStrategy.{method}")
        self._types[name] = strategy
        self.origins[name] = origin

    def get(self, type_name: str) -> type[DiscoveryStrategy]:
        return self._types[type_name]

    def types(self) -> Sequence[str]:
        return sorted(self._types)

    def supported(self, type_name: str) -> bool:
        return type_name in self._types

    def _register_many(self, items: Iterable[Any], origin: str) -> None:
        for item in items:
            try:
                self.register(item, origin)
            except (TypeError, ValueError) as exc:
                self.load_errors.append(f"{origin}: {exc}")
                log.error("strategy not registered", extra={"origin": origin, "error": str(exc)})

    @classmethod
    def default(cls, discovery_path: Path | None = None, *, use_entry_points: bool = True) -> Registry:
        reg = cls()
        reg.register(SeedListStrategy, "core")
        reg.register(RecursiveStrategy, "core")
        path = discovery_path or default_discovery_path()
        try:
            module = load_discovery_package(path)
        except Exception as exc:
            reg.load_errors.append(f"{path}: {type(exc).__name__}: {exc}")
            log.exception("discovery package failed to import", extra={"path": str(path)})
            module = None
        if module is not None:
            strategies = getattr(module, "STRATEGIES", None)
            if isinstance(strategies, (list, tuple)):
                reg._register_many(strategies, f"package:{path}")
            else:
                reg.load_errors.append(f"{path}: package has no STRATEGIES list")
        if use_entry_points:
            for ep in entry_points(group=ENTRY_POINT_GROUP):
                try:
                    loaded = ep.load()
                except Exception as exc:
                    reg.load_errors.append(f"entry point {ep.name}: {type(exc).__name__}: {exc}")
                    continue
                items = loaded if isinstance(loaded, (list, tuple)) else [loaded]
                reg._register_many(items, f"entry_point:{ep.name}")
        return reg
