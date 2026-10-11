# Модуль `jane_extractor_sdk.package`

> Згенеровано `scripts/docs_reference.py` з [libs/extractor-sdk/src/jane_extractor_sdk/package.py](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py). Не редагуйте вручну.

Package utilities: manifest, canonical archive and digest, safe unpacking, test-case inputs.

Package layout and manifest: ``contracts/docs/handler-packages.md``, ``package-manifest.schema.json``.

## Зміст

- [Клас `PackageError`](#клас-packageerror)
- [Клас `UnpackLimits`](#клас-unpacklimits)
- [Функція `build_archive`](#функція-build_archive)
- [Функція `case_input`](#функція-case_input)
- [Функція `digest_of`](#функція-digest_of)
- [Функція `iter_package_files`](#функція-iter_package_files)
- [Функція `load_manifest`](#функція-load_manifest)
- [Функція `material_from_bytes`](#функція-material_from_bytes)
- [Функція `material_from_file`](#функція-material_from_file)
- [Функція `read_package_file`](#функція-read_package_file)
- [Функція `safe_unpack`](#функція-safe_unpack)

## Класи

### Клас `PackageError`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_extractor_sdk.package` |
| Успадкування | `ValueError` |
| Код | [package.py:56](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L56) |

```python
class PackageError(ValueError): ...
```

Invalid package (bad path, symlink, size above a limit, missing manifest...).

### Клас `UnpackLimits`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_extractor_sdk.package` |
| Код | [package.py:61](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L61) |

```python
@dataclass(frozen=True)
class UnpackLimits: ...
```

Bounds for unpacking an untrusted archive; values come from the runtime configuration.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_archive_bytes` | `int` | — | читання |  |
| `max_unpacked_bytes` | `int` | — | читання |  |
| `max_files` | `int` | — | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

## Функції

### Функція `build_archive`

```python
def build_archive(package_dir: Path) -> bytes: ...
```

Canonical zip of a package directory - the same bytes, and so the same digest, as the registry.

The algorithm is the one of the registry (``services/registry/README.md``, "Канонічний архів і дайджест"): one entry per regular file (no directory entries, no symlinks), names sorted in ascending byte order, compression method 0 (**stored**: the bytes do not depend on a zlib build), timestamp 1980-01-01 00:00:00, ``external_attr = 0o100644 << 16``, ``create_system = 3`` (Unix), no extra fields, no comments. The same directory always gives the same bytes on Windows and Linux.

Винятки в коді функції: `PackageError`.

Код: [package.py:93](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L93).

### Функція `case_input`

```python
def case_input(package_dir: Path, case: Mapping[str, Any]) -> dict[str, Any]: ...
```

``HandlerInput`` for a manifest ``TestCase.input``.

* ``material`` - JSON ``Material``; an optional top-level ``content_file`` (package path) replaces the content with the file (inline);
* ``file`` (+ ``media_type``, ``url``) - raw file, minimal metadata;
* ``entities`` / ``data`` - JSON file with an ``EntityRecord`` array / any JSON.

Винятки в коді функції: `PackageError`.

Код: [package.py:268](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L268).

### Функція `digest_of`

```python
def digest_of(data: bytes) -> str: ...
```

``sha256:<hex>`` - the ``Digest`` format of the contracts.

Код: [package.py:116](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L116).

### Функція `iter_package_files`

```python
def iter_package_files(package_dir: Path) -> Iterator[tuple[str, Path]]: ...
```

``(package path, file)`` for every file of a package directory, sorted, caches skipped.

Symlinks are rejected (the archive format forbids them).

Винятки в коді функції: `PackageError`.

Код: [package.py:75](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L75).

### Функція `load_manifest`

```python
def load_manifest(package_dir: Path) -> dict[str, Any]: ...
```

Винятки в коді функції: `PackageError`.

Код: [package.py:160](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L160).

### Функція `material_from_bytes`

```python
def material_from_bytes(
    data: bytes,
    *,
    media_type: str,
    url: str | None = None,
    source_id: str | None = None,
    charset: str | None = None,
    fetched_at: str | None = None,
) -> dict[str, Any]: ...
```

A standalone ``Material`` with inline content (for CLI runs and package tests).

``material_id`` follows the collector rule for web (``web:`` + sha256(url)[:32]) when a URL is given, otherwise ``file:`` + sha256(content)[:32]; ``observation_id`` is derived from the content hash.

Код: [package.py:190](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L190).

### Функція `material_from_file`

```python
def material_from_file(
    path: Path,
    *,
    media_type: str | None = None,
    url: str | None = None,
    source_id: str | None = None,
) -> dict[str, Any]: ...
```

Код: [package.py:249](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L249).

### Функція `read_package_file`

```python
def read_package_file(package_dir: Path, name: str) -> bytes: ...
```

Винятки в коді функції: `PackageError`.

Код: [package.py:173](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L173).

### Функція `safe_unpack`

```python
def safe_unpack(archive: bytes, dest: Path, limits: UnpackLimits) -> None: ...
```

Unpack an untrusted package zip into ``dest`` with path, symlink, count and size checks.

Винятки в коді функції: `PackageError`.

Код: [package.py:121](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L121).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `MANIFEST_NAME` | — | `'jane-package.json'` |  |
