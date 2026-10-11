# jane_registry.service

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_registry.service.STATUS_TRANSITIONS](#jane_registryservicestatus_transitions)
- [jane_registry.service.package_wire](#jane_registryservicepackage_wire)
- [jane_registry.service.version_wire](#jane_registryserviceversion_wire)
- [jane_registry.service.PortPlan](#jane_registryserviceportplan)
- [jane_registry.service.PortPlan.__init__](#jane_registryserviceportplan__init__)
- [jane_registry.service.PortPlan.fork](#jane_registryserviceportplanfork)
- [jane_registry.service.PortPlan.parent_id](#jane_registryserviceportplanparent_id)
- [jane_registry.service.PortPlan.parent_version](#jane_registryserviceportplanparent_version)
- [jane_registry.service.PortPlan.base_version](#jane_registryserviceportplanbase_version)
- [jane_registry.service.PortPlan.merge_base](#jane_registryserviceportplanmerge_base)
- [jane_registry.service.PortPlan.new_version](#jane_registryserviceportplannew_version)
- [jane_registry.service.PortPlan.requested_by](#jane_registryserviceportplanrequested_by)
- [jane_registry.service.RegistryService](#jane_registryserviceregistryservice)
- [jane_registry.service.RegistryService.__init__](#jane_registryserviceregistryservice__init__)
- [jane_registry.service.RegistryService.store](#jane_registryserviceregistryservicestore)
- [jane_registry.service.RegistryService.blobs](#jane_registryserviceregistryserviceblobs)
- [jane_registry.service.RegistryService.validator](#jane_registryserviceregistryservicevalidator)
- [jane_registry.service.RegistryService.profiles](#jane_registryserviceregistryserviceprofiles)
- [jane_registry.service.RegistryService.limits](#jane_registryserviceregistryservicelimits)
- [jane_registry.service.RegistryService.cache](#jane_registryserviceregistryservicecache)
- [jane_registry.service.RegistryService.archive_limits](#jane_registryserviceregistryservicearchive_limits)
- [jane_registry.service.RegistryService.package](#jane_registryserviceregistryservicepackage)
- [jane_registry.service.RegistryService.create_package](#jane_registryserviceregistryservicecreate_package)
- [jane_registry.service.RegistryService.update_package](#jane_registryserviceregistryserviceupdate_package)
- [jane_registry.service.RegistryService.archive](#jane_registryserviceregistryservicearchive)
- [jane_registry.service.RegistryService.files_of](#jane_registryserviceregistryservicefiles_of)
- [jane_registry.service.RegistryService.version](#jane_registryserviceregistryserviceversion)
- [jane_registry.service.RegistryService.files_from_json](#jane_registryserviceregistryservicefiles_from_json)
- [jane_registry.service.RegistryService.files_from_zip](#jane_registryserviceregistryservicefiles_from_zip)
- [jane_registry.service.RegistryService.publish](#jane_registryserviceregistryservicepublish)
- [jane_registry.service.RegistryService.set_status](#jane_registryserviceregistryserviceset_status)
- [jane_registry.service.RegistryService.record_test_results](#jane_registryserviceregistryservicerecord_test_results)
- [jane_registry.service.RegistryService.fork](#jane_registryserviceregistryservicefork)
- [jane_registry.service.RegistryService.diff](#jane_registryserviceregistryservicediff)
- [jane_registry.service.RegistryService.upstream](#jane_registryserviceregistryserviceupstream)
- [jane_registry.service.RegistryService.plan_port](#jane_registryserviceregistryserviceplan_port)
- [jane_registry.service.RegistryService.port](#jane_registryserviceregistryserviceport)
- [jane_registry.service.RegistryService.list_packages](#jane_registryserviceregistryservicelist_packages)

## jane_registry.service.STATUS_TRANSITIONS

**Константа.** Код: [services/registry/src/jane_registry/service.py:69](../../../../../../services/registry/src/jane_registry/service.py#L69).

```python
STATUS_TRANSITIONS: dict[str, frozenset[str]] = {'draft': frozenset({'approved', 'rejected', 'deprecated', 'yanked'}), 'approved': frozenset({'deprecated', 'yanked'}), 'deprecated': frozenset({'approved', 'yanked'}), 'rejected': frozenset(), 'yanked': frozenset()}
```

## jane_registry.service.package_wire

**Функція.** Код: [services/registry/src/jane_registry/service.py:87](../../../../../../services/registry/src/jane_registry/service.py#L87).

```python
def package_wire(pkg: PackageRecord, forks_count: int | None=None) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `pkg` | `PackageRecord` | `—` | positional-or-keyword |
| `forks_count` | `int \| None` | `None` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_registry.service.version_wire

**Функція.** Код: [services/registry/src/jane_registry/service.py:115](../../../../../../services/registry/src/jane_registry/service.py#L115).

```python
def version_wire(v: VersionRecord, *, full: bool=True) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `v` | `VersionRecord` | `—` | positional-or-keyword |
| `full` | `bool` | `True` | keyword-only |

Результат: `dict[str, Any]`.

## jane_registry.service.PortPlan

**Клас.** Код: [services/registry/src/jane_registry/service.py:180](../../../../../../services/registry/src/jane_registry/service.py#L180).

```python
class PortPlan:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [fork](jane_registry.service.md#jane_registryserviceportplanfork) | Поле | ні |
| [parent_id](jane_registry.service.md#jane_registryserviceportplanparent_id) | Поле | ні |
| [parent_version](jane_registry.service.md#jane_registryserviceportplanparent_version) | Поле | ні |
| [base_version](jane_registry.service.md#jane_registryserviceportplanbase_version) | Поле | ні |
| [merge_base](jane_registry.service.md#jane_registryserviceportplanmerge_base) | Поле | ні |
| [new_version](jane_registry.service.md#jane_registryserviceportplannew_version) | Поле | ні |
| [requested_by](jane_registry.service.md#jane_registryserviceportplanrequested_by) | Поле | ні |
| [__init__](jane_registry.service.md#jane_registryserviceportplan__init__) | Конструктор dataclass | ні |

## jane_registry.service.PortPlan.__init__

**Конструктор dataclass.** Код: [services/registry/src/jane_registry/service.py:180](../../../../../../services/registry/src/jane_registry/service.py#L180).

```python
def __init__(self, fork: PackageRecord, parent_id: str, parent_version: str, base_version: str, merge_base: str, new_version: str, requested_by: str) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `fork` | `PackageRecord` | `—` | positional-or-keyword |
| `parent_id` | `str` | `—` | positional-or-keyword |
| `parent_version` | `str` | `—` | positional-or-keyword |
| `base_version` | `str` | `—` | positional-or-keyword |
| `merge_base` | `str` | `—` | positional-or-keyword |
| `new_version` | `str` | `—` | positional-or-keyword |
| `requested_by` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.service.PortPlan.fork

**Поле.** Код: [services/registry/src/jane_registry/service.py:181](../../../../../../services/registry/src/jane_registry/service.py#L181).

```python
fork: PackageRecord
```

Доступ: читання — так; запис — ні.

## jane_registry.service.PortPlan.parent_id

**Поле.** Код: [services/registry/src/jane_registry/service.py:182](../../../../../../services/registry/src/jane_registry/service.py#L182).

```python
parent_id: str
```

Доступ: читання — так; запис — ні.

## jane_registry.service.PortPlan.parent_version

**Поле.** Код: [services/registry/src/jane_registry/service.py:183](../../../../../../services/registry/src/jane_registry/service.py#L183).

```python
parent_version: str
```

Доступ: читання — так; запис — ні.

## jane_registry.service.PortPlan.base_version

**Поле.** Код: [services/registry/src/jane_registry/service.py:184](../../../../../../services/registry/src/jane_registry/service.py#L184).

```python
base_version: str
```

Доступ: читання — так; запис — ні.

## jane_registry.service.PortPlan.merge_base

**Поле.** Код: [services/registry/src/jane_registry/service.py:185](../../../../../../services/registry/src/jane_registry/service.py#L185).

```python
merge_base: str
```

Доступ: читання — так; запис — ні.

## jane_registry.service.PortPlan.new_version

**Поле.** Код: [services/registry/src/jane_registry/service.py:186](../../../../../../services/registry/src/jane_registry/service.py#L186).

```python
new_version: str
```

Доступ: читання — так; запис — ні.

## jane_registry.service.PortPlan.requested_by

**Поле.** Код: [services/registry/src/jane_registry/service.py:187](../../../../../../services/registry/src/jane_registry/service.py#L187).

```python
requested_by: str
```

Доступ: читання — так; запис — ні.

## jane_registry.service.RegistryService

**Клас.** Код: [services/registry/src/jane_registry/service.py:214](../../../../../../services/registry/src/jane_registry/service.py#L214).

```python
class RegistryService:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_registry.service.md#jane_registryserviceregistryservice__init__) | Конструктор | ні |
| [store](jane_registry.service.md#jane_registryserviceregistryservicestore) | Поле екземпляра | ні |
| [blobs](jane_registry.service.md#jane_registryserviceregistryserviceblobs) | Поле екземпляра | ні |
| [validator](jane_registry.service.md#jane_registryserviceregistryservicevalidator) | Поле екземпляра | ні |
| [profiles](jane_registry.service.md#jane_registryserviceregistryserviceprofiles) | Поле екземпляра | ні |
| [limits](jane_registry.service.md#jane_registryserviceregistryservicelimits) | Поле екземпляра | ні |
| [cache](jane_registry.service.md#jane_registryserviceregistryservicecache) | Поле екземпляра | ні |
| [archive_limits](jane_registry.service.md#jane_registryserviceregistryservicearchive_limits) | Властивість | ні |
| [package](jane_registry.service.md#jane_registryserviceregistryservicepackage) | Метод | ні |
| [create_package](jane_registry.service.md#jane_registryserviceregistryservicecreate_package) | Метод | ні |
| [update_package](jane_registry.service.md#jane_registryserviceregistryserviceupdate_package) | Метод | ні |
| [archive](jane_registry.service.md#jane_registryserviceregistryservicearchive) | Метод | ні |
| [files_of](jane_registry.service.md#jane_registryserviceregistryservicefiles_of) | Метод | ні |
| [version](jane_registry.service.md#jane_registryserviceregistryserviceversion) | Метод | ні |
| [files_from_json](jane_registry.service.md#jane_registryserviceregistryservicefiles_from_json) | Метод | ні |
| [files_from_zip](jane_registry.service.md#jane_registryserviceregistryservicefiles_from_zip) | Метод | ні |
| [publish](jane_registry.service.md#jane_registryserviceregistryservicepublish) | Метод | ні |
| [set_status](jane_registry.service.md#jane_registryserviceregistryserviceset_status) | Метод | ні |
| [record_test_results](jane_registry.service.md#jane_registryserviceregistryservicerecord_test_results) | Метод | ні |
| [fork](jane_registry.service.md#jane_registryserviceregistryservicefork) | Метод | ні |
| [diff](jane_registry.service.md#jane_registryserviceregistryservicediff) | Метод | ні |
| [upstream](jane_registry.service.md#jane_registryserviceregistryserviceupstream) | Метод | ні |
| [plan_port](jane_registry.service.md#jane_registryserviceregistryserviceplan_port) | Метод | ні |
| [port](jane_registry.service.md#jane_registryserviceregistryserviceport) | Метод | ні |
| [list_packages](jane_registry.service.md#jane_registryserviceregistryservicelist_packages) | Метод | ні |

## jane_registry.service.RegistryService.__init__

**Конструктор.** Код: [services/registry/src/jane_registry/service.py:215](../../../../../../services/registry/src/jane_registry/service.py#L215).

```python
def __init__(self, store: MetadataStore, blobs: BlobStore, validator: PackageValidator, profiles: ProfileSource, limits: ServiceLimits) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `store` | `MetadataStore` | `—` | positional-or-keyword |
| `blobs` | `BlobStore` | `—` | positional-or-keyword |
| `validator` | `PackageValidator` | `—` | positional-or-keyword |
| `profiles` | `ProfileSource` | `—` | positional-or-keyword |
| `limits` | `ServiceLimits` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.service.RegistryService.store

**Поле екземпляра.** Код: [services/registry/src/jane_registry/service.py:223](../../../../../../services/registry/src/jane_registry/service.py#L223).

```python
self.store = store
```

## jane_registry.service.RegistryService.blobs

**Поле екземпляра.** Код: [services/registry/src/jane_registry/service.py:224](../../../../../../services/registry/src/jane_registry/service.py#L224).

```python
self.blobs = blobs
```

## jane_registry.service.RegistryService.validator

**Поле екземпляра.** Код: [services/registry/src/jane_registry/service.py:225](../../../../../../services/registry/src/jane_registry/service.py#L225).

```python
self.validator = validator
```

## jane_registry.service.RegistryService.profiles

**Поле екземпляра.** Код: [services/registry/src/jane_registry/service.py:226](../../../../../../services/registry/src/jane_registry/service.py#L226).

```python
self.profiles = profiles
```

## jane_registry.service.RegistryService.limits

**Поле екземпляра.** Код: [services/registry/src/jane_registry/service.py:227](../../../../../../services/registry/src/jane_registry/service.py#L227).

```python
self.limits = limits
```

## jane_registry.service.RegistryService.cache

**Поле екземпляра.** Код: [services/registry/src/jane_registry/service.py:228](../../../../../../services/registry/src/jane_registry/service.py#L228).

```python
self.cache = ArchiveCache(limits.packages.archive_cache_bytes)
```

## jane_registry.service.RegistryService.archive_limits

**Властивість.** Код: [services/registry/src/jane_registry/service.py:231](../../../../../../services/registry/src/jane_registry/service.py#L231).

```python
def archive_limits(self) -> ArchiveLimits:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `ArchiveLimits`.

Доступ: читання — так; запис — ні.

## jane_registry.service.RegistryService.package

**Метод.** Код: [services/registry/src/jane_registry/service.py:236](../../../../../../services/registry/src/jane_registry/service.py#L236).

```python
async def package(self, package_id: str) -> PackageRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |

Результат: `PackageRecord`.

Явні `raise` у тілі: `NotFound`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_registry.service.RegistryService.create_package

**Метод.** Код: [services/registry/src/jane_registry/service.py:242](../../../../../../services/registry/src/jane_registry/service.py#L242).

```python
async def create_package(self, body: Mapping[str, Any], principal: Principal) -> PackageRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `body` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `principal` | `Principal` | `—` | positional-or-keyword |

Результат: `PackageRecord`.

Явні `raise` у тілі: `Conflict`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_registry.service.RegistryService.update_package

**Метод.** Код: [services/registry/src/jane_registry/service.py:260](../../../../../../services/registry/src/jane_registry/service.py#L260).

```python
async def update_package(self, package_id: str, changes: dict[str, Any], if_match: str | None) -> PackageRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |
| `changes` | `dict[str, Any]` | `—` | positional-or-keyword |
| `if_match` | `str \| None` | `—` | positional-or-keyword |

Результат: `PackageRecord`.

Явні `raise` у тілі: `JaneError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_registry.service.RegistryService.archive

**Метод.** Код: [services/registry/src/jane_registry/service.py:277](../../../../../../services/registry/src/jane_registry/service.py#L277).

```python
async def archive(self, v: VersionRecord) -> bytes:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `v` | `VersionRecord` | `—` | positional-or-keyword |

Результат: `bytes`.

Явні `raise` у тілі: `UpstreamUnavailable`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_registry.service.RegistryService.files_of

**Метод.** Код: [services/registry/src/jane_registry/service.py:287](../../../../../../services/registry/src/jane_registry/service.py#L287).

```python
async def files_of(self, v: VersionRecord) -> dict[str, bytes]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `v` | `VersionRecord` | `—` | positional-or-keyword |

Результат: `dict[str, bytes]`.

## jane_registry.service.RegistryService.version

**Метод.** Код: [services/registry/src/jane_registry/service.py:290](../../../../../../services/registry/src/jane_registry/service.py#L290).

```python
async def version(self, package_id: str, version: str) -> VersionRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |
| `version` | `str` | `—` | positional-or-keyword |

Результат: `VersionRecord`.

Явні `raise` у тілі: `NotFound`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_registry.service.RegistryService.files_from_json

**Метод.** Код: [services/registry/src/jane_registry/service.py:299](../../../../../../services/registry/src/jane_registry/service.py#L299).

```python
def files_from_json(body: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, bytes]]:
```

Декоратори: `staticmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `body` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `tuple[dict[str, Any], dict[str, bytes]]`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_registry.service.RegistryService.files_from_zip

**Метод.** Код: [services/registry/src/jane_registry/service.py:329](../../../../../../services/registry/src/jane_registry/service.py#L329).

```python
def files_from_zip(self, data: bytes) -> tuple[Any, dict[str, bytes]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `data` | `bytes` | `—` | positional-or-keyword |

Результат: `tuple[Any, dict[str, bytes]]`.

Явні `raise` у тілі: `LimitExceeded`, `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_registry.service.RegistryService.publish

**Метод.** Код: [services/registry/src/jane_registry/service.py:451](../../../../../../services/registry/src/jane_registry/service.py#L451).

```python
async def publish(self, pkg: PackageRecord, manifest: Any, files: dict[str, bytes], principal: Principal, *, from_zip: bool, ported_parent_version: str | None=None, created_package: bool=False) -> VersionRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `pkg` | `PackageRecord` | `—` | positional-or-keyword |
| `manifest` | `Any` | `—` | positional-or-keyword |
| `files` | `dict[str, bytes]` | `—` | positional-or-keyword |
| `principal` | `Principal` | `—` | positional-or-keyword |
| `from_zip` | `bool` | `—` | keyword-only |
| `ported_parent_version` | `str \| None` | `None` | keyword-only |
| `created_package` | `bool` | `False` | keyword-only |

Результат: `VersionRecord`.

Явні `raise` у тілі: `Forbidden`, `JaneError`, `LimitExceeded`, `ValidationFailed`, `version_exists`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Validate and store a new immutable version (status ``draft``).
```

## jane_registry.service.RegistryService.set_status

**Метод.** Код: [services/registry/src/jane_registry/service.py:599](../../../../../../services/registry/src/jane_registry/service.py#L599).

```python
async def set_status(self, package_id: str, version: str, status: str, reason: str | None, principal: Principal) -> VersionRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |
| `version` | `str` | `—` | positional-or-keyword |
| `status` | `str` | `—` | positional-or-keyword |
| `reason` | `str \| None` | `—` | positional-or-keyword |
| `principal` | `Principal` | `—` | positional-or-keyword |

Результат: `VersionRecord`.

Явні `raise` у тілі: `Conflict`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_registry.service.RegistryService.record_test_results

**Метод.** Код: [services/registry/src/jane_registry/service.py:615](../../../../../../services/registry/src/jane_registry/service.py#L615).

```python
async def record_test_results(self, package_id: str, version: str, record: dict[str, Any]) -> VersionRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |
| `version` | `str` | `—` | positional-or-keyword |
| `record` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `VersionRecord`.

Явні `raise` у тілі: `JaneError`, `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_registry.service.RegistryService.fork

**Метод.** Код: [services/registry/src/jane_registry/service.py:639](../../../../../../services/registry/src/jane_registry/service.py#L639).

```python
async def fork(self, parent_id: str, body: Mapping[str, Any], principal: Principal) -> tuple[PackageRecord, VersionRecord]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `parent_id` | `str` | `—` | positional-or-keyword |
| `body` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `principal` | `Principal` | `—` | positional-or-keyword |

Результат: `tuple[PackageRecord, VersionRecord]`.

Явні `raise` у тілі: `Conflict`, `повторний raise`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_registry.service.RegistryService.diff

**Метод.** Код: [services/registry/src/jane_registry/service.py:708](../../../../../../services/registry/src/jane_registry/service.py#L708).

```python
async def diff(self, package_id: str, from_ref: str | None, to_ref: str, context_lines: int) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |
| `from_ref` | `str \| None` | `—` | positional-or-keyword |
| `to_ref` | `str` | `—` | positional-or-keyword |
| `context_lines` | `int` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_registry.service.RegistryService.upstream

**Метод.** Код: [services/registry/src/jane_registry/service.py:761](../../../../../../services/registry/src/jane_registry/service.py#L761).

```python
async def upstream(self, package_id: str) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_registry.service.RegistryService.plan_port

**Метод.** Код: [services/registry/src/jane_registry/service.py:776](../../../../../../services/registry/src/jane_registry/service.py#L776).

```python
async def plan_port(self, package_id: str, body: Mapping[str, Any], principal: Principal) -> PortPlan:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |
| `body` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `principal` | `Principal` | `—` | positional-or-keyword |

Результат: `PortPlan`.

Явні `raise` у тілі: `Conflict`, `version_exists`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_registry.service.RegistryService.port

**Метод.** Код: [services/registry/src/jane_registry/service.py:799](../../../../../../services/registry/src/jane_registry/service.py#L799).

```python
async def port(self, plan: PortPlan, principal: Principal, before_publish: Callable[[], Awaitable[None]] | None=None) -> VersionRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `plan` | `PortPlan` | `—` | positional-or-keyword |
| `principal` | `Principal` | `—` | positional-or-keyword |
| `before_publish` | `Callable[[], Awaitable[None]] \| None` | `None` | positional-or-keyword |

Результат: `VersionRecord`.

Явні `raise` у тілі: `JaneError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_registry.service.RegistryService.list_packages

**Метод.** Код: [services/registry/src/jane_registry/service.py:850](../../../../../../services/registry/src/jane_registry/service.py#L850).

```python
async def list_packages(self, flt: PackageFilter, after: str | None, limit: int) -> list[PackageRecord]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `flt` | `PackageFilter` | `—` | positional-or-keyword |
| `after` | `str \| None` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |

Результат: `list[PackageRecord]`.
