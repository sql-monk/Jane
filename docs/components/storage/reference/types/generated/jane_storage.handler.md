# jane_storage.handler

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_storage.handler.new_id](#jane_storagehandlernew_id)
- [jane_storage.handler.AdapterProvider](#jane_storagehandleradapterprovider)
- [jane_storage.handler.AdapterProvider.check](#jane_storagehandleradapterprovidercheck)
- [jane_storage.handler.AdapterProvider.adapter_for](#jane_storagehandleradapterprovideradapter_for)
- [jane_storage.handler.AdapterProvider.lease](#jane_storagehandleradapterproviderlease)
- [jane_storage.handler.PackageSource](#jane_storagehandlerpackagesource)
- [jane_storage.handler.PackageSource.get](#jane_storagehandlerpackagesourceget)
- [jane_storage.handler.Prepared](#jane_storagehandlerprepared)
- [jane_storage.handler.Prepared.__init__](#jane_storagehandlerprepared__init__)
- [jane_storage.handler.Prepared.invocation](#jane_storagehandlerpreparedinvocation)
- [jane_storage.handler.Prepared.package](#jane_storagehandlerpreparedpackage)
- [jane_storage.handler.Prepared.params](#jane_storagehandlerpreparedparams)
- [jane_storage.handler.Prepared.connection_id](#jane_storagehandlerpreparedconnection_id)
- [jane_storage.handler.Prepared.options](#jane_storagehandlerpreparedoptions)
- [jane_storage.handler.Prepared.raw_format](#jane_storagehandlerpreparedraw_format)
- [jane_storage.handler.Prepared.test_mode](#jane_storagehandlerpreparedtest_mode)
- [jane_storage.handler.Prepared.started_at](#jane_storagehandlerpreparedstarted_at)
- [jane_storage.handler.Prepared.invocation_id](#jane_storagehandlerpreparedinvocation_id)
- [jane_storage.handler.StorageHandler](#jane_storagehandlerstoragehandler)
- [jane_storage.handler.StorageHandler.__init__](#jane_storagehandlerstoragehandler__init__)
- [jane_storage.handler.StorageHandler.catalog](#jane_storagehandlerstoragehandlercatalog)
- [jane_storage.handler.StorageHandler.adapters](#jane_storagehandlerstoragehandleradapters)
- [jane_storage.handler.StorageHandler.content](#jane_storagehandlerstoragehandlercontent)
- [jane_storage.handler.StorageHandler.retries](#jane_storagehandlerstoragehandlerretries)
- [jane_storage.handler.StorageHandler.request_validator](#jane_storagehandlerstoragehandlerrequest_validator)
- [jane_storage.handler.StorageHandler.registry](#jane_storagehandlerstoragehandlerregistry)
- [jane_storage.handler.StorageHandler.archive_limits](#jane_storagehandlerstoragehandlerarchive_limits)
- [jane_storage.handler.StorageHandler.installed_adapters](#jane_storagehandlerstoragehandlerinstalled_adapters)
- [jane_storage.handler.StorageHandler.resolve_package](#jane_storagehandlerstoragehandlerresolve_package)
- [jane_storage.handler.StorageHandler.prepare](#jane_storagehandlerstoragehandlerprepare)
- [jane_storage.handler.StorageHandler.execute](#jane_storagehandlerstoragehandlerexecute)
- [jane_storage.handler.StorageHandler.invoke](#jane_storagehandlerstoragehandlerinvoke)

## jane_storage.handler.new_id

**Функція.** Код: [services/storage/src/jane_storage/handler.py:74](../../../../../../services/storage/src/jane_storage/handler.py#L74).

```python
def new_id(prefix: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `prefix` | `str` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
Sortable opaque id: ``<prefix>_<ms timestamp hex><random>`` (``Id`` pattern).
```

## jane_storage.handler.AdapterProvider

**Клас.** Код: [services/storage/src/jane_storage/handler.py:79](../../../../../../services/storage/src/jane_storage/handler.py#L79).

```python
class AdapterProvider(Protocol):
```

Базові типи / інтерфейси: `Protocol`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [check](jane_storage.handler.md#jane_storagehandleradapterprovidercheck) | Метод | ні |
| [adapter_for](jane_storage.handler.md#jane_storagehandleradapterprovideradapter_for) | Метод | ні |
| [lease](jane_storage.handler.md#jane_storagehandleradapterproviderlease) | Метод | ні |

## jane_storage.handler.AdapterProvider.check

**Метод.** Код: [services/storage/src/jane_storage/handler.py:80](../../../../../../services/storage/src/jane_storage/handler.py#L80).

```python
def check(self, connection_id: str, adapter_kind: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection_id` | `str` | `—` | positional-or-keyword |
| `adapter_kind` | `str` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Raise NotFound (unknown connection) or ValidationFailed (kind mismatch) before execution.
```

## jane_storage.handler.AdapterProvider.adapter_for

**Метод.** Код: [services/storage/src/jane_storage/handler.py:84](../../../../../../services/storage/src/jane_storage/handler.py#L84).

```python
async def adapter_for(self, connection_id: str, adapter_kind: str, options: Mapping[str, Any]) -> StorageAdapter:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection_id` | `str` | `—` | positional-or-keyword |
| `adapter_kind` | `str` | `—` | positional-or-keyword |
| `options` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `StorageAdapter`.

### Опис із вихідного коду

```text
Opened adapter for the connection (raises NotFound / ValidationFailed / AdapterError).
```

## jane_storage.handler.AdapterProvider.lease

**Метод.** Код: [services/storage/src/jane_storage/handler.py:90](../../../../../../services/storage/src/jane_storage/handler.py#L90).

```python
def lease(self, connection_id: str, adapter_kind: str, options: Mapping[str, Any]) -> AbstractAsyncContextManager[StorageAdapter]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection_id` | `str` | `—` | positional-or-keyword |
| `adapter_kind` | `str` | `—` | positional-or-keyword |
| `options` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `AbstractAsyncContextManager[StorageAdapter]`.

### Опис із вихідного коду

```text
The opened adapter held for a block: a changed connection does not close it under the work in progress.
```

## jane_storage.handler.PackageSource

**Клас.** Код: [services/storage/src/jane_storage/handler.py:97](../../../../../../services/storage/src/jane_storage/handler.py#L97).

```python
class PackageSource(Protocol):
```

Базові типи / інтерфейси: `Protocol`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [get](jane_storage.handler.md#jane_storagehandlerpackagesourceget) | Метод | ні |

## jane_storage.handler.PackageSource.get

**Метод.** Код: [services/storage/src/jane_storage/handler.py:98](../../../../../../services/storage/src/jane_storage/handler.py#L98).

```python
async def get(self, ref: Mapping[str, Any]) -> StoragePackage:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ref` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `StoragePackage`.

### Опис із вихідного коду

```text
Verified package of ``ref`` (``package_id``, ``version``, digest when given) or a JaneError.
```

## jane_storage.handler.Prepared

**Клас.** Код: [services/storage/src/jane_storage/handler.py:104](../../../../../../services/storage/src/jane_storage/handler.py#L104).

```python
class Prepared:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [invocation](jane_storage.handler.md#jane_storagehandlerpreparedinvocation) | Поле | ні |
| [package](jane_storage.handler.md#jane_storagehandlerpreparedpackage) | Поле | ні |
| [params](jane_storage.handler.md#jane_storagehandlerpreparedparams) | Поле | ні |
| [connection_id](jane_storage.handler.md#jane_storagehandlerpreparedconnection_id) | Поле | ні |
| [options](jane_storage.handler.md#jane_storagehandlerpreparedoptions) | Поле | ні |
| [raw_format](jane_storage.handler.md#jane_storagehandlerpreparedraw_format) | Поле | ні |
| [test_mode](jane_storage.handler.md#jane_storagehandlerpreparedtest_mode) | Поле | ні |
| [started_at](jane_storage.handler.md#jane_storagehandlerpreparedstarted_at) | Поле | ні |
| [invocation_id](jane_storage.handler.md#jane_storagehandlerpreparedinvocation_id) | Поле | ні |
| [__init__](jane_storage.handler.md#jane_storagehandlerprepared__init__) | Конструктор dataclass | ні |

## jane_storage.handler.Prepared.__init__

**Конструктор dataclass.** Код: [services/storage/src/jane_storage/handler.py:104](../../../../../../services/storage/src/jane_storage/handler.py#L104).

```python
def __init__(self, invocation: dict[str, Any], package: StoragePackage, params: dict[str, Any], connection_id: str | None, options: dict[str, Any], raw_format: str, test_mode: bool, started_at: datetime, invocation_id: str = <factory lambda: new_id('inv')>) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `invocation` | `dict[str, Any]` | `—` | positional-or-keyword |
| `package` | `StoragePackage` | `—` | positional-or-keyword |
| `params` | `dict[str, Any]` | `—` | positional-or-keyword |
| `connection_id` | `str \| None` | `—` | positional-or-keyword |
| `options` | `dict[str, Any]` | `—` | positional-or-keyword |
| `raw_format` | `str` | `—` | positional-or-keyword |
| `test_mode` | `bool` | `—` | positional-or-keyword |
| `started_at` | `datetime` | `—` | positional-or-keyword |
| `invocation_id` | `str` | `factory: lambda: new_id('inv')` | positional-or-keyword |

Результат: `None`.

## jane_storage.handler.Prepared.invocation

**Поле.** Код: [services/storage/src/jane_storage/handler.py:105](../../../../../../services/storage/src/jane_storage/handler.py#L105).

```python
invocation: dict[str, Any]
```

Доступ: читання — так; запис — так.

## jane_storage.handler.Prepared.package

**Поле.** Код: [services/storage/src/jane_storage/handler.py:106](../../../../../../services/storage/src/jane_storage/handler.py#L106).

```python
package: StoragePackage
```

Доступ: читання — так; запис — так.

## jane_storage.handler.Prepared.params

**Поле.** Код: [services/storage/src/jane_storage/handler.py:107](../../../../../../services/storage/src/jane_storage/handler.py#L107).

```python
params: dict[str, Any]
```

Доступ: читання — так; запис — так.

## jane_storage.handler.Prepared.connection_id

**Поле.** Код: [services/storage/src/jane_storage/handler.py:108](../../../../../../services/storage/src/jane_storage/handler.py#L108).

```python
connection_id: str | None
```

Доступ: читання — так; запис — так.

## jane_storage.handler.Prepared.options

**Поле.** Код: [services/storage/src/jane_storage/handler.py:109](../../../../../../services/storage/src/jane_storage/handler.py#L109).

```python
options: dict[str, Any]
```

Доступ: читання — так; запис — так.

## jane_storage.handler.Prepared.raw_format

**Поле.** Код: [services/storage/src/jane_storage/handler.py:110](../../../../../../services/storage/src/jane_storage/handler.py#L110).

```python
raw_format: str
```

Доступ: читання — так; запис — так.

## jane_storage.handler.Prepared.test_mode

**Поле.** Код: [services/storage/src/jane_storage/handler.py:111](../../../../../../services/storage/src/jane_storage/handler.py#L111).

```python
test_mode: bool
```

Доступ: читання — так; запис — так.

## jane_storage.handler.Prepared.started_at

**Поле.** Код: [services/storage/src/jane_storage/handler.py:112](../../../../../../services/storage/src/jane_storage/handler.py#L112).

```python
started_at: datetime
```

Доступ: читання — так; запис — так.

## jane_storage.handler.Prepared.invocation_id

**Поле.** Код: [services/storage/src/jane_storage/handler.py:113](../../../../../../services/storage/src/jane_storage/handler.py#L113).

```python
invocation_id: str = field(default_factory=lambda: new_id('inv'))
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "lambda: new_id('inv')"
}
```

## jane_storage.handler.StorageHandler

**Клас.** Код: [services/storage/src/jane_storage/handler.py:150](../../../../../../services/storage/src/jane_storage/handler.py#L150).

```python
class StorageHandler:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_storage.handler.md#jane_storagehandlerstoragehandler__init__) | Конструктор | ні |
| [catalog](jane_storage.handler.md#jane_storagehandlerstoragehandlercatalog) | Поле екземпляра | ні |
| [adapters](jane_storage.handler.md#jane_storagehandlerstoragehandleradapters) | Поле екземпляра | ні |
| [content](jane_storage.handler.md#jane_storagehandlerstoragehandlercontent) | Поле екземпляра | ні |
| [retries](jane_storage.handler.md#jane_storagehandlerstoragehandlerretries) | Поле екземпляра | ні |
| [request_validator](jane_storage.handler.md#jane_storagehandlerstoragehandlerrequest_validator) | Поле екземпляра | ні |
| [registry](jane_storage.handler.md#jane_storagehandlerstoragehandlerregistry) | Поле екземпляра | ні |
| [archive_limits](jane_storage.handler.md#jane_storagehandlerstoragehandlerarchive_limits) | Поле екземпляра | ні |
| [installed_adapters](jane_storage.handler.md#jane_storagehandlerstoragehandlerinstalled_adapters) | Поле екземпляра | ні |
| [resolve_package](jane_storage.handler.md#jane_storagehandlerstoragehandlerresolve_package) | Метод | ні |
| [prepare](jane_storage.handler.md#jane_storagehandlerstoragehandlerprepare) | Метод | ні |
| [execute](jane_storage.handler.md#jane_storagehandlerstoragehandlerexecute) | Метод | ні |
| [invoke](jane_storage.handler.md#jane_storagehandlerstoragehandlerinvoke) | Метод | ні |

## jane_storage.handler.StorageHandler.__init__

**Конструктор.** Код: [services/storage/src/jane_storage/handler.py:151](../../../../../../services/storage/src/jane_storage/handler.py#L151).

```python
def __init__(self, catalog: PackageCatalog, adapters: AdapterProvider, content: ContentReader, *, retries: RetryPolicy | None=None, request_validator: Callable[[dict[str, Any]], list[FieldError]] | None=None, clock: Callable[[], datetime]=utcnow, registry: PackageSource | None=None, archive_limits: ArchiveLimits | None=None, installed_adapters: Collection[str] | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `catalog` | `PackageCatalog` | `—` | positional-or-keyword |
| `adapters` | `AdapterProvider` | `—` | positional-or-keyword |
| `content` | `ContentReader` | `—` | positional-or-keyword |
| `retries` | `RetryPolicy \| None` | `None` | keyword-only |
| `request_validator` | `Callable[[dict[str, Any]], list[FieldError]] \| None` | `None` | keyword-only |
| `clock` | `Callable[[], datetime]` | `utcnow` | keyword-only |
| `registry` | `PackageSource \| None` | `None` | keyword-only |
| `archive_limits` | `ArchiveLimits \| None` | `None` | keyword-only |
| `installed_adapters` | `Collection[str] \| None` | `None` | keyword-only |

Результат: `None`.

## jane_storage.handler.StorageHandler.catalog

**Поле екземпляра.** Код: [services/storage/src/jane_storage/handler.py:164](../../../../../../services/storage/src/jane_storage/handler.py#L164).

```python
self.catalog = catalog
```

## jane_storage.handler.StorageHandler.adapters

**Поле екземпляра.** Код: [services/storage/src/jane_storage/handler.py:165](../../../../../../services/storage/src/jane_storage/handler.py#L165).

```python
self.adapters = adapters
```

## jane_storage.handler.StorageHandler.content

**Поле екземпляра.** Код: [services/storage/src/jane_storage/handler.py:166](../../../../../../services/storage/src/jane_storage/handler.py#L166).

```python
self.content = content
```

## jane_storage.handler.StorageHandler.retries

**Поле екземпляра.** Код: [services/storage/src/jane_storage/handler.py:167](../../../../../../services/storage/src/jane_storage/handler.py#L167).

```python
self.retries = retries or RetryPolicy()
```

## jane_storage.handler.StorageHandler.request_validator

**Поле екземпляра.** Код: [services/storage/src/jane_storage/handler.py:168](../../../../../../services/storage/src/jane_storage/handler.py#L168).

```python
self.request_validator = request_validator
```

## jane_storage.handler.StorageHandler.registry

**Поле екземпляра.** Код: [services/storage/src/jane_storage/handler.py:170](../../../../../../services/storage/src/jane_storage/handler.py#L170).

```python
self.registry = registry
```

## jane_storage.handler.StorageHandler.archive_limits

**Поле екземпляра.** Код: [services/storage/src/jane_storage/handler.py:172](../../../../../../services/storage/src/jane_storage/handler.py#L172).

```python
self.archive_limits = archive_limits or ArchiveLimits()
```

## jane_storage.handler.StorageHandler.installed_adapters

**Поле екземпляра.** Код: [services/storage/src/jane_storage/handler.py:173](../../../../../../services/storage/src/jane_storage/handler.py#L173).

```python
self.installed_adapters = None if installed_adapters is None else frozenset(installed_adapters)
```

## jane_storage.handler.StorageHandler.resolve_package

**Метод.** Код: [services/storage/src/jane_storage/handler.py:198](../../../../../../services/storage/src/jane_storage/handler.py#L198).

```python
async def resolve_package(self, ref: Mapping[str, Any], archive_ref: Mapping[str, Any] | None=None) -> StoragePackage:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ref` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `archive_ref` | `Mapping[str, Any] \| None` | `None` | positional-or-keyword |

Результат: `StoragePackage`.

Явні `raise` у тілі: `JaneError`, `NotFound`, `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
The package of ``ref``: ``archive_ref`` (``package_archive``), else built in, else the registry.
```

## jane_storage.handler.StorageHandler.prepare

**Метод.** Код: [services/storage/src/jane_storage/handler.py:236](../../../../../../services/storage/src/jane_storage/handler.py#L236).

```python
async def prepare(self, invocation: dict[str, Any], *, package: StoragePackage | None=None) -> Prepared:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `invocation` | `dict[str, Any]` | `—` | positional-or-keyword |
| `package` | `StoragePackage \| None` | `None` | keyword-only |

Результат: `Prepared`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Validate ``invocation``; ``package`` — already resolved (test runs), else :meth:`resolve_package`.
```

## jane_storage.handler.StorageHandler.execute

**Метод.** Код: [services/storage/src/jane_storage/handler.py:349](../../../../../../services/storage/src/jane_storage/handler.py#L349).

```python
async def execute(self, prep: Prepared) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `prep` | `Prepared` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_storage.handler.StorageHandler.invoke

**Метод.** Код: [services/storage/src/jane_storage/handler.py:480](../../../../../../services/storage/src/jane_storage/handler.py#L480).

```python
async def invoke(self, invocation: dict[str, Any]) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `invocation` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
``prepare`` + ``execute`` (JaneError from ``prepare`` propagates).
```
