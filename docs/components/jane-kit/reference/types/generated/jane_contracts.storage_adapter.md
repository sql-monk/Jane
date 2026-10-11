# jane_contracts.storage_adapter

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_contracts.storage_adapter.RawFormat](#jane_contractsstorage_adapterrawformat)
- [jane_contracts.storage_adapter.ResolvedConnection](#jane_contractsstorage_adapterresolvedconnection)
- [jane_contracts.storage_adapter.ResolvedConnection.__init__](#jane_contractsstorage_adapterresolvedconnection__init__)
- [jane_contracts.storage_adapter.ResolvedConnection.connection_id](#jane_contractsstorage_adapterresolvedconnectionconnection_id)
- [jane_contracts.storage_adapter.ResolvedConnection.kind](#jane_contractsstorage_adapterresolvedconnectionkind)
- [jane_contracts.storage_adapter.ResolvedConnection.params](#jane_contractsstorage_adapterresolvedconnectionparams)
- [jane_contracts.storage_adapter.ResolvedConnection.secrets](#jane_contractsstorage_adapterresolvedconnectionsecrets)
- [jane_contracts.storage_adapter.OrderKey](#jane_contractsstorage_adapterorderkey)
- [jane_contracts.storage_adapter.OrderKey.__init__](#jane_contractsstorage_adapterorderkey__init__)
- [jane_contracts.storage_adapter.OrderKey.observed_at](#jane_contractsstorage_adapterorderkeyobserved_at)
- [jane_contracts.storage_adapter.OrderKey.observation_id](#jane_contractsstorage_adapterorderkeyobservation_id)
- [jane_contracts.storage_adapter.OrderKey.sequence](#jane_contractsstorage_adapterorderkeysequence)
- [jane_contracts.storage_adapter.order_tuple](#jane_contractsstorage_adapterorder_tuple)
- [jane_contracts.storage_adapter.RawObject](#jane_contractsstorage_adapterrawobject)
- [jane_contracts.storage_adapter.RawObject.__init__](#jane_contractsstorage_adapterrawobject__init__)
- [jane_contracts.storage_adapter.RawObject.object_key](#jane_contractsstorage_adapterrawobjectobject_key)
- [jane_contracts.storage_adapter.RawObject.material_id](#jane_contractsstorage_adapterrawobjectmaterial_id)
- [jane_contracts.storage_adapter.RawObject.observation_id](#jane_contractsstorage_adapterrawobjectobservation_id)
- [jane_contracts.storage_adapter.RawObject.source_id](#jane_contractsstorage_adapterrawobjectsource_id)
- [jane_contracts.storage_adapter.RawObject.media_type](#jane_contractsstorage_adapterrawobjectmedia_type)
- [jane_contracts.storage_adapter.RawObject.format](#jane_contractsstorage_adapterrawobjectformat)
- [jane_contracts.storage_adapter.RawObject.content](#jane_contractsstorage_adapterrawobjectcontent)
- [jane_contracts.storage_adapter.RawObject.sha256](#jane_contractsstorage_adapterrawobjectsha256)
- [jane_contracts.storage_adapter.RawObject.metadata](#jane_contractsstorage_adapterrawobjectmetadata)
- [jane_contracts.storage_adapter.ObjectRecord](#jane_contractsstorage_adapterobjectrecord)
- [jane_contracts.storage_adapter.ObjectRecord.__init__](#jane_contractsstorage_adapterobjectrecord__init__)
- [jane_contracts.storage_adapter.ObjectRecord.object_id](#jane_contractsstorage_adapterobjectrecordobject_id)
- [jane_contracts.storage_adapter.ObjectRecord.object_key](#jane_contractsstorage_adapterobjectrecordobject_key)
- [jane_contracts.storage_adapter.ObjectRecord.locator](#jane_contractsstorage_adapterobjectrecordlocator)
- [jane_contracts.storage_adapter.ObjectRecord.media_type](#jane_contractsstorage_adapterobjectrecordmedia_type)
- [jane_contracts.storage_adapter.ObjectRecord.size_bytes](#jane_contractsstorage_adapterobjectrecordsize_bytes)
- [jane_contracts.storage_adapter.ObjectRecord.sha256](#jane_contractsstorage_adapterobjectrecordsha256)
- [jane_contracts.storage_adapter.ObjectRecord.stored_at](#jane_contractsstorage_adapterobjectrecordstored_at)
- [jane_contracts.storage_adapter.ObjectRecord.metadata](#jane_contractsstorage_adapterobjectrecordmetadata)
- [jane_contracts.storage_adapter.EntitySnapshot](#jane_contractsstorage_adapterentitysnapshot)
- [jane_contracts.storage_adapter.EntitySnapshot.__init__](#jane_contractsstorage_adapterentitysnapshot__init__)
- [jane_contracts.storage_adapter.EntitySnapshot.entity_type](#jane_contractsstorage_adapterentitysnapshotentity_type)
- [jane_contracts.storage_adapter.EntitySnapshot.canonical_key](#jane_contractsstorage_adapterentitysnapshotcanonical_key)
- [jane_contracts.storage_adapter.EntitySnapshot.key](#jane_contractsstorage_adapterentitysnapshotkey)
- [jane_contracts.storage_adapter.EntitySnapshot.fields](#jane_contractsstorage_adapterentitysnapshotfields)
- [jane_contracts.storage_adapter.EntitySnapshot.field_orders](#jane_contractsstorage_adapterentitysnapshotfield_orders)
- [jane_contracts.storage_adapter.EntitySnapshot.cleared_fields](#jane_contractsstorage_adapterentitysnapshotcleared_fields)
- [jane_contracts.storage_adapter.EntitySnapshot.version](#jane_contractsstorage_adapterentitysnapshotversion)
- [jane_contracts.storage_adapter.EntitySnapshot.updated_at](#jane_contractsstorage_adapterentitysnapshotupdated_at)
- [jane_contracts.storage_adapter.HistoryEvent](#jane_contractsstorage_adapterhistoryevent)
- [jane_contracts.storage_adapter.HistoryEvent.__init__](#jane_contractsstorage_adapterhistoryevent__init__)
- [jane_contracts.storage_adapter.HistoryEvent.entity_type](#jane_contractsstorage_adapterhistoryevententity_type)
- [jane_contracts.storage_adapter.HistoryEvent.canonical_key](#jane_contractsstorage_adapterhistoryeventcanonical_key)
- [jane_contracts.storage_adapter.HistoryEvent.record](#jane_contractsstorage_adapterhistoryeventrecord)
- [jane_contracts.storage_adapter.HistoryEvent.delivery_key](#jane_contractsstorage_adapterhistoryeventdelivery_key)
- [jane_contracts.storage_adapter.HistoryEvent.received_at](#jane_contractsstorage_adapterhistoryeventreceived_at)
- [jane_contracts.storage_adapter.HistoryEvent.applied_fields](#jane_contractsstorage_adapterhistoryeventapplied_fields)
- [jane_contracts.storage_adapter.HistoryEvent.stale_fields](#jane_contractsstorage_adapterhistoryeventstale_fields)
- [jane_contracts.storage_adapter.DeliveryRecord](#jane_contractsstorage_adapterdeliveryrecord)
- [jane_contracts.storage_adapter.DeliveryRecord.__init__](#jane_contractsstorage_adapterdeliveryrecord__init__)
- [jane_contracts.storage_adapter.DeliveryRecord.delivery_key](#jane_contractsstorage_adapterdeliveryrecorddelivery_key)
- [jane_contracts.storage_adapter.DeliveryRecord.recorded_at](#jane_contractsstorage_adapterdeliveryrecordrecorded_at)
- [jane_contracts.storage_adapter.DeliveryRecord.acks](#jane_contractsstorage_adapterdeliveryrecordacks)
- [jane_contracts.storage_adapter.CommitOutcome](#jane_contractsstorage_adaptercommitoutcome)
- [jane_contracts.storage_adapter.CommitOutcome.COMMITTED](#jane_contractsstorage_adaptercommitoutcomecommitted)
- [jane_contracts.storage_adapter.CommitOutcome.CONFLICT](#jane_contractsstorage_adaptercommitoutcomeconflict)
- [jane_contracts.storage_adapter.CommitOutcome.DUPLICATE](#jane_contractsstorage_adaptercommitoutcomeduplicate)
- [jane_contracts.storage_adapter.CommitResult](#jane_contractsstorage_adaptercommitresult)
- [jane_contracts.storage_adapter.CommitResult.__init__](#jane_contractsstorage_adaptercommitresult__init__)
- [jane_contracts.storage_adapter.CommitResult.outcome](#jane_contractsstorage_adaptercommitresultoutcome)
- [jane_contracts.storage_adapter.CommitResult.snapshot](#jane_contractsstorage_adaptercommitresultsnapshot)
- [jane_contracts.storage_adapter.AdapterError](#jane_contractsstorage_adapteradaptererror)
- [jane_contracts.storage_adapter.AdapterError.__init__](#jane_contractsstorage_adapteradaptererror__init__)
- [jane_contracts.storage_adapter.AdapterError.retryable](#jane_contractsstorage_adapteradaptererrorretryable)
- [jane_contracts.storage_adapter.StorageAdapter](#jane_contractsstorage_adapterstorageadapter)
- [jane_contracts.storage_adapter.StorageAdapter.kind](#jane_contractsstorage_adapterstorageadapterkind)
- [jane_contracts.storage_adapter.StorageAdapter.capabilities](#jane_contractsstorage_adapterstorageadaptercapabilities)
- [jane_contracts.storage_adapter.StorageAdapter.open](#jane_contractsstorage_adapterstorageadapteropen)
- [jane_contracts.storage_adapter.StorageAdapter.close](#jane_contractsstorage_adapterstorageadapterclose)
- [jane_contracts.storage_adapter.StorageAdapter.health](#jane_contractsstorage_adapterstorageadapterhealth)
- [jane_contracts.storage_adapter.StorageAdapter.ensure_schema](#jane_contractsstorage_adapterstorageadapterensure_schema)
- [jane_contracts.storage_adapter.StorageAdapter.put_object](#jane_contractsstorage_adapterstorageadapterput_object)
- [jane_contracts.storage_adapter.StorageAdapter.get_object](#jane_contractsstorage_adapterstorageadapterget_object)
- [jane_contracts.storage_adapter.StorageAdapter.read_object_content](#jane_contractsstorage_adapterstorageadapterread_object_content)
- [jane_contracts.storage_adapter.StorageAdapter.list_objects](#jane_contractsstorage_adapterstorageadapterlist_objects)
- [jane_contracts.storage_adapter.StorageAdapter.read_entity](#jane_contractsstorage_adapterstorageadapterread_entity)
- [jane_contracts.storage_adapter.StorageAdapter.commit_entity](#jane_contractsstorage_adapterstorageadaptercommit_entity)
- [jane_contracts.storage_adapter.StorageAdapter.list_entities](#jane_contractsstorage_adapterstorageadapterlist_entities)
- [jane_contracts.storage_adapter.StorageAdapter.list_history](#jane_contractsstorage_adapterstorageadapterlist_history)
- [jane_contracts.storage_adapter.StorageAdapter.get_delivery](#jane_contractsstorage_adapterstorageadapterget_delivery)
- [jane_contracts.storage_adapter.StorageAdapter.record_delivery](#jane_contractsstorage_adapterstorageadapterrecord_delivery)

## jane_contracts.storage_adapter.RawFormat

**Змінна.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:29](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L29).

```python
RawFormat = Literal['original', 'html', 'json']
```

## jane_contracts.storage_adapter.ResolvedConnection

**Клас.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:33](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L33).

```python
class ResolvedConnection:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [connection_id](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterresolvedconnectionconnection_id) | Поле | ні |
| [kind](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterresolvedconnectionkind) | Поле | ні |
| [params](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterresolvedconnectionparams) | Поле | ні |
| [secrets](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterresolvedconnectionsecrets) | Поле | ні |
| [__init__](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterresolvedconnection__init__) | Конструктор dataclass | ні |

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/files/tests/test_compat.py:25](../../../../../../services/storage/adapters/files/tests/test_compat.py#L25).

```python
return ResolvedConnection(
            connection_id="compat-files", kind="filesystem", params={"base_path": str(self.base / "store")}
        )
```

Контекст і передумови: [services/storage/adapters/files/tests/test_compat.py:32](../../../../../../services/storage/adapters/files/tests/test_compat.py#L32).

```python
return ResolvedConnection(
            connection_id="compat-files-down", kind="filesystem", params={"base_path": str(blocker / "store")}
        )
```

## jane_contracts.storage_adapter.ResolvedConnection.__init__

**Конструктор dataclass.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:33](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L33).

```python
def __init__(self, connection_id: str, kind: str, params: Mapping[str, Any], secrets: Mapping[str, str] = <factory dict>) -> None:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `connection_id` | `str` | `—` | positional-or-keyword |
| `kind` | `str` | `—` | positional-or-keyword |
| `params` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `secrets` | `Mapping[str, str]` | `factory: dict` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/files/tests/test_compat.py:25](../../../../../../services/storage/adapters/files/tests/test_compat.py#L25).

```python
return ResolvedConnection(
            connection_id="compat-files", kind="filesystem", params={"base_path": str(self.base / "store")}
        )
```

Контекст і передумови: [services/storage/adapters/files/tests/test_compat.py:32](../../../../../../services/storage/adapters/files/tests/test_compat.py#L32).

```python
return ResolvedConnection(
            connection_id="compat-files-down", kind="filesystem", params={"base_path": str(blocker / "store")}
        )
```

## jane_contracts.storage_adapter.ResolvedConnection.connection_id

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:34](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L34).

```python
connection_id: str
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.ResolvedConnection.kind

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:35](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L35).

```python
kind: str
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.ResolvedConnection.params

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:36](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L36).

```python
params: Mapping[str, Any]
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.ResolvedConnection.secrets

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:37](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L37).

```python
secrets: Mapping[str, str] = field(repr=False, default_factory=dict)
```

Доступ: читання — так; запис — ні.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict",
  "repr": "False"
}
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_secret_policy.py:411](../../../../../../services/storage/tests/test_secret_policy.py#L411).

```python
secrets = connection.secrets
```

## jane_contracts.storage_adapter.OrderKey

**Клас.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:41](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L41).

```python
class OrderKey:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [observed_at](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterorderkeyobserved_at) | Поле | ні |
| [observation_id](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterorderkeyobservation_id) | Поле | ні |
| [sequence](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterorderkeysequence) | Поле | ні |
| [__init__](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterorderkey__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
Observation order (entity.schema.json#/$defs/ObservationOrder). Compare with :func:`order_tuple`.
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_core.py:115](../../../../../../services/storage/tests/test_core.py#L115).

```python
order = OrderKey(observed_at=NOW, observation_id="x", sequence=None)
```

## jane_contracts.storage_adapter.OrderKey.__init__

**Конструктор dataclass.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:41](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L41).

```python
def __init__(self, observed_at: datetime, observation_id: str, sequence: int | None = None) -> None:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `observed_at` | `datetime` | `—` | positional-or-keyword |
| `observation_id` | `str` | `—` | positional-or-keyword |
| `sequence` | `int \| None` | `None` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_core.py:115](../../../../../../services/storage/tests/test_core.py#L115).

```python
order = OrderKey(observed_at=NOW, observation_id="x", sequence=None)
```

## jane_contracts.storage_adapter.OrderKey.observed_at

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:44](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L44).

```python
observed_at: datetime
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.OrderKey.observation_id

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:45](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L45).

```python
observation_id: str
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.OrderKey.sequence

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:46](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L46).

```python
sequence: int | None = None
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.order_tuple

**Функція.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:49](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L49).

```python
def order_tuple(key: OrderKey) -> tuple[datetime, int, str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `key` | `OrderKey` | `—` | positional-or-keyword |

Результат: `tuple[datetime, int, str]`.

### Опис із вихідного коду

```text
Total order used by the core: observed_at, then sequence (missing = -1), then observation_id.
```

## jane_contracts.storage_adapter.RawObject

**Клас.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:55](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L55).

```python
class RawObject:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [object_key](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterrawobjectobject_key) | Поле | ні |
| [material_id](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterrawobjectmaterial_id) | Поле | ні |
| [observation_id](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterrawobjectobservation_id) | Поле | ні |
| [source_id](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterrawobjectsource_id) | Поле | ні |
| [media_type](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterrawobjectmedia_type) | Поле | ні |
| [format](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterrawobjectformat) | Поле | ні |
| [content](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterrawobjectcontent) | Поле | ні |
| [sha256](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterrawobjectsha256) | Поле | ні |
| [metadata](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterrawobjectmetadata) | Поле | ні |
| [__init__](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterrawobject__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
A material (RAW) or result document to persist as an object.
```

## jane_contracts.storage_adapter.RawObject.__init__

**Конструктор dataclass.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:55](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L55).

```python
def __init__(self, object_key: str, material_id: str, observation_id: str, source_id: str | None, media_type: str, format: RawFormat, content: bytes, sha256: str, metadata: Mapping[str, Any] = <factory dict>) -> None:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `object_key` | `str` | `—` | positional-or-keyword |
| `material_id` | `str` | `—` | positional-or-keyword |
| `observation_id` | `str` | `—` | positional-or-keyword |
| `source_id` | `str \| None` | `—` | positional-or-keyword |
| `media_type` | `str` | `—` | positional-or-keyword |
| `format` | `RawFormat` | `—` | positional-or-keyword |
| `content` | `bytes` | `—` | positional-or-keyword |
| `sha256` | `str` | `—` | positional-or-keyword |
| `metadata` | `Mapping[str, Any]` | `factory: dict` | positional-or-keyword |

Результат: `None`.

## jane_contracts.storage_adapter.RawObject.object_key

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:58](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L58).

```python
object_key: str
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
Deterministic key built by the core: ``<source_id>/<yyyy>/<mm>/<dd>/<material_id>/<observation_id>.<ext>``
    (filesystem-safe: ':' replaced by '_'). Same key + same sha256 = same object.
```

## jane_contracts.storage_adapter.RawObject.material_id

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:61](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L61).

```python
material_id: str
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.RawObject.observation_id

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:62](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L62).

```python
observation_id: str
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.RawObject.source_id

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:63](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L63).

```python
source_id: str | None
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.RawObject.media_type

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:64](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L64).

```python
media_type: str
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.RawObject.format

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:65](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L65).

```python
format: RawFormat
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.RawObject.content

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:66](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L66).

```python
content: bytes
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.RawObject.sha256

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:67](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L67).

```python
sha256: str
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.RawObject.metadata

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:68](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L68).

```python
metadata: Mapping[str, Any] = field(default_factory=dict)
```

Доступ: читання — так; запис — ні.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

### Опис із вихідного коду

```text
Material without content (JSON-compatible), stored next to the object for reprocessing.
```

## jane_contracts.storage_adapter.ObjectRecord

**Клас.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:73](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L73).

```python
class ObjectRecord:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [object_id](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterobjectrecordobject_id) | Поле | ні |
| [object_key](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterobjectrecordobject_key) | Поле | ні |
| [locator](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterobjectrecordlocator) | Поле | ні |
| [media_type](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterobjectrecordmedia_type) | Поле | ні |
| [size_bytes](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterobjectrecordsize_bytes) | Поле | ні |
| [sha256](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterobjectrecordsha256) | Поле | ні |
| [stored_at](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterobjectrecordstored_at) | Поле | ні |
| [metadata](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterobjectrecordmetadata) | Поле | ні |
| [__init__](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterobjectrecord__init__) | Конструктор dataclass | ні |

## jane_contracts.storage_adapter.ObjectRecord.__init__

**Конструктор dataclass.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:73](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L73).

```python
def __init__(self, object_id: str, object_key: str, locator: Mapping[str, str | int], media_type: str, size_bytes: int, sha256: str, stored_at: datetime, metadata: Mapping[str, Any] = <factory dict>) -> None:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `object_id` | `str` | `—` | positional-or-keyword |
| `object_key` | `str` | `—` | positional-or-keyword |
| `locator` | `Mapping[str, str \| int]` | `—` | positional-or-keyword |
| `media_type` | `str` | `—` | positional-or-keyword |
| `size_bytes` | `int` | `—` | positional-or-keyword |
| `sha256` | `str` | `—` | positional-or-keyword |
| `stored_at` | `datetime` | `—` | positional-or-keyword |
| `metadata` | `Mapping[str, Any]` | `factory: dict` | positional-or-keyword |

Результат: `None`.

## jane_contracts.storage_adapter.ObjectRecord.object_id

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:74](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L74).

```python
object_id: str
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.ObjectRecord.object_key

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:75](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L75).

```python
object_key: str
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.ObjectRecord.locator

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:76](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L76).

```python
locator: Mapping[str, str | int]
```

Доступ: читання — так; запис — ні.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/files/tests/test_compat.py:43](../../../../../../services/storage/adapters/files/tests/test_compat.py#L43).

```python
path = self.base / "store" / str(rec.locator["path"])
```

Контекст і передумови: [services/storage/adapters/minio/tests/test_compat.py:74](../../../../../../services/storage/adapters/minio/tests/test_compat.py#L74).

```python
key = str(rec.locator["key"])
```

## jane_contracts.storage_adapter.ObjectRecord.media_type

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:77](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L77).

```python
media_type: str
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.ObjectRecord.size_bytes

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:78](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L78).

```python
size_bytes: int
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.ObjectRecord.sha256

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:79](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L79).

```python
sha256: str
```

Доступ: читання — так; запис — ні.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/minio/tests/test_compat.py:76](../../../../../../services/storage/adapters/minio/tests/test_compat.py#L76).

```python
assert head["Metadata"]["sha256"] == rec.sha256
```

Контекст і передумови: [services/storage/adapters/s3/tests/test_compat.py:81](../../../../../../services/storage/adapters/s3/tests/test_compat.py#L81).

```python
assert head["Metadata"]["sha256"] == rec.sha256
```

## jane_contracts.storage_adapter.ObjectRecord.stored_at

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:80](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L80).

```python
stored_at: datetime
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.ObjectRecord.metadata

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:81](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L81).

```python
metadata: Mapping[str, Any] = field(default_factory=dict)
```

Доступ: читання — так; запис — ні.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## jane_contracts.storage_adapter.EntitySnapshot

**Клас.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:85](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L85).

```python
class EntitySnapshot:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [entity_type](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterentitysnapshotentity_type) | Поле | ні |
| [canonical_key](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterentitysnapshotcanonical_key) | Поле | ні |
| [key](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterentitysnapshotkey) | Поле | ні |
| [fields](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterentitysnapshotfields) | Поле | ні |
| [field_orders](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterentitysnapshotfield_orders) | Поле | ні |
| [cleared_fields](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterentitysnapshotcleared_fields) | Поле | ні |
| [version](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterentitysnapshotversion) | Поле | ні |
| [updated_at](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterentitysnapshotupdated_at) | Поле | ні |
| [__init__](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterentitysnapshot__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
Current state of one entity (entity.schema.json#/$defs/EntityState).
```

## jane_contracts.storage_adapter.EntitySnapshot.__init__

**Конструктор dataclass.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:85](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L85).

```python
def __init__(self, entity_type: str, canonical_key: str, key: Mapping[str, Any], fields: Mapping[str, Any], field_orders: Mapping[str, OrderKey], cleared_fields: frozenset[str], version: int, updated_at: datetime) -> None:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `entity_type` | `str` | `—` | positional-or-keyword |
| `canonical_key` | `str` | `—` | positional-or-keyword |
| `key` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `fields` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `field_orders` | `Mapping[str, OrderKey]` | `—` | positional-or-keyword |
| `cleared_fields` | `frozenset[str]` | `—` | positional-or-keyword |
| `version` | `int` | `—` | positional-or-keyword |
| `updated_at` | `datetime` | `—` | positional-or-keyword |

Результат: `None`.

## jane_contracts.storage_adapter.EntitySnapshot.entity_type

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:88](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L88).

```python
entity_type: str
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.EntitySnapshot.canonical_key

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:89](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L89).

```python
canonical_key: str
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.EntitySnapshot.key

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:90](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L90).

```python
key: Mapping[str, Any]
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.EntitySnapshot.fields

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:91](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L91).

```python
fields: Mapping[str, Any]
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.EntitySnapshot.field_orders

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:92](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L92).

```python
field_orders: Mapping[str, OrderKey]
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.EntitySnapshot.cleared_fields

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:93](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L93).

```python
cleared_fields: frozenset[str]
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.EntitySnapshot.version

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:94](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L94).

```python
version: int
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.EntitySnapshot.updated_at

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:95](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L95).

```python
updated_at: datetime
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.HistoryEvent

**Клас.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:99](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L99).

```python
class HistoryEvent:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [entity_type](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterhistoryevententity_type) | Поле | ні |
| [canonical_key](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterhistoryeventcanonical_key) | Поле | ні |
| [record](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterhistoryeventrecord) | Поле | ні |
| [delivery_key](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterhistoryeventdelivery_key) | Поле | ні |
| [received_at](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterhistoryeventreceived_at) | Поле | ні |
| [applied_fields](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterhistoryeventapplied_fields) | Поле | ні |
| [stale_fields](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterhistoryeventstale_fields) | Поле | ні |
| [__init__](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterhistoryevent__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
One accepted update (also stale ones) — entity.schema.json#/$defs/EntityHistoryEntry.
```

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/mongodb/tests/test_recovery.py:138](../../../../../../services/storage/adapters/mongodb/tests/test_recovery.py#L138).

```python
event = HistoryEvent("product", key, rec, "K#0", datetime.now(UTC), merged.applied, [])
```

Контекст і передумови: [services/storage/adapters/s3/tests/test_recovery.py:130](../../../../../../services/storage/adapters/s3/tests/test_recovery.py#L130).

```python
return HistoryEvent("product", KEY, rec, delivery_key, datetime.now(UTC), applied, [])
```

## jane_contracts.storage_adapter.HistoryEvent.__init__

**Конструктор dataclass.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:99](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L99).

```python
def __init__(self, entity_type: str, canonical_key: str, record: Mapping[str, Any], delivery_key: str, received_at: datetime, applied_fields: Sequence[str], stale_fields: Sequence[str]) -> None:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `entity_type` | `str` | `—` | positional-or-keyword |
| `canonical_key` | `str` | `—` | positional-or-keyword |
| `record` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `delivery_key` | `str` | `—` | positional-or-keyword |
| `received_at` | `datetime` | `—` | positional-or-keyword |
| `applied_fields` | `Sequence[str]` | `—` | positional-or-keyword |
| `stale_fields` | `Sequence[str]` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/mongodb/tests/test_recovery.py:138](../../../../../../services/storage/adapters/mongodb/tests/test_recovery.py#L138).

```python
event = HistoryEvent("product", key, rec, "K#0", datetime.now(UTC), merged.applied, [])
```

Контекст і передумови: [services/storage/adapters/s3/tests/test_recovery.py:130](../../../../../../services/storage/adapters/s3/tests/test_recovery.py#L130).

```python
return HistoryEvent("product", KEY, rec, delivery_key, datetime.now(UTC), applied, [])
```

## jane_contracts.storage_adapter.HistoryEvent.entity_type

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:102](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L102).

```python
entity_type: str
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.HistoryEvent.canonical_key

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:103](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L103).

```python
canonical_key: str
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.HistoryEvent.record

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:104](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L104).

```python
record: Mapping[str, Any]
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.HistoryEvent.delivery_key

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:105](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L105).

```python
delivery_key: str
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.HistoryEvent.received_at

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:106](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L106).

```python
received_at: datetime
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.HistoryEvent.applied_fields

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:107](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L107).

```python
applied_fields: Sequence[str]
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.HistoryEvent.stale_fields

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:108](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L108).

```python
stale_fields: Sequence[str]
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.DeliveryRecord

**Клас.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:112](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L112).

```python
class DeliveryRecord:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [delivery_key](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterdeliveryrecorddelivery_key) | Поле | ні |
| [recorded_at](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterdeliveryrecordrecorded_at) | Поле | ні |
| [acks](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterdeliveryrecordacks) | Поле | ні |
| [__init__](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterdeliveryrecord__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
What was acknowledged for a delivery key (serialized WriteAck list).
```

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/files/tests/test_files_adapter.py:97](../../../../../../services/storage/adapters/files/tests/test_files_adapter.py#L97).

```python
ghost = DeliveryRecord(
        delivery_key="dk-1#0",
        recorded_at=utcnow(),
        acks=[
            {
                "entity": {"entity_type": "product", "canonical_key": KEY, "version": 2},
                "delivery_key": "dk-1#0",
            }
        ],
    )
```

Контекст і передумови: [services/storage/adapters/s3/tests/test_recovery.py:311](../../../../../../services/storage/adapters/s3/tests/test_recovery.py#L311).

```python
rec = DeliveryRecord("obj-dk", datetime.now(UTC), [{"note": "no object ack"}])
```

## jane_contracts.storage_adapter.DeliveryRecord.__init__

**Конструктор dataclass.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:112](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L112).

```python
def __init__(self, delivery_key: str, recorded_at: datetime, acks: Sequence[Mapping[str, Any]]) -> None:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `delivery_key` | `str` | `—` | positional-or-keyword |
| `recorded_at` | `datetime` | `—` | positional-or-keyword |
| `acks` | `Sequence[Mapping[str, Any]]` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/files/tests/test_files_adapter.py:97](../../../../../../services/storage/adapters/files/tests/test_files_adapter.py#L97).

```python
ghost = DeliveryRecord(
        delivery_key="dk-1#0",
        recorded_at=utcnow(),
        acks=[
            {
                "entity": {"entity_type": "product", "canonical_key": KEY, "version": 2},
                "delivery_key": "dk-1#0",
            }
        ],
    )
```

Контекст і передумови: [services/storage/adapters/s3/tests/test_recovery.py:311](../../../../../../services/storage/adapters/s3/tests/test_recovery.py#L311).

```python
rec = DeliveryRecord("obj-dk", datetime.now(UTC), [{"note": "no object ack"}])
```

## jane_contracts.storage_adapter.DeliveryRecord.delivery_key

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:115](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L115).

```python
delivery_key: str
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.DeliveryRecord.recorded_at

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:116](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L116).

```python
recorded_at: datetime
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.DeliveryRecord.acks

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:117](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L117).

```python
acks: Sequence[Mapping[str, Any]]
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.CommitOutcome

**Клас.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:120](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L120).

```python
class CommitOutcome(Enum):
```

Базові типи / інтерфейси: `Enum`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [COMMITTED](jane_contracts.storage_adapter.md#jane_contractsstorage_adaptercommitoutcomecommitted) | Поле | ні |
| [CONFLICT](jane_contracts.storage_adapter.md#jane_contractsstorage_adaptercommitoutcomeconflict) | Поле | ні |
| [DUPLICATE](jane_contracts.storage_adapter.md#jane_contractsstorage_adaptercommitoutcomeduplicate) | Поле | ні |

## jane_contracts.storage_adapter.CommitOutcome.COMMITTED

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:121](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L121).

```python
COMMITTED = 'committed'
```

Доступ: читання — так; запис — ні.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/mongodb/tests/test_recovery.py:152](../../../../../../services/storage/adapters/mongodb/tests/test_recovery.py#L152).

```python
assert result.outcome is CommitOutcome.COMMITTED
```

Контекст і передумови: [services/storage/adapters/s3/tests/test_recovery.py:344](../../../../../../services/storage/adapters/s3/tests/test_recovery.py#L344).

```python
assert result.outcome is CommitOutcome.COMMITTED
```

## jane_contracts.storage_adapter.CommitOutcome.CONFLICT

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:122](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L122).

```python
CONFLICT = 'conflict'
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
``expected_version`` did not match: the core re-reads, re-merges and retries (bounded).
```

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/mongodb/tests/test_recovery.py:171](../../../../../../services/storage/adapters/mongodb/tests/test_recovery.py#L171).

```python
assert result.outcome in {CommitOutcome.DUPLICATE, CommitOutcome.CONFLICT}
```

Контекст і передумови: [services/storage/adapters/s3/tests/test_recovery.py:173](../../../../../../services/storage/adapters/s3/tests/test_recovery.py#L173).

```python
assert result.outcome is CommitOutcome.CONFLICT
```

## jane_contracts.storage_adapter.CommitOutcome.DUPLICATE

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:124](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L124).

```python
DUPLICATE = 'duplicate'
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
The delivery key (for this entity) was already committed: nothing written.
```

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/mongodb/tests/test_recovery.py:171](../../../../../../services/storage/adapters/mongodb/tests/test_recovery.py#L171).

```python
assert result.outcome in {CommitOutcome.DUPLICATE, CommitOutcome.CONFLICT}
```

Контекст і передумови: [services/storage/adapters/s3/tests/test_recovery.py:346](../../../../../../services/storage/adapters/s3/tests/test_recovery.py#L346).

```python
assert outcomes["after_cas"].outcome is CommitOutcome.DUPLICATE
```

## jane_contracts.storage_adapter.CommitResult

**Клас.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:129](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L129).

```python
class CommitResult:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [outcome](jane_contracts.storage_adapter.md#jane_contractsstorage_adaptercommitresultoutcome) | Поле | ні |
| [snapshot](jane_contracts.storage_adapter.md#jane_contractsstorage_adaptercommitresultsnapshot) | Поле | ні |
| [__init__](jane_contracts.storage_adapter.md#jane_contractsstorage_adaptercommitresult__init__) | Конструктор dataclass | ні |

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_reprocess_reads.py:287](../../../../../../services/storage/tests/test_reprocess_reads.py#L287).

```python
return CommitResult(CommitOutcome.CONFLICT, None)
```

## jane_contracts.storage_adapter.CommitResult.__init__

**Конструктор dataclass.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:129](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L129).

```python
def __init__(self, outcome: CommitOutcome, snapshot: EntitySnapshot | None) -> None:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `outcome` | `CommitOutcome` | `—` | positional-or-keyword |
| `snapshot` | `EntitySnapshot \| None` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_reprocess_reads.py:287](../../../../../../services/storage/tests/test_reprocess_reads.py#L287).

```python
return CommitResult(CommitOutcome.CONFLICT, None)
```

## jane_contracts.storage_adapter.CommitResult.outcome

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:130](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L130).

```python
outcome: CommitOutcome
```

Доступ: читання — так; запис — ні.

## jane_contracts.storage_adapter.CommitResult.snapshot

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:131](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L131).

```python
snapshot: EntitySnapshot | None
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
Snapshot after the commit (COMMITTED) or the current one (CONFLICT/DUPLICATE), if known.
```

## jane_contracts.storage_adapter.AdapterError

**Клас.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:135](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L135).

```python
class AdapterError(Exception):
```

Базові типи / інтерфейси: `Exception`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_contracts.storage_adapter.md#jane_contractsstorage_adapteradaptererror__init__) | Конструктор | ні |
| [retryable](jane_contracts.storage_adapter.md#jane_contractsstorage_adapteradaptererrorretryable) | Поле екземпляра | ні |

### Опис із вихідного коду

```text
Adapter failure. ``retryable`` maps to Problem.retryable / HandlerResult.failure.retryable.
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_secret_policy.py:412](../../../../../../services/storage/tests/test_secret_policy.py#L412).

```python
AdapterError(
            f"login failed for user {secrets['username']!r} (dsn postgresql://{secrets['username']}:"
            f"{secrets['password']}@db.internal.test/jane)",
            retryable=True,
        )
```

## jane_contracts.storage_adapter.AdapterError.__init__

**Конструктор.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:138](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L138).

```python
def __init__(self, message: str, *, retryable: bool) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `message` | `str` | `—` | positional-or-keyword |
| `retryable` | `bool` | `—` | keyword-only |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_secret_policy.py:412](../../../../../../services/storage/tests/test_secret_policy.py#L412).

```python
AdapterError(
            f"login failed for user {secrets['username']!r} (dsn postgresql://{secrets['username']}:"
            f"{secrets['password']}@db.internal.test/jane)",
            retryable=True,
        )
```

## jane_contracts.storage_adapter.AdapterError.retryable

**Поле екземпляра.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:140](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L140).

```python
self.retryable = retryable
```

## jane_contracts.storage_adapter.StorageAdapter

**Клас.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:144](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L144).

```python
class StorageAdapter(Protocol):
```

Базові типи / інтерфейси: `Protocol`.

Декоратори: `runtime_checkable`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [kind](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterstorageadapterkind) | Поле | ні |
| [capabilities](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterstorageadaptercapabilities) | Поле | ні |
| [open](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterstorageadapteropen) | Метод | ні |
| [close](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterstorageadapterclose) | Метод | ні |
| [health](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterstorageadapterhealth) | Метод | ні |
| [ensure_schema](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterstorageadapterensure_schema) | Метод | ні |
| [put_object](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterstorageadapterput_object) | Метод | ні |
| [get_object](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterstorageadapterget_object) | Метод | ні |
| [read_object_content](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterstorageadapterread_object_content) | Метод | ні |
| [list_objects](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterstorageadapterlist_objects) | Метод | ні |
| [read_entity](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterstorageadapterread_entity) | Метод | ні |
| [commit_entity](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterstorageadaptercommit_entity) | Метод | ні |
| [list_entities](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterstorageadapterlist_entities) | Метод | ні |
| [list_history](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterstorageadapterlist_history) | Метод | ні |
| [get_delivery](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterstorageadapterget_delivery) | Метод | ні |
| [record_delivery](jane_contracts.storage_adapter.md#jane_contractsstorage_adapterstorageadapterrecord_delivery) | Метод | ні |

## jane_contracts.storage_adapter.StorageAdapter.kind

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:145](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L145).

```python
kind: ClassVar[str]
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``filesystem``, ``postgresql``, ``sqlserver``, ``mongodb``, ``minio``, ``s3``.
```

## jane_contracts.storage_adapter.StorageAdapter.capabilities

**Поле.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:147](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L147).

```python
capabilities: ClassVar[frozenset[str]]
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Must equal {"objects", "entities", "history"} for every initial adapter (TZ §12 item 12: each
    adapter stores both RAW and structured results). Object stores (minio, s3) keep entity snapshots,
    history events and delivery records as JSON documents and implement :meth:`commit_entity` with
    conditional writes (If-None-Match: * for create, If-Match: <ETag> for update); see
    contracts/docs/storage-adapter.md, section "Object stores".
```

## jane_contracts.storage_adapter.StorageAdapter.open

**Метод.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:154](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L154).

```python
async def open(self, connection: ResolvedConnection, options: Mapping[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection` | `ResolvedConnection` | `—` | positional-or-keyword |
| `options` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.

## jane_contracts.storage_adapter.StorageAdapter.close

**Метод.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:156](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L156).

```python
async def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_contracts.storage_adapter.StorageAdapter.health

**Метод.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:158](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L158).

```python
async def health(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_contracts.storage_adapter.StorageAdapter.ensure_schema

**Метод.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:160](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L160).

```python
async def ensure_schema(self, entity_types: Sequence[str]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `entity_types` | `Sequence[str]` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Idempotently create tables/collections/buckets/directories.
```

## jane_contracts.storage_adapter.StorageAdapter.put_object

**Метод.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:166](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L166).

```python
async def put_object(self, obj: RawObject) -> ObjectRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `obj` | `RawObject` | `—` | positional-or-keyword |

Результат: `ObjectRecord`.

### Опис із вихідного коду

```text
Idempotent by ``object_key``: an existing object with the same sha256 is returned as is;
a different sha256 raises ``AdapterError(retryable=False)``.
```

## jane_contracts.storage_adapter.StorageAdapter.get_object

**Метод.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:171](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L171).

```python
async def get_object(self, object_id: str) -> ObjectRecord | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `object_id` | `str` | `—` | positional-or-keyword |

Результат: `ObjectRecord | None`.

## jane_contracts.storage_adapter.StorageAdapter.read_object_content

**Метод.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:173](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L173).

```python
async def read_object_content(self, object_id: str) -> bytes:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `object_id` | `str` | `—` | positional-or-keyword |

Результат: `bytes`.

## jane_contracts.storage_adapter.StorageAdapter.list_objects

**Метод.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:175](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L175).

```python
async def list_objects(self, *, source_id: str | None=None, material_id: str | None=None, since: datetime | None=None, until: datetime | None=None, cursor: str | None=None, limit: int) -> tuple[Sequence[ObjectRecord], str | None]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `source_id` | `str \| None` | `None` | keyword-only |
| `material_id` | `str \| None` | `None` | keyword-only |
| `since` | `datetime \| None` | `None` | keyword-only |
| `until` | `datetime \| None` | `None` | keyword-only |
| `cursor` | `str \| None` | `None` | keyword-only |
| `limit` | `int` | `—` | keyword-only |

Результат: `tuple[Sequence[ObjectRecord], str | None]`.

## jane_contracts.storage_adapter.StorageAdapter.read_entity

**Метод.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:188](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L188).

```python
async def read_entity(self, entity_type: str, canonical_key: str) -> EntitySnapshot | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `entity_type` | `str` | `—` | positional-or-keyword |
| `canonical_key` | `str` | `—` | positional-or-keyword |

Результат: `EntitySnapshot | None`.

## jane_contracts.storage_adapter.StorageAdapter.commit_entity

**Метод.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:190](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L190).

```python
async def commit_entity(self, *, new: EntitySnapshot, expected_version: int | None, event: HistoryEvent) -> CommitResult:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `new` | `EntitySnapshot` | `—` | keyword-only |
| `expected_version` | `int \| None` | `—` | keyword-only |
| `event` | `HistoryEvent` | `—` | keyword-only |

Результат: `CommitResult`.

### Опис із вихідного коду

```text
Atomically: if (event.delivery_key, entity) already recorded → DUPLICATE; else if the stored
version != expected_version (None = must not exist) → CONFLICT; else write ``new`` (whose
version = expected_version + 1, or 1) and append ``event`` → COMMITTED. A stale-only update
is committed with ``new`` equal to the current snapshot fields and the same version + 1.
```

## jane_contracts.storage_adapter.StorageAdapter.list_entities

**Метод.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:199](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L199).

```python
async def list_entities(self, entity_type: str, *, scope: str | None=None, updated_since: datetime | None=None, cursor: str | None=None, limit: int) -> tuple[Sequence[EntitySnapshot], str | None]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `entity_type` | `str` | `—` | positional-or-keyword |
| `scope` | `str \| None` | `None` | keyword-only |
| `updated_since` | `datetime \| None` | `None` | keyword-only |
| `cursor` | `str \| None` | `None` | keyword-only |
| `limit` | `int` | `—` | keyword-only |

Результат: `tuple[Sequence[EntitySnapshot], str | None]`.

## jane_contracts.storage_adapter.StorageAdapter.list_history

**Метод.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:209](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L209).

```python
async def list_history(self, entity_type: str, canonical_key: str, *, cursor: str | None=None, limit: int) -> tuple[Sequence[HistoryEvent], str | None]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `entity_type` | `str` | `—` | positional-or-keyword |
| `canonical_key` | `str` | `—` | positional-or-keyword |
| `cursor` | `str \| None` | `None` | keyword-only |
| `limit` | `int` | `—` | keyword-only |

Результат: `tuple[Sequence[HistoryEvent], str | None]`.

## jane_contracts.storage_adapter.StorageAdapter.get_delivery

**Метод.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:215](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L215).

```python
async def get_delivery(self, delivery_key: str) -> DeliveryRecord | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `delivery_key` | `str` | `—` | positional-or-keyword |

Результат: `DeliveryRecord | None`.

## jane_contracts.storage_adapter.StorageAdapter.record_delivery

**Метод.** Код: [contracts/python/src/jane_contracts/storage_adapter.py:217](../../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L217).

```python
async def record_delivery(self, record: DeliveryRecord) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `record` | `DeliveryRecord` | `—` | positional-or-keyword |

Результат: `bool`.

### Опис із вихідного коду

```text
Insert-if-absent. Returns False if the key already exists (used for object-only writes).
```
