# Модуль `jane_registry.service`

> Згенеровано `scripts/docs_reference.py` з [services/registry/src/jane_registry/service.py](../../../../../services/registry/src/jane_registry/service.py). Не редагуйте вручну.

Domain logic of the registry (registry.v1): packages, immutable versions, statuses, test reports, forks, diff, upstream status and explicit upstream ports. HTTP-agnostic; :mod:`jane_registry.app` maps it to the API.

## Зміст

- [Клас `PortPlan`](#клас-portplan)
- [Клас `RegistryService`](#клас-registryservice)
- [Функція `package_wire`](#функція-package_wire)
- [Функція `version_wire`](#функція-version_wire)

## Класи

### Клас `PortPlan`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_registry.service` |
| Код | [service.py:180](../../../../../services/registry/src/jane_registry/service.py#L180) |

```python
@dataclass(frozen=True)
class PortPlan: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `fork` | `PackageRecord` | — | читання |  |
| `parent_id` | `str` | — | читання |  |
| `parent_version` | `str` | — | читання |  |
| `base_version` | `str` | — | читання |  |
| `merge_base` | `str` | — | читання |  |
| `new_version` | `str` | — | читання |  |
| `requested_by` | `str` | — | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `RegistryService`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.service` |
| Код | [service.py:214](../../../../../services/registry/src/jane_registry/service.py#L214) |

```python
class RegistryService: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `archive_limits` | `ArchiveLimits` | — | читання (властивість) |  |

#### Конструктор `RegistryService.__init__`

```python
def __init__(
    self,
    store: MetadataStore,
    blobs: BlobStore,
    validator: PackageValidator,
    profiles: ProfileSource,
    limits: ServiceLimits,
) -> None: ...
```

Код: [service.py:215](../../../../../services/registry/src/jane_registry/service.py#L215).

#### Метод `RegistryService.package`

```python
async def package(self, package_id: str) -> PackageRecord: ...
```

Винятки в коді методу: `NotFound`.

Код: [service.py:236](../../../../../services/registry/src/jane_registry/service.py#L236).

#### Метод `RegistryService.create_package`

```python
async def create_package(self, body: Mapping[str, Any], principal: Principal) -> PackageRecord: ...
```

Винятки в коді методу: `Conflict`.

Код: [service.py:242](../../../../../services/registry/src/jane_registry/service.py#L242).

#### Метод `RegistryService.update_package`

```python
async def update_package(
    self,
    package_id: str,
    changes: dict[str, Any],
    if_match: str | None,
) -> PackageRecord: ...
```

Винятки в коді методу: `JaneError`.

Код: [service.py:260](../../../../../services/registry/src/jane_registry/service.py#L260).

#### Метод `RegistryService.archive`

```python
async def archive(self, v: VersionRecord) -> bytes: ...
```

Винятки в коді методу: `UpstreamUnavailable`.

Код: [service.py:277](../../../../../services/registry/src/jane_registry/service.py#L277).

#### Метод `RegistryService.files_of`

```python
async def files_of(self, v: VersionRecord) -> dict[str, bytes]: ...
```

Код: [service.py:287](../../../../../services/registry/src/jane_registry/service.py#L287).

#### Метод `RegistryService.version`

```python
async def version(self, package_id: str, version: str) -> VersionRecord: ...
```

Винятки в коді методу: `NotFound`.

Код: [service.py:290](../../../../../services/registry/src/jane_registry/service.py#L290).

#### Метод `RegistryService.files_from_json`

```python
@staticmethod
def files_from_json(body: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, bytes]]: ...
```

Винятки в коді методу: `ValidationFailed`.

Код: [service.py:299](../../../../../services/registry/src/jane_registry/service.py#L299).

#### Метод `RegistryService.files_from_zip`

```python
def files_from_zip(self, data: bytes) -> tuple[Any, dict[str, bytes]]: ...
```

Винятки в коді методу: `ValidationFailed`, `LimitExceeded`.

Код: [service.py:329](../../../../../services/registry/src/jane_registry/service.py#L329).

#### Метод `RegistryService.publish`

```python
async def publish(
    self,
    pkg: PackageRecord,
    manifest: Any,
    files: dict[str, bytes],
    principal: Principal,
    *,
    from_zip: bool,
    ported_parent_version: str | None = None,
    created_package: bool = False,
) -> VersionRecord: ...
```

Validate and store a new immutable version (status ``draft``).

Винятки в коді методу: `ValidationFailed`, `Forbidden`, `LimitExceeded`, `JaneError`.

Код: [service.py:451](../../../../../services/registry/src/jane_registry/service.py#L451).

#### Метод `RegistryService.set_status`

```python
async def set_status(
    self,
    package_id: str,
    version: str,
    status: str,
    reason: str | None,
    principal: Principal,
) -> VersionRecord: ...
```

Винятки в коді методу: `Conflict`.

Код: [service.py:599](../../../../../services/registry/src/jane_registry/service.py#L599).

#### Метод `RegistryService.record_test_results`

```python
async def record_test_results(
    self,
    package_id: str,
    version: str,
    record: dict[str, Any],
) -> VersionRecord: ...
```

Винятки в коді методу: `ValidationFailed`, `JaneError`.

Код: [service.py:615](../../../../../services/registry/src/jane_registry/service.py#L615).

#### Метод `RegistryService.fork`

```python
async def fork(
    self,
    parent_id: str,
    body: Mapping[str, Any],
    principal: Principal,
) -> tuple[PackageRecord, VersionRecord]: ...
```

Винятки в коді методу: `Conflict`.

Код: [service.py:639](../../../../../services/registry/src/jane_registry/service.py#L639).

#### Метод `RegistryService.diff`

```python
async def diff(
    self,
    package_id: str,
    from_ref: str | None,
    to_ref: str,
    context_lines: int,
) -> dict[str, Any]: ...
```

Винятки в коді методу: `ValidationFailed`.

Код: [service.py:708](../../../../../services/registry/src/jane_registry/service.py#L708).

#### Метод `RegistryService.upstream`

```python
async def upstream(self, package_id: str) -> dict[str, Any]: ...
```

Код: [service.py:761](../../../../../services/registry/src/jane_registry/service.py#L761).

#### Метод `RegistryService.plan_port`

```python
async def plan_port(
    self,
    package_id: str,
    body: Mapping[str, Any],
    principal: Principal,
) -> PortPlan: ...
```

Винятки в коді методу: `Conflict`.

Код: [service.py:776](../../../../../services/registry/src/jane_registry/service.py#L776).

#### Метод `RegistryService.port`

```python
async def port(
    self,
    plan: PortPlan,
    principal: Principal,
    before_publish: Callable[[], Awaitable[None]] | None = None,
) -> VersionRecord: ...
```

Винятки в коді методу: `JaneError`.

Код: [service.py:799](../../../../../services/registry/src/jane_registry/service.py#L799).

#### Метод `RegistryService.list_packages`

```python
async def list_packages(
    self,
    flt: PackageFilter,
    after: str | None,
    limit: int,
) -> list[PackageRecord]: ...
```

Код: [service.py:850](../../../../../services/registry/src/jane_registry/service.py#L850).

## Функції

### Функція `package_wire`

```python
def package_wire(pkg: PackageRecord, forks_count: int | None = None) -> dict[str, Any]: ...
```

Код: [service.py:87](../../../../../services/registry/src/jane_registry/service.py#L87).

### Функція `version_wire`

```python
def version_wire(v: VersionRecord, *, full: bool = True) -> dict[str, Any]: ...
```

Код: [service.py:115](../../../../../services/registry/src/jane_registry/service.py#L115).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `STATUS_TRANSITIONS` | `dict[str, frozenset[str]]` | `{'draft': frozenset({'approved', 'rejected', 'deprecated', 'yanked'}), 'approved` |  |
