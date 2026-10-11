# Модуль `jane_storage.packages`

> Згенеровано `scripts/docs_reference.py` з [services/storage/src/jane_storage/packages.py](../../../../../services/storage/src/jane_storage/packages.py). Не редагуйте вручну.

Storage packages (``kind: storage``): catalog of installed packages, canonical archive, publication.

A storage package is a manifest plus configuration, without code (contracts/docs/handler-packages.md): ``jane-package.json`` with ``StorageEntry`` (adapter, writes, formats), ``schemas/params.schema.json`` and tests. Every adapter distribution ships its package and registers it in the entry-point group ``jane.storage.packages`` (see :mod:`jane_storage.adapters`), so the storage service knows the packages of all installed adapters without the registry (ADR-0009: standard ``jane.storage-*`` packages are built into the service).

Other storage packages (forks, new versions) come as ``HandlerInvocation.package_archive`` or from the registry (:mod:`jane_storage.registry_packages`); both are untrusted archives read by :func:`package_from_archive` within :class:`ArchiveLimits`. A storage package has no code, so - like the built-in ones - it declares no dependencies (runtime profile, Python requirements, other packages).

Publication to the registry (``registry.v1``: ``POST /v1/packages`` + ``POST /v1/packages/{id}/versions``) is done by ``jane-storage-packages publish --registry <url>``.

## Зміст

