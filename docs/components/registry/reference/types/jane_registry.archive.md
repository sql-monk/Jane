# Модуль `jane_registry.archive`

> Згенеровано `scripts/docs_reference.py` з [services/registry/src/jane_registry/archive.py](../../../../../services/registry/src/jane_registry/archive.py). Не редагуйте вручну.

Canonical package archive and its digest (ADR-0002 §2).

The registry stores every version as a **canonical zip** and publishes ``digest = "sha256:" + sha256(archive bytes)``. The same set of files always gives the same bytes on Windows and Linux:

* one entry per regular file, no directory entries, no symlinks;
* entry names are package paths (``PackagePath`` of the manifest schema: ASCII ``[A-Za-z0-9._/-]``, ``/`` separator, no leading ``/``, no ``..``), unique, sorted in ascending byte order;
* compression method 0 (**stored**, no compression) - the bytes do not depend on a zlib build;
* timestamp 1980-01-01 00:00:00, ``external_attr = 0o100644 << 16`` (regular file, rw-r--r--), ``create_system = 3`` (Unix), no extra fields, no comments, no encryption;
* written by Python ``zipfile`` (local headers + central directory, no data descriptors).

An uploaded zip may be built in any way (deflated, other timestamps, directory entries): the registry unpacks it with limits and re-packs the files canonically, so the digest depends only on the file paths and contents. ``jane-package.json`` produced from a JSON ``manifest`` is serialised by :func:`manifest_bytes`.

## Зміст

- [Клас `ArchiveError`](#клас-archiveerror)
- [Клас `ArchiveLimits`](#клас-archivelimits)
- [Функція `canonical_archive`](#функція-canonical_archive)
- [Функція `check_package_path`](#функція-check_package_path)
- [Функція `check_unique_paths`](#функція-check_unique_paths)
- [Функція `digest_of`](#функція-digest_of)
- [Функція `files_from_dir`](#функція-files_from_dir)
- [Функція `is_canonical`](#функція-is_canonical)
- [Функція `manifest_bytes`](#функція-manifest_bytes)
- [Функція `read_archive`](#функція-read_archive)

## Класи

### Клас `ArchiveError`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_registry.archive` |
| Успадкування | `ValueError` |
| Код | [archive.py:57](../../../../../services/registry/src/jane_registry/archive.py#L57) |

```python
class ArchiveError(ValueError): ...
```

The archive or a path in it is not acceptable; ``limit`` is set when a size limit was exceeded.

#### Конструктор `ArchiveError.__init__`

```python
def __init__(self, message: str, *, limit: str | None = None, path: str | None = None) -> None: ...
```

Код: [archive.py:60](../../../../../services/registry/src/jane_registry/archive.py#L60).

### Клас `ArchiveLimits`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_registry.archive` |
| Код | [archive.py:67](../../../../../services/registry/src/jane_registry/archive.py#L67) |

```python
@dataclass(frozen=True)
class ArchiveLimits: ...
```

Bounds for reading an untrusted archive; values come from ``RegistryLimits.packages``.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_archive_bytes` | `int` | — | читання |  |
| `max_unpacked_bytes` | `int` | — | читання |  |
| `max_files` | `int` | — | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

## Функції

### Функція `canonical_archive`

```python
def canonical_archive(files: Mapping[str, bytes]) -> bytes: ...
```

The canonical zip of ``files`` (package path -> content).

Код: [archive.py:96](../../../../../services/registry/src/jane_registry/archive.py#L96).

### Функція `check_package_path`

```python
def check_package_path(name: str) -> str: ...
```

Винятки в коді функції: `ArchiveError`.

Код: [archive.py:75](../../../../../services/registry/src/jane_registry/archive.py#L75).

### Функція `check_unique_paths`

```python
def check_unique_paths(names: list[str]) -> None: ...
```

Paths that differ only in letter case would collide on Windows/macOS file systems.

Винятки в коді функції: `ArchiveError`.

Код: [archive.py:81](../../../../../services/registry/src/jane_registry/archive.py#L81).

### Функція `digest_of`

```python
def digest_of(data: bytes) -> str: ...
```

``sha256:<hex>`` - ``Digest`` of the contracts.

Код: [archive.py:91](../../../../../services/registry/src/jane_registry/archive.py#L91).

### Функція `files_from_dir`

```python
def files_from_dir(package_dir: Path) -> dict[str, bytes]: ...
```

Files of a package directory (for the CLI): caches skipped, symlinks rejected.

Винятки в коді функції: `ArchiveError`.

Код: [archive.py:170](../../../../../services/registry/src/jane_registry/archive.py#L170).

### Функція `is_canonical`

```python
def is_canonical(data: bytes, limits: ArchiveLimits) -> bool: ...
```

``True`` if ``data`` is exactly the canonical archive of its own files.

Код: [archive.py:156](../../../../../services/registry/src/jane_registry/archive.py#L156).

### Функція `manifest_bytes`

```python
def manifest_bytes(manifest: Mapping[str, Any]) -> bytes: ...
```

Serialisation of ``jane-package.json`` written by the registry (JSON publish, fork, upstream port): UTF-8, two-space indent, key order as given, non-ASCII kept, trailing newline.

Код: [archive.py:164](../../../../../services/registry/src/jane_registry/archive.py#L164).

### Функція `read_archive`

```python
def read_archive(data: bytes, limits: ArchiveLimits) -> dict[str, bytes]: ...
```

Files of an untrusted zip with path, symlink, duplicate, count and size checks.

Винятки в коді функції: `ArchiveError`.

Код: [archive.py:110](../../../../../services/registry/src/jane_registry/archive.py#L110).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `MANIFEST_NAME` | — | `'jane-package.json'` |  |
| `SKIP_PARTS` | — | `frozenset({'__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', '.git',` | Cache/VCS directories that :func:`files_from_dir` never packs (they are not part of a package). |
