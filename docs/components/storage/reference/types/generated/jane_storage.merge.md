# jane_storage.merge

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_storage.merge.InvalidRecord](#jane_storagemergeinvalidrecord)
- [jane_storage.merge.MergeResult](#jane_storagemergemergeresult)
- [jane_storage.merge.MergeResult.__init__](#jane_storagemergemergeresult__init__)
- [jane_storage.merge.MergeResult.snapshot](#jane_storagemergemergeresultsnapshot)
- [jane_storage.merge.MergeResult.applied](#jane_storagemergemergeresultapplied)
- [jane_storage.merge.MergeResult.stale](#jane_storagemergemergeresultstale)
- [jane_storage.merge.MergeResult.status](#jane_storagemergemergeresultstatus)
- [jane_storage.merge.order_of](#jane_storagemergeorder_of)
- [jane_storage.merge.validate_record](#jane_storagemergevalidate_record)
- [jane_storage.merge.merge](#jane_storagemergemerge)

## jane_storage.merge.InvalidRecord

**Клас.** Код: [services/storage/src/jane_storage/merge.py:30](../../../../../../services/storage/src/jane_storage/merge.py#L30).

```python
class InvalidRecord(ValueError):
```

Базові типи / інтерфейси: `ValueError`.

### Опис із вихідного коду

```text
The record violates EntityRecord semantics (null value, field both set and cleared...).
```

## jane_storage.merge.MergeResult

**Клас.** Код: [services/storage/src/jane_storage/merge.py:35](../../../../../../services/storage/src/jane_storage/merge.py#L35).

```python
class MergeResult:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [snapshot](jane_storage.merge.md#jane_storagemergemergeresultsnapshot) | Поле | ні |
| [applied](jane_storage.merge.md#jane_storagemergemergeresultapplied) | Поле | ні |
| [stale](jane_storage.merge.md#jane_storagemergemergeresultstale) | Поле | ні |
| [status](jane_storage.merge.md#jane_storagemergemergeresultstatus) | Властивість | ні |
| [__init__](jane_storage.merge.md#jane_storagemergemergeresult__init__) | Конструктор dataclass | ні |

## jane_storage.merge.MergeResult.__init__

**Конструктор dataclass.** Код: [services/storage/src/jane_storage/merge.py:35](../../../../../../services/storage/src/jane_storage/merge.py#L35).

```python
def __init__(self, snapshot: EntitySnapshot, applied: list[str], stale: list[str]) -> None:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `snapshot` | `EntitySnapshot` | `—` | positional-or-keyword |
| `applied` | `list[str]` | `—` | positional-or-keyword |
| `stale` | `list[str]` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.merge.MergeResult.snapshot

**Поле.** Код: [services/storage/src/jane_storage/merge.py:36](../../../../../../services/storage/src/jane_storage/merge.py#L36).

```python
snapshot: EntitySnapshot
```

Доступ: читання — так; запис — ні.

## jane_storage.merge.MergeResult.applied

**Поле.** Код: [services/storage/src/jane_storage/merge.py:37](../../../../../../services/storage/src/jane_storage/merge.py#L37).

```python
applied: list[str]
```

Доступ: читання — так; запис — ні.

## jane_storage.merge.MergeResult.stale

**Поле.** Код: [services/storage/src/jane_storage/merge.py:38](../../../../../../services/storage/src/jane_storage/merge.py#L38).

```python
stale: list[str]
```

Доступ: читання — так; запис — ні.

## jane_storage.merge.MergeResult.status

**Властивість.** Код: [services/storage/src/jane_storage/merge.py:41](../../../../../../services/storage/src/jane_storage/merge.py#L41).

```python
def status(self) -> str:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
``WriteAck.status`` for this merge.
```

## jane_storage.merge.order_of

**Функція.** Код: [services/storage/src/jane_storage/merge.py:50](../../../../../../services/storage/src/jane_storage/merge.py#L50).

```python
def order_of(record: Mapping[str, Any]) -> OrderKey:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `record` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `OrderKey`.

## jane_storage.merge.validate_record

**Функція.** Код: [services/storage/src/jane_storage/merge.py:60](../../../../../../services/storage/src/jane_storage/merge.py#L60).

```python
def validate_record(record: Mapping[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `record` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `InvalidRecord`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_storage.merge.merge

**Функція.** Код: [services/storage/src/jane_storage/merge.py:78](../../../../../../services/storage/src/jane_storage/merge.py#L78).

```python
def merge(current: EntitySnapshot | None, record: Mapping[str, Any], *, now: datetime) -> MergeResult:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `current` | `EntitySnapshot \| None` | `—` | positional-or-keyword |
| `record` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `now` | `datetime` | `—` | keyword-only |

Результат: `MergeResult`.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/mongodb/tests/test_recovery.py:137](../../../../../../services/storage/adapters/mongodb/tests/test_recovery.py#L137).

```python
merged = merge(current, rec, now=datetime.now(UTC))
```

Контекст і передумови: [services/storage/adapters/s3/tests/test_recovery.py:168](../../../../../../services/storage/adapters/s3/tests/test_recovery.py#L168).

```python
merged = merge(None, rec, now=datetime.now(UTC))
```
