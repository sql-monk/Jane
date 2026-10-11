# Модуль `jane_registry.store`

> Згенеровано `scripts/docs_reference.py` з [services/registry/src/jane_registry/store.py](../../../../../services/registry/src/jane_registry/store.py). Не редагуйте вручну.

Metadata store of the registry: records, the store protocol and the in-memory implementation.

The PostgreSQL implementation (:mod:`jane_registry.postgres`) is the production store (ADR-0002 §1). :class:`MemoryStore` keeps the same semantics in one process (``JANE_REGISTRY_DB=memory``): local experiments and fast tests; it loses everything on restart and does not support several instances.

## Зміст

- [Клас `AlreadyExists`](#клас-alreadyexists)
- [Клас `LimitReached`](#клас-limitreached)
- [Клас `MemoryStore`](#клас-memorystore)
- [Клас `MetadataStore`](#клас-metadatastore)
- [Клас `PackageFilter`](#клас-packagefilter)
- [Клас `PackageRecord`](#клас-packagerecord)
- [Клас `RevisionMismatch`](#клас-revisionmismatch)
- [Клас `StatusMismatch`](#клас-statusmismatch)
- [Клас `VersionExists`](#клас-versionexists)
- [Клас `VersionRecord`](#клас-versionrecord)
- [Функція `iso`](#функція-iso)
- [Функція `now`](#функція-now)
- [Функція `pick_latest`](#функція-pick_latest)

## Класи

### Клас `AlreadyExists`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_registry.store` |
| Успадкування | `Exception` |
| Код | [store.py:49](../../../../../services/registry/src/jane_registry/store.py#L49) |

```python
class AlreadyExists(Exception): ...
```

### Клас `LimitReached`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_registry.store` |
| Успадкування | `Exception` |
| Код | [store.py:203](../../../../../services/registry/src/jane_registry/store.py#L203) |

```python
class LimitReached(Exception): ...
```

#### Конструктор `LimitReached.__init__`

```python
def __init__(self, count: int) -> None: ...
```

Код: [store.py:204](../../../../../services/registry/src/jane_registry/store.py#L204).

### Клас `MemoryStore`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.store` |
| Код | [store.py:209](../../../../../services/registry/src/jane_registry/store.py#L209) |

```python
class MemoryStore: ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `name` | `'memory'` |  |

#### Конструктор `MemoryStore.__init__`

```python
def __init__(self) -> None: ...
```

Код: [store.py:212](../../../../../services/registry/src/jane_registry/store.py#L212).

#### Метод `MemoryStore.open`

```python
async def open(self) -> None: ...
```

Код: [store.py:218](../../../../../services/registry/src/jane_registry/store.py#L218).

#### Метод `MemoryStore.close`

```python
async def close(self) -> None: ...
```

Код: [store.py:221](../../../../../services/registry/src/jane_registry/store.py#L221).

#### Метод `MemoryStore.check`

```python
async def check(self) -> bool: ...
```

Код: [store.py:224](../../../../../services/registry/src/jane_registry/store.py#L224).

#### Метод `MemoryStore.create_package`

```python
async def create_package(self, pkg: PackageRecord) -> PackageRecord: ...
```

Винятки в коді методу: `AlreadyExists`.

Код: [store.py:238](../../../../../services/registry/src/jane_registry/store.py#L238).

#### Метод `MemoryStore.get_package`

```python
async def get_package(self, package_id: str) -> PackageRecord | None: ...
```

Код: [store.py:245](../../../../../services/registry/src/jane_registry/store.py#L245).

#### Метод `MemoryStore.update_package`

```python
async def update_package(
    self,
    package_id: str,
    changes: dict[str, Any],
    expected_revision: int | None,
) -> PackageRecord: ...
```

Винятки в коді методу: `RevisionMismatch`.

Код: [store.py:249](../../../../../services/registry/src/jane_registry/store.py#L249).

#### Метод `MemoryStore.list_packages`

```python
async def list_packages(
    self,
    flt: PackageFilter,
    after: str | None,
    limit: int,
) -> list[PackageRecord]: ...
```

Код: [store.py:260](../../../../../services/registry/src/jane_registry/store.py#L260).

#### Метод `MemoryStore.count_forks`

```python
async def count_forks(self, package_id: str) -> int: ...
```

Код: [store.py:268](../../../../../services/registry/src/jane_registry/store.py#L268).

#### Метод `MemoryStore.delete_package_if_empty`

```python
async def delete_package_if_empty(self, package_id: str) -> None: ...
```

Код: [store.py:271](../../../../../services/registry/src/jane_registry/store.py#L271).

#### Метод `MemoryStore.insert_version`

```python
async def insert_version(self, version: VersionRecord, max_versions: int) -> VersionRecord: ...
```

Винятки в коді методу: `VersionExists`, `LimitReached`.

Код: [store.py:276](../../../../../services/registry/src/jane_registry/store.py#L276).

#### Метод `MemoryStore.get_version`

```python
async def get_version(self, package_id: str, version: str) -> VersionRecord | None: ...
```

Код: [store.py:293](../../../../../services/registry/src/jane_registry/store.py#L293).

#### Метод `MemoryStore.list_versions`

```python
async def list_versions(
    self,
    package_id: str,
    status: str | None,
    before_seq: int | None,
    limit: int,
) -> list[VersionRecord]: ...
```

Код: [store.py:297](../../../../../services/registry/src/jane_registry/store.py#L297).

#### Метод `MemoryStore.version_numbers`

```python
async def version_numbers(self, package_id: str) -> list[tuple[str, str]]: ...
```

Код: [store.py:313](../../../../../services/registry/src/jane_registry/store.py#L313).

#### Метод `MemoryStore.count_versions`

```python
async def count_versions(self, package_id: str) -> int: ...
```

Код: [store.py:316](../../../../../services/registry/src/jane_registry/store.py#L316).

#### Метод `MemoryStore.set_status`

```python
async def set_status(
    self,
    package_id: str,
    version: str,
    expected: str,
    entry: dict[str, Any],
) -> VersionRecord: ...
```

Винятки в коді методу: `StatusMismatch`.

Код: [store.py:319](../../../../../services/registry/src/jane_registry/store.py#L319).

#### Метод `MemoryStore.add_test_report`

```python
async def add_test_report(
    self,
    package_id: str,
    version: str,
    record: dict[str, Any],
    test_status: str,
) -> VersionRecord: ...
```

Код: [store.py:334](../../../../../services/registry/src/jane_registry/store.py#L334).

### Клас `MetadataStore`

| Властивість | Значення |
|---|---|
| Вид | протокол |
| Модуль | `jane_registry.store` |
| Успадкування | `Protocol` |
| Код | [store.py:170](../../../../../services/registry/src/jane_registry/store.py#L170) |

```python
class MetadataStore(Protocol): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `name` | `str` | — | читання й запис |  |

#### Метод `MetadataStore.open`

```python
async def open(self) -> None: ...
```

Код: [store.py:173](../../../../../services/registry/src/jane_registry/store.py#L173).

#### Метод `MetadataStore.close`

```python
async def close(self) -> None: ...
```

Код: [store.py:174](../../../../../services/registry/src/jane_registry/store.py#L174).

#### Метод `MetadataStore.check`

```python
async def check(self) -> bool: ...
```

Код: [store.py:175](../../../../../services/registry/src/jane_registry/store.py#L175).

#### Метод `MetadataStore.create_package`

```python
async def create_package(self, pkg: PackageRecord) -> PackageRecord: ...
```

Код: [store.py:177](../../../../../services/registry/src/jane_registry/store.py#L177).

#### Метод `MetadataStore.get_package`

```python
async def get_package(self, package_id: str) -> PackageRecord | None: ...
```

Код: [store.py:178](../../../../../services/registry/src/jane_registry/store.py#L178).

#### Метод `MetadataStore.update_package`

```python
async def update_package(
    self,
    package_id: str,
    changes: dict[str, Any],
    expected_revision: int | None,
) -> PackageRecord: ...
```

Код: [store.py:179](../../../../../services/registry/src/jane_registry/store.py#L179).

#### Метод `MetadataStore.list_packages`

```python
async def list_packages(
    self,
    flt: PackageFilter,
    after: str | None,
    limit: int,
) -> list[PackageRecord]: ...
```

Код: [store.py:182](../../../../../services/registry/src/jane_registry/store.py#L182).

#### Метод `MetadataStore.count_forks`

```python
async def count_forks(self, package_id: str) -> int: ...
```

Код: [store.py:185](../../../../../services/registry/src/jane_registry/store.py#L185).

#### Метод `MetadataStore.delete_package_if_empty`

```python
async def delete_package_if_empty(self, package_id: str) -> None: ...
```

Код: [store.py:186](../../../../../services/registry/src/jane_registry/store.py#L186).

#### Метод `MetadataStore.insert_version`

```python
async def insert_version(self, version: VersionRecord, max_versions: int) -> VersionRecord: ...
```

Код: [store.py:188](../../../../../services/registry/src/jane_registry/store.py#L188).

#### Метод `MetadataStore.get_version`

```python
async def get_version(self, package_id: str, version: str) -> VersionRecord | None: ...
```

Код: [store.py:189](../../../../../services/registry/src/jane_registry/store.py#L189).

#### Метод `MetadataStore.list_versions`

```python
async def list_versions(
    self,
    package_id: str,
    status: str | None,
    before_seq: int | None,
    limit: int,
) -> list[VersionRecord]: ...
```

Код: [store.py:190](../../../../../services/registry/src/jane_registry/store.py#L190).

#### Метод `MetadataStore.version_numbers`

```python
async def version_numbers(self, package_id: str) -> list[tuple[str, str]]: ...
```

Код: [store.py:193](../../../../../services/registry/src/jane_registry/store.py#L193).

#### Метод `MetadataStore.count_versions`

```python
async def count_versions(self, package_id: str) -> int: ...
```

Код: [store.py:194](../../../../../services/registry/src/jane_registry/store.py#L194).

#### Метод `MetadataStore.set_status`

```python
async def set_status(
    self,
    package_id: str,
    version: str,
    expected: str,
    entry: dict[str, Any],
) -> VersionRecord: ...
```

Код: [store.py:195](../../../../../services/registry/src/jane_registry/store.py#L195).

#### Метод `MetadataStore.add_test_report`

```python
async def add_test_report(
    self,
    package_id: str,
    version: str,
    record: dict[str, Any],
    test_status: str,
) -> VersionRecord: ...
```

Код: [store.py:198](../../../../../services/registry/src/jane_registry/store.py#L198).

### Клас `PackageFilter`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_registry.store` |
| Код | [store.py:121](../../../../../services/registry/src/jane_registry/store.py#L121) |

```python
@dataclass(frozen=True)
class PackageFilter: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `kind` | `str \| None` | `None` | читання |  |
| `q` | `str \| None` | `None` | читання |  |
| `tag` | `str \| None` | `None` | читання |  |
| `entity_type` | `str \| None` | `None` | читання |  |
| `media_type` | `str \| None` | `None` | читання |  |
| `domain` | `str \| None` | `None` | читання |  |
| `fork_of` | `str \| None` | `None` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `PackageRecord`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_registry.store` |
| Код | [store.py:68](../../../../../services/registry/src/jane_registry/store.py#L68) |

```python
@dataclass
class PackageRecord: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `package_id` | `str` | — | читання й запис |  |
| `kind` | `str` | — | читання й запис |  |
| `title` | `str` | — | читання й запис |  |
| `auto_changes_allowed` | `bool` | — | читання й запис |  |
| `created_at` | `datetime` | — | читання й запис |  |
| `updated_at` | `datetime` | — | читання й запис |  |
| `description` | `str \| None` | `None` | читання й запис |  |
| `deprecated` | `bool` | `False` | читання й запис |  |
| `fork_of` | `dict[str, str] \| None` | `None` | читання й запис |  |
| `owner` | `str \| None` | `None` | читання й запис |  |
| `labels` | `dict[str, str]` | `field(default_factory=dict)` | читання й запис |  |
| `revision` | `int` | `1` | читання й запис |  |
| `latest_version` | `str \| None` | `None` | читання й запис |  |
| `tags` | `list[str]` | `field(default_factory=list)` | читання й запис |  |
| `entity_types` | `list[str]` | `field(default_factory=list)` | читання й запис |  |
| `media_types` | `list[str]` | `field(default_factory=list)` | читання й запис |  |
| `domains` | `list[str]` | `field(default_factory=list)` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `RevisionMismatch`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_registry.store` |
| Успадкування | `Exception` |
| Код | [store.py:57](../../../../../services/registry/src/jane_registry/store.py#L57) |

```python
class RevisionMismatch(Exception): ...
```

### Клас `StatusMismatch`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_registry.store` |
| Успадкування | `Exception` |
| Код | [store.py:61](../../../../../services/registry/src/jane_registry/store.py#L61) |

```python
class StatusMismatch(Exception): ...
```

#### Конструктор `StatusMismatch.__init__`

```python
def __init__(self, actual: str) -> None: ...
```

Код: [store.py:62](../../../../../services/registry/src/jane_registry/store.py#L62).

### Клас `VersionExists`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_registry.store` |
| Успадкування | `Exception` |
| Код | [store.py:53](../../../../../services/registry/src/jane_registry/store.py#L53) |

```python
class VersionExists(Exception): ...
```

### Клас `VersionRecord`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_registry.store` |
| Код | [store.py:89](../../../../../services/registry/src/jane_registry/store.py#L89) |

```python
@dataclass
class VersionRecord: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `package_id` | `str` | — | читання й запис |  |
| `version` | `str` | — | читання й запис |  |
| `digest` | `str` | — | читання й запис |  |
| `status` | `str` | — | читання й запис |  |
| `test_status` | `str` | — | читання й запис |  |
| `manifest` | `dict[str, Any]` | — | читання й запис |  |
| `files` | `list[dict[str, Any]]` | — | читання й запис |  |
| `size_bytes` | `int` | — | читання й запис |  |
| `created_at` | `datetime` | — | читання й запис |  |
| `created_by` | `str` | — | читання й запис |  |
| `published_by` | `str \| None` | `None` | читання й запис |  |
| `ported_parent_version` | `str \| None` | `None` | читання й запис |  |
| `seq` | `int` | `0` | читання й запис |  |
| `status_history` | `list[dict[str, Any]]` | `field(default_factory=list)` | читання й запис |  |
| `test_reports` | `list[dict[str, Any]]` | `field(default_factory=list)` | читання й запис |  |
| `search_fields` | `dict[str, list[str]]` | — | читання (властивість) |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

## Функції

### Функція `iso`

```python
def iso(t: datetime) -> str: ...
```

RFC 3339 UTC with ``Z`` and milliseconds, as the contracts require.

Код: [store.py:44](../../../../../services/registry/src/jane_registry/store.py#L44).

### Функція `now`

```python
def now() -> datetime: ...
```

Код: [store.py:39](../../../../../services/registry/src/jane_registry/store.py#L39).

### Функція `pick_latest`

```python
def pick_latest(versions: Sequence[tuple[str, str]]) -> str | None: ...
```

Highest SemVer among versions whose status is not rejected/yanked.

Код: [store.py:131](../../../../../services/registry/src/jane_registry/store.py#L131).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `INACTIVE_FOR_LATEST` | — | `frozenset({'rejected', 'yanked'})` |  |
