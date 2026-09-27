"""Discovery strategies of the Web Collector: registry, built-ins and link extraction helpers."""

from .builtin import RecursiveStrategy, SeedListStrategy
from .registry import ENTRY_POINT_GROUP, Registry, default_discovery_path, load_discovery_package

__all__ = [
    "ENTRY_POINT_GROUP",
    "RecursiveStrategy",
    "Registry",
    "SeedListStrategy",
    "default_discovery_path",
    "load_discovery_package",
]
