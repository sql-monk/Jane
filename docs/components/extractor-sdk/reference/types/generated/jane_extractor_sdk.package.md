# jane_extractor_sdk.package

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_extractor_sdk.package.MANIFEST_NAME](#jane_extractor_sdkpackagemanifest_name)
- [jane_extractor_sdk.package.PackageError](#jane_extractor_sdkpackagepackageerror)
- [jane_extractor_sdk.package.UnpackLimits](#jane_extractor_sdkpackageunpacklimits)
- [jane_extractor_sdk.package.UnpackLimits.__init__](#jane_extractor_sdkpackageunpacklimits__init__)
- [jane_extractor_sdk.package.UnpackLimits.max_archive_bytes](#jane_extractor_sdkpackageunpacklimitsmax_archive_bytes)
- [jane_extractor_sdk.package.UnpackLimits.max_unpacked_bytes](#jane_extractor_sdkpackageunpacklimitsmax_unpacked_bytes)
- [jane_extractor_sdk.package.UnpackLimits.max_files](#jane_extractor_sdkpackageunpacklimitsmax_files)
- [jane_extractor_sdk.package.iter_package_files](#jane_extractor_sdkpackageiter_package_files)
- [jane_extractor_sdk.package.build_archive](#jane_extractor_sdkpackagebuild_archive)
- [jane_extractor_sdk.package.digest_of](#jane_extractor_sdkpackagedigest_of)
- [jane_extractor_sdk.package.safe_unpack](#jane_extractor_sdkpackagesafe_unpack)
- [jane_extractor_sdk.package.load_manifest](#jane_extractor_sdkpackageload_manifest)
- [jane_extractor_sdk.package.read_package_file](#jane_extractor_sdkpackageread_package_file)
- [jane_extractor_sdk.package.material_from_bytes](#jane_extractor_sdkpackagematerial_from_bytes)
- [jane_extractor_sdk.package.material_from_file](#jane_extractor_sdkpackagematerial_from_file)
- [jane_extractor_sdk.package.case_input](#jane_extractor_sdkpackagecase_input)

## jane_extractor_sdk.package.MANIFEST_NAME

**Константа.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/package.py:37](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L37).

```python
MANIFEST_NAME = 'jane-package.json'
```

## jane_extractor_sdk.package.PackageError

**Клас.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/package.py:56](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L56).

```python
class PackageError(ValueError):
```

Базові типи / інтерфейси: `ValueError`.

### Опис із вихідного коду

```text
Invalid package (bad path, symlink, size above a limit, missing manifest...).
```

## jane_extractor_sdk.package.UnpackLimits

**Клас.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/package.py:61](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L61).

```python
class UnpackLimits:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_archive_bytes](jane_extractor_sdk.package.md#jane_extractor_sdkpackageunpacklimitsmax_archive_bytes) | Поле | ні |
| [max_unpacked_bytes](jane_extractor_sdk.package.md#jane_extractor_sdkpackageunpacklimitsmax_unpacked_bytes) | Поле | ні |
| [max_files](jane_extractor_sdk.package.md#jane_extractor_sdkpackageunpacklimitsmax_files) | Поле | ні |
| [__init__](jane_extractor_sdk.package.md#jane_extractor_sdkpackageunpacklimits__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
Bounds for unpacking an untrusted archive; values come from the runtime configuration.
```

### Приклади з тестів

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:31](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L31).

```python
LIMITS = UnpackLimits(max_archive_bytes=1_000_000, max_unpacked_bytes=1_000_000, max_files=100)
```

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:192](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L192).

```python
safe_unpack(many, tmp_path / "a", UnpackLimits(10_000, 10_000, 3))
```

## jane_extractor_sdk.package.UnpackLimits.__init__

**Конструктор dataclass.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/package.py:61](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L61).

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

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:31](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L31).

```python
LIMITS = UnpackLimits(max_archive_bytes=1_000_000, max_unpacked_bytes=1_000_000, max_files=100)
```

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:192](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L192).

```python
safe_unpack(many, tmp_path / "a", UnpackLimits(10_000, 10_000, 3))
```

## jane_extractor_sdk.package.UnpackLimits.max_archive_bytes

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/package.py:64](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L64).

```python
max_archive_bytes: int
```

Доступ: читання — так; запис — ні.

## jane_extractor_sdk.package.UnpackLimits.max_unpacked_bytes

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/package.py:65](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L65).

```python
max_unpacked_bytes: int
```

Доступ: читання — так; запис — ні.

## jane_extractor_sdk.package.UnpackLimits.max_files

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/package.py:66](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L66).

```python
max_files: int
```

Доступ: читання — так; запис — ні.

## jane_extractor_sdk.package.iter_package_files

**Функція.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/package.py:75](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L75).

```python
def iter_package_files(package_dir: Path) -> Iterator[tuple[str, Path]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `package_dir` | `Path` | `—` | positional-or-keyword |

Результат: `Iterator[tuple[str, Path]]`.

Явні `raise` у тілі: `PackageError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
``(package path, file)`` for every file of a package directory, sorted, caches skipped.

Symlinks are rejected (the archive format forbids them).
```

## jane_extractor_sdk.package.build_archive

**Функція.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/package.py:93](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L93).

```python
def build_archive(package_dir: Path) -> bytes:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `package_dir` | `Path` | `—` | positional-or-keyword |

Результат: `bytes`.

Явні `raise` у тілі: `PackageError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Canonical zip of a package directory - the same bytes, and so the same digest, as the registry.

The algorithm is the one of the registry (``services/registry/README.md``, "Канонічний архів і дайджест"):
one entry per regular file (no directory entries, no symlinks), names sorted in ascending byte order,
compression method 0 (**stored**: the bytes do not depend on a zlib build), timestamp
1980-01-01 00:00:00, ``external_attr = 0o100644 << 16``, ``create_system = 3`` (Unix), no extra fields,
no comments. The same directory always gives the same bytes on Windows and Linux.
```

### Приклади з тестів

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:125](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L125).

```python
first = build_archive(EXAMPLE)
```

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:145](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L145).

```python
archive = build_archive(tmp_path)
```

## jane_extractor_sdk.package.digest_of

**Функція.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/package.py:116](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L116).

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
``sha256:<hex>`` - the ``Digest`` format of the contracts.
```

### Приклади з тестів

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:146](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L146).

```python
assert digest_of(archive) == "sha256:e80692e640c2cb1a1976caaad1ba67460a0af0926012748f85748d15c6a404a0"
```

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:127](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L127).

```python
assert digest_of(first).startswith("sha256:") and len(digest_of(first)) == 71
```

## jane_extractor_sdk.package.safe_unpack

**Функція.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/package.py:121](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L121).

```python
def safe_unpack(archive: bytes, dest: Path, limits: UnpackLimits) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `archive` | `bytes` | `—` | positional-or-keyword |
| `dest` | `Path` | `—` | positional-or-keyword |
| `limits` | `UnpackLimits` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `PackageError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Unpack an untrusted package zip into ``dest`` with path, symlink, count and size checks.
```

### Приклади з тестів

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:130](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L130).

