"""Jane internal interface contracts (plan.md WP-00).

- :mod:`jane_contracts.discovery` — material discovery strategy for the Web Collector (WP-02/WP-03).
- :mod:`jane_contracts.storage_adapter` — storage adapter used by the storage handler (WP-07/WP-08).

Only typing Protocols and plain dataclasses; no runtime dependencies. Semantics are described in
``contracts/docs/discovery-strategy.md`` and ``contracts/docs/storage-adapter.md``.
"""

CONTRACT_VERSION = "1.1.0"
"""1.1.0 (WP-16): additive changes of ``discovery`` (``fetch`` method/body, ``emit_material``,
``DiscoveredMaterial``, ``RefreshingStrategy``); every 1.0 implementation of a strategy works unchanged."""
