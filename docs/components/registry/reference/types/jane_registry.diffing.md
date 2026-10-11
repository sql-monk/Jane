# Модуль `jane_registry.diffing`

> Згенеровано `scripts/docs_reference.py` з [services/registry/src/jane_registry/diffing.py](../../../../../services/registry/src/jane_registry/diffing.py). Не редагуйте вручну.

Differences between two package versions (``GET /v1/packages/{id}/diff``, ``PackageDiff``).

* ``manifest_changes`` - JSON Pointer (RFC 6901) changes of ``jane-package.json`` (objects are compared key by key, arrays and scalars as whole values);
* ``files`` - every other file: ``added | removed | modified | unchanged``; text files get a unified diff (``modified`` only), non-UTF-8 files are ``binary: true``; files above ``diff.max_diff_file_bytes`` get the status only.

## Зміст

- [Функція `diff_files`](#функція-diff_files)
- [Функція `diff_manifest`](#функція-diff_manifest)
- [Функція `escape_pointer`](#функція-escape_pointer)
- [Функція `is_text`](#функція-is_text)

## Функції

### Функція `diff_files`

```python
def diff_files(
    old: Mapping[str, bytes],
    new: Mapping[str, bytes],
    *,
    context_lines: int,
    max_file_bytes: int,
    old_label: str,
    new_label: str,
) -> list[dict[str, Any]]: ...
```

Код: [diffing.py:55](../../../../../services/registry/src/jane_registry/diffing.py#L55).

### Функція `diff_manifest`

```python
def diff_manifest(old: Any, new: Any, pointer: str = '') -> list[dict[str, Any]]: ...
```

Код: [diffing.py:27](../../../../../services/registry/src/jane_registry/diffing.py#L27).

### Функція `escape_pointer`

```python
def escape_pointer(token: str) -> str: ...
```

Код: [diffing.py:23](../../../../../services/registry/src/jane_registry/diffing.py#L23).

### Функція `is_text`

```python
def is_text(data: bytes) -> bool: ...
```

Код: [diffing.py:45](../../../../../services/registry/src/jane_registry/diffing.py#L45).
