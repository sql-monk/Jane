# Модуль `jane_storage.merge`

> Згенеровано `scripts/docs_reference.py` з [services/storage/src/jane_storage/merge.py](../../../../../services/storage/src/jane_storage/merge.py). Не редагуйте вручну.

Merge of an ``EntityRecord`` into the current state — a pure function (no I/O).

Semantics (``entity.schema.json``, TZ §6, §11):

1. a field in ``fields`` sets the value;
2. a field absent from ``fields`` and ``cleared`` is left unchanged (omission is not deletion);
3. a field in ``cleared`` is removed from ``fields`` and remembered in ``cleared_fields``;
4. every field (also a cleared one) remembers the observation order of its last change; an update of a field applies only if the record's order is strictly newer (``order_tuple``), otherwise the field is reported in ``stale`` and only the history keeps it;
5. the new snapshot always has ``version + 1`` (also for a stale-only update, whose fields equal the current ones) — the adapter commits it with compare-and-swap on the old version.

## Зміст

- [Клас `InvalidRecord`](#клас-invalidrecord)
- [Клас `MergeResult`](#клас-mergeresult)
- [Функція `merge`](#функція-merge)
- [Функція `order_of`](#функція-order_of)
- [Функція `validate_record`](#функція-validate_record)

## Класи

### Клас `InvalidRecord`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_storage.merge` |
| Успадкування | `ValueError` |
| Код | [merge.py:30](../../../../../services/storage/src/jane_storage/merge.py#L30) |

```python
class InvalidRecord(ValueError): ...
```

The record violates EntityRecord semantics (null value, field both set and cleared...).

### Клас `MergeResult`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_storage.merge` |
| Код | [merge.py:35](../../../../../services/storage/src/jane_storage/merge.py#L35) |

```python
@dataclass(frozen=True, slots=True)
class MergeResult: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `snapshot` | `EntitySnapshot` | — | читання |  |
| `applied` | `list[str]` | — | читання |  |
| `stale` | `list[str]` | — | читання |  |
| `status` | `str` | — | читання (властивість) | ``WriteAck.status`` for this merge. |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

## Функції

### Функція `merge`

```python
def merge(
    current: EntitySnapshot | None,
    record: Mapping[str, Any],
    *,
    now: datetime,
) -> MergeResult: ...
```

Код: [merge.py:78](../../../../../services/storage/src/jane_storage/merge.py#L78).

### Функція `order_of`

```python
def order_of(record: Mapping[str, Any]) -> OrderKey: ...
```

Код: [merge.py:50](../../../../../services/storage/src/jane_storage/merge.py#L50).

### Функція `validate_record`

```python
def validate_record(record: Mapping[str, Any]) -> None: ...
```

Винятки в коді функції: `InvalidRecord`.

Код: [merge.py:60](../../../../../services/storage/src/jane_storage/merge.py#L60).
