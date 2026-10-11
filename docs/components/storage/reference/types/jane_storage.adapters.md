# Модуль `jane_storage.adapters`

> Згенеровано `scripts/docs_reference.py` з [services/storage/src/jane_storage/adapters.py](../../../../../services/storage/src/jane_storage/adapters.py). Не редагуйте вручну.

Adapter registry: adapters are separate distributions discovered through entry points.

An adapter package (``services/storage/adapters/<name>/``, distribution ``jane-storage-<name>``) declares in its ``pyproject.toml``::

    [project.entry-points."jane.storage.adapters"]
    filesystem = "jane_storage_files:FilesystemAdapter"      # name == Adapter.kind == Connection.kind

    [project.entry-points."jane.storage.packages"]
    "jane.storage-files" = "jane_storage_files:package_dir"  # () -> Path of the storage package directory

The core never imports adapters directly: installing the distribution is enough (``uv sync --all-packages`` in development, the Dockerfile installs every ``services/storage/adapters/*``).

## Зміст

- [Клас `UnknownAdapter`](#клас-unknownadapter)
- [Функція `adapter_class`](#функція-adapter_class)
- [Функція `available_adapters`](#функція-available_adapters)
- [Функція `create_adapter`](#функція-create_adapter)
- [Функція `package_dirs`](#функція-package_dirs)

## Класи

### Клас `UnknownAdapter`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_storage.adapters` |
| Успадкування | `LookupError` |
| Код | [adapters.py:41](../../../../../services/storage/src/jane_storage/adapters.py#L41) |

```python
class UnknownAdapter(LookupError): ...
```

## Функції

### Функція `adapter_class`

```python
def adapter_class(kind: str) -> type[StorageAdapter]: ...
```

Винятки в коді функції: `UnknownAdapter`.

Код: [adapters.py:60](../../../../../services/storage/src/jane_storage/adapters.py#L60).

### Функція `available_adapters`

```python
def available_adapters() -> dict[str, type[StorageAdapter]]: ...
```

``kind`` → adapter class for every installed adapter distribution.

Винятки в коді функції: `TypeError`.

Код: [adapters.py:45](../../../../../services/storage/src/jane_storage/adapters.py#L45).

### Функція `create_adapter`

```python
def create_adapter(kind: str, **kwargs: Any) -> StorageAdapter: ...
```

New, not yet opened adapter instance of ``kind``.

Код: [adapters.py:70](../../../../../services/storage/src/jane_storage/adapters.py#L70).

### Функція `package_dirs`

```python
def package_dirs() -> Mapping[str, Path]: ...
```

``package_id`` → directory with ``jane-package.json`` for every installed storage package.

Винятки в коді функції: `FileNotFoundError`.

Код: [adapters.py:76](../../../../../services/storage/src/jane_storage/adapters.py#L76).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `ADAPTER_GROUP` | — | `'jane.storage.adapters'` |  |
| `PACKAGE_GROUP` | — | `'jane.storage.packages'` |  |
| `REQUIRED_CAPABILITIES` | — | `frozenset({'objects', 'entities', 'history'})` |  |
