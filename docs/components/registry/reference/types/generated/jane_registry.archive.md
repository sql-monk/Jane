# jane_registry.archive

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_registry.archive.MANIFEST_NAME](#jane_registryarchivemanifest_name)
- [jane_registry.archive.SKIP_PARTS](#jane_registryarchiveskip_parts)
- [jane_registry.archive.ArchiveError](#jane_registryarchivearchiveerror)
- [jane_registry.archive.ArchiveError.__init__](#jane_registryarchivearchiveerror__init__)
- [jane_registry.archive.ArchiveError.limit](#jane_registryarchivearchiveerrorlimit)
- [jane_registry.archive.ArchiveError.path](#jane_registryarchivearchiveerrorpath)
- [jane_registry.archive.ArchiveLimits](#jane_registryarchivearchivelimits)
- [jane_registry.archive.ArchiveLimits.__init__](#jane_registryarchivearchivelimits__init__)
- [jane_registry.archive.ArchiveLimits.max_archive_bytes](#jane_registryarchivearchivelimitsmax_archive_bytes)
- [jane_registry.archive.ArchiveLimits.max_unpacked_bytes](#jane_registryarchivearchivelimitsmax_unpacked_bytes)
- [jane_registry.archive.ArchiveLimits.max_files](#jane_registryarchivearchivelimitsmax_files)
- [jane_registry.archive.check_package_path](#jane_registryarchivecheck_package_path)
- [jane_registry.archive.check_unique_paths](#jane_registryarchivecheck_unique_paths)
- [jane_registry.archive.digest_of](#jane_registryarchivedigest_of)
- [jane_registry.archive.canonical_archive](#jane_registryarchivecanonical_archive)
- [jane_registry.archive.read_archive](#jane_registryarchiveread_archive)
- [jane_registry.archive.is_canonical](#jane_registryarchiveis_canonical)
- [jane_registry.archive.manifest_bytes](#jane_registryarchivemanifest_bytes)
- [jane_registry.archive.files_from_dir](#jane_registryarchivefiles_from_dir)

## jane_registry.archive.MANIFEST_NAME

**Константа.** Код: [services/registry/src/jane_registry/archive.py:48](../../../../../../services/registry/src/jane_registry/archive.py#L48).

```python
MANIFEST_NAME = 'jane-package.json'
```

## jane_registry.archive.SKIP_PARTS

**Константа.** Код: [services/registry/src/jane_registry/archive.py:53](../../../../../../services/registry/src/jane_registry/archive.py#L53).

```python
SKIP_PARTS = frozenset({'__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', '.git', '.venv'})
```

### Опис із вихідного коду

```text
Cache/VCS directories that :func:`files_from_dir` never packs (they are not part of a package).
```

## jane_registry.archive.ArchiveError

**Клас.** Код: [services/registry/src/jane_registry/archive.py:57](../../../../../../services/registry/src/jane_registry/archive.py#L57).

```python
class ArchiveError(ValueError):
```

Базові типи / інтерфейси: `ValueError`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_registry.archive.md#jane_registryarchivearchiveerror__init__) | Конструктор | ні |
| [limit](jane_registry.archive.md#jane_registryarchivearchiveerrorlimit) | Поле екземпляра | ні |
| [path](jane_registry.archive.md#jane_registryarchivearchiveerrorpath) | Поле екземпляра | ні |

### Опис із вихідного коду

```text
The archive or a path in it is not acceptable; ``limit`` is set when a size limit was exceeded.
```

## jane_registry.archive.ArchiveError.__init__

**Конструктор.** Код: [services/registry/src/jane_registry/archive.py:60](../../../../../../services/registry/src/jane_registry/archive.py#L60).

```python
def __init__(self, message: str, *, limit: str | None=None, path: str | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `message` | `str` | `—` | positional-or-keyword |
| `limit` | `str \| None` | `None` | keyword-only |
| `path` | `str \| None` | `None` | keyword-only |

Результат: `None`.

## jane_registry.archive.ArchiveError.limit

**Поле екземпляра.** Код: [services/registry/src/jane_registry/archive.py:62](../../../../../../services/registry/src/jane_registry/archive.py#L62).

```python
self.limit = limit
```

## jane_registry.archive.ArchiveError.path

**Поле екземпляра.** Код: [services/registry/src/jane_registry/archive.py:63](../../../../../../services/registry/src/jane_registry/archive.py#L63).

```python
self.path = path
```

## jane_registry.archive.ArchiveLimits

**Клас.** Код: [services/registry/src/jane_registry/archive.py:67](../../../../../../services/registry/src/jane_registry/archive.py#L67).

```python
class ArchiveLimits:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_archive_bytes](jane_registry.archive.md#jane_registryarchivearchivelimitsmax_archive_bytes) | Поле | ні |
| [max_unpacked_bytes](jane_registry.archive.md#jane_registryarchivearchivelimitsmax_unpacked_bytes) | Поле | ні |
| [max_files](jane_registry.archive.md#jane_registryarchivearchivelimitsmax_files) | Поле | ні |
| [__init__](jane_registry.archive.md#jane_registryarchivearchivelimits__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
Bounds for reading an untrusted archive; values come from ``RegistryLimits.packages``.
```

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_units.py:37](../../../../../../services/registry/tests/test_units.py#L37).

```python
LIMITS = ArchiveLimits(max_archive_bytes=10_000_000, max_unpacked_bytes=10_000_000, max_files=100)
```

Контекст і передумови: [services/registry/tests/test_units.py:104](../../../../../../services/registry/tests/test_units.py#L104).

```python
read_archive(big, ArchiveLimits(10_000, 10_000, 4))
```

## jane_registry.archive.ArchiveLimits.__init__

**Конструктор dataclass.** Код: [services/registry/src/jane_registry/archive.py:67](../../../../../../services/registry/src/jane_registry/archive.py#L67).

```python
def __init__(self, max_archive_bytes: int, max_unpacked_bytes: int, max_files: int) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `max_archive_bytes` | `int` | `—` | positional-or-keyword |
| `max_unpacked_bytes` | `int` | `—` | positional-or-keyword |
| `max_files` | `int` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_units.py:37](../../../../../../services/registry/tests/test_units.py#L37).

```python
LIMITS = ArchiveLimits(max_archive_bytes=10_000_000, max_unpacked_bytes=10_000_000, max_files=100)
```

Контекст і передумови: [services/registry/tests/test_units.py:104](../../../../../../services/registry/tests/test_units.py#L104).

```python
read_archive(big, ArchiveLimits(10_000, 10_000, 4))
```

## jane_registry.archive.ArchiveLimits.max_archive_bytes

**Поле.** Код: [services/registry/src/jane_registry/archive.py:70](../../../../../../services/registry/src/jane_registry/archive.py#L70).

```python
max_archive_bytes: int
```

Доступ: читання — так; запис — ні.

## jane_registry.archive.ArchiveLimits.max_unpacked_bytes

**Поле.** Код: [services/registry/src/jane_registry/archive.py:71](../../../../../../services/registry/src/jane_registry/archive.py#L71).

```python
max_unpacked_bytes: int
```

Доступ: читання — так; запис — ні.

## jane_registry.archive.ArchiveLimits.max_files

**Поле.** Код: [services/registry/src/jane_registry/archive.py:72](../../../../../../services/registry/src/jane_registry/archive.py#L72).

```python
max_files: int
```

Доступ: читання — так; запис — ні.

## jane_registry.archive.check_package_path

**Функція.** Код: [services/registry/src/jane_registry/archive.py:75](../../../../../../services/registry/src/jane_registry/archive.py#L75).

```python
def check_package_path(name: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `name` | `str` | `—` | positional-or-keyword |

Результат: `str`.

Явні `raise` у тілі: `ArchiveError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_units.py:254](../../../../../../services/registry/tests/test_units.py#L254).

```python
check_package_path("src/.hidden/x.py")
```

Контекст і передумови: [services/registry/tests/test_units.py:253](../../../../../../services/registry/tests/test_units.py#L253).

```python
check_package_path(bad)
```

## jane_registry.archive.check_unique_paths

**Функція.** Код: [services/registry/src/jane_registry/archive.py:81](../../../../../../services/registry/src/jane_registry/archive.py#L81).

```python
def check_unique_paths(names: list[str]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `names` | `list[str]` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `ArchiveError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Paths that differ only in letter case would collide on Windows/macOS file systems.
```

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_units.py:256](../../../../../../services/registry/tests/test_units.py#L256).

```python
check_unique_paths(["tests/Readme.txt", "tests/README.txt"])
```

## jane_registry.archive.digest_of

**Функція.** Код: [services/registry/src/jane_registry/archive.py:91](../../../../../../services/registry/src/jane_registry/archive.py#L91).

```python
def digest_of(data: bytes) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `data` | `bytes` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
``sha256:<hex>`` - ``Digest`` of the contracts.
```

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_api.py:102](../../../../../../services/registry/tests/test_api.py#L102).

```python
expected = digest_of(canonical_archive({**files, "jane-package.json": manifest_bytes(manifest_b)}))
```

Контекст і передумови: [services/registry/tests/test_api.py:64](../../../../../../services/registry/tests/test_api.py#L64).

```python
assert digest_of(archive.content) == v["digest"]
```

## jane_registry.archive.canonical_archive

**Функція.** Код: [services/registry/src/jane_registry/archive.py:96](../../../../../../services/registry/src/jane_registry/archive.py#L96).

```python
def canonical_archive(files: Mapping[str, bytes]) -> bytes:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `files` | `Mapping[str, bytes]` | `—` | positional-or-keyword |

Результат: `bytes`.

### Опис із вихідного коду

```text
The canonical zip of ``files`` (package path -> content).
```

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_api.py:72](../../../../../../services/registry/tests/test_api.py#L72).

```python
assert canonical_archive(files) == archive.content
```

Контекст і передумови: [services/registry/tests/test_api.py:102](../../../../../../services/registry/tests/test_api.py#L102).

```python
expected = digest_of(canonical_archive({**files, "jane-package.json": manifest_bytes(manifest_b)}))
```

## jane_registry.archive.read_archive

**Функція.** Код: [services/registry/src/jane_registry/archive.py:110](../../../../../../services/registry/src/jane_registry/archive.py#L110).

```python
def read_archive(data: bytes, limits: ArchiveLimits) -> dict[str, bytes]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `data` | `bytes` | `—` | positional-or-keyword |
| `limits` | `ArchiveLimits` | `—` | positional-or-keyword |

Результат: `dict[str, bytes]`.

Явні `raise` у тілі: `ArchiveError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Files of an untrusted zip with path, symlink, duplicate, count and size checks.
```

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_units.py:66](../../../../../../services/registry/tests/test_units.py#L66).

```python
repacked = canonical_archive(read_archive(zip_of(manifest, files), LIMITS))
```

Контекст і передумови: [services/registry/tests/test_units.py:84](../../../../../../services/registry/tests/test_units.py#L84).

```python
read_archive(buf.getvalue(), LIMITS)
```

## jane_registry.archive.is_canonical

**Функція.** Код: [services/registry/src/jane_registry/archive.py:156](../../../../../../services/registry/src/jane_registry/archive.py#L156).

```python
def is_canonical(data: bytes, limits: ArchiveLimits) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `data` | `bytes` | `—` | positional-or-keyword |
| `limits` | `ArchiveLimits` | `—` | positional-or-keyword |

Результат: `bool`.

### Опис із вихідного коду

```text
``True`` if ``data`` is exactly the canonical archive of its own files.
```

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_units.py:68](../../../../../../services/registry/tests/test_units.py#L68).

```python
assert is_canonical(a, LIMITS) and not is_canonical(zip_of(manifest, files), LIMITS)
```

## jane_registry.archive.manifest_bytes

**Функція.** Код: [services/registry/src/jane_registry/archive.py:164](../../../../../../services/registry/src/jane_registry/archive.py#L164).

```python
def manifest_bytes(manifest: Mapping[str, Any]) -> bytes:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `manifest` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `bytes`.

### Опис із вихідного коду

```text
Serialisation of ``jane-package.json`` written by the registry (JSON publish, fork, upstream port):
UTF-8, two-space indent, key order as given, non-ASCII kept, trailing newline.
```

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_api.py:73](../../../../../../services/registry/tests/test_api.py#L73).

```python
assert files["jane-package.json"] == manifest_bytes(extractor_manifest(pid))
```

Контекст і передумови: [services/registry/tests/test_api.py:102](../../../../../../services/registry/tests/test_api.py#L102).

```python
expected = digest_of(canonical_archive({**files, "jane-package.json": manifest_bytes(manifest_b)}))
```

## jane_registry.archive.files_from_dir

**Функція.** Код: [services/registry/src/jane_registry/archive.py:170](../../../../../../services/registry/src/jane_registry/archive.py#L170).

```python
def files_from_dir(package_dir: Path) -> dict[str, bytes]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `package_dir` | `Path` | `—` | positional-or-keyword |

Результат: `dict[str, bytes]`.

Явні `raise` у тілі: `ArchiveError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Files of a package directory (for the CLI): caches skipped, symlinks rejected.
```

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_runtime_compat.py:97](../../../../../../services/registry/tests/test_runtime_compat.py#L97).

```python
files = files_from_dir(EXAMPLE)
```

Контекст і передумови: [services/registry/tests/test_runtime_compat.py:77](../../../../../../services/registry/tests/test_runtime_compat.py#L77).

```python
ours = canonical_archive(files_from_dir(EXAMPLE))
```
