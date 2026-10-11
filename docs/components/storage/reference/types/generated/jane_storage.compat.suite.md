# jane_storage.compat.suite

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_storage.compat.suite.SCENARIOS](#jane_storagecompatsuitescenarios)
- [jane_storage.compat.suite.CompatTarget](#jane_storagecompatsuitecompattarget)
- [jane_storage.compat.suite.CompatTarget.kind](#jane_storagecompatsuitecompattargetkind)
- [jane_storage.compat.suite.CompatTarget.entity_formats](#jane_storagecompatsuitecompattargetentity_formats)
- [jane_storage.compat.suite.CompatTarget.connection](#jane_storagecompatsuitecompattargetconnection)
- [jane_storage.compat.suite.CompatTarget.unavailable_connection](#jane_storagecompatsuitecompattargetunavailable_connection)
- [jane_storage.compat.suite.CompatTarget.options](#jane_storagecompatsuitecompattargetoptions)
- [jane_storage.compat.suite.CompatTarget.cleanup](#jane_storagecompatsuitecompattargetcleanup)
- [jane_storage.compat.suite.CompatTarget.native_object_path](#jane_storagecompatsuitecompattargetnative_object_path)
- [jane_storage.compat.suite.CompatTarget.native_entity_document](#jane_storagecompatsuitecompattargetnative_entity_document)
- [jane_storage.compat.suite.CompatTarget.native_history_documents](#jane_storagecompatsuitecompattargetnative_history_documents)
- [jane_storage.compat.suite.CompatEnv](#jane_storagecompatsuitecompatenv)
- [jane_storage.compat.suite.CompatEnv.__init__](#jane_storagecompatsuitecompatenv__init__)
- [jane_storage.compat.suite.CompatEnv.target](#jane_storagecompatsuitecompatenvtarget)
- [jane_storage.compat.suite.CompatEnv.adapter](#jane_storagecompatsuitecompatenvadapter)
- [jane_storage.compat.suite.CompatEnv.restart](#jane_storagecompatsuitecompatenvrestart)
- [jane_storage.compat.suite.CompatEnv.engine](#jane_storagecompatsuitecompatenvengine)
- [jane_storage.compat.suite.CompatEnv.package](#jane_storagecompatsuitecompatenvpackage)
- [jane_storage.compat.suite.CompatEnv.handler](#jane_storagecompatsuitecompatenvhandler)
- [jane_storage.compat.suite.CompatEnv.close](#jane_storagecompatsuitecompatenvclose)
- [jane_storage.compat.suite.AdapterCompatSuite](#jane_storagecompatsuiteadaptercompatsuite)
- [jane_storage.compat.suite.AdapterCompatSuite.compat_target](#jane_storagecompatsuiteadaptercompatsuitecompat_target)
- [jane_storage.compat.suite.AdapterCompatSuite.env](#jane_storagecompatsuiteadaptercompatsuiteenv)
- [jane_storage.compat.suite.AdapterCompatSuite.test_registered_with_required_capabilities](#jane_storagecompatsuiteadaptercompatsuitetest_registered_with_required_capabilities)
- [jane_storage.compat.suite.AdapterCompatSuite.test_c01_new_entity](#jane_storagecompatsuiteadaptercompatsuitetest_c01_new_entity)
- [jane_storage.compat.suite.AdapterCompatSuite.test_c02_redelivery_after_restart_is_duplicate](#jane_storagecompatsuiteadaptercompatsuitetest_c02_redelivery_after_restart_is_duplicate)
- [jane_storage.compat.suite.AdapterCompatSuite.test_c03_new_observation_updates](#jane_storagecompatsuiteadaptercompatsuitetest_c03_new_observation_updates)
- [jane_storage.compat.suite.AdapterCompatSuite.test_c04_partial_update_keeps_other_fields](#jane_storagecompatsuiteadaptercompatsuitetest_c04_partial_update_keeps_other_fields)
- [jane_storage.compat.suite.AdapterCompatSuite.test_c05_explicit_clear](#jane_storagecompatsuiteadaptercompatsuitetest_c05_explicit_clear)
- [jane_storage.compat.suite.AdapterCompatSuite.test_c06_late_observation_is_stale](#jane_storagecompatsuiteadaptercompatsuitetest_c06_late_observation_is_stale)
- [jane_storage.compat.suite.AdapterCompatSuite.test_c07_mixed_partially_stale](#jane_storagecompatsuiteadaptercompatsuitetest_c07_mixed_partially_stale)
- [jane_storage.compat.suite.AdapterCompatSuite.test_c08_same_time_higher_sequence_wins](#jane_storagecompatsuiteadaptercompatsuitetest_c08_same_time_higher_sequence_wins)
- [jane_storage.compat.suite.AdapterCompatSuite.test_c09_concurrent_commits](#jane_storagecompatsuiteadaptercompatsuitetest_c09_concurrent_commits)
- [jane_storage.compat.suite.AdapterCompatSuite.test_c10_put_object_is_idempotent](#jane_storagecompatsuiteadaptercompatsuitetest_c10_put_object_is_idempotent)
- [jane_storage.compat.suite.AdapterCompatSuite.test_c11_same_key_other_content_is_rejected](#jane_storagecompatsuiteadaptercompatsuitetest_c11_same_key_other_content_is_rejected)
- [jane_storage.compat.suite.AdapterCompatSuite.test_c12_raw_html_round_trip](#jane_storagecompatsuiteadaptercompatsuitetest_c12_raw_html_round_trip)
- [jane_storage.compat.suite.AdapterCompatSuite.test_c13_entities_are_json_documents](#jane_storagecompatsuiteadaptercompatsuitetest_c13_entities_are_json_documents)
- [jane_storage.compat.suite.AdapterCompatSuite.test_c14_unicode_and_long_keys](#jane_storagecompatsuiteadaptercompatsuitetest_c14_unicode_and_long_keys)
- [jane_storage.compat.suite.AdapterCompatSuite.test_c15_pagination](#jane_storagecompatsuiteadaptercompatsuitetest_c15_pagination)
- [jane_storage.compat.suite.AdapterCompatSuite.test_c16_unavailable_storage](#jane_storagecompatsuiteadaptercompatsuitetest_c16_unavailable_storage)

## jane_storage.compat.suite.SCENARIOS

**Константа.** Код: [services/storage/src/jane_storage/compat/suite.py:44](../../../../../../services/storage/src/jane_storage/compat/suite.py#L44).

```python
SCENARIOS = {'C-01': 'new entity', 'C-02': 'repeated delivery after adapter restart', 'C-03': 'new observation with new values', 'C-04': 'partial update', 'C-05': 'explicit clear', 'C-06': 'late observation', 'C-07': 'mixed: one field newer, another not', 'C-08': 'same observed_at, different sequence', 'C-09': 'concurrent commits with one expected_version', 'C-10': 'put_object with the same key and sha256', 'C-11': 'put_object with the same key, different sha256', 'C-12': 'RAW HTML round trip', 'C-13': 'entities as JSON documents; entities format override', 'C-14': 'unicode, special characters and a long key', 'C-15': 'pagination of entities, history and objects', 'C-16': 'unavailable storage'}
```

## jane_storage.compat.suite.CompatTarget

**Клас.** Код: [services/storage/src/jane_storage/compat/suite.py:121](../../../../../../services/storage/src/jane_storage/compat/suite.py#L121).

```python
class CompatTarget(ABC):
```

Базові типи / інтерфейси: `ABC`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [kind](jane_storage.compat.suite.md#jane_storagecompatsuitecompattargetkind) | Поле | ні |
| [entity_formats](jane_storage.compat.suite.md#jane_storagecompatsuitecompattargetentity_formats) | Поле | ні |
| [connection](jane_storage.compat.suite.md#jane_storagecompatsuitecompattargetconnection) | Метод | ні |
| [unavailable_connection](jane_storage.compat.suite.md#jane_storagecompatsuitecompattargetunavailable_connection) | Метод | ні |
| [options](jane_storage.compat.suite.md#jane_storagecompatsuitecompattargetoptions) | Метод | ні |
| [cleanup](jane_storage.compat.suite.md#jane_storagecompatsuitecompattargetcleanup) | Метод | ні |
| [native_object_path](jane_storage.compat.suite.md#jane_storagecompatsuitecompattargetnative_object_path) | Метод | ні |
| [native_entity_document](jane_storage.compat.suite.md#jane_storagecompatsuitecompattargetnative_entity_document) | Метод | ні |
| [native_history_documents](jane_storage.compat.suite.md#jane_storagecompatsuitecompattargetnative_history_documents) | Метод | ні |

### Опис із вихідного коду

```text
What an adapter package provides to the suite. One instance = one isolated namespace.
```

## jane_storage.compat.suite.CompatTarget.kind

**Поле.** Код: [services/storage/src/jane_storage/compat/suite.py:124](../../../../../../services/storage/src/jane_storage/compat/suite.py#L124).

```python
kind: ClassVar[str]
```

Доступ: читання — так; запис — так.

## jane_storage.compat.suite.CompatTarget.entity_formats

**Поле.** Код: [services/storage/src/jane_storage/compat/suite.py:125](../../../../../../services/storage/src/jane_storage/compat/suite.py#L125).

```python
entity_formats: ClassVar[tuple[str, ...]] = ('json',)
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Values of ``options["entities_format"]`` the adapter supports (filesystem: json and jsonl).
```

## jane_storage.compat.suite.CompatTarget.connection

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:129](../../../../../../services/storage/src/jane_storage/compat/suite.py#L129).

```python
def connection(self) -> ResolvedConnection:
```

Декоратори: `abstractmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `ResolvedConnection`.

### Опис із вихідного коду

```text
Connection to an empty namespace of a reachable storage (same one on every call).
```

## jane_storage.compat.suite.CompatTarget.unavailable_connection

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:133](../../../../../../services/storage/src/jane_storage/compat/suite.py#L133).

```python
def unavailable_connection(self) -> ResolvedConnection:
```

Декоратори: `abstractmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `ResolvedConnection`.

### Опис із вихідного коду

```text
Connection of the same kind whose storage is not reachable (C-16).
```

## jane_storage.compat.suite.CompatTarget.options

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:136](../../../../../../services/storage/src/jane_storage/compat/suite.py#L136).

```python
def options(self) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
Base ``adapter.open`` options (e.g. prefix); the suite adds ``entities_format``.
```

## jane_storage.compat.suite.CompatTarget.cleanup

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:140](../../../../../../services/storage/src/jane_storage/compat/suite.py#L140).

```python
async def cleanup(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Drop the namespace after the test (optional).
```

## jane_storage.compat.suite.CompatTarget.native_object_path

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:143](../../../../../../services/storage/src/jane_storage/compat/suite.py#L143).

```python
async def native_object_path(self, rec: ObjectRecord) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `rec` | `ObjectRecord` | `—` | positional-or-keyword |

Результат: `str | None`.

### Опис із вихідного коду

```text
Adapter-native name of a stored object (filesystem: relative path) — C-12; None if n/a.
```

## jane_storage.compat.suite.CompatTarget.native_entity_document

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:147](../../../../../../services/storage/src/jane_storage/compat/suite.py#L147).

```python
async def native_entity_document(self, entity_type: str, canonical_key: str, options: Mapping[str, Any]) -> Any | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `entity_type` | `str` | `—` | positional-or-keyword |
| `canonical_key` | `str` | `—` | positional-or-keyword |
| `options` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `Any | None`.

### Опис із вихідного коду

```text
The stored entity document as the adapter keeps it (parsed JSON) — C-13; None if n/a.
```

## jane_storage.compat.suite.CompatTarget.native_history_documents

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:153](../../../../../../services/storage/src/jane_storage/compat/suite.py#L153).

```python
async def native_history_documents(self, entity_type: str, canonical_key: str, options: Mapping[str, Any]) -> list[Any] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `entity_type` | `str` | `—` | positional-or-keyword |
| `canonical_key` | `str` | `—` | positional-or-keyword |
| `options` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `list[Any] | None`.

### Опис із вихідного коду

```text
Stored history documents in the adapter's native layout — C-13 format override; None if n/a.
```

## jane_storage.compat.suite.CompatEnv

**Клас.** Код: [services/storage/src/jane_storage/compat/suite.py:160](../../../../../../services/storage/src/jane_storage/compat/suite.py#L160).

```python
class CompatEnv:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_storage.compat.suite.md#jane_storagecompatsuitecompatenv__init__) | Конструктор | ні |
| [target](jane_storage.compat.suite.md#jane_storagecompatsuitecompatenvtarget) | Поле екземпляра | ні |
| [adapter](jane_storage.compat.suite.md#jane_storagecompatsuitecompatenvadapter) | Метод | ні |
| [restart](jane_storage.compat.suite.md#jane_storagecompatsuitecompatenvrestart) | Метод | ні |
| [engine](jane_storage.compat.suite.md#jane_storagecompatsuitecompatenvengine) | Метод | ні |
| [package](jane_storage.compat.suite.md#jane_storagecompatsuitecompatenvpackage) | Метод | ні |
| [handler](jane_storage.compat.suite.md#jane_storagecompatsuitecompatenvhandler) | Метод | ні |
| [close](jane_storage.compat.suite.md#jane_storagecompatsuitecompatenvclose) | Метод | ні |

### Опис із вихідного коду

```text
Opened adapters, engines and the handler over one :class:`CompatTarget`.
```

## jane_storage.compat.suite.CompatEnv.__init__

**Конструктор.** Код: [services/storage/src/jane_storage/compat/suite.py:163](../../../../../../services/storage/src/jane_storage/compat/suite.py#L163).

```python
def __init__(self, target: CompatTarget) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `target` | `CompatTarget` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.compat.suite.CompatEnv.target

**Поле екземпляра.** Код: [services/storage/src/jane_storage/compat/suite.py:164](../../../../../../services/storage/src/jane_storage/compat/suite.py#L164).

```python
self.target = target
```

## jane_storage.compat.suite.CompatEnv.adapter

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:167](../../../../../../services/storage/src/jane_storage/compat/suite.py#L167).

```python
async def adapter(self, *, connection: ResolvedConnection | None=None, **options: Any) -> StorageAdapter:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection` | `ResolvedConnection \| None` | `None` | keyword-only |
| `options` | `Any` | `—` | var-keyword |

Результат: `StorageAdapter`.

## jane_storage.compat.suite.CompatEnv.restart

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:176](../../../../../../services/storage/src/jane_storage/compat/suite.py#L176).

```python
async def restart(self, adapter: StorageAdapter, **options: Any) -> StorageAdapter:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `adapter` | `StorageAdapter` | `—` | positional-or-keyword |
| `options` | `Any` | `—` | var-keyword |

Результат: `StorageAdapter`.

## jane_storage.compat.suite.CompatEnv.engine

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:181](../../../../../../services/storage/src/jane_storage/compat/suite.py#L181).

```python
def engine(self, adapter: StorageAdapter) -> StorageEngine:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `adapter` | `StorageAdapter` | `—` | positional-or-keyword |

Результат: `StorageEngine`.

## jane_storage.compat.suite.CompatEnv.package

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:186](../../../../../../services/storage/src/jane_storage/compat/suite.py#L186).

```python
def package(self) -> StoragePackage:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `StoragePackage`.

Явні `raise` у тілі: `AssertionError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_storage.compat.suite.CompatEnv.handler

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:196](../../../../../../services/storage/src/jane_storage/compat/suite.py#L196).

```python
def handler(self, connection: ResolvedConnection) -> tuple[StorageHandler, AdapterPool]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection` | `ResolvedConnection` | `—` | positional-or-keyword |

Результат: `tuple[StorageHandler, AdapterPool]`.

## jane_storage.compat.suite.CompatEnv.close

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:204](../../../../../../services/storage/src/jane_storage/compat/suite.py#L204).

```python
async def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.compat.suite.AdapterCompatSuite

**Клас.** Код: [services/storage/src/jane_storage/compat/suite.py:273](../../../../../../services/storage/src/jane_storage/compat/suite.py#L273).

```python
class AdapterCompatSuite:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [compat_target](jane_storage.compat.suite.md#jane_storagecompatsuiteadaptercompatsuitecompat_target) | Метод | ні |
| [env](jane_storage.compat.suite.md#jane_storagecompatsuiteadaptercompatsuiteenv) | Метод | ні |
| [test_registered_with_required_capabilities](jane_storage.compat.suite.md#jane_storagecompatsuiteadaptercompatsuitetest_registered_with_required_capabilities) | Метод | ні |
| [test_c01_new_entity](jane_storage.compat.suite.md#jane_storagecompatsuiteadaptercompatsuitetest_c01_new_entity) | Метод | ні |
| [test_c02_redelivery_after_restart_is_duplicate](jane_storage.compat.suite.md#jane_storagecompatsuiteadaptercompatsuitetest_c02_redelivery_after_restart_is_duplicate) | Метод | ні |
| [test_c03_new_observation_updates](jane_storage.compat.suite.md#jane_storagecompatsuiteadaptercompatsuitetest_c03_new_observation_updates) | Метод | ні |
| [test_c04_partial_update_keeps_other_fields](jane_storage.compat.suite.md#jane_storagecompatsuiteadaptercompatsuitetest_c04_partial_update_keeps_other_fields) | Метод | ні |
| [test_c05_explicit_clear](jane_storage.compat.suite.md#jane_storagecompatsuiteadaptercompatsuitetest_c05_explicit_clear) | Метод | ні |
| [test_c06_late_observation_is_stale](jane_storage.compat.suite.md#jane_storagecompatsuiteadaptercompatsuitetest_c06_late_observation_is_stale) | Метод | ні |
| [test_c07_mixed_partially_stale](jane_storage.compat.suite.md#jane_storagecompatsuiteadaptercompatsuitetest_c07_mixed_partially_stale) | Метод | ні |
| [test_c08_same_time_higher_sequence_wins](jane_storage.compat.suite.md#jane_storagecompatsuiteadaptercompatsuitetest_c08_same_time_higher_sequence_wins) | Метод | ні |
| [test_c09_concurrent_commits](jane_storage.compat.suite.md#jane_storagecompatsuiteadaptercompatsuitetest_c09_concurrent_commits) | Метод | ні |
| [test_c10_put_object_is_idempotent](jane_storage.compat.suite.md#jane_storagecompatsuiteadaptercompatsuitetest_c10_put_object_is_idempotent) | Метод | ні |
| [test_c11_same_key_other_content_is_rejected](jane_storage.compat.suite.md#jane_storagecompatsuiteadaptercompatsuitetest_c11_same_key_other_content_is_rejected) | Метод | ні |
| [test_c12_raw_html_round_trip](jane_storage.compat.suite.md#jane_storagecompatsuiteadaptercompatsuitetest_c12_raw_html_round_trip) | Метод | ні |
| [test_c13_entities_are_json_documents](jane_storage.compat.suite.md#jane_storagecompatsuiteadaptercompatsuitetest_c13_entities_are_json_documents) | Метод | ні |
| [test_c14_unicode_and_long_keys](jane_storage.compat.suite.md#jane_storagecompatsuiteadaptercompatsuitetest_c14_unicode_and_long_keys) | Метод | ні |
| [test_c15_pagination](jane_storage.compat.suite.md#jane_storagecompatsuiteadaptercompatsuitetest_c15_pagination) | Метод | ні |
| [test_c16_unavailable_storage](jane_storage.compat.suite.md#jane_storagecompatsuiteadaptercompatsuitetest_c16_unavailable_storage) | Метод | ні |

### Опис із вихідного коду

```text
Base class; subclasses provide the ``compat_target`` fixture. Test names carry the scenario id.
```

## jane_storage.compat.suite.AdapterCompatSuite.compat_target

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:277](../../../../../../services/storage/src/jane_storage/compat/suite.py#L277).

```python
def compat_target(self) -> CompatTarget:
```

Декоратори: `pytest.fixture`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `CompatTarget`.

Явні `raise` у тілі: `NotImplementedError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_storage.compat.suite.AdapterCompatSuite.env

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:281](../../../../../../services/storage/src/jane_storage/compat/suite.py#L281).

```python
async def env(self, compat_target: CompatTarget) -> AsyncIterator[CompatEnv]:
```

Декоратори: `pytest.fixture`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `compat_target` | `CompatTarget` | `—` | positional-or-keyword |

Результат: `AsyncIterator[CompatEnv]`.

## jane_storage.compat.suite.AdapterCompatSuite.test_registered_with_required_capabilities

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:289](../../../../../../services/storage/src/jane_storage/compat/suite.py#L289).

```python
async def test_registered_with_required_capabilities(self, env: CompatEnv) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `env` | `CompatEnv` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.compat.suite.AdapterCompatSuite.test_c01_new_entity

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:300](../../../../../../services/storage/src/jane_storage/compat/suite.py#L300).

```python
async def test_c01_new_entity(self, env: CompatEnv) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `env` | `CompatEnv` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.compat.suite.AdapterCompatSuite.test_c02_redelivery_after_restart_is_duplicate

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:331](../../../../../../services/storage/src/jane_storage/compat/suite.py#L331).

```python
async def test_c02_redelivery_after_restart_is_duplicate(self, env: CompatEnv) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `env` | `CompatEnv` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.compat.suite.AdapterCompatSuite.test_c03_new_observation_updates

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:358](../../../../../../services/storage/src/jane_storage/compat/suite.py#L358).

```python
async def test_c03_new_observation_updates(self, env: CompatEnv) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `env` | `CompatEnv` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.compat.suite.AdapterCompatSuite.test_c04_partial_update_keeps_other_fields

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:374](../../../../../../services/storage/src/jane_storage/compat/suite.py#L374).

```python
async def test_c04_partial_update_keeps_other_fields(self, env: CompatEnv) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `env` | `CompatEnv` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.compat.suite.AdapterCompatSuite.test_c05_explicit_clear

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:388](../../../../../../services/storage/src/jane_storage/compat/suite.py#L388).

```python
async def test_c05_explicit_clear(self, env: CompatEnv) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `env` | `CompatEnv` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.compat.suite.AdapterCompatSuite.test_c06_late_observation_is_stale

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:410](../../../../../../services/storage/src/jane_storage/compat/suite.py#L410).

```python
async def test_c06_late_observation_is_stale(self, env: CompatEnv) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `env` | `CompatEnv` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.compat.suite.AdapterCompatSuite.test_c07_mixed_partially_stale

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:433](../../../../../../services/storage/src/jane_storage/compat/suite.py#L433).

```python
async def test_c07_mixed_partially_stale(self, env: CompatEnv) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `env` | `CompatEnv` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.compat.suite.AdapterCompatSuite.test_c08_same_time_higher_sequence_wins

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:449](../../../../../../services/storage/src/jane_storage/compat/suite.py#L449).

```python
async def test_c08_same_time_higher_sequence_wins(self, env: CompatEnv) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `env` | `CompatEnv` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.compat.suite.AdapterCompatSuite.test_c09_concurrent_commits

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:466](../../../../../../services/storage/src/jane_storage/compat/suite.py#L466).

```python
async def test_c09_concurrent_commits(self, env: CompatEnv) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `env` | `CompatEnv` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.compat.suite.AdapterCompatSuite.test_c10_put_object_is_idempotent

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:504](../../../../../../services/storage/src/jane_storage/compat/suite.py#L504).

```python
async def test_c10_put_object_is_idempotent(self, env: CompatEnv) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `env` | `CompatEnv` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.compat.suite.AdapterCompatSuite.test_c11_same_key_other_content_is_rejected

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:533](../../../../../../services/storage/src/jane_storage/compat/suite.py#L533).

```python
async def test_c11_same_key_other_content_is_rejected(self, env: CompatEnv) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `env` | `CompatEnv` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.compat.suite.AdapterCompatSuite.test_c12_raw_html_round_trip

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:545](../../../../../../services/storage/src/jane_storage/compat/suite.py#L545).

```python
async def test_c12_raw_html_round_trip(self, env: CompatEnv) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `env` | `CompatEnv` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.compat.suite.AdapterCompatSuite.test_c13_entities_are_json_documents

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:602](../../../../../../services/storage/src/jane_storage/compat/suite.py#L602).

```python
async def test_c13_entities_are_json_documents(self, env: CompatEnv) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `env` | `CompatEnv` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.compat.suite.AdapterCompatSuite.test_c14_unicode_and_long_keys

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:639](../../../../../../services/storage/src/jane_storage/compat/suite.py#L639).

```python
async def test_c14_unicode_and_long_keys(self, env: CompatEnv) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `env` | `CompatEnv` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.compat.suite.AdapterCompatSuite.test_c15_pagination

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:665](../../../../../../services/storage/src/jane_storage/compat/suite.py#L665).

```python
async def test_c15_pagination(self, env: CompatEnv) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `env` | `CompatEnv` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.compat.suite.AdapterCompatSuite.test_c16_unavailable_storage

**Метод.** Код: [services/storage/src/jane_storage/compat/suite.py:707](../../../../../../services/storage/src/jane_storage/compat/suite.py#L707).

```python
async def test_c16_unavailable_storage(self, env: CompatEnv) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `env` | `CompatEnv` | `—` | positional-or-keyword |

Результат: `None`.
