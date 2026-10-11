# Модуль `jane_storage.handler`

> Згенеровано `scripts/docs_reference.py` з [services/storage/src/jane_storage/handler.py](../../../../../services/storage/src/jane_storage/handler.py). Не редагуйте вручну.

Storage handler: ``HandlerInvocation`` → ``HandlerResult`` (handler.v1, ``handler_kind: storage``).

The package (:meth:`StorageHandler.resolve_package`) comes from, in this order: ``package_archive`` of the request; the built-in catalog (installed adapter distributions; its ``package_id@version`` is authoritative, a different ``digest`` is ``digest_mismatch`` without asking the registry); the registry, when configured (:mod:`jane_storage.registry_packages`). Not found anywhere → 404; registry unreachable → 502 ``upstream_unavailable`` (retryable).

Two phases:

* :meth:`StorageHandler.prepare` validates the request and raises :class:`jane_kit.errors.JaneError` (HTTP 404/422/502: unknown package or connection, digest mismatch, invalid params, input kind not accepted by the package, registry unavailable) — the call did not happen;
* :meth:`StorageHandler.execute` runs it; storage failures are ``status: failed`` results (``AdapterError(retryable=True)`` → ``failure.kind = connection_error``), never exceptions.

Delivery keys of the parts of one invocation — :mod:`jane_storage.keys`; ``test_mode`` validates and returns ``simulated`` acks without touching the adapter.

## Зміст

- [Клас `AdapterProvider`](#клас-adapterprovider)
- [Клас `PackageSource`](#клас-packagesource)
- [Клас `Prepared`](#клас-prepared)
- [Клас `StorageHandler`](#клас-storagehandler)
- [Функція `new_id`](#функція-new_id)

## Класи

### Клас `AdapterProvider`

| Властивість | Значення |
|---|---|
| Вид | протокол |
| Модуль | `jane_storage.handler` |
| Успадкування | `Protocol` |
| Код | [handler.py:79](../../../../../services/storage/src/jane_storage/handler.py#L79) |

```python
class AdapterProvider(Protocol): ...
```

#### Метод `AdapterProvider.check`

```python
def check(self, connection_id: str, adapter_kind: str) -> None: ...
```

Raise NotFound (unknown connection) or ValidationFailed (kind mismatch) before execution.

Код: [handler.py:80](../../../../../services/storage/src/jane_storage/handler.py#L80).

#### Метод `AdapterProvider.adapter_for`

```python
async def adapter_for(
    self,
    connection_id: str,
    adapter_kind: str,
    options: Mapping[str, Any],
) -> StorageAdapter: ...
```

Opened adapter for the connection (raises NotFound / ValidationFailed / AdapterError).

Код: [handler.py:84](../../../../../services/storage/src/jane_storage/handler.py#L84).

#### Метод `AdapterProvider.lease`

```python
def lease(
    self,
    connection_id: str,
    adapter_kind: str,
    options: Mapping[str, Any],
) -> AbstractAsyncContextManager[StorageAdapter]: ...
```

The opened adapter held for a block: a changed connection does not close it under the work in progress.

Код: [handler.py:90](../../../../../services/storage/src/jane_storage/handler.py#L90).

### Клас `PackageSource`

| Властивість | Значення |
|---|---|
| Вид | протокол |
| Модуль | `jane_storage.handler` |
| Успадкування | `Protocol` |
| Код | [handler.py:97](../../../../../services/storage/src/jane_storage/handler.py#L97) |

```python
class PackageSource(Protocol): ...
```

#### Метод `PackageSource.get`

```python
async def get(self, ref: Mapping[str, Any]) -> StoragePackage: ...
```

Verified package of ``ref`` (``package_id``, ``version``, digest when given) or a JaneError.

Код: [handler.py:98](../../../../../services/storage/src/jane_storage/handler.py#L98).

### Клас `Prepared`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_storage.handler` |
| Код | [handler.py:104](../../../../../services/storage/src/jane_storage/handler.py#L104) |

```python
@dataclass
class Prepared: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `invocation` | `dict[str, Any]` | — | читання й запис |  |
| `package` | `StoragePackage` | — | читання й запис |  |
| `params` | `dict[str, Any]` | — | читання й запис |  |
| `connection_id` | `str \| None` | — | читання й запис |  |
| `options` | `dict[str, Any]` | — | читання й запис |  |
| `raw_format` | `str` | — | читання й запис |  |
| `test_mode` | `bool` | — | читання й запис |  |
| `started_at` | `datetime` | — | читання й запис |  |
| `invocation_id` | `str` | `field(default_factory=lambda: new_id('inv'))` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `StorageHandler`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage.handler` |
| Код | [handler.py:150](../../../../../services/storage/src/jane_storage/handler.py#L150) |

```python
class StorageHandler: ...
```

#### Конструктор `StorageHandler.__init__`

```python
def __init__(
    self,
    catalog: PackageCatalog,
    adapters: AdapterProvider,
    content: ContentReader,
    *,
    retries: RetryPolicy | None = None,
    request_validator: Callable[[dict[str, Any]], list[FieldError]] | None = None,
    clock: Callable[[], datetime] = utcnow,
    registry: PackageSource | None = None,
    archive_limits: ArchiveLimits | None = None,
    installed_adapters: Collection[str] | None = None,
) -> None: ...
```

Код: [handler.py:151](../../../../../services/storage/src/jane_storage/handler.py#L151).

#### Метод `StorageHandler.resolve_package`

```python
async def resolve_package(
    self,
    ref: Mapping[str, Any],
    archive_ref: Mapping[str, Any] | None = None,
) -> StoragePackage: ...
```

The package of ``ref``: ``archive_ref`` (``package_archive``), else built in, else the registry.

Винятки в коді методу: `JaneError`, `ValidationFailed`, `NotFound`.

Код: [handler.py:198](../../../../../services/storage/src/jane_storage/handler.py#L198).

#### Метод `StorageHandler.prepare`

```python
async def prepare(
    self,
    invocation: dict[str, Any],
    *,
    package: StoragePackage | None = None,
) -> Prepared: ...
```

Validate ``invocation``; ``package`` — already resolved (test runs), else :meth:`resolve_package`.

Винятки в коді методу: `ValidationFailed`.

Код: [handler.py:236](../../../../../services/storage/src/jane_storage/handler.py#L236).

#### Метод `StorageHandler.execute`

```python
async def execute(self, prep: Prepared) -> dict[str, Any]: ...
```

Код: [handler.py:349](../../../../../services/storage/src/jane_storage/handler.py#L349).

#### Метод `StorageHandler.invoke`

```python
async def invoke(self, invocation: dict[str, Any]) -> dict[str, Any]: ...
```

``prepare`` + ``execute`` (JaneError from ``prepare`` propagates).

Код: [handler.py:480](../../../../../services/storage/src/jane_storage/handler.py#L480).

## Функції

### Функція `new_id`

```python
def new_id(prefix: str) -> str: ...
```

Sortable opaque id: ``<prefix>_<ms timestamp hex><random>`` (``Id`` pattern).

Код: [handler.py:74](../../../../../services/storage/src/jane_storage/handler.py#L74).
