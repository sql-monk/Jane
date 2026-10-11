# Модуль `jane_storage.compat.suite`

> Згенеровано `scripts/docs_reference.py` з [services/storage/src/jane_storage/compat/suite.py](../../../../../services/storage/src/jane_storage/compat/suite.py). Не редагуйте вручну.

Scenarios C-01…C-16 as a pytest base class (see :mod:`jane_storage.compat`).

## Класи

### Клас `AdapterCompatSuite`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage.compat.suite` |
| Код | [suite.py:273](../../../../../services/storage/src/jane_storage/compat/suite.py#L273) |

```python
class AdapterCompatSuite: ...
```

Base class; subclasses provide the ``compat_target`` fixture. Test names carry the scenario id.

#### Метод `AdapterCompatSuite.compat_target`

```python
@pytest.fixture
def compat_target(self) -> CompatTarget: ...
```

Винятки в коді методу: `NotImplementedError`.

Код: [suite.py:277](../../../../../services/storage/src/jane_storage/compat/suite.py#L277).

#### Метод `AdapterCompatSuite.env`

```python
@pytest.fixture
async def env(self, compat_target: CompatTarget) -> AsyncIterator[CompatEnv]: ...
```

Код: [suite.py:281](../../../../../services/storage/src/jane_storage/compat/suite.py#L281).

#### Метод `AdapterCompatSuite.test_registered_with_required_capabilities`

```python
async def test_registered_with_required_capabilities(self, env: CompatEnv) -> None: ...
```

Код: [suite.py:289](../../../../../services/storage/src/jane_storage/compat/suite.py#L289).

#### Метод `AdapterCompatSuite.test_c01_new_entity`

```python
async def test_c01_new_entity(self, env: CompatEnv) -> None: ...
```

Код: [suite.py:300](../../../../../services/storage/src/jane_storage/compat/suite.py#L300).

#### Метод `AdapterCompatSuite.test_c02_redelivery_after_restart_is_duplicate`

```python
async def test_c02_redelivery_after_restart_is_duplicate(self, env: CompatEnv) -> None: ...
```

Код: [suite.py:331](../../../../../services/storage/src/jane_storage/compat/suite.py#L331).

#### Метод `AdapterCompatSuite.test_c03_new_observation_updates`

```python
async def test_c03_new_observation_updates(self, env: CompatEnv) -> None: ...
```

Код: [suite.py:358](../../../../../services/storage/src/jane_storage/compat/suite.py#L358).

#### Метод `AdapterCompatSuite.test_c04_partial_update_keeps_other_fields`

```python
async def test_c04_partial_update_keeps_other_fields(self, env: CompatEnv) -> None: ...
```

Код: [suite.py:374](../../../../../services/storage/src/jane_storage/compat/suite.py#L374).

#### Метод `AdapterCompatSuite.test_c05_explicit_clear`

```python
async def test_c05_explicit_clear(self, env: CompatEnv) -> None: ...
```

Код: [suite.py:388](../../../../../services/storage/src/jane_storage/compat/suite.py#L388).

#### Метод `AdapterCompatSuite.test_c06_late_observation_is_stale`

```python
async def test_c06_late_observation_is_stale(self, env: CompatEnv) -> None: ...
```

Код: [suite.py:410](../../../../../services/storage/src/jane_storage/compat/suite.py#L410).

#### Метод `AdapterCompatSuite.test_c07_mixed_partially_stale`

```python
async def test_c07_mixed_partially_stale(self, env: CompatEnv) -> None: ...
```

Код: [suite.py:433](../../../../../services/storage/src/jane_storage/compat/suite.py#L433).

#### Метод `AdapterCompatSuite.test_c08_same_time_higher_sequence_wins`

```python
async def test_c08_same_time_higher_sequence_wins(self, env: CompatEnv) -> None: ...
```

Код: [suite.py:449](../../../../../services/storage/src/jane_storage/compat/suite.py#L449).

#### Метод `AdapterCompatSuite.test_c09_concurrent_commits`

```python
async def test_c09_concurrent_commits(self, env: CompatEnv) -> None: ...
```

Код: [suite.py:466](../../../../../services/storage/src/jane_storage/compat/suite.py#L466).

#### Метод `AdapterCompatSuite.test_c10_put_object_is_idempotent`

```python
async def test_c10_put_object_is_idempotent(self, env: CompatEnv) -> None: ...
```

Код: [suite.py:504](../../../../../services/storage/src/jane_storage/compat/suite.py#L504).

#### Метод `AdapterCompatSuite.test_c11_same_key_other_content_is_rejected`

```python
async def test_c11_same_key_other_content_is_rejected(self, env: CompatEnv) -> None: ...
```

Код: [suite.py:533](../../../../../services/storage/src/jane_storage/compat/suite.py#L533).

#### Метод `AdapterCompatSuite.test_c12_raw_html_round_trip`

```python
async def test_c12_raw_html_round_trip(self, env: CompatEnv) -> None: ...
```

Код: [suite.py:545](../../../../../services/storage/src/jane_storage/compat/suite.py#L545).

#### Метод `AdapterCompatSuite.test_c13_entities_are_json_documents`

```python
async def test_c13_entities_are_json_documents(self, env: CompatEnv) -> None: ...
```

Код: [suite.py:602](../../../../../services/storage/src/jane_storage/compat/suite.py#L602).

#### Метод `AdapterCompatSuite.test_c14_unicode_and_long_keys`

```python
async def test_c14_unicode_and_long_keys(self, env: CompatEnv) -> None: ...
```

Код: [suite.py:639](../../../../../services/storage/src/jane_storage/compat/suite.py#L639).

#### Метод `AdapterCompatSuite.test_c15_pagination`

```python
async def test_c15_pagination(self, env: CompatEnv) -> None: ...
```

Код: [suite.py:665](../../../../../services/storage/src/jane_storage/compat/suite.py#L665).

#### Метод `AdapterCompatSuite.test_c16_unavailable_storage`

```python
async def test_c16_unavailable_storage(self, env: CompatEnv) -> None: ...
```

Код: [suite.py:707](../../../../../services/storage/src/jane_storage/compat/suite.py#L707).

### Клас `CompatEnv`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage.compat.suite` |
| Код | [suite.py:160](../../../../../services/storage/src/jane_storage/compat/suite.py#L160) |

```python
class CompatEnv: ...
```

Opened adapters, engines and the handler over one :class:`CompatTarget`.

#### Конструктор `CompatEnv.__init__`

```python
def __init__(self, target: CompatTarget) -> None: ...
```

Код: [suite.py:163](../../../../../services/storage/src/jane_storage/compat/suite.py#L163).

#### Метод `CompatEnv.adapter`

```python
async def adapter(
    self,
    *,
    connection: ResolvedConnection | None = None,
    **options: Any,
) -> StorageAdapter: ...
```

Код: [suite.py:167](../../../../../services/storage/src/jane_storage/compat/suite.py#L167).

#### Метод `CompatEnv.restart`

```python
async def restart(self, adapter: StorageAdapter, **options: Any) -> StorageAdapter: ...
```

Код: [suite.py:176](../../../../../services/storage/src/jane_storage/compat/suite.py#L176).

#### Метод `CompatEnv.engine`

```python
def engine(self, adapter: StorageAdapter) -> StorageEngine: ...
```

Код: [suite.py:181](../../../../../services/storage/src/jane_storage/compat/suite.py#L181).

#### Метод `CompatEnv.package`

```python
def package(self) -> StoragePackage: ...
```

Винятки в коді методу: `AssertionError`.

Код: [suite.py:186](../../../../../services/storage/src/jane_storage/compat/suite.py#L186).

#### Метод `CompatEnv.handler`

```python
def handler(self, connection: ResolvedConnection) -> tuple[StorageHandler, AdapterPool]: ...
```

Код: [suite.py:196](../../../../../services/storage/src/jane_storage/compat/suite.py#L196).

#### Метод `CompatEnv.close`

```python
async def close(self) -> None: ...
```

Код: [suite.py:204](../../../../../services/storage/src/jane_storage/compat/suite.py#L204).

### Клас `CompatTarget`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage.compat.suite` |
| Успадкування | `ABC` |
| Код | [suite.py:121](../../../../../services/storage/src/jane_storage/compat/suite.py#L121) |

```python
class CompatTarget(ABC): ...
```

What an adapter package provides to the suite. One instance = one isolated namespace.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `kind` | `ClassVar[str]` | — | читання |  |
| `entity_formats` | `ClassVar[tuple[str, ...]]` | `('json',)` | читання | Values of ``options["entities_format"]`` the adapter supports (filesystem: json and jsonl). |

#### Метод `CompatTarget.connection`

```python
@abstractmethod
def connection(self) -> ResolvedConnection: ...
```

Connection to an empty namespace of a reachable storage (same one on every call).

Код: [suite.py:129](../../../../../services/storage/src/jane_storage/compat/suite.py#L129).

#### Метод `CompatTarget.unavailable_connection`

```python
@abstractmethod
def unavailable_connection(self) -> ResolvedConnection: ...
```

Connection of the same kind whose storage is not reachable (C-16).

Код: [suite.py:133](../../../../../services/storage/src/jane_storage/compat/suite.py#L133).

#### Метод `CompatTarget.options`

```python
def options(self) -> dict[str, Any]: ...
```

Base ``adapter.open`` options (e.g. prefix); the suite adds ``entities_format``.

Код: [suite.py:136](../../../../../services/storage/src/jane_storage/compat/suite.py#L136).

#### Метод `CompatTarget.cleanup`

```python
async def cleanup(self) -> None: ...
```

Drop the namespace after the test (optional).

Код: [suite.py:140](../../../../../services/storage/src/jane_storage/compat/suite.py#L140).

#### Метод `CompatTarget.native_object_path`

```python
async def native_object_path(self, rec: ObjectRecord) -> str | None: ...
```

Adapter-native name of a stored object (filesystem: relative path) — C-12; None if n/a.

Код: [suite.py:143](../../../../../services/storage/src/jane_storage/compat/suite.py#L143).

#### Метод `CompatTarget.native_entity_document`

```python
async def native_entity_document(
    self,
    entity_type: str,
    canonical_key: str,
    options: Mapping[str, Any],
) -> Any | None: ...
```

The stored entity document as the adapter keeps it (parsed JSON) — C-13; None if n/a.

Код: [suite.py:147](../../../../../services/storage/src/jane_storage/compat/suite.py#L147).

#### Метод `CompatTarget.native_history_documents`

```python
async def native_history_documents(
    self,
    entity_type: str,
    canonical_key: str,
    options: Mapping[str, Any],
) -> list[Any] | None: ...
```

Stored history documents in the adapter's native layout — C-13 format override; None if n/a.

Код: [suite.py:153](../../../../../services/storage/src/jane_storage/compat/suite.py#L153).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `SCENARIOS` | — | `{'C-01': 'new entity', 'C-02': 'repeated delivery after adapter restart', 'C-03'` |  |
