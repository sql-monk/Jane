# Модуль `jane_storage.codec`

> Згенеровано `scripts/docs_reference.py` з [services/storage/src/jane_storage/codec.py](../../../../../services/storage/src/jane_storage/codec.py). Не редагуйте вручну.

Adapter kit: JSON documents for the dataclasses of ``jane_contracts.storage_adapter``.

Shared by every adapter that keeps snapshots, history events, delivery records and object metadata as JSON (filesystem, MinIO, S3, MongoDB; SQL adapters use it for JSON columns). Using the same codec guarantees that all adapters return identical values to the core (e.g. timestamps with microseconds in UTC, ``field_orders`` with ``sequence``).

Document shapes follow ``entity.schema.json`` (``EntityState``, ``EntityHistoryEntry``) plus the internal fields the core needs (``version`` of a history event, ``canonical_key``).

## Зміст

- [Функція `delivery_from_json`](#функція-delivery_from_json)
- [Функція `delivery_to_json`](#функція-delivery_to_json)
- [Функція `dumps`](#функція-dumps)
- [Функція `entity_ack`](#функція-entity_ack)
- [Функція `event_from_json`](#функція-event_from_json)
- [Функція `event_to_json`](#функція-event_to_json)
- [Функція `format_ts`](#функція-format_ts)
- [Функція `loads`](#функція-loads)
- [Функція `object_record_from_json`](#функція-object_record_from_json)
- [Функція `object_record_to_json`](#функція-object_record_to_json)
- [Функція `order_from_json`](#функція-order_from_json)
- [Функція `order_to_json`](#функція-order_to_json)
- [Функція `parse_ts`](#функція-parse_ts)
- [Функція `snapshot_from_json`](#функція-snapshot_from_json)
- [Функція `snapshot_to_json`](#функція-snapshot_to_json)
- [Функція `utcnow`](#функція-utcnow)

## Функції

### Функція `delivery_from_json`

```python
def delivery_from_json(doc: Mapping[str, Any]) -> DeliveryRecord: ...
```

Код: [codec.py:156](../../../../../services/storage/src/jane_storage/codec.py#L156).

### Функція `delivery_to_json`

```python
def delivery_to_json(record: DeliveryRecord) -> dict[str, Any]: ...
```

Код: [codec.py:148](../../../../../services/storage/src/jane_storage/codec.py#L148).

### Функція `dumps`

```python
def dumps(document: Any) -> bytes: ...
```

Canonical UTF-8 JSON (sorted keys, no ASCII escaping).

Код: [codec.py:68](../../../../../services/storage/src/jane_storage/codec.py#L68).

### Функція `entity_ack`

```python
def entity_ack(new: EntitySnapshot, event: HistoryEvent) -> dict[str, Any]: ...
```

What ``commit_entity`` records as the only ack of the entity delivery (``DeliveryRecord.acks[0]``).

The core turns it into a ``WriteAck`` with ``status: duplicate`` on a repeated delivery. Every adapter must record exactly this document so that duplicates look the same everywhere.

Код: [codec.py:190](../../../../../services/storage/src/jane_storage/codec.py#L190).

### Функція `event_from_json`

```python
def event_from_json(doc: Mapping[str, Any]) -> HistoryEvent: ...
```

Код: [codec.py:136](../../../../../services/storage/src/jane_storage/codec.py#L136).

### Функція `event_to_json`

```python
def event_to_json(event: HistoryEvent, version: int) -> dict[str, Any]: ...
```

History event document; ``version`` = snapshot version this event produced.

Код: [codec.py:122](../../../../../services/storage/src/jane_storage/codec.py#L122).

### Функція `format_ts`

```python
def format_ts(value: datetime) -> str: ...
```

RFC 3339 UTC with microseconds: ``2026-09-27T10:00:05.000000Z``.

Код: [codec.py:51](../../../../../services/storage/src/jane_storage/codec.py#L51).

### Функція `loads`

```python
def loads(raw: bytes | str) -> Any: ...
```

Код: [codec.py:73](../../../../../services/storage/src/jane_storage/codec.py#L73).

### Функція `object_record_from_json`

```python
def object_record_from_json(doc: Mapping[str, Any]) -> ObjectRecord: ...
```

Код: [codec.py:177](../../../../../services/storage/src/jane_storage/codec.py#L177).

### Функція `object_record_to_json`

```python
def object_record_to_json(rec: ObjectRecord) -> dict[str, Any]: ...
```

Код: [codec.py:164](../../../../../services/storage/src/jane_storage/codec.py#L164).

### Функція `order_from_json`

```python
def order_from_json(doc: Mapping[str, Any]) -> OrderKey: ...
```

Код: [codec.py:87](../../../../../services/storage/src/jane_storage/codec.py#L87).

### Функція `order_to_json`

```python
def order_to_json(order: OrderKey) -> dict[str, Any]: ...
```

Код: [codec.py:77](../../../../../services/storage/src/jane_storage/codec.py#L77).

### Функція `parse_ts`

```python
def parse_ts(value: str | datetime) -> datetime: ...
```

Код: [codec.py:58](../../../../../services/storage/src/jane_storage/codec.py#L58).

### Функція `snapshot_from_json`

```python
def snapshot_from_json(doc: Mapping[str, Any]) -> EntitySnapshot: ...
```

Код: [codec.py:109](../../../../../services/storage/src/jane_storage/codec.py#L109).

### Функція `snapshot_to_json`

```python
def snapshot_to_json(snap: EntitySnapshot) -> dict[str, Any]: ...
```

Код: [codec.py:96](../../../../../services/storage/src/jane_storage/codec.py#L96).

### Функція `utcnow`

```python
def utcnow() -> datetime: ...
```

Код: [codec.py:47](../../../../../services/storage/src/jane_storage/codec.py#L47).
