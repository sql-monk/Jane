# jane_llm.store

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_llm.store.ConfigKind](#jane_llmstoreconfigkind)
- [jane_llm.store.CounterKey](#jane_llmstorecounterkey)
- [jane_llm.store.CounterKey.__init__](#jane_llmstorecounterkey__init__)
- [jane_llm.store.CounterKey.scope_type](#jane_llmstorecounterkeyscope_type)
- [jane_llm.store.CounterKey.scope_id](#jane_llmstorecounterkeyscope_id)
- [jane_llm.store.CounterKey.window](#jane_llmstorecounterkeywindow)
- [jane_llm.store.CounterKey.as_tuple](#jane_llmstorecounterkeyas_tuple)
- [jane_llm.store.BudgetCheck](#jane_llmstorebudgetcheck)
- [jane_llm.store.BudgetCheck.__init__](#jane_llmstorebudgetcheck__init__)
- [jane_llm.store.BudgetCheck.key](#jane_llmstorebudgetcheckkey)
- [jane_llm.store.BudgetCheck.limit](#jane_llmstorebudgetchecklimit)
- [jane_llm.store.BudgetCheck.currency](#jane_llmstorebudgetcheckcurrency)
- [jane_llm.store.BudgetCheck.period](#jane_llmstorebudgetcheckperiod)
- [jane_llm.store.BudgetCheck.resets_at](#jane_llmstorebudgetcheckresets_at)
- [jane_llm.store.RateCheck](#jane_llmstoreratecheck)
- [jane_llm.store.RateCheck.__init__](#jane_llmstoreratecheck__init__)
- [jane_llm.store.RateCheck.key](#jane_llmstoreratecheckkey)
- [jane_llm.store.RateCheck.limit](#jane_llmstoreratechecklimit)
- [jane_llm.store.RateCheck.retry_after_seconds](#jane_llmstoreratecheckretry_after_seconds)
- [jane_llm.store.UsageRecord](#jane_llmstoreusagerecord)
- [jane_llm.store.UsageRecord.__init__](#jane_llmstoreusagerecord__init__)
- [jane_llm.store.UsageRecord.completion_id](#jane_llmstoreusagerecordcompletion_id)
- [jane_llm.store.UsageRecord.created_at](#jane_llmstoreusagerecordcreated_at)
- [jane_llm.store.UsageRecord.provider_id](#jane_llmstoreusagerecordprovider_id)
- [jane_llm.store.UsageRecord.model_id](#jane_llmstoreusagerecordmodel_id)
- [jane_llm.store.UsageRecord.purpose](#jane_llmstoreusagerecordpurpose)
- [jane_llm.store.UsageRecord.source_id](#jane_llmstoreusagerecordsource_id)
- [jane_llm.store.UsageRecord.task_id](#jane_llmstoreusagerecordtask_id)
- [jane_llm.store.UsageRecord.run_id](#jane_llmstoreusagerecordrun_id)
- [jane_llm.store.UsageRecord.input_tokens](#jane_llmstoreusagerecordinput_tokens)
- [jane_llm.store.UsageRecord.output_tokens](#jane_llmstoreusagerecordoutput_tokens)
- [jane_llm.store.UsageRecord.cost](#jane_llmstoreusagerecordcost)
- [jane_llm.store.UsageRecord.currency](#jane_llmstoreusagerecordcurrency)
- [jane_llm.store.UsageRecord.test_mode](#jane_llmstoreusagerecordtest_mode)
- [jane_llm.store.UsageRecord.outcome](#jane_llmstoreusagerecordoutcome)
- [jane_llm.store.UsageQuery](#jane_llmstoreusagequery)
- [jane_llm.store.UsageQuery.__init__](#jane_llmstoreusagequery__init__)
- [jane_llm.store.UsageQuery.scope_type](#jane_llmstoreusagequeryscope_type)
- [jane_llm.store.UsageQuery.scope_id](#jane_llmstoreusagequeryscope_id)
- [jane_llm.store.UsageQuery.since](#jane_llmstoreusagequerysince)
- [jane_llm.store.UsageQuery.until](#jane_llmstoreusagequeryuntil)
- [jane_llm.store.UsageQuery.group_by](#jane_llmstoreusagequerygroup_by)
- [jane_llm.store.UsageRow](#jane_llmstoreusagerow)
- [jane_llm.store.UsageRow.__init__](#jane_llmstoreusagerow__init__)
- [jane_llm.store.UsageRow.requests](#jane_llmstoreusagerowrequests)
- [jane_llm.store.UsageRow.input_tokens](#jane_llmstoreusagerowinput_tokens)
- [jane_llm.store.UsageRow.output_tokens](#jane_llmstoreusagerowoutput_tokens)
- [jane_llm.store.UsageRow.cost](#jane_llmstoreusagerowcost)
- [jane_llm.store.UsageRow.currency](#jane_llmstoreusagerowcurrency)
- [jane_llm.store.UsageRow.period_start](#jane_llmstoreusagerowperiod_start)
- [jane_llm.store.UsageRow.scope_type](#jane_llmstoreusagerowscope_type)
- [jane_llm.store.UsageRow.scope_id](#jane_llmstoreusagerowscope_id)
- [jane_llm.store.UsageRow.model](#jane_llmstoreusagerowmodel)
- [jane_llm.store.UsageRow.purpose](#jane_llmstoreusagerowpurpose)
- [jane_llm.store.UsageRow.test_mode](#jane_llmstoreusagerowtest_mode)
- [jane_llm.store.UsageRow.extra](#jane_llmstoreusagerowextra)
- [jane_llm.store.BudgetExceeded](#jane_llmstorebudgetexceeded)
- [jane_llm.store.BudgetExceeded.__init__](#jane_llmstorebudgetexceeded__init__)
- [jane_llm.store.RateExceeded](#jane_llmstorerateexceeded)
- [jane_llm.store.RateExceeded.__init__](#jane_llmstorerateexceeded__init__)
- [jane_llm.store.RateExceeded.check](#jane_llmstorerateexceededcheck)
- [jane_llm.store.Store](#jane_llmstorestore)
- [jane_llm.store.Store.migrate](#jane_llmstorestoremigrate)
- [jane_llm.store.Store.ping](#jane_llmstorestoreping)
- [jane_llm.store.Store.close](#jane_llmstorestoreclose)
- [jane_llm.store.Store.get_doc](#jane_llmstorestoreget_doc)
- [jane_llm.store.Store.list_docs](#jane_llmstorestorelist_docs)
- [jane_llm.store.Store.put_doc](#jane_llmstorestoreput_doc)
- [jane_llm.store.Store.seed_doc](#jane_llmstorestoreseed_doc)
- [jane_llm.store.Store.delete_doc](#jane_llmstorestoredelete_doc)
- [jane_llm.store.Store.reserve](#jane_llmstorestorereserve)
- [jane_llm.store.Store.settle](#jane_llmstorestoresettle)
- [jane_llm.store.Store.release](#jane_llmstorestorerelease)
- [jane_llm.store.Store.counter](#jane_llmstorestorecounter)
- [jane_llm.store.Store.usage](#jane_llmstorestoreusage)
- [jane_llm.store.Store.save_invocation](#jane_llmstorestoresave_invocation)
- [jane_llm.store.Store.get_invocation](#jane_llmstorestoreget_invocation)
- [jane_llm.store.Store.idempotency](#jane_llmstorestoreidempotency)
- [jane_llm.store.Store.jobs](#jane_llmstorestorejobs)
- [jane_llm.store.MemoryStore](#jane_llmstorememorystore)
- [jane_llm.store.MemoryStore.__init__](#jane_llmstorememorystore__init__)
- [jane_llm.store.MemoryStore.idempotency](#jane_llmstorememorystoreidempotency)
- [jane_llm.store.MemoryStore.jobs](#jane_llmstorememorystorejobs)
- [jane_llm.store.MemoryStore.migrate](#jane_llmstorememorystoremigrate)
- [jane_llm.store.MemoryStore.ping](#jane_llmstorememorystoreping)
- [jane_llm.store.MemoryStore.close](#jane_llmstorememorystoreclose)
- [jane_llm.store.MemoryStore.get_doc](#jane_llmstorememorystoreget_doc)
- [jane_llm.store.MemoryStore.list_docs](#jane_llmstorememorystorelist_docs)
- [jane_llm.store.MemoryStore.put_doc](#jane_llmstorememorystoreput_doc)
- [jane_llm.store.MemoryStore.seed_doc](#jane_llmstorememorystoreseed_doc)
- [jane_llm.store.MemoryStore.delete_doc](#jane_llmstorememorystoredelete_doc)
- [jane_llm.store.MemoryStore.reserve](#jane_llmstorememorystorereserve)
- [jane_llm.store.MemoryStore.settle](#jane_llmstorememorystoresettle)
- [jane_llm.store.MemoryStore.release](#jane_llmstorememorystorerelease)
- [jane_llm.store.MemoryStore.counter](#jane_llmstorememorystorecounter)
- [jane_llm.store.MemoryStore.usage](#jane_llmstorememorystoreusage)
- [jane_llm.store.MemoryStore.save_invocation](#jane_llmstorememorystoresave_invocation)
- [jane_llm.store.MemoryStore.get_invocation](#jane_llmstorememorystoreget_invocation)
- [jane_llm.store.PostgresStore](#jane_llmstorepostgresstore)
- [jane_llm.store.PostgresStore.__init__](#jane_llmstorepostgresstore__init__)
- [jane_llm.store.PostgresStore.schema](#jane_llmstorepostgresstoreschema)
- [jane_llm.store.PostgresStore.pool](#jane_llmstorepostgresstorepool)
- [jane_llm.store.PostgresStore.pg_idempotency](#jane_llmstorepostgresstorepg_idempotency)
- [jane_llm.store.PostgresStore.pg_jobs](#jane_llmstorepostgresstorepg_jobs)
- [jane_llm.store.PostgresStore.idempotency](#jane_llmstorepostgresstoreidempotency)
- [jane_llm.store.PostgresStore.jobs](#jane_llmstorepostgresstorejobs)
- [jane_llm.store.PostgresStore.migrate](#jane_llmstorepostgresstoremigrate)
- [jane_llm.store.PostgresStore.ping](#jane_llmstorepostgresstoreping)
- [jane_llm.store.PostgresStore.close](#jane_llmstorepostgresstoreclose)
- [jane_llm.store.PostgresStore.get_doc](#jane_llmstorepostgresstoreget_doc)
- [jane_llm.store.PostgresStore.list_docs](#jane_llmstorepostgresstorelist_docs)
- [jane_llm.store.PostgresStore.put_doc](#jane_llmstorepostgresstoreput_doc)
- [jane_llm.store.PostgresStore.seed_doc](#jane_llmstorepostgresstoreseed_doc)
- [jane_llm.store.PostgresStore.delete_doc](#jane_llmstorepostgresstoredelete_doc)
- [jane_llm.store.PostgresStore.reserve](#jane_llmstorepostgresstorereserve)
- [jane_llm.store.PostgresStore.settle](#jane_llmstorepostgresstoresettle)
- [jane_llm.store.PostgresStore.release](#jane_llmstorepostgresstorerelease)
- [jane_llm.store.PostgresStore.counter](#jane_llmstorepostgresstorecounter)
- [jane_llm.store.PostgresStore.usage](#jane_llmstorepostgresstoreusage)
- [jane_llm.store.PostgresStore.save_invocation](#jane_llmstorepostgresstoresave_invocation)
- [jane_llm.store.PostgresStore.get_invocation](#jane_llmstorepostgresstoreget_invocation)
- [jane_llm.store.iter_keys](#jane_llmstoreiter_keys)

## jane_llm.store.ConfigKind

**Змінна.** Код: [services/llm/src/jane_llm/store.py:35](../../../../../../services/llm/src/jane_llm/store.py#L35).

```python
ConfigKind = Literal['provider', 'alias', 'budget', 'connection']
```

## jane_llm.store.CounterKey

**Клас.** Код: [services/llm/src/jane_llm/store.py:40](../../../../../../services/llm/src/jane_llm/store.py#L40).

```python
class CounterKey:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [scope_type](jane_llm.store.md#jane_llmstorecounterkeyscope_type) | Поле | ні |
| [scope_id](jane_llm.store.md#jane_llmstorecounterkeyscope_id) | Поле | ні |
| [window](jane_llm.store.md#jane_llmstorecounterkeywindow) | Поле | ні |
| [as_tuple](jane_llm.store.md#jane_llmstorecounterkeyas_tuple) | Метод | ні |
| [__init__](jane_llm.store.md#jane_llmstorecounterkey__init__) | Конструктор dataclass | ні |

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_units.py:143](../../../../../../services/llm/tests/test_units.py#L143).

```python
return BudgetCheck(CounterKey("task", "t", key), limit, "USD", "day", None)
```

Контекст і передумови: [services/llm/tests/test_units.py:161](../../../../../../services/llm/tests/test_units.py#L161).

```python
spent, reserved = store.counter(CounterKey("task", "t", "k"))
```

## jane_llm.store.CounterKey.__init__

**Конструктор dataclass.** Код: [services/llm/src/jane_llm/store.py:40](../../../../../../services/llm/src/jane_llm/store.py#L40).

```python
def __init__(self, scope_type: str, scope_id: str, window: str) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `scope_type` | `str` | `—` | positional-or-keyword |
| `scope_id` | `str` | `—` | positional-or-keyword |
| `window` | `str` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_units.py:143](../../../../../../services/llm/tests/test_units.py#L143).

```python
return BudgetCheck(CounterKey("task", "t", key), limit, "USD", "day", None)
```

Контекст і передумови: [services/llm/tests/test_units.py:161](../../../../../../services/llm/tests/test_units.py#L161).

```python
spent, reserved = store.counter(CounterKey("task", "t", "k"))
```

## jane_llm.store.CounterKey.scope_type

**Поле.** Код: [services/llm/src/jane_llm/store.py:41](../../../../../../services/llm/src/jane_llm/store.py#L41).

```python
scope_type: str
```

Доступ: читання — так; запис — ні.

## jane_llm.store.CounterKey.scope_id

**Поле.** Код: [services/llm/src/jane_llm/store.py:42](../../../../../../services/llm/src/jane_llm/store.py#L42).

```python
scope_id: str
```

Доступ: читання — так; запис — ні.

## jane_llm.store.CounterKey.window

**Поле.** Код: [services/llm/src/jane_llm/store.py:43](../../../../../../services/llm/src/jane_llm/store.py#L43).

```python
window: str
```

Доступ: читання — так; запис — ні.

## jane_llm.store.CounterKey.as_tuple

**Метод.** Код: [services/llm/src/jane_llm/store.py:45](../../../../../../services/llm/src/jane_llm/store.py#L45).

```python
def as_tuple(self) -> tuple[str, str, str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `tuple[str, str, str]`.

## jane_llm.store.BudgetCheck

**Клас.** Код: [services/llm/src/jane_llm/store.py:50](../../../../../../services/llm/src/jane_llm/store.py#L50).

```python
class BudgetCheck:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [key](jane_llm.store.md#jane_llmstorebudgetcheckkey) | Поле | ні |
| [limit](jane_llm.store.md#jane_llmstorebudgetchecklimit) | Поле | ні |
| [currency](jane_llm.store.md#jane_llmstorebudgetcheckcurrency) | Поле | ні |
| [period](jane_llm.store.md#jane_llmstorebudgetcheckperiod) | Поле | ні |
| [resets_at](jane_llm.store.md#jane_llmstorebudgetcheckresets_at) | Поле | ні |
| [__init__](jane_llm.store.md#jane_llmstorebudgetcheck__init__) | Конструктор dataclass | ні |

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_units.py:143](../../../../../../services/llm/tests/test_units.py#L143).

```python
return BudgetCheck(CounterKey("task", "t", key), limit, "USD", "day", None)
```

## jane_llm.store.BudgetCheck.__init__

**Конструктор dataclass.** Код: [services/llm/src/jane_llm/store.py:50](../../../../../../services/llm/src/jane_llm/store.py#L50).

```python
def __init__(self, key: CounterKey, limit: float, currency: str, period: str, resets_at: datetime | None) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `key` | `CounterKey` | `—` | positional-or-keyword |
| `limit` | `float` | `—` | positional-or-keyword |
| `currency` | `str` | `—` | positional-or-keyword |
| `period` | `str` | `—` | positional-or-keyword |
| `resets_at` | `datetime \| None` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_units.py:143](../../../../../../services/llm/tests/test_units.py#L143).

```python
return BudgetCheck(CounterKey("task", "t", key), limit, "USD", "day", None)
```

## jane_llm.store.BudgetCheck.key

**Поле.** Код: [services/llm/src/jane_llm/store.py:51](../../../../../../services/llm/src/jane_llm/store.py#L51).

```python
key: CounterKey
```

Доступ: читання — так; запис — ні.

## jane_llm.store.BudgetCheck.limit

**Поле.** Код: [services/llm/src/jane_llm/store.py:52](../../../../../../services/llm/src/jane_llm/store.py#L52).

```python
limit: float
```

Доступ: читання — так; запис — ні.

## jane_llm.store.BudgetCheck.currency

**Поле.** Код: [services/llm/src/jane_llm/store.py:53](../../../../../../services/llm/src/jane_llm/store.py#L53).

```python
currency: str
```

Доступ: читання — так; запис — ні.

## jane_llm.store.BudgetCheck.period

**Поле.** Код: [services/llm/src/jane_llm/store.py:54](../../../../../../services/llm/src/jane_llm/store.py#L54).

```python
period: str
```

Доступ: читання — так; запис — ні.

## jane_llm.store.BudgetCheck.resets_at

**Поле.** Код: [services/llm/src/jane_llm/store.py:55](../../../../../../services/llm/src/jane_llm/store.py#L55).

```python
resets_at: datetime | None
```

Доступ: читання — так; запис — ні.

## jane_llm.store.RateCheck

**Клас.** Код: [services/llm/src/jane_llm/store.py:59](../../../../../../services/llm/src/jane_llm/store.py#L59).

```python
class RateCheck:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [key](jane_llm.store.md#jane_llmstoreratecheckkey) | Поле | ні |
| [limit](jane_llm.store.md#jane_llmstoreratechecklimit) | Поле | ні |
| [retry_after_seconds](jane_llm.store.md#jane_llmstoreratecheckretry_after_seconds) | Поле | ні |
| [__init__](jane_llm.store.md#jane_llmstoreratecheck__init__) | Конструктор dataclass | ні |

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_units.py:168](../../../../../../services/llm/tests/test_units.py#L168).

```python
rate = RateCheck(CounterKey("platform", "platform", "rpm:1"), 2, 30)
```

## jane_llm.store.RateCheck.__init__

**Конструктор dataclass.** Код: [services/llm/src/jane_llm/store.py:59](../../../../../../services/llm/src/jane_llm/store.py#L59).

```python
def __init__(self, key: CounterKey, limit: int, retry_after_seconds: int) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `key` | `CounterKey` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |
| `retry_after_seconds` | `int` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_units.py:168](../../../../../../services/llm/tests/test_units.py#L168).

```python
rate = RateCheck(CounterKey("platform", "platform", "rpm:1"), 2, 30)
```

## jane_llm.store.RateCheck.key

**Поле.** Код: [services/llm/src/jane_llm/store.py:60](../../../../../../services/llm/src/jane_llm/store.py#L60).

```python
key: CounterKey
```

Доступ: читання — так; запис — ні.

## jane_llm.store.RateCheck.limit

**Поле.** Код: [services/llm/src/jane_llm/store.py:61](../../../../../../services/llm/src/jane_llm/store.py#L61).

```python
limit: int
```

Доступ: читання — так; запис — ні.

## jane_llm.store.RateCheck.retry_after_seconds

**Поле.** Код: [services/llm/src/jane_llm/store.py:62](../../../../../../services/llm/src/jane_llm/store.py#L62).

```python
retry_after_seconds: int
```

Доступ: читання — так; запис — ні.

## jane_llm.store.UsageRecord

**Клас.** Код: [services/llm/src/jane_llm/store.py:66](../../../../../../services/llm/src/jane_llm/store.py#L66).

```python
class UsageRecord:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [completion_id](jane_llm.store.md#jane_llmstoreusagerecordcompletion_id) | Поле | ні |
| [created_at](jane_llm.store.md#jane_llmstoreusagerecordcreated_at) | Поле | ні |
| [provider_id](jane_llm.store.md#jane_llmstoreusagerecordprovider_id) | Поле | ні |
| [model_id](jane_llm.store.md#jane_llmstoreusagerecordmodel_id) | Поле | ні |
| [purpose](jane_llm.store.md#jane_llmstoreusagerecordpurpose) | Поле | ні |
| [source_id](jane_llm.store.md#jane_llmstoreusagerecordsource_id) | Поле | ні |
| [task_id](jane_llm.store.md#jane_llmstoreusagerecordtask_id) | Поле | ні |
| [run_id](jane_llm.store.md#jane_llmstoreusagerecordrun_id) | Поле | ні |
| [input_tokens](jane_llm.store.md#jane_llmstoreusagerecordinput_tokens) | Поле | ні |
| [output_tokens](jane_llm.store.md#jane_llmstoreusagerecordoutput_tokens) | Поле | ні |
| [cost](jane_llm.store.md#jane_llmstoreusagerecordcost) | Поле | ні |
| [currency](jane_llm.store.md#jane_llmstoreusagerecordcurrency) | Поле | ні |
| [test_mode](jane_llm.store.md#jane_llmstoreusagerecordtest_mode) | Поле | ні |
| [outcome](jane_llm.store.md#jane_llmstoreusagerecordoutcome) | Поле | ні |
| [__init__](jane_llm.store.md#jane_llmstoreusagerecord__init__) | Конструктор dataclass | ні |

## jane_llm.store.UsageRecord.__init__

**Конструктор dataclass.** Код: [services/llm/src/jane_llm/store.py:66](../../../../../../services/llm/src/jane_llm/store.py#L66).

```python
def __init__(self, completion_id: str, created_at: datetime, provider_id: str, model_id: str, purpose: str, source_id: str | None, task_id: str | None, run_id: str | None, input_tokens: int, output_tokens: int, cost: float, currency: str, test_mode: bool, outcome: str = 'ok') -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `completion_id` | `str` | `—` | positional-or-keyword |
| `created_at` | `datetime` | `—` | positional-or-keyword |
| `provider_id` | `str` | `—` | positional-or-keyword |
| `model_id` | `str` | `—` | positional-or-keyword |
| `purpose` | `str` | `—` | positional-or-keyword |
| `source_id` | `str \| None` | `—` | positional-or-keyword |
| `task_id` | `str \| None` | `—` | positional-or-keyword |
| `run_id` | `str \| None` | `—` | positional-or-keyword |
| `input_tokens` | `int` | `—` | positional-or-keyword |
| `output_tokens` | `int` | `—` | positional-or-keyword |
| `cost` | `float` | `—` | positional-or-keyword |
| `currency` | `str` | `—` | positional-or-keyword |
| `test_mode` | `bool` | `—` | positional-or-keyword |
| `outcome` | `str` | `'ok'` | positional-or-keyword |

Результат: `None`.

## jane_llm.store.UsageRecord.completion_id

**Поле.** Код: [services/llm/src/jane_llm/store.py:67](../../../../../../services/llm/src/jane_llm/store.py#L67).

```python
completion_id: str
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageRecord.created_at

**Поле.** Код: [services/llm/src/jane_llm/store.py:68](../../../../../../services/llm/src/jane_llm/store.py#L68).

```python
created_at: datetime
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageRecord.provider_id

**Поле.** Код: [services/llm/src/jane_llm/store.py:69](../../../../../../services/llm/src/jane_llm/store.py#L69).

```python
provider_id: str
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageRecord.model_id

**Поле.** Код: [services/llm/src/jane_llm/store.py:70](../../../../../../services/llm/src/jane_llm/store.py#L70).

```python
model_id: str
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageRecord.purpose

**Поле.** Код: [services/llm/src/jane_llm/store.py:71](../../../../../../services/llm/src/jane_llm/store.py#L71).

```python
purpose: str
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageRecord.source_id

**Поле.** Код: [services/llm/src/jane_llm/store.py:72](../../../../../../services/llm/src/jane_llm/store.py#L72).

```python
source_id: str | None
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageRecord.task_id

**Поле.** Код: [services/llm/src/jane_llm/store.py:73](../../../../../../services/llm/src/jane_llm/store.py#L73).

```python
task_id: str | None
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageRecord.run_id

**Поле.** Код: [services/llm/src/jane_llm/store.py:74](../../../../../../services/llm/src/jane_llm/store.py#L74).

```python
run_id: str | None
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageRecord.input_tokens

**Поле.** Код: [services/llm/src/jane_llm/store.py:75](../../../../../../services/llm/src/jane_llm/store.py#L75).

```python
input_tokens: int
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageRecord.output_tokens

**Поле.** Код: [services/llm/src/jane_llm/store.py:76](../../../../../../services/llm/src/jane_llm/store.py#L76).

```python
output_tokens: int
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageRecord.cost

**Поле.** Код: [services/llm/src/jane_llm/store.py:77](../../../../../../services/llm/src/jane_llm/store.py#L77).

```python
cost: float
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageRecord.currency

**Поле.** Код: [services/llm/src/jane_llm/store.py:78](../../../../../../services/llm/src/jane_llm/store.py#L78).

```python
currency: str
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageRecord.test_mode

**Поле.** Код: [services/llm/src/jane_llm/store.py:79](../../../../../../services/llm/src/jane_llm/store.py#L79).

```python
test_mode: bool
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageRecord.outcome

**Поле.** Код: [services/llm/src/jane_llm/store.py:80](../../../../../../services/llm/src/jane_llm/store.py#L80).

```python
outcome: str = 'ok'
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageQuery

**Клас.** Код: [services/llm/src/jane_llm/store.py:84](../../../../../../services/llm/src/jane_llm/store.py#L84).

```python
class UsageQuery:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [scope_type](jane_llm.store.md#jane_llmstoreusagequeryscope_type) | Поле | ні |
| [scope_id](jane_llm.store.md#jane_llmstoreusagequeryscope_id) | Поле | ні |
| [since](jane_llm.store.md#jane_llmstoreusagequerysince) | Поле | ні |
| [until](jane_llm.store.md#jane_llmstoreusagequeryuntil) | Поле | ні |
| [group_by](jane_llm.store.md#jane_llmstoreusagequerygroup_by) | Поле | ні |
| [__init__](jane_llm.store.md#jane_llmstoreusagequery__init__) | Конструктор dataclass | ні |

## jane_llm.store.UsageQuery.__init__

**Конструктор dataclass.** Код: [services/llm/src/jane_llm/store.py:84](../../../../../../services/llm/src/jane_llm/store.py#L84).

```python
def __init__(self, scope_type: str | None = None, scope_id: str | None = None, since: datetime | None = None, until: datetime | None = None, group_by: str = 'day') -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `scope_type` | `str \| None` | `None` | positional-or-keyword |
| `scope_id` | `str \| None` | `None` | positional-or-keyword |
| `since` | `datetime \| None` | `None` | positional-or-keyword |
| `until` | `datetime \| None` | `None` | positional-or-keyword |
| `group_by` | `str` | `'day'` | positional-or-keyword |

Результат: `None`.

## jane_llm.store.UsageQuery.scope_type

**Поле.** Код: [services/llm/src/jane_llm/store.py:85](../../../../../../services/llm/src/jane_llm/store.py#L85).

```python
scope_type: str | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageQuery.scope_id

**Поле.** Код: [services/llm/src/jane_llm/store.py:86](../../../../../../services/llm/src/jane_llm/store.py#L86).

```python
scope_id: str | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageQuery.since

**Поле.** Код: [services/llm/src/jane_llm/store.py:87](../../../../../../services/llm/src/jane_llm/store.py#L87).

```python
since: datetime | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageQuery.until

**Поле.** Код: [services/llm/src/jane_llm/store.py:88](../../../../../../services/llm/src/jane_llm/store.py#L88).

```python
until: datetime | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageQuery.group_by

**Поле.** Код: [services/llm/src/jane_llm/store.py:89](../../../../../../services/llm/src/jane_llm/store.py#L89).

```python
group_by: str = 'day'
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageRow

**Клас.** Код: [services/llm/src/jane_llm/store.py:93](../../../../../../services/llm/src/jane_llm/store.py#L93).

```python
class UsageRow:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [requests](jane_llm.store.md#jane_llmstoreusagerowrequests) | Поле | ні |
| [input_tokens](jane_llm.store.md#jane_llmstoreusagerowinput_tokens) | Поле | ні |
| [output_tokens](jane_llm.store.md#jane_llmstoreusagerowoutput_tokens) | Поле | ні |
| [cost](jane_llm.store.md#jane_llmstoreusagerowcost) | Поле | ні |
| [currency](jane_llm.store.md#jane_llmstoreusagerowcurrency) | Поле | ні |
| [period_start](jane_llm.store.md#jane_llmstoreusagerowperiod_start) | Поле | ні |
| [scope_type](jane_llm.store.md#jane_llmstoreusagerowscope_type) | Поле | ні |
| [scope_id](jane_llm.store.md#jane_llmstoreusagerowscope_id) | Поле | ні |
| [model](jane_llm.store.md#jane_llmstoreusagerowmodel) | Поле | ні |
| [purpose](jane_llm.store.md#jane_llmstoreusagerowpurpose) | Поле | ні |
| [test_mode](jane_llm.store.md#jane_llmstoreusagerowtest_mode) | Поле | ні |
| [extra](jane_llm.store.md#jane_llmstoreusagerowextra) | Поле | ні |
| [__init__](jane_llm.store.md#jane_llmstoreusagerow__init__) | Конструктор dataclass | ні |

## jane_llm.store.UsageRow.__init__

**Конструктор dataclass.** Код: [services/llm/src/jane_llm/store.py:93](../../../../../../services/llm/src/jane_llm/store.py#L93).

```python
def __init__(self, requests: int = 0, input_tokens: int = 0, output_tokens: int = 0, cost: float = 0.0, currency: str = 'USD', period_start: datetime | None = None, scope_type: str | None = None, scope_id: str | None = None, model: str | None = None, purpose: str | None = None, test_mode: bool | None = None, extra: dict[str, Any] = <factory dict>) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `requests` | `int` | `0` | positional-or-keyword |
| `input_tokens` | `int` | `0` | positional-or-keyword |
| `output_tokens` | `int` | `0` | positional-or-keyword |
| `cost` | `float` | `0.0` | positional-or-keyword |
| `currency` | `str` | `'USD'` | positional-or-keyword |
| `period_start` | `datetime \| None` | `None` | positional-or-keyword |
| `scope_type` | `str \| None` | `None` | positional-or-keyword |
| `scope_id` | `str \| None` | `None` | positional-or-keyword |
| `model` | `str \| None` | `None` | positional-or-keyword |
| `purpose` | `str \| None` | `None` | positional-or-keyword |
| `test_mode` | `bool \| None` | `None` | positional-or-keyword |
| `extra` | `dict[str, Any]` | `factory: dict` | positional-or-keyword |

Результат: `None`.

## jane_llm.store.UsageRow.requests

**Поле.** Код: [services/llm/src/jane_llm/store.py:94](../../../../../../services/llm/src/jane_llm/store.py#L94).

```python
requests: int = 0
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageRow.input_tokens

**Поле.** Код: [services/llm/src/jane_llm/store.py:95](../../../../../../services/llm/src/jane_llm/store.py#L95).

```python
input_tokens: int = 0
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageRow.output_tokens

**Поле.** Код: [services/llm/src/jane_llm/store.py:96](../../../../../../services/llm/src/jane_llm/store.py#L96).

```python
output_tokens: int = 0
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageRow.cost

**Поле.** Код: [services/llm/src/jane_llm/store.py:97](../../../../../../services/llm/src/jane_llm/store.py#L97).

```python
cost: float = 0.0
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageRow.currency

**Поле.** Код: [services/llm/src/jane_llm/store.py:98](../../../../../../services/llm/src/jane_llm/store.py#L98).

```python
currency: str = 'USD'
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageRow.period_start

**Поле.** Код: [services/llm/src/jane_llm/store.py:99](../../../../../../services/llm/src/jane_llm/store.py#L99).

```python
period_start: datetime | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageRow.scope_type

**Поле.** Код: [services/llm/src/jane_llm/store.py:100](../../../../../../services/llm/src/jane_llm/store.py#L100).

```python
scope_type: str | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageRow.scope_id

**Поле.** Код: [services/llm/src/jane_llm/store.py:101](../../../../../../services/llm/src/jane_llm/store.py#L101).

```python
scope_id: str | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageRow.model

**Поле.** Код: [services/llm/src/jane_llm/store.py:102](../../../../../../services/llm/src/jane_llm/store.py#L102).

```python
model: str | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageRow.purpose

**Поле.** Код: [services/llm/src/jane_llm/store.py:103](../../../../../../services/llm/src/jane_llm/store.py#L103).

```python
purpose: str | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageRow.test_mode

**Поле.** Код: [services/llm/src/jane_llm/store.py:104](../../../../../../services/llm/src/jane_llm/store.py#L104).

```python
test_mode: bool | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.store.UsageRow.extra

**Поле.** Код: [services/llm/src/jane_llm/store.py:105](../../../../../../services/llm/src/jane_llm/store.py#L105).

```python
extra: dict[str, Any] = field(default_factory=dict)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## jane_llm.store.BudgetExceeded

**Клас.** Код: [services/llm/src/jane_llm/store.py:108](../../../../../../services/llm/src/jane_llm/store.py#L108).

```python
class BudgetExceeded(Exception):
```

Базові типи / інтерфейси: `Exception`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_llm.store.md#jane_llmstorebudgetexceeded__init__) | Конструктор | ні |

## jane_llm.store.BudgetExceeded.__init__

**Конструктор.** Код: [services/llm/src/jane_llm/store.py:109](../../../../../../services/llm/src/jane_llm/store.py#L109).

```python
def __init__(self, check: BudgetCheck, spent: float, reserved: float, requested: float) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `check` | `BudgetCheck` | `—` | positional-or-keyword |
| `spent` | `float` | `—` | positional-or-keyword |
| `reserved` | `float` | `—` | positional-or-keyword |
| `requested` | `float` | `—` | positional-or-keyword |

Результат: `None`.

## jane_llm.store.RateExceeded

**Клас.** Код: [services/llm/src/jane_llm/store.py:114](../../../../../../services/llm/src/jane_llm/store.py#L114).

```python
class RateExceeded(Exception):
```

Базові типи / інтерфейси: `Exception`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_llm.store.md#jane_llmstorerateexceeded__init__) | Конструктор | ні |
| [check](jane_llm.store.md#jane_llmstorerateexceededcheck) | Поле екземпляра | ні |

## jane_llm.store.RateExceeded.__init__

**Конструктор.** Код: [services/llm/src/jane_llm/store.py:115](../../../../../../services/llm/src/jane_llm/store.py#L115).

```python
def __init__(self, check: RateCheck) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `check` | `RateCheck` | `—` | positional-or-keyword |

Результат: `None`.

## jane_llm.store.RateExceeded.check

**Поле екземпляра.** Код: [services/llm/src/jane_llm/store.py:116](../../../../../../services/llm/src/jane_llm/store.py#L116).

```python
self.check = check
```

## jane_llm.store.Store

**Клас.** Код: [services/llm/src/jane_llm/store.py:121](../../../../../../services/llm/src/jane_llm/store.py#L121).

```python
class Store(Protocol):
```

Базові типи / інтерфейси: `Protocol`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [migrate](jane_llm.store.md#jane_llmstorestoremigrate) | Метод | ні |
| [ping](jane_llm.store.md#jane_llmstorestoreping) | Метод | ні |
| [close](jane_llm.store.md#jane_llmstorestoreclose) | Метод | ні |
| [get_doc](jane_llm.store.md#jane_llmstorestoreget_doc) | Метод | ні |
| [list_docs](jane_llm.store.md#jane_llmstorestorelist_docs) | Метод | ні |
| [put_doc](jane_llm.store.md#jane_llmstorestoreput_doc) | Метод | ні |
| [seed_doc](jane_llm.store.md#jane_llmstorestoreseed_doc) | Метод | ні |
| [delete_doc](jane_llm.store.md#jane_llmstorestoredelete_doc) | Метод | ні |
| [reserve](jane_llm.store.md#jane_llmstorestorereserve) | Метод | ні |
| [settle](jane_llm.store.md#jane_llmstorestoresettle) | Метод | ні |
| [release](jane_llm.store.md#jane_llmstorestorerelease) | Метод | ні |
| [counter](jane_llm.store.md#jane_llmstorestorecounter) | Метод | ні |
| [usage](jane_llm.store.md#jane_llmstorestoreusage) | Метод | ні |
| [save_invocation](jane_llm.store.md#jane_llmstorestoresave_invocation) | Метод | ні |
| [get_invocation](jane_llm.store.md#jane_llmstorestoreget_invocation) | Метод | ні |
| [idempotency](jane_llm.store.md#jane_llmstorestoreidempotency) | Поле | ні |
| [jobs](jane_llm.store.md#jane_llmstorestorejobs) | Поле | ні |

## jane_llm.store.Store.migrate

**Метод.** Код: [services/llm/src/jane_llm/store.py:122](../../../../../../services/llm/src/jane_llm/store.py#L122).

```python
def migrate(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_llm.store.Store.ping

**Метод.** Код: [services/llm/src/jane_llm/store.py:123](../../../../../../services/llm/src/jane_llm/store.py#L123).

```python
def ping(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_llm.store.Store.close

**Метод.** Код: [services/llm/src/jane_llm/store.py:124](../../../../../../services/llm/src/jane_llm/store.py#L124).

```python
def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_llm.store.Store.get_doc

**Метод.** Код: [services/llm/src/jane_llm/store.py:127](../../../../../../services/llm/src/jane_llm/store.py#L127).

```python
def get_doc(self, kind: ConfigKind, key: str) -> dict[str, Any] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `kind` | `ConfigKind` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any] | None`.

## jane_llm.store.Store.list_docs

**Метод.** Код: [services/llm/src/jane_llm/store.py:128](../../../../../../services/llm/src/jane_llm/store.py#L128).

```python
def list_docs(self, kind: ConfigKind) -> list[dict[str, Any]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `kind` | `ConfigKind` | `—` | positional-or-keyword |

Результат: `list[dict[str, Any]]`.

## jane_llm.store.Store.put_doc

**Метод.** Код: [services/llm/src/jane_llm/store.py:129](../../../../../../services/llm/src/jane_llm/store.py#L129).

```python
def put_doc(self, kind: ConfigKind, key: str, doc: dict[str, Any]) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `kind` | `ConfigKind` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |
| `doc` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `bool`.

### Опис із вихідного коду

```text
Create or replace; returns True if created.
```

## jane_llm.store.Store.seed_doc

**Метод.** Код: [services/llm/src/jane_llm/store.py:133](../../../../../../services/llm/src/jane_llm/store.py#L133).

```python
def seed_doc(self, kind: ConfigKind, key: str, doc: dict[str, Any]) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `kind` | `ConfigKind` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |
| `doc` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `bool`.

### Опис із вихідного коду

```text
Create only if absent; returns True if created.
```

## jane_llm.store.Store.delete_doc

**Метод.** Код: [services/llm/src/jane_llm/store.py:137](../../../../../../services/llm/src/jane_llm/store.py#L137).

```python
def delete_doc(self, kind: ConfigKind, key: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `kind` | `ConfigKind` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_llm.store.Store.reserve

**Метод.** Код: [services/llm/src/jane_llm/store.py:140](../../../../../../services/llm/src/jane_llm/store.py#L140).

```python
def reserve(self, reservation_id: str, amount: float, budgets: list[BudgetCheck], rates: list[RateCheck], now: datetime, stale_after: timedelta) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `reservation_id` | `str` | `—` | positional-or-keyword |
| `amount` | `float` | `—` | positional-or-keyword |
| `budgets` | `list[BudgetCheck]` | `—` | positional-or-keyword |
| `rates` | `list[RateCheck]` | `—` | positional-or-keyword |
| `now` | `datetime` | `—` | positional-or-keyword |
| `stale_after` | `timedelta` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Atomically check budgets (spent + reserved + amount <= limit) and rates, then reserve.
```

## jane_llm.store.Store.settle

**Метод.** Код: [services/llm/src/jane_llm/store.py:152](../../../../../../services/llm/src/jane_llm/store.py#L152).

```python
def settle(self, reservation_id: str, cost: float, usage: UsageRecord | None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `reservation_id` | `str` | `—` | positional-or-keyword |
| `cost` | `float` | `—` | positional-or-keyword |
| `usage` | `UsageRecord \| None` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Replace a reservation by the actual cost and append the usage record.
```

## jane_llm.store.Store.release

**Метод.** Код: [services/llm/src/jane_llm/store.py:156](../../../../../../services/llm/src/jane_llm/store.py#L156).

```python
def release(self, reservation_id: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `reservation_id` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_llm.store.Store.counter

**Метод.** Код: [services/llm/src/jane_llm/store.py:157](../../../../../../services/llm/src/jane_llm/store.py#L157).

```python
def counter(self, key: CounterKey) -> tuple[float, float]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `key` | `CounterKey` | `—` | positional-or-keyword |

Результат: `tuple[float, float]`.

### Опис із вихідного коду

```text
``(spent, reserved)`` of a counter row (zeros if absent).
```

## jane_llm.store.Store.usage

**Метод.** Код: [services/llm/src/jane_llm/store.py:161](../../../../../../services/llm/src/jane_llm/store.py#L161).

```python
def usage(self, query: UsageQuery) -> list[UsageRow]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `query` | `UsageQuery` | `—` | positional-or-keyword |

Результат: `list[UsageRow]`.

## jane_llm.store.Store.save_invocation

**Метод.** Код: [services/llm/src/jane_llm/store.py:164](../../../../../../services/llm/src/jane_llm/store.py#L164).

```python
def save_invocation(self, invocation_id: str, result: dict[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `invocation_id` | `str` | `—` | positional-or-keyword |
| `result` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.

## jane_llm.store.Store.get_invocation

**Метод.** Код: [services/llm/src/jane_llm/store.py:165](../../../../../../services/llm/src/jane_llm/store.py#L165).

```python
def get_invocation(self, invocation_id: str) -> dict[str, Any] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `invocation_id` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any] | None`.

## jane_llm.store.Store.idempotency

**Поле.** Код: [services/llm/src/jane_llm/store.py:168](../../../../../../services/llm/src/jane_llm/store.py#L168).

```python
idempotency: IdempotencyStore
```

Доступ: читання — так; запис — так.

## jane_llm.store.Store.jobs

**Поле.** Код: [services/llm/src/jane_llm/store.py:169](../../../../../../services/llm/src/jane_llm/store.py#L169).

```python
jobs: JobStore
```

Доступ: читання — так; запис — так.

## jane_llm.store.MemoryStore

**Клас.** Код: [services/llm/src/jane_llm/store.py:219](../../../../../../services/llm/src/jane_llm/store.py#L219).

```python
class MemoryStore:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_llm.store.md#jane_llmstorememorystore__init__) | Конструктор | ні |
| [idempotency](jane_llm.store.md#jane_llmstorememorystoreidempotency) | Поле екземпляра | ні |
| [jobs](jane_llm.store.md#jane_llmstorememorystorejobs) | Поле екземпляра | ні |
| [migrate](jane_llm.store.md#jane_llmstorememorystoremigrate) | Метод | ні |
| [ping](jane_llm.store.md#jane_llmstorememorystoreping) | Метод | ні |
| [close](jane_llm.store.md#jane_llmstorememorystoreclose) | Метод | ні |
| [get_doc](jane_llm.store.md#jane_llmstorememorystoreget_doc) | Метод | ні |
| [list_docs](jane_llm.store.md#jane_llmstorememorystorelist_docs) | Метод | ні |
| [put_doc](jane_llm.store.md#jane_llmstorememorystoreput_doc) | Метод | ні |
| [seed_doc](jane_llm.store.md#jane_llmstorememorystoreseed_doc) | Метод | ні |
| [delete_doc](jane_llm.store.md#jane_llmstorememorystoredelete_doc) | Метод | ні |
| [reserve](jane_llm.store.md#jane_llmstorememorystorereserve) | Метод | ні |
| [settle](jane_llm.store.md#jane_llmstorememorystoresettle) | Метод | ні |
| [release](jane_llm.store.md#jane_llmstorememorystorerelease) | Метод | ні |
| [counter](jane_llm.store.md#jane_llmstorememorystorecounter) | Метод | ні |
| [usage](jane_llm.store.md#jane_llmstorememorystoreusage) | Метод | ні |
| [save_invocation](jane_llm.store.md#jane_llmstorememorystoresave_invocation) | Метод | ні |
| [get_invocation](jane_llm.store.md#jane_llmstorememorystoreget_invocation) | Метод | ні |

### Опис із вихідного коду

```text
In-process store with the same semantics as :class:`PostgresStore` (tests, demos).
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_llm_budget.py:87](../../../../../../services/assistant/tests/test_llm_budget.py#L87).

```python
app = build_llm_app(
        LlmSettings(log_format="console", store="memory"),
        store=MemoryStore(),
        adapters={**ADAPTERS, "fake": provider},
    )
```

Контекст і передумови: [services/llm/tests/conftest.py:68](../../../../../../services/llm/tests/conftest.py#L68).

```python
memory = MemoryStore()
```

## jane_llm.store.MemoryStore.__init__

**Конструктор.** Код: [services/llm/src/jane_llm/store.py:222](../../../../../../services/llm/src/jane_llm/store.py#L222).

```python
def __init__(self, jobs: JobLimits | None=None, idempotency: IdempotencyLimits | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `jobs` | `JobLimits \| None` | `None` | positional-or-keyword |
| `idempotency` | `IdempotencyLimits \| None` | `None` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_llm_budget.py:87](../../../../../../services/assistant/tests/test_llm_budget.py#L87).

```python
app = build_llm_app(
        LlmSettings(log_format="console", store="memory"),
        store=MemoryStore(),
        adapters={**ADAPTERS, "fake": provider},
    )
```

Контекст і передумови: [services/llm/tests/conftest.py:68](../../../../../../services/llm/tests/conftest.py#L68).

```python
memory = MemoryStore()
```

## jane_llm.store.MemoryStore.idempotency

**Поле екземпляра.** Код: [services/llm/src/jane_llm/store.py:229](../../../../../../services/llm/src/jane_llm/store.py#L229).

```python
self.idempotency: IdempotencyStore = InMemoryIdempotencyStore(idempotency)
```

## jane_llm.store.MemoryStore.jobs

**Поле екземпляра.** Код: [services/llm/src/jane_llm/store.py:230](../../../../../../services/llm/src/jane_llm/store.py#L230).

```python
self.jobs: JobStore = InMemoryJobStore(jobs)
```

## jane_llm.store.MemoryStore.migrate

**Метод.** Код: [services/llm/src/jane_llm/store.py:232](../../../../../../services/llm/src/jane_llm/store.py#L232).

```python
def migrate(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_llm.store.MemoryStore.ping

**Метод.** Код: [services/llm/src/jane_llm/store.py:235](../../../../../../services/llm/src/jane_llm/store.py#L235).

```python
def ping(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_llm.store.MemoryStore.close

**Метод.** Код: [services/llm/src/jane_llm/store.py:238](../../../../../../services/llm/src/jane_llm/store.py#L238).

```python
def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_llm.store.MemoryStore.get_doc

**Метод.** Код: [services/llm/src/jane_llm/store.py:241](../../../../../../services/llm/src/jane_llm/store.py#L241).

```python
def get_doc(self, kind: ConfigKind, key: str) -> dict[str, Any] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `kind` | `ConfigKind` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any] | None`.

## jane_llm.store.MemoryStore.list_docs

**Метод.** Код: [services/llm/src/jane_llm/store.py:246](../../../../../../services/llm/src/jane_llm/store.py#L246).

```python
def list_docs(self, kind: ConfigKind) -> list[dict[str, Any]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `kind` | `ConfigKind` | `—` | positional-or-keyword |

Результат: `list[dict[str, Any]]`.

## jane_llm.store.MemoryStore.put_doc

**Метод.** Код: [services/llm/src/jane_llm/store.py:250](../../../../../../services/llm/src/jane_llm/store.py#L250).

```python
def put_doc(self, kind: ConfigKind, key: str, doc: dict[str, Any]) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `kind` | `ConfigKind` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |
| `doc` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_llm.store.MemoryStore.seed_doc

**Метод.** Код: [services/llm/src/jane_llm/store.py:256](../../../../../../services/llm/src/jane_llm/store.py#L256).

```python
def seed_doc(self, kind: ConfigKind, key: str, doc: dict[str, Any]) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `kind` | `ConfigKind` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |
| `doc` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_llm.store.MemoryStore.delete_doc

**Метод.** Код: [services/llm/src/jane_llm/store.py:263](../../../../../../services/llm/src/jane_llm/store.py#L263).

```python
def delete_doc(self, kind: ConfigKind, key: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `kind` | `ConfigKind` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_llm.store.MemoryStore.reserve

**Метод.** Код: [services/llm/src/jane_llm/store.py:276](../../../../../../services/llm/src/jane_llm/store.py#L276).

```python
def reserve(self, reservation_id: str, amount: float, budgets: list[BudgetCheck], rates: list[RateCheck], now: datetime, stale_after: timedelta) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `reservation_id` | `str` | `—` | positional-or-keyword |
| `amount` | `float` | `—` | positional-or-keyword |
| `budgets` | `list[BudgetCheck]` | `—` | positional-or-keyword |
| `rates` | `list[RateCheck]` | `—` | positional-or-keyword |
| `now` | `datetime` | `—` | positional-or-keyword |
| `stale_after` | `timedelta` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `BudgetExceeded`, `RateExceeded`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_units.py:150](../../../../../../services/llm/tests/test_units.py#L150).

```python
store.reserve("r1", 0.6, [_check(1.0)], [], now, ttl)
```

Контекст і передумови: [services/llm/tests/test_units.py:155](../../../../../../services/llm/tests/test_units.py#L155).

```python
store.reserve("r3", 0.6, [_check(1.0)], [], now, ttl)
```

## jane_llm.store.MemoryStore.settle

**Метод.** Код: [services/llm/src/jane_llm/store.py:302](../../../../../../services/llm/src/jane_llm/store.py#L302).

```python
def settle(self, reservation_id: str, cost: float, usage: UsageRecord | None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `reservation_id` | `str` | `—` | positional-or-keyword |
| `cost` | `float` | `—` | positional-or-keyword |
| `usage` | `UsageRecord \| None` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_units.py:153](../../../../../../services/llm/tests/test_units.py#L153).

```python
store.settle("r1", 0.2, None)
```

## jane_llm.store.MemoryStore.release

**Метод.** Код: [services/llm/src/jane_llm/store.py:314](../../../../../../services/llm/src/jane_llm/store.py#L314).

```python
def release(self, reservation_id: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `reservation_id` | `str` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_units.py:156](../../../../../../services/llm/tests/test_units.py#L156).

```python
store.release("r3")
```

## jane_llm.store.MemoryStore.counter

**Метод.** Код: [services/llm/src/jane_llm/store.py:322](../../../../../../services/llm/src/jane_llm/store.py#L322).

```python
def counter(self, key: CounterKey) -> tuple[float, float]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `key` | `CounterKey` | `—` | positional-or-keyword |

Результат: `tuple[float, float]`.

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_units.py:161](../../../../../../services/llm/tests/test_units.py#L161).

```python
spent, reserved = store.counter(CounterKey("task", "t", "k"))
```

Контекст і передумови: [services/llm/tests/test_units.py:154](../../../../../../services/llm/tests/test_units.py#L154).

```python
assert store.counter(CounterKey("task", "t", "k")) == (0.2, 0.0)
```

## jane_llm.store.MemoryStore.usage

**Метод.** Код: [services/llm/src/jane_llm/store.py:327](../../../../../../services/llm/src/jane_llm/store.py#L327).

```python
def usage(self, query: UsageQuery) -> list[UsageRow]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `query` | `UsageQuery` | `—` | positional-or-keyword |

Результат: `list[UsageRow]`.

## jane_llm.store.MemoryStore.save_invocation

**Метод.** Код: [services/llm/src/jane_llm/store.py:342](../../../../../../services/llm/src/jane_llm/store.py#L342).

```python
def save_invocation(self, invocation_id: str, result: dict[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `invocation_id` | `str` | `—` | positional-or-keyword |
| `result` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.

## jane_llm.store.MemoryStore.get_invocation

**Метод.** Код: [services/llm/src/jane_llm/store.py:346](../../../../../../services/llm/src/jane_llm/store.py#L346).

```python
def get_invocation(self, invocation_id: str) -> dict[str, Any] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `invocation_id` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any] | None`.

## jane_llm.store.PostgresStore

**Клас.** Код: [services/llm/src/jane_llm/store.py:375](../../../../../../services/llm/src/jane_llm/store.py#L375).

```python
class PostgresStore:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_llm.store.md#jane_llmstorepostgresstore__init__) | Конструктор | ні |
| [schema](jane_llm.store.md#jane_llmstorepostgresstoreschema) | Поле екземпляра | ні |
| [pool](jane_llm.store.md#jane_llmstorepostgresstorepool) | Поле екземпляра | ні |
| [pg_idempotency](jane_llm.store.md#jane_llmstorepostgresstorepg_idempotency) | Поле екземпляра | ні |
| [pg_jobs](jane_llm.store.md#jane_llmstorepostgresstorepg_jobs) | Поле екземпляра | ні |
| [idempotency](jane_llm.store.md#jane_llmstorepostgresstoreidempotency) | Поле екземпляра | ні |
| [jobs](jane_llm.store.md#jane_llmstorepostgresstorejobs) | Поле екземпляра | ні |
| [migrate](jane_llm.store.md#jane_llmstorepostgresstoremigrate) | Метод | ні |
| [ping](jane_llm.store.md#jane_llmstorepostgresstoreping) | Метод | ні |
| [close](jane_llm.store.md#jane_llmstorepostgresstoreclose) | Метод | ні |
| [get_doc](jane_llm.store.md#jane_llmstorepostgresstoreget_doc) | Метод | ні |
| [list_docs](jane_llm.store.md#jane_llmstorepostgresstorelist_docs) | Метод | ні |
| [put_doc](jane_llm.store.md#jane_llmstorepostgresstoreput_doc) | Метод | ні |
| [seed_doc](jane_llm.store.md#jane_llmstorepostgresstoreseed_doc) | Метод | ні |
| [delete_doc](jane_llm.store.md#jane_llmstorepostgresstoredelete_doc) | Метод | ні |
| [reserve](jane_llm.store.md#jane_llmstorepostgresstorereserve) | Метод | ні |
| [settle](jane_llm.store.md#jane_llmstorepostgresstoresettle) | Метод | ні |
| [release](jane_llm.store.md#jane_llmstorepostgresstorerelease) | Метод | ні |
| [counter](jane_llm.store.md#jane_llmstorepostgresstorecounter) | Метод | ні |
| [usage](jane_llm.store.md#jane_llmstorepostgresstoreusage) | Метод | ні |
| [save_invocation](jane_llm.store.md#jane_llmstorepostgresstoresave_invocation) | Метод | ні |
| [get_invocation](jane_llm.store.md#jane_llmstorepostgresstoreget_invocation) | Метод | ні |

### Опис із вихідного коду

```text
Store in the service's own PostgreSQL schema; safe for several instances.
```

### Приклади з тестів

Контекст і передумови: [services/llm/tests/conftest.py:75](../../../../../../services/llm/tests/conftest.py#L75).

```python
store = PostgresStore(
            dsn, schema, min_size=defaults.db_pool_min_size, max_size=defaults.db_pool_max_size
        )
```

## jane_llm.store.PostgresStore.__init__

**Конструктор.** Код: [services/llm/src/jane_llm/store.py:378](../../../../../../services/llm/src/jane_llm/store.py#L378).

```python
def __init__(self, dsn: str, schema: str, *, min_size: int, max_size: int, owner: str | None=None, leases: LeaseLimits | None=None, job_retention_s: float | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `dsn` | `str` | `—` | positional-or-keyword |
| `schema` | `str` | `—` | positional-or-keyword |
| `min_size` | `int` | `—` | keyword-only |
| `max_size` | `int` | `—` | keyword-only |
| `owner` | `str \| None` | `None` | keyword-only |
| `leases` | `LeaseLimits \| None` | `None` | keyword-only |
| `job_retention_s` | `float \| None` | `None` | keyword-only |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/llm/tests/conftest.py:75](../../../../../../services/llm/tests/conftest.py#L75).

```python
store = PostgresStore(
            dsn, schema, min_size=defaults.db_pool_min_size, max_size=defaults.db_pool_max_size
        )
```

## jane_llm.store.PostgresStore.schema

**Поле екземпляра.** Код: [services/llm/src/jane_llm/store.py:393](../../../../../../services/llm/src/jane_llm/store.py#L393).

```python
self.schema = schema
```

## jane_llm.store.PostgresStore.pool

**Поле екземпляра.** Код: [services/llm/src/jane_llm/store.py:394](../../../../../../services/llm/src/jane_llm/store.py#L394).

```python
self.pool = ConnectionPool(dsn, min_size=min_size, max_size=max_size, open=True)
```

## jane_llm.store.PostgresStore.pg_idempotency

**Поле екземпляра.** Код: [services/llm/src/jane_llm/store.py:399](../../../../../../services/llm/src/jane_llm/store.py#L399).

```python
self.pg_idempotency = PgIdempotencyStore(tx, owner=owner, in_progress_lease_s=leases.in_progress_lease_ms / 1000, schema=schema, layout='json')
```

## jane_llm.store.PostgresStore.pg_jobs

**Поле екземпляра.** Код: [services/llm/src/jane_llm/store.py:406](../../../../../../services/llm/src/jane_llm/store.py#L406).

```python
self.pg_jobs = PgJobStore(tx, owner=owner, lease_s=leases.job_lease_ms / 1000, retention_s=JobLimits().job_retention_seconds if job_retention_s is None else job_retention_s, schema=schema, doc_column='job')
```

## jane_llm.store.PostgresStore.idempotency

**Поле екземпляра.** Код: [services/llm/src/jane_llm/store.py:414](../../../../../../services/llm/src/jane_llm/store.py#L414).

```python
self.idempotency: IdempotencyStore = self.pg_idempotency
```

## jane_llm.store.PostgresStore.jobs

**Поле екземпляра.** Код: [services/llm/src/jane_llm/store.py:415](../../../../../../services/llm/src/jane_llm/store.py#L415).

```python
self.jobs: JobStore = self.pg_jobs
```

## jane_llm.store.PostgresStore.migrate

**Метод.** Код: [services/llm/src/jane_llm/store.py:425](../../../../../../services/llm/src/jane_llm/store.py#L425).

```python
def migrate(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_llm.store.PostgresStore.ping

**Метод.** Код: [services/llm/src/jane_llm/store.py:433](../../../../../../services/llm/src/jane_llm/store.py#L433).

```python
def ping(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_llm.store.PostgresStore.close

**Метод.** Код: [services/llm/src/jane_llm/store.py:438](../../../../../../services/llm/src/jane_llm/store.py#L438).

```python
def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_llm.store.PostgresStore.get_doc

**Метод.** Код: [services/llm/src/jane_llm/store.py:442](../../../../../../services/llm/src/jane_llm/store.py#L442).

```python
def get_doc(self, kind: ConfigKind, key: str) -> dict[str, Any] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `kind` | `ConfigKind` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any] | None`.

## jane_llm.store.PostgresStore.list_docs

**Метод.** Код: [services/llm/src/jane_llm/store.py:448](../../../../../../services/llm/src/jane_llm/store.py#L448).

```python
def list_docs(self, kind: ConfigKind) -> list[dict[str, Any]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `kind` | `ConfigKind` | `—` | positional-or-keyword |

Результат: `list[dict[str, Any]]`.

## jane_llm.store.PostgresStore.put_doc

**Метод.** Код: [services/llm/src/jane_llm/store.py:453](../../../../../../services/llm/src/jane_llm/store.py#L453).

```python
def put_doc(self, kind: ConfigKind, key: str, doc: dict[str, Any]) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `kind` | `ConfigKind` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |
| `doc` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_llm.store.PostgresStore.seed_doc

**Метод.** Код: [services/llm/src/jane_llm/store.py:464](../../../../../../services/llm/src/jane_llm/store.py#L464).

```python
def seed_doc(self, kind: ConfigKind, key: str, doc: dict[str, Any]) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `kind` | `ConfigKind` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |
| `doc` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_llm.store.PostgresStore.delete_doc

**Метод.** Код: [services/llm/src/jane_llm/store.py:473](../../../../../../services/llm/src/jane_llm/store.py#L473).

```python
def delete_doc(self, kind: ConfigKind, key: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `kind` | `ConfigKind` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_llm.store.PostgresStore.reserve

**Метод.** Код: [services/llm/src/jane_llm/store.py:494](../../../../../../services/llm/src/jane_llm/store.py#L494).

```python
def reserve(self, reservation_id: str, amount: float, budgets: list[BudgetCheck], rates: list[RateCheck], now: datetime, stale_after: timedelta) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `reservation_id` | `str` | `—` | positional-or-keyword |
| `amount` | `float` | `—` | positional-or-keyword |
| `budgets` | `list[BudgetCheck]` | `—` | positional-or-keyword |
| `rates` | `list[RateCheck]` | `—` | positional-or-keyword |
| `now` | `datetime` | `—` | positional-or-keyword |
| `stale_after` | `timedelta` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `BudgetExceeded`, `RateExceeded`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_llm.store.PostgresStore.settle

**Метод.** Код: [services/llm/src/jane_llm/store.py:576](../../../../../../services/llm/src/jane_llm/store.py#L576).

```python
def settle(self, reservation_id: str, cost: float, usage: UsageRecord | None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `reservation_id` | `str` | `—` | positional-or-keyword |
| `cost` | `float` | `—` | positional-or-keyword |
| `usage` | `UsageRecord \| None` | `—` | positional-or-keyword |

Результат: `None`.

## jane_llm.store.PostgresStore.release

**Метод.** Код: [services/llm/src/jane_llm/store.py:587](../../../../../../services/llm/src/jane_llm/store.py#L587).

```python
def release(self, reservation_id: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `reservation_id` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_llm.store.PostgresStore.counter

**Метод.** Код: [services/llm/src/jane_llm/store.py:591](../../../../../../services/llm/src/jane_llm/store.py#L591).

```python
def counter(self, key: CounterKey) -> tuple[float, float]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `key` | `CounterKey` | `—` | positional-or-keyword |

Результат: `tuple[float, float]`.

## jane_llm.store.PostgresStore.usage

**Метод.** Код: [services/llm/src/jane_llm/store.py:601](../../../../../../services/llm/src/jane_llm/store.py#L601).

```python
def usage(self, query: UsageQuery) -> list[UsageRow]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `query` | `UsageQuery` | `—` | positional-or-keyword |

Результат: `list[UsageRow]`.

## jane_llm.store.PostgresStore.save_invocation

**Метод.** Код: [services/llm/src/jane_llm/store.py:651](../../../../../../services/llm/src/jane_llm/store.py#L651).

```python
def save_invocation(self, invocation_id: str, result: dict[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `invocation_id` | `str` | `—` | positional-or-keyword |
| `result` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.

## jane_llm.store.PostgresStore.get_invocation

**Метод.** Код: [services/llm/src/jane_llm/store.py:659](../../../../../../services/llm/src/jane_llm/store.py#L659).

```python
def get_invocation(self, invocation_id: str) -> dict[str, Any] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `invocation_id` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any] | None`.

## jane_llm.store.iter_keys

**Функція.** Код: [services/llm/src/jane_llm/store.py:668](../../../../../../services/llm/src/jane_llm/store.py#L668).

```python
def iter_keys(checks: Iterable[BudgetCheck]) -> list[CounterKey]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `checks` | `Iterable[BudgetCheck]` | `—` | positional-or-keyword |

Результат: `list[CounterKey]`.
