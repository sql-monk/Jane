# jane_storage.codec

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_storage.codec.utcnow](#jane_storagecodecutcnow)
- [jane_storage.codec.format_ts](#jane_storagecodecformat_ts)
- [jane_storage.codec.parse_ts](#jane_storagecodecparse_ts)
- [jane_storage.codec.dumps](#jane_storagecodecdumps)
- [jane_storage.codec.loads](#jane_storagecodecloads)
- [jane_storage.codec.order_to_json](#jane_storagecodecorder_to_json)
- [jane_storage.codec.order_from_json](#jane_storagecodecorder_from_json)
- [jane_storage.codec.snapshot_to_json](#jane_storagecodecsnapshot_to_json)
- [jane_storage.codec.snapshot_from_json](#jane_storagecodecsnapshot_from_json)
- [jane_storage.codec.event_to_json](#jane_storagecodecevent_to_json)
- [jane_storage.codec.event_from_json](#jane_storagecodecevent_from_json)
- [jane_storage.codec.delivery_to_json](#jane_storagecodecdelivery_to_json)
- [jane_storage.codec.delivery_from_json](#jane_storagecodecdelivery_from_json)
- [jane_storage.codec.object_record_to_json](#jane_storagecodecobject_record_to_json)
- [jane_storage.codec.object_record_from_json](#jane_storagecodecobject_record_from_json)
- [jane_storage.codec.entity_ack](#jane_storagecodecentity_ack)

## jane_storage.codec.utcnow

**Функція.** Код: [services/storage/src/jane_storage/codec.py:47](../../../../../../services/storage/src/jane_storage/codec.py#L47).

```python
def utcnow() -> datetime:
```

Результат: `datetime`.

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

## jane_storage.codec.format_ts

**Функція.** Код: [services/storage/src/jane_storage/codec.py:51](../../../../../../services/storage/src/jane_storage/codec.py#L51).

```python
def format_ts(value: datetime) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `datetime` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
RFC 3339 UTC with microseconds: ``2026-09-27T10:00:05.000000Z``.
```

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/s3/tests/test_recovery.py:134](../../../../../../services/storage/adapters/s3/tests/test_recovery.py#L134).

```python
return {
        "delivery_key": delivery_key,
        "recorded_at": format_ts(claimed_at),
        "claimed_at": format_ts(claimed_at),
        "claim_id": uuid.uuid4().hex,
        "acks": [{"entity": {"entity_type": "product", "canonical_key": KEY, "version": version}}],
    }
```

Контекст і передумови: [services/storage/tests/test_core.py:117](../../../../../../services/storage/tests/test_core.py#L117).

```python
assert format_ts(parse_ts("2026-09-27T10:00:05Z")) == "2026-09-27T10:00:05.000000Z"
```

## jane_storage.codec.parse_ts

**Функція.** Код: [services/storage/src/jane_storage/codec.py:58](../../../../../../services/storage/src/jane_storage/codec.py#L58).

```python
def parse_ts(value: str | datetime) -> datetime:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `str \| datetime` | `—` | positional-or-keyword |

Результат: `datetime`.

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_core.py:52](../../../../../../services/storage/tests/test_core.py#L52).

```python
key = object_key(
        material_id="web:3704326c",
        observation_id="obs_1",
        source_id="shop-example",
        fetched_at=parse_ts("2026-09-27T23:30:00-03:00"),
        ext="html",
    )
```

Контекст і передумови: [services/storage/tests/test_core.py:117](../../../../../../services/storage/tests/test_core.py#L117).

```python
assert format_ts(parse_ts("2026-09-27T10:00:05Z")) == "2026-09-27T10:00:05.000000Z"
```

## jane_storage.codec.dumps

**Функція.** Код: [services/storage/src/jane_storage/codec.py:68](../../../../../../services/storage/src/jane_storage/codec.py#L68).

```python
def dumps(document: Any) -> bytes:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `document` | `Any` | `—` | positional-or-keyword |

Результат: `bytes`.

### Опис із вихідного коду

```text
Canonical UTF-8 JSON (sorted keys, no ASCII escaping).
```

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/files/tests/test_files_adapter.py:107](../../../../../../services/storage/adapters/files/tests/test_files_adapter.py#L107).

```python
(tmp_path / "deliveries" / f"{key_digest('dk-1#0')}.json").write_bytes(dumps(delivery_to_json(ghost)))
```

Контекст і передумови: [services/storage/adapters/s3/tests/test_recovery.py:98](../../../../../../services/storage/adapters/s3/tests/test_recovery.py#L98).

```python
self.client.put_object(Bucket=self.bucket, Key=f"{PREFIX}/{key}", Body=dumps(doc))
```

## jane_storage.codec.loads

**Функція.** Код: [services/storage/src/jane_storage/codec.py:73](../../../../../../services/storage/src/jane_storage/codec.py#L73).

```python
def loads(raw: bytes | str) -> Any:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `raw` | `bytes \| str` | `—` | positional-or-keyword |

Результат: `Any`.

## jane_storage.codec.order_to_json

**Функція.** Код: [services/storage/src/jane_storage/codec.py:77](../../../../../../services/storage/src/jane_storage/codec.py#L77).

```python
def order_to_json(order: OrderKey) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `order` | `OrderKey` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_core.py:116](../../../../../../services/storage/tests/test_core.py#L116).

```python
assert order_from_json(order_to_json(order)) == order
```

## jane_storage.codec.order_from_json

**Функція.** Код: [services/storage/src/jane_storage/codec.py:87](../../../../../../services/storage/src/jane_storage/codec.py#L87).

```python
def order_from_json(doc: Mapping[str, Any]) -> OrderKey:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `doc` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `OrderKey`.

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_core.py:116](../../../../../../services/storage/tests/test_core.py#L116).

```python
assert order_from_json(order_to_json(order)) == order
```

## jane_storage.codec.snapshot_to_json

**Функція.** Код: [services/storage/src/jane_storage/codec.py:96](../../../../../../services/storage/src/jane_storage/codec.py#L96).

```python
def snapshot_to_json(snap: EntitySnapshot) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `snap` | `EntitySnapshot` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_core.py:114](../../../../../../services/storage/tests/test_core.py#L114).

```python
assert snapshot_from_json(snapshot_to_json(snap)) == snap
```

## jane_storage.codec.snapshot_from_json

**Функція.** Код: [services/storage/src/jane_storage/codec.py:109](../../../../../../services/storage/src/jane_storage/codec.py#L109).

```python
def snapshot_from_json(doc: Mapping[str, Any]) -> EntitySnapshot:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `doc` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `EntitySnapshot`.

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_core.py:114](../../../../../../services/storage/tests/test_core.py#L114).

```python
assert snapshot_from_json(snapshot_to_json(snap)) == snap
```

## jane_storage.codec.event_to_json

**Функція.** Код: [services/storage/src/jane_storage/codec.py:122](../../../../../../services/storage/src/jane_storage/codec.py#L122).

```python
def event_to_json(event: HistoryEvent, version: int) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `event` | `HistoryEvent` | `—` | positional-or-keyword |
| `version` | `int` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
History event document; ``version`` = snapshot version this event produced.
```

## jane_storage.codec.event_from_json

**Функція.** Код: [services/storage/src/jane_storage/codec.py:136](../../../../../../services/storage/src/jane_storage/codec.py#L136).

```python
def event_from_json(doc: Mapping[str, Any]) -> HistoryEvent:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `doc` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `HistoryEvent`.

## jane_storage.codec.delivery_to_json

**Функція.** Код: [services/storage/src/jane_storage/codec.py:148](../../../../../../services/storage/src/jane_storage/codec.py#L148).

```python
def delivery_to_json(record: DeliveryRecord) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `record` | `DeliveryRecord` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/files/tests/test_files_adapter.py:107](../../../../../../services/storage/adapters/files/tests/test_files_adapter.py#L107).

```python
(tmp_path / "deliveries" / f"{key_digest('dk-1#0')}.json").write_bytes(dumps(delivery_to_json(ghost)))
```

## jane_storage.codec.delivery_from_json

**Функція.** Код: [services/storage/src/jane_storage/codec.py:156](../../../../../../services/storage/src/jane_storage/codec.py#L156).

```python
def delivery_from_json(doc: Mapping[str, Any]) -> DeliveryRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `doc` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `DeliveryRecord`.

## jane_storage.codec.object_record_to_json

**Функція.** Код: [services/storage/src/jane_storage/codec.py:164](../../../../../../services/storage/src/jane_storage/codec.py#L164).

```python
def object_record_to_json(rec: ObjectRecord) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `rec` | `ObjectRecord` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_storage.codec.object_record_from_json

**Функція.** Код: [services/storage/src/jane_storage/codec.py:177](../../../../../../services/storage/src/jane_storage/codec.py#L177).

```python
def object_record_from_json(doc: Mapping[str, Any]) -> ObjectRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `doc` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `ObjectRecord`.

## jane_storage.codec.entity_ack

**Функція.** Код: [services/storage/src/jane_storage/codec.py:190](../../../../../../services/storage/src/jane_storage/codec.py#L190).

```python
def entity_ack(new: EntitySnapshot, event: HistoryEvent) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `new` | `EntitySnapshot` | `—` | positional-or-keyword |
| `event` | `HistoryEvent` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
What ``commit_entity`` records as the only ack of the entity delivery (``DeliveryRecord.acks[0]``).

The core turns it into a ``WriteAck`` with ``status: duplicate`` on a repeated delivery. Every
adapter must record exactly this document so that duplicates look the same everywhere.
```

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/mongodb/tests/test_recovery.py:68](../../../../../../services/storage/adapters/mongodb/tests/test_recovery.py#L68).

```python
pending = {"version": 2, "delivery_key": "m-b#0", "event": event, "ack": entity_ack(snap, history[0])}
```
