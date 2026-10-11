# Модуль `jane_storage.compat`

> Згенеровано `scripts/docs_reference.py` з [services/storage/src/jane_storage/compat/__init__.py](../../../../../services/storage/src/jane_storage/compat/__init__.py). Не редагуйте вручну.

Adapter compatibility suite C-01…C-16 (contracts/docs/storage-adapter.md) — reusable by every adapter.

Usage in an adapter package (``services/storage/adapters/<name>/tests/test_compat.py``)::

    import pytest
    from jane_storage.compat import AdapterCompatSuite, CompatTarget

    class MyTarget(CompatTarget):
        kind = "mongodb"
        def connection(self): ...              # ResolvedConnection to an isolated namespace
        def unavailable_connection(self): ...  # same kind, storage not reachable

    class TestMongoCompat(AdapterCompatSuite):
        @pytest.fixture
        def compat_target(self):
            return MyTarget(...)

Every scenario is mandatory for all six adapters; the suite runs the real adapter (discovered through the ``jane.storage.adapters`` entry point) together with the real storage core.

## Реекспорт

| Назва | Визначено в |
|---|---|
| `SCENARIOS` | [`jane_storage.compat.suite`](jane_storage.compat.suite.md) |
| `AdapterCompatSuite` | [`jane_storage.compat.suite`](jane_storage.compat.suite.md) |
| `CompatEnv` | [`jane_storage.compat.suite`](jane_storage.compat.suite.md) |
| `CompatTarget` | [`jane_storage.compat.suite`](jane_storage.compat.suite.md) |