```python
safe_unpack(first, tmp_path / "out", LIMITS)
```

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:186](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L186).

```python
safe_unpack(archive, tmp_path / "out", LIMITS)
```

## jane_extractor_sdk.package.load_manifest

**Функція.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/package.py:160](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L160).

```python
def load_manifest(package_dir: Path) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `package_dir` | `Path` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `PackageError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:56](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L56).

```python
manifest = load_manifest(package_dir)
```

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:198](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L198).

```python
manifest = load_manifest(EXAMPLE)
```

## jane_extractor_sdk.package.read_package_file

**Функція.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/package.py:173](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L173).

```python
def read_package_file(package_dir: Path, name: str) -> bytes:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `package_dir` | `Path` | `—` | positional-or-keyword |
| `name` | `str` | `—` | positional-or-keyword |

Результат: `bytes`.

Явні `raise` у тілі: `PackageError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_extractor_sdk.package.material_from_bytes

**Функція.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/package.py:190](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L190).

```python
def material_from_bytes(data: bytes, *, media_type: str, url: str | None=None, source_id: str | None=None, charset: str | None=None, fetched_at: str | None=None) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `data` | `bytes` | `—` | positional-or-keyword |
| `media_type` | `str` | `—` | keyword-only |
| `url` | `str \| None` | `None` | keyword-only |
| `source_id` | `str \| None` | `None` | keyword-only |
| `charset` | `str \| None` | `None` | keyword-only |
| `fetched_at` | `str \| None` | `None` | keyword-only |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
A standalone ``Material`` with inline content (for CLI runs and package tests).

``material_id`` follows the collector rule for web (``web:`` + sha256(url)[:32]) when a URL is given,
otherwise ``file:`` + sha256(content)[:32]; ``observation_id`` is derived from the content hash.
```

### Приклади з тестів

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:84](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L84).

```python
m = material_from_bytes("Привіт".encode("cp1251"), media_type="text/html", charset="cp1251")
```

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:87](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L87).

```python
binary = material_from_bytes(b"\x00\x01\xff", media_type="application/octet-stream")
```

## jane_extractor_sdk.package.material_from_file

**Функція.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/package.py:249](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L249).

```python
def material_from_file(path: Path, *, media_type: str | None=None, url: str | None=None, source_id: str | None=None) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `path` | `Path` | `—` | positional-or-keyword |
| `media_type` | `str \| None` | `None` | keyword-only |
| `url` | `str \| None` | `None` | keyword-only |
| `source_id` | `str \| None` | `None` | keyword-only |

Результат: `dict[str, Any]`.

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/conftest.py:37](../../../../../../services/handler-runtime/tests/conftest.py#L37).

```python
return material_from_file(
        EXAMPLE / "tests" / name / "page.html",
        media_type="text/html",
        url=f"https://testsite.example.test/product/{name.removeprefix('product-')}",
        source_id=source_id,
    )
```

## jane_extractor_sdk.package.case_input

**Функція.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/package.py:268](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/package.py#L268).

```python
def case_input(package_dir: Path, case: Mapping[str, Any]) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `package_dir` | `Path` | `—` | positional-or-keyword |
| `case` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `PackageError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
``HandlerInput`` for a manifest ``TestCase.input``.

* ``material`` - JSON ``Material``; an optional top-level ``content_file`` (package path) replaces the
  content with the file (inline);
* ``file`` (+ ``media_type``, ``url``) - raw file, minimal metadata;
* ``entities`` / ``data`` - JSON file with an ``EntityRecord`` array / any JSON.
```

### Приклади з тестів

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:200](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L200).

```python
file_input = case_input(EXAMPLE, by_name["product-phone-alpha"])
```

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:202](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L202).

```python
material_input = case_input(EXAMPLE, by_name["unknown-page-empty"])
```
