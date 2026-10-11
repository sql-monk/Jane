# jane_storage.packages

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_storage.packages.canonical_archive](#jane_storagepackagescanonical_archive)
- [jane_storage.packages.StoragePackage](#jane_storagepackagesstoragepackage)
- [jane_storage.packages.StoragePackage.__init__](#jane_storagepackagesstoragepackage__init__)
- [jane_storage.packages.StoragePackage.manifest](#jane_storagepackagesstoragepackagemanifest)
- [jane_storage.packages.StoragePackage.files](#jane_storagepackagesstoragepackagefiles)
- [jane_storage.packages.StoragePackage.params_schema](#jane_storagepackagesstoragepackageparams_schema)
- [jane_storage.packages.StoragePackage.archive](#jane_storagepackagesstoragepackagearchive)
- [jane_storage.packages.StoragePackage.package_id](#jane_storagepackagesstoragepackagepackage_id)
- [jane_storage.packages.StoragePackage.version](#jane_storagepackagesstoragepackageversion)
- [jane_storage.packages.StoragePackage.digest](#jane_storagepackagesstoragepackagedigest)
- [jane_storage.packages.StoragePackage.entry](#jane_storagepackagesstoragepackageentry)
- [jane_storage.packages.StoragePackage.adapter](#jane_storagepackagesstoragepackageadapter)
- [jane_storage.packages.StoragePackage.writes](#jane_storagepackagesstoragepackagewrites)
- [jane_storage.packages.StoragePackage.accepts](#jane_storagepackagesstoragepackageaccepts)
- [jane_storage.packages.StoragePackage.ref](#jane_storagepackagesstoragepackageref)
- [jane_storage.packages.StoragePackage.file](#jane_storagepackagesstoragepackagefile)
- [jane_storage.packages.DependencyNotAllowed](#jane_storagepackagesdependencynotallowed)
- [jane_storage.packages.ArchiveLimits](#jane_storagepackagesarchivelimits)
- [jane_storage.packages.ArchiveLimits.__init__](#jane_storagepackagesarchivelimits__init__)
- [jane_storage.packages.ArchiveLimits.max_archive_bytes](#jane_storagepackagesarchivelimitsmax_archive_bytes)
- [jane_storage.packages.ArchiveLimits.max_unpacked_bytes](#jane_storagepackagesarchivelimitsmax_unpacked_bytes)
- [jane_storage.packages.ArchiveLimits.max_files](#jane_storagepackagesarchivelimitsmax_files)
- [jane_storage.packages.load_package](#jane_storagepackagesload_package)
- [jane_storage.packages.package_from_archive](#jane_storagepackagespackage_from_archive)
- [jane_storage.packages.PackageCatalog](#jane_storagepackagespackagecatalog)
- [jane_storage.packages.PackageCatalog.__init__](#jane_storagepackagespackagecatalog__init__)
- [jane_storage.packages.PackageCatalog.discover](#jane_storagepackagespackagecatalogdiscover)
- [jane_storage.packages.PackageCatalog.add](#jane_storagepackagespackagecatalogadd)
- [jane_storage.packages.PackageCatalog.get](#jane_storagepackagespackagecatalogget)
- [jane_storage.packages.PackageCatalog.all](#jane_storagepackagespackagecatalogall)
- [jane_storage.packages.PublishOutcome](#jane_storagepackagespublishoutcome)
- [jane_storage.packages.PublishOutcome.__init__](#jane_storagepackagespublishoutcome__init__)
- [jane_storage.packages.PublishOutcome.package_id](#jane_storagepackagespublishoutcomepackage_id)
- [jane_storage.packages.PublishOutcome.version](#jane_storagepackagespublishoutcomeversion)
- [jane_storage.packages.PublishOutcome.digest](#jane_storagepackagespublishoutcomedigest)
- [jane_storage.packages.PublishOutcome.package_status](#jane_storagepackagespublishoutcomepackage_status)
- [jane_storage.packages.PublishOutcome.version_status](#jane_storagepackagespublishoutcomeversion_status)
- [jane_storage.packages.PublishOutcome.ok](#jane_storagepackagespublishoutcomeok)
- [jane_storage.packages.publish](#jane_storagepackagespublish)
- [jane_storage.packages.main](#jane_storagepackagesmain)

## jane_storage.packages.canonical_archive

**Функція.** Код: [services/storage/src/jane_storage/packages.py:66](../../../../../../services/storage/src/jane_storage/packages.py#L66).

```python
def canonical_archive(files: Sequence[tuple[str, bytes]]) -> bytes:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `files` | `Sequence[tuple[str, bytes]]` | `—` | positional-or-keyword |

Результат: `bytes`.

### Опис із вихідного коду

```text
Deterministic zip: paths sorted, fixed time and permissions, no compression.

The same files always give the same bytes (and digest) on Windows and Linux.
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_app.py:333](../../../../../../services/storage/tests/test_app.py#L333).

```python
archive = canonical_archive([*files, ("jane-package.json", json.dumps(manifest).encode())])
```

Контекст і передумови: [services/storage/tests/test_app.py:399](../../../../../../services/storage/tests/test_app.py#L399).

```python
archive = canonical_archive([*files, ("jane-package.json", json.dumps(manifest).encode())])
```

## jane_storage.packages.StoragePackage

**Клас.** Код: [services/storage/src/jane_storage/packages.py:82](../../../../../../services/storage/src/jane_storage/packages.py#L82).

```python
class StoragePackage:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [manifest](jane_storage.packages.md#jane_storagepackagesstoragepackagemanifest) | Поле | ні |
| [files](jane_storage.packages.md#jane_storagepackagesstoragepackagefiles) | Поле | ні |
| [params_schema](jane_storage.packages.md#jane_storagepackagesstoragepackageparams_schema) | Поле | ні |
| [archive](jane_storage.packages.md#jane_storagepackagesstoragepackagearchive) | Поле | ні |
| [package_id](jane_storage.packages.md#jane_storagepackagesstoragepackagepackage_id) | Властивість | ні |
| [version](jane_storage.packages.md#jane_storagepackagesstoragepackageversion) | Властивість | ні |
| [digest](jane_storage.packages.md#jane_storagepackagesstoragepackagedigest) | Властивість | ні |
| [entry](jane_storage.packages.md#jane_storagepackagesstoragepackageentry) | Властивість | ні |
| [adapter](jane_storage.packages.md#jane_storagepackagesstoragepackageadapter) | Властивість | ні |
| [writes](jane_storage.packages.md#jane_storagepackagesstoragepackagewrites) | Властивість | ні |
| [accepts](jane_storage.packages.md#jane_storagepackagesstoragepackageaccepts) | Властивість | ні |
| [ref](jane_storage.packages.md#jane_storagepackagesstoragepackageref) | Властивість | ні |
| [file](jane_storage.packages.md#jane_storagepackagesstoragepackagefile) | Метод | ні |
| [__init__](jane_storage.packages.md#jane_storagepackagesstoragepackage__init__) | Конструктор dataclass | ні |

## jane_storage.packages.StoragePackage.__init__

**Конструктор dataclass.** Код: [services/storage/src/jane_storage/packages.py:82](../../../../../../services/storage/src/jane_storage/packages.py#L82).

```python
def __init__(self, manifest: dict[str, Any], files: tuple[tuple[str, bytes], ...], params_schema: dict[str, Any] | None, archive: bytes = field(repr=False)) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `manifest` | `dict[str, Any]` | `—` | positional-or-keyword |
| `files` | `tuple[tuple[str, bytes], ...]` | `—` | positional-or-keyword |
| `params_schema` | `dict[str, Any] \| None` | `—` | positional-or-keyword |
| `archive` | `bytes` | `field(repr=False)` | positional-or-keyword |

Результат: `None`.

## jane_storage.packages.StoragePackage.manifest

**Поле.** Код: [services/storage/src/jane_storage/packages.py:83](../../../../../../services/storage/src/jane_storage/packages.py#L83).

```python
manifest: dict[str, Any]
```

Доступ: читання — так; запис — ні.

## jane_storage.packages.StoragePackage.files

**Поле.** Код: [services/storage/src/jane_storage/packages.py:84](../../../../../../services/storage/src/jane_storage/packages.py#L84).

```python
files: tuple[tuple[str, bytes], ...]
```

Доступ: читання — так; запис — ні.

## jane_storage.packages.StoragePackage.params_schema

**Поле.** Код: [services/storage/src/jane_storage/packages.py:85](../../../../../../services/storage/src/jane_storage/packages.py#L85).

```python
params_schema: dict[str, Any] | None
```

Доступ: читання — так; запис — ні.

## jane_storage.packages.StoragePackage.archive

**Поле.** Код: [services/storage/src/jane_storage/packages.py:86](../../../../../../services/storage/src/jane_storage/packages.py#L86).

```python
archive: bytes = field(repr=False)
```

Доступ: читання — так; запис — ні.

Обмеження й метадані декларації:

```json
{
  "repr": "False"
}
```

## jane_storage.packages.StoragePackage.package_id

**Властивість.** Код: [services/storage/src/jane_storage/packages.py:89](../../../../../../services/storage/src/jane_storage/packages.py#L89).

```python
def package_id(self) -> str:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

Доступ: читання — так; запис — ні.

## jane_storage.packages.StoragePackage.version

**Властивість.** Код: [services/storage/src/jane_storage/packages.py:93](../../../../../../services/storage/src/jane_storage/packages.py#L93).

```python
def version(self) -> str:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

Доступ: читання — так; запис — ні.

## jane_storage.packages.StoragePackage.digest

**Властивість.** Код: [services/storage/src/jane_storage/packages.py:97](../../../../../../services/storage/src/jane_storage/packages.py#L97).

```python
def digest(self) -> str:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

Доступ: читання — так; запис — ні.

## jane_storage.packages.StoragePackage.entry

**Властивість.** Код: [services/storage/src/jane_storage/packages.py:101](../../../../../../services/storage/src/jane_storage/packages.py#L101).

```python
def entry(self) -> dict[str, Any]:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

Доступ: читання — так; запис — ні.

## jane_storage.packages.StoragePackage.adapter

**Властивість.** Код: [services/storage/src/jane_storage/packages.py:105](../../../../../../services/storage/src/jane_storage/packages.py#L105).

```python
def adapter(self) -> str:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

Доступ: читання — так; запис — ні.

## jane_storage.packages.StoragePackage.writes

**Властивість.** Код: [services/storage/src/jane_storage/packages.py:109](../../../../../../services/storage/src/jane_storage/packages.py#L109).

```python
def writes(self) -> str:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

Доступ: читання — так; запис — ні.

## jane_storage.packages.StoragePackage.accepts

**Властивість.** Код: [services/storage/src/jane_storage/packages.py:113](../../../../../../services/storage/src/jane_storage/packages.py#L113).

```python
def accepts(self) -> list[str]:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `list[str]`.

Доступ: читання — так; запис — ні.

## jane_storage.packages.StoragePackage.ref

**Властивість.** Код: [services/storage/src/jane_storage/packages.py:117](../../../../../../services/storage/src/jane_storage/packages.py#L117).

```python
def ref(self) -> dict[str, str]:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, str]`.

Доступ: читання — так; запис — ні.

## jane_storage.packages.StoragePackage.file

**Метод.** Код: [services/storage/src/jane_storage/packages.py:120](../../../../../../services/storage/src/jane_storage/packages.py#L120).

```python
def file(self, path: str) -> bytes:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `path` | `str` | `—` | positional-or-keyword |

Результат: `bytes`.

Явні `raise` у тілі: `KeyError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_storage.packages.DependencyNotAllowed

**Клас.** Код: [services/storage/src/jane_storage/packages.py:127](../../../../../../services/storage/src/jane_storage/packages.py#L127).

```python
class DependencyNotAllowed(ValueError):
```

Базові типи / інтерфейси: `ValueError`.

### Опис із вихідного коду

```text
The manifest declares dependencies the storage executor cannot provide (``dependency_not_allowed``).
```

## jane_storage.packages.ArchiveLimits

**Клас.** Код: [services/storage/src/jane_storage/packages.py:132](../../../../../../services/storage/src/jane_storage/packages.py#L132).

```python
class ArchiveLimits:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_archive_bytes](jane_storage.packages.md#jane_storagepackagesarchivelimitsmax_archive_bytes) | Поле | ні |
| [max_unpacked_bytes](jane_storage.packages.md#jane_storagepackagesarchivelimitsmax_unpacked_bytes) | Поле | ні |
| [max_files](jane_storage.packages.md#jane_storagepackagesarchivelimitsmax_files) | Поле | ні |
| [__init__](jane_storage.packages.md#jane_storagepackagesarchivelimits__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
Bounds for reading an untrusted package archive (``limits.packages`` of the service).
```

## jane_storage.packages.ArchiveLimits.__init__

**Конструктор dataclass.** Код: [services/storage/src/jane_storage/packages.py:132](../../../../../../services/storage/src/jane_storage/packages.py#L132).

```python
def __init__(self, max_archive_bytes: int = 20 * 1024 * 1024, max_unpacked_bytes: int = 50 * 1024 * 1024, max_files: int = 2000) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `max_archive_bytes` | `int` | `20 * 1024 * 1024` | positional-or-keyword |
| `max_unpacked_bytes` | `int` | `50 * 1024 * 1024` | positional-or-keyword |
| `max_files` | `int` | `2000` | positional-or-keyword |

Результат: `None`.

## jane_storage.packages.ArchiveLimits.max_archive_bytes

**Поле.** Код: [services/storage/src/jane_storage/packages.py:135](../../../../../../services/storage/src/jane_storage/packages.py#L135).

```python
max_archive_bytes: int = 20 * 1024 * 1024
```

Доступ: читання — так; запис — ні.

## jane_storage.packages.ArchiveLimits.max_unpacked_bytes

**Поле.** Код: [services/storage/src/jane_storage/packages.py:136](../../../../../../services/storage/src/jane_storage/packages.py#L136).

```python
max_unpacked_bytes: int = 50 * 1024 * 1024
```

Доступ: читання — так; запис — ні.

## jane_storage.packages.ArchiveLimits.max_files

**Поле.** Код: [services/storage/src/jane_storage/packages.py:137](../../../../../../services/storage/src/jane_storage/packages.py#L137).

```python
max_files: int = 2000
```

Доступ: читання — так; запис — ні.

## jane_storage.packages.load_package

**Функція.** Код: [services/storage/src/jane_storage/packages.py:224](../../../../../../services/storage/src/jane_storage/packages.py#L224).

```python
def load_package(root: Path) -> StoragePackage:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `root` | `Path` | `—` | positional-or-keyword |

Результат: `StoragePackage`.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/minio/tests/test_minio_profile.py:19](../../../../../../services/storage/adapters/minio/tests/test_minio_profile.py#L19).

```python
pkg = load_package(package_dirs()["jane.storage-minio"])
```

Контекст і передумови: [services/storage/adapters/mongodb/tests/test_mongo_config.py:17](../../../../../../services/storage/adapters/mongodb/tests/test_mongo_config.py#L17).

```python
pkg = load_package(package_dirs()["jane.storage-mongodb"])
```

## jane_storage.packages.package_from_archive

**Функція.** Код: [services/storage/src/jane_storage/packages.py:234](../../../../../../services/storage/src/jane_storage/packages.py#L234).

```python
def package_from_archive(archive: bytes, limits: ArchiveLimits | None=None) -> StoragePackage:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `archive` | `bytes` | `—` | positional-or-keyword |
| `limits` | `ArchiveLimits \| None` | `None` | positional-or-keyword |

Результат: `StoragePackage`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Package from an untrusted zip with ``jane-package.json`` (``package_archive`` or a registry download).

Raises ``ValueError`` (:class:`DependencyNotAllowed` for declared dependencies) when the archive is not a
readable zip, exceeds ``limits``, has unsafe, duplicate or symlink entries, or is not a storage package.
The package's digest is that of the canonical archive of its files (the registry's algorithm).
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_packages.py:39](../../../../../../services/storage/tests/test_packages.py#L39).

```python
again = package_from_archive(a.archive)
```

## jane_storage.packages.PackageCatalog

**Клас.** Код: [services/storage/src/jane_storage/packages.py:278](../../../../../../services/storage/src/jane_storage/packages.py#L278).

```python
class PackageCatalog:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_storage.packages.md#jane_storagepackagespackagecatalog__init__) | Конструктор | ні |
| [discover](jane_storage.packages.md#jane_storagepackagespackagecatalogdiscover) | Метод | ні |
| [add](jane_storage.packages.md#jane_storagepackagespackagecatalogadd) | Метод | ні |
| [get](jane_storage.packages.md#jane_storagepackagespackagecatalogget) | Метод | ні |
| [all](jane_storage.packages.md#jane_storagepackagespackagecatalogall) | Метод | ні |

### Опис із вихідного коду

```text
Storage packages known to this service (installed adapter distributions + extra directories).
```

## jane_storage.packages.PackageCatalog.__init__

**Конструктор.** Код: [services/storage/src/jane_storage/packages.py:281](../../../../../../services/storage/src/jane_storage/packages.py#L281).

```python
def __init__(self, packages: Sequence[StoragePackage]=()) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `packages` | `Sequence[StoragePackage]` | `()` | positional-or-keyword |

Результат: `None`.

## jane_storage.packages.PackageCatalog.discover

**Метод.** Код: [services/storage/src/jane_storage/packages.py:287](../../../../../../services/storage/src/jane_storage/packages.py#L287).

```python
def discover(cls, extra_dirs: Sequence[Path]=()) -> PackageCatalog:
```

Декоратори: `classmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `cls` | `не вказано` | `—` | positional-or-keyword |
| `extra_dirs` | `Sequence[Path]` | `()` | positional-or-keyword |

Результат: `PackageCatalog`.

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_app.py:324](../../../../../../services/storage/tests/test_app.py#L324).

```python
files_pkg = next(p for p in PackageCatalog.discover().all() if p.package_id == "jane.storage-files")
```

Контекст і передумови: [services/storage/tests/test_app.py:392](../../../../../../services/storage/tests/test_app.py#L392).

```python
files_pkg = next(p for p in PackageCatalog.discover().all() if p.package_id == "jane.storage-files")
```

## jane_storage.packages.PackageCatalog.add

**Метод.** Код: [services/storage/src/jane_storage/packages.py:291](../../../../../../services/storage/src/jane_storage/packages.py#L291).

```python
def add(self, pkg: StoragePackage) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `pkg` | `StoragePackage` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.packages.PackageCatalog.get

**Метод.** Код: [services/storage/src/jane_storage/packages.py:294](../../../../../../services/storage/src/jane_storage/packages.py#L294).

```python
def get(self, package_id: str, version: str) -> StoragePackage | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |
| `version` | `str` | `—` | positional-or-keyword |

Результат: `StoragePackage | None`.

## jane_storage.packages.PackageCatalog.all

**Метод.** Код: [services/storage/src/jane_storage/packages.py:297](../../../../../../services/storage/src/jane_storage/packages.py#L297).

```python
def all(self) -> list[StoragePackage]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `list[StoragePackage]`.

## jane_storage.packages.PublishOutcome

**Клас.** Код: [services/storage/src/jane_storage/packages.py:303](../../../../../../services/storage/src/jane_storage/packages.py#L303).

```python
class PublishOutcome:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [package_id](jane_storage.packages.md#jane_storagepackagespublishoutcomepackage_id) | Поле | ні |
| [version](jane_storage.packages.md#jane_storagepackagespublishoutcomeversion) | Поле | ні |
| [digest](jane_storage.packages.md#jane_storagepackagespublishoutcomedigest) | Поле | ні |
| [package_status](jane_storage.packages.md#jane_storagepackagespublishoutcomepackage_status) | Поле | ні |
| [version_status](jane_storage.packages.md#jane_storagepackagespublishoutcomeversion_status) | Поле | ні |
| [ok](jane_storage.packages.md#jane_storagepackagespublishoutcomeok) | Властивість | ні |
| [__init__](jane_storage.packages.md#jane_storagepackagespublishoutcome__init__) | Конструктор dataclass | ні |

## jane_storage.packages.PublishOutcome.__init__

**Конструктор dataclass.** Код: [services/storage/src/jane_storage/packages.py:303](../../../../../../services/storage/src/jane_storage/packages.py#L303).

```python
def __init__(self, package_id: str, version: str, digest: str, package_status: int, version_status: int) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `package_id` | `str` | `—` | positional-or-keyword |
| `version` | `str` | `—` | positional-or-keyword |
| `digest` | `str` | `—` | positional-or-keyword |
| `package_status` | `int` | `—` | positional-or-keyword |
| `version_status` | `int` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.packages.PublishOutcome.package_id

**Поле.** Код: [services/storage/src/jane_storage/packages.py:304](../../../../../../services/storage/src/jane_storage/packages.py#L304).

```python
package_id: str
```

Доступ: читання — так; запис — ні.

## jane_storage.packages.PublishOutcome.version

**Поле.** Код: [services/storage/src/jane_storage/packages.py:305](../../../../../../services/storage/src/jane_storage/packages.py#L305).

```python
version: str
```

Доступ: читання — так; запис — ні.

## jane_storage.packages.PublishOutcome.digest

**Поле.** Код: [services/storage/src/jane_storage/packages.py:306](../../../../../../services/storage/src/jane_storage/packages.py#L306).

```python
digest: str
```

Доступ: читання — так; запис — ні.

## jane_storage.packages.PublishOutcome.package_status

**Поле.** Код: [services/storage/src/jane_storage/packages.py:307](../../../../../../services/storage/src/jane_storage/packages.py#L307).

```python
package_status: int
```

Доступ: читання — так; запис — ні.

## jane_storage.packages.PublishOutcome.version_status

**Поле.** Код: [services/storage/src/jane_storage/packages.py:308](../../../../../../services/storage/src/jane_storage/packages.py#L308).

```python
version_status: int
```

Доступ: читання — так; запис — ні.

## jane_storage.packages.PublishOutcome.ok

**Властивість.** Код: [services/storage/src/jane_storage/packages.py:311](../../../../../../services/storage/src/jane_storage/packages.py#L311).

```python
def ok(self) -> bool:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

Доступ: читання — так; запис — ні.

## jane_storage.packages.publish

**Функція.** Код: [services/storage/src/jane_storage/packages.py:328](../../../../../../services/storage/src/jane_storage/packages.py#L328).

```python
def publish(client: httpx.Client, packages: Sequence[StoragePackage], headers: Mapping[str, str] | None=None) -> list[PublishOutcome]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `httpx.Client` | `—` | positional-or-keyword |
| `packages` | `Sequence[StoragePackage]` | `—` | positional-or-keyword |
| `headers` | `Mapping[str, str] \| None` | `None` | positional-or-keyword |

Результат: `list[PublishOutcome]`.

### Опис із вихідного коду

```text
Create the package (409 = already exists) and publish its version (409 = version exists).
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_packages.py:50](../../../../../../services/storage/tests/test_packages.py#L50).

```python
outcomes = publish(registry, packages)
```

Контекст і передумови: [services/storage/tests/test_registry_packages.py:519](../../../../../../services/storage/tests/test_registry_packages.py#L519).

```python
(outcome,) = publish(registry, [files_package()])
```

## jane_storage.packages.main

**Функція.** Код: [services/storage/src/jane_storage/packages.py:359](../../../../../../services/storage/src/jane_storage/packages.py#L359).

```python
def main(argv: Sequence[str] | None=None) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `argv` | `Sequence[str] \| None` | `None` | positional-or-keyword |

Результат: `int`.

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_packages.py:57](../../../../../../services/storage/tests/test_packages.py#L57).

```python
assert main(["list"]) == 0
```