- [Клас `ArchiveLimits`](#клас-archivelimits)
- [Клас `DependencyNotAllowed`](#клас-dependencynotallowed)
- [Клас `PackageCatalog`](#клас-packagecatalog)
- [Клас `PublishOutcome`](#клас-publishoutcome)
- [Клас `StoragePackage`](#клас-storagepackage)
- [Функція `canonical_archive`](#функція-canonical_archive)
- [Функція `load_package`](#функція-load_package)
- [Функція `main`](#функція-main)
- [Функція `package_from_archive`](#функція-package_from_archive)
- [Функція `publish`](#функція-publish)

## Класи

### Клас `ArchiveLimits`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_storage.packages` |
| Код | [packages.py:132](../../../../../services/storage/src/jane_storage/packages.py#L132) |

```python
@dataclass(frozen=True)
class ArchiveLimits: ...
```

Bounds for reading an untrusted package archive (``limits.packages`` of the service).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_archive_bytes` | `int` | `20 * 1024 * 1024` | читання |  |
| `max_unpacked_bytes` | `int` | `50 * 1024 * 1024` | читання |  |
| `max_files` | `int` | `2000` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `DependencyNotAllowed`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_storage.packages` |
| Успадкування | `ValueError` |
| Код | [packages.py:127](../../../../../services/storage/src/jane_storage/packages.py#L127) |

```python
class DependencyNotAllowed(ValueError): ...
```

The manifest declares dependencies the storage executor cannot provide (``dependency_not_allowed``).

### Клас `PackageCatalog`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage.packages` |
| Код | [packages.py:278](../../../../../services/storage/src/jane_storage/packages.py#L278) |

```python
class PackageCatalog: ...
```

Storage packages known to this service (installed adapter distributions + extra directories).

#### Конструктор `PackageCatalog.__init__`

```python
def __init__(self, packages: Sequence[StoragePackage] = ()) -> None: ...
```

Код: [packages.py:281](../../../../../services/storage/src/jane_storage/packages.py#L281).

#### Метод `PackageCatalog.discover`

```python
@classmethod
def discover(cls, extra_dirs: Sequence[Path] = ()) -> PackageCatalog: ...
```

Код: [packages.py:287](../../../../../services/storage/src/jane_storage/packages.py#L287).

#### Метод `PackageCatalog.add`

```python
def add(self, pkg: StoragePackage) -> None: ...
```

Код: [packages.py:291](../../../../../services/storage/src/jane_storage/packages.py#L291).

#### Метод `PackageCatalog.get`

```python
def get(self, package_id: str, version: str) -> StoragePackage | None: ...
```

Код: [packages.py:294](../../../../../services/storage/src/jane_storage/packages.py#L294).

#### Метод `PackageCatalog.all`

```python
def all(self) -> list[StoragePackage]: ...
```

Код: [packages.py:297](../../../../../services/storage/src/jane_storage/packages.py#L297).

### Клас `PublishOutcome`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_storage.packages` |
| Код | [packages.py:303](../../../../../services/storage/src/jane_storage/packages.py#L303) |

```python
@dataclass(frozen=True)
class PublishOutcome: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `package_id` | `str` | — | читання |  |
| `version` | `str` | — | читання |  |
| `digest` | `str` | — | читання |  |
| `package_status` | `int` | — | читання |  |
| `version_status` | `int` | — | читання |  |
| `ok` | `bool` | — | читання (властивість) |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `StoragePackage`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_storage.packages` |
| Код | [packages.py:82](../../../../../services/storage/src/jane_storage/packages.py#L82) |

```python
@dataclass(frozen=True)
class StoragePackage: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `manifest` | `dict[str, Any]` | — | читання |  |
| `files` | `tuple[tuple[str, bytes], ...]` | — | читання |  |
| `params_schema` | `dict[str, Any] \| None` | — | читання |  |
| `archive` | `bytes` | `field(repr=False)` | читання |  |
| `package_id` | `str` | — | читання (властивість) |  |
| `version` | `str` | — | читання (властивість) |  |
| `digest` | `str` | — | читання (властивість) |  |
| `entry` | `dict[str, Any]` | — | читання (властивість) |  |
| `adapter` | `str` | — | читання (властивість) |  |
| `writes` | `str` | — | читання (властивість) |  |
| `accepts` | `list[str]` | — | читання (властивість) |  |
| `ref` | `dict[str, str]` | — | читання (властивість) |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `StoragePackage.file`

```python
def file(self, path: str) -> bytes: ...
```

Винятки в коді методу: `KeyError`.

Код: [packages.py:120](../../../../../services/storage/src/jane_storage/packages.py#L120).

## Функції

### Функція `canonical_archive`

```python
def canonical_archive(files: Sequence[tuple[str, bytes]]) -> bytes: ...
```

Deterministic zip: paths sorted, fixed time and permissions, no compression.

The same files always give the same bytes (and digest) on Windows and Linux.

Код: [packages.py:66](../../../../../services/storage/src/jane_storage/packages.py#L66).

### Функція `load_package`

```python
def load_package(root: Path) -> StoragePackage: ...
```

Код: [packages.py:224](../../../../../services/storage/src/jane_storage/packages.py#L224).

### Функція `main`

```python
def main(argv: Sequence[str] | None = None) -> int: ...
```

Код: [packages.py:359](../../../../../services/storage/src/jane_storage/packages.py#L359).

### Функція `package_from_archive`

```python
def package_from_archive(archive: bytes, limits: ArchiveLimits | None = None) -> StoragePackage: ...
```

Package from an untrusted zip with ``jane-package.json`` (``package_archive`` or a registry download).

Raises ``ValueError`` (:class:`DependencyNotAllowed` for declared dependencies) when the archive is not a readable zip, exceeds ``limits``, has unsafe, duplicate or symlink entries, or is not a storage package. The package's digest is that of the canonical archive of its files (the registry's algorithm).

Винятки в коді функції: `ValueError`.

Код: [packages.py:234](../../../../../services/storage/src/jane_storage/packages.py#L234).

### Функція `publish`

```python
def publish(
    client: httpx.Client,
    packages: Sequence[StoragePackage],
    headers: Mapping[str, str] | None = None,
) -> list[PublishOutcome]: ...
```

Create the package (409 = already exists) and publish its version (409 = version exists).

Код: [packages.py:328](../../../../../services/storage/src/jane_storage/packages.py#L328).
