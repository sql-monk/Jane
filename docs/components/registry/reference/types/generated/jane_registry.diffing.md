# jane_registry.diffing

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_registry.diffing.escape_pointer](#jane_registrydiffingescape_pointer)
- [jane_registry.diffing.diff_manifest](#jane_registrydiffingdiff_manifest)
- [jane_registry.diffing.is_text](#jane_registrydiffingis_text)
- [jane_registry.diffing.diff_files](#jane_registrydiffingdiff_files)

## jane_registry.diffing.escape_pointer

**Функція.** Код: [services/registry/src/jane_registry/diffing.py:23](../../../../../../services/registry/src/jane_registry/diffing.py#L23).

```python
def escape_pointer(token: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `token` | `str` | `—` | positional-or-keyword |

Результат: `str`.

## jane_registry.diffing.diff_manifest

**Функція.** Код: [services/registry/src/jane_registry/diffing.py:27](../../../../../../services/registry/src/jane_registry/diffing.py#L27).

```python
def diff_manifest(old: Any, new: Any, pointer: str='') -> list[dict[str, Any]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `old` | `Any` | `—` | positional-or-keyword |
| `new` | `Any` | `—` | positional-or-keyword |
| `pointer` | `str` | `''` | positional-or-keyword |

Результат: `list[dict[str, Any]]`.

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_units.py:352](../../../../../../services/registry/tests/test_units.py#L352).

```python
changes = diff_manifest({"a": 1, "b": {"c": [1]}, "x/y": 1}, {"a": 2, "b": {"c": [1, 2]}, "d": True})
```

## jane_registry.diffing.is_text

**Функція.** Код: [services/registry/src/jane_registry/diffing.py:45](../../../../../../services/registry/src/jane_registry/diffing.py#L45).

```python
def is_text(data: bytes) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `data` | `bytes` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_registry.diffing.diff_files

**Функція.** Код: [services/registry/src/jane_registry/diffing.py:55](../../../../../../services/registry/src/jane_registry/diffing.py#L55).

```python
def diff_files(old: Mapping[str, bytes], new: Mapping[str, bytes], *, context_lines: int, max_file_bytes: int, old_label: str, new_label: str) -> list[dict[str, Any]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `old` | `Mapping[str, bytes]` | `—` | positional-or-keyword |
| `new` | `Mapping[str, bytes]` | `—` | positional-or-keyword |
| `context_lines` | `int` | `—` | keyword-only |
| `max_file_bytes` | `int` | `—` | keyword-only |
| `old_label` | `str` | `—` | keyword-only |
| `new_label` | `str` | `—` | keyword-only |

Результат: `list[dict[str, Any]]`.

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_units.py:359](../../../../../../services/registry/tests/test_units.py#L359).

```python
files = diff_files(
        {"a.txt": b"1\n2\n", "gone": b"g", "img.png": b"\0\1", "jane-package.json": b"{}"},
        {"a.txt": b"1\n3\n", "new": b"n", "img.png": b"\0\2", "jane-package.json": b"{ }"},
        context_lines=1,
        max_file_bytes=1000,
        old_label="p@1",
        new_label="p@2",
    )
```
