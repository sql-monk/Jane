# jane_telegram_collector.stores

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_telegram_collector.stores.SqliteJobStore](#jane_telegram_collectorstoressqlitejobstore)
- [jane_telegram_collector.stores.SqliteJobStore.__init__](#jane_telegram_collectorstoressqlitejobstore__init__)
- [jane_telegram_collector.stores.SqliteJobStore.state](#jane_telegram_collectorstoressqlitejobstorestate)
- [jane_telegram_collector.stores.SqliteJobStore.instance_id](#jane_telegram_collectorstoressqlitejobstoreinstance_id)
- [jane_telegram_collector.stores.SqliteIdempotencyStore](#jane_telegram_collectorstoressqliteidempotencystore)
- [jane_telegram_collector.stores.SqliteIdempotencyStore.__init__](#jane_telegram_collectorstoressqliteidempotencystore__init__)
- [jane_telegram_collector.stores.SqliteIdempotencyStore.state](#jane_telegram_collectorstoressqliteidempotencystorestate)

## jane_telegram_collector.stores.SqliteJobStore

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/stores.py:22](../../../../../../services/telegram-collector/src/jane_telegram_collector/stores.py#L22).

```python
class SqliteJobStore(SqliteWorkJobStore):
```

Базові типи / інтерфейси: `SqliteWorkJobStore`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_telegram_collector.stores.md#jane_telegram_collectorstoressqlitejobstore__init__) | Конструктор | ні |
| [state](jane_telegram_collector.stores.md#jane_telegram_collectorstoressqlitejobstorestate) | Поле екземпляра | ні |
| [instance_id](jane_telegram_collector.stores.md#jane_telegram_collectorstoressqlitejobstoreinstance_id) | Поле екземпляра | ні |
| [work](../../../../jane-kit/reference/types/generated/jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteworkjobstorework) | Поле екземпляра | так |
| [owner](../../../../jane-kit/reference/types/generated/jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteworkjobstoreowner) | Поле екземпляра | так |
| [migrate](../../../../jane-kit/reference/types/generated/jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteworkjobstoremigrate) | Метод | так |
| [create_sync](../../../../jane-kit/reference/types/generated/jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteworkjobstorecreate_sync) | Метод | так |
| [save_sync](../../../../jane-kit/reference/types/generated/jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteworkjobstoresave_sync) | Метод | так |

### Опис із вихідного коду

```text
Jobs of collections, shared by all instances on the state file.
```

## jane_telegram_collector.stores.SqliteJobStore.__init__

**Конструктор.** Код: [services/telegram-collector/src/jane_telegram_collector/stores.py:25](../../../../../../services/telegram-collector/src/jane_telegram_collector/stores.py#L25).

```python
def __init__(self, state: StateStore, instance_id: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `state` | `StateStore` | `—` | positional-or-keyword |
| `instance_id` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.stores.SqliteJobStore.state

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/stores.py:27](../../../../../../services/telegram-collector/src/jane_telegram_collector/stores.py#L27).

```python
self.state = state
```

## jane_telegram_collector.stores.SqliteJobStore.instance_id

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/stores.py:28](../../../../../../services/telegram-collector/src/jane_telegram_collector/stores.py#L28).

```python
self.instance_id = instance_id
```

## jane_telegram_collector.stores.SqliteIdempotencyStore

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/stores.py:32](../../../../../../services/telegram-collector/src/jane_telegram_collector/stores.py#L32).

```python
class SqliteIdempotencyStore(_KitIdempotency):
```

Базові типи / інтерфейси: `_KitIdempotency`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_telegram_collector.stores.md#jane_telegram_collectorstoressqliteidempotencystore__init__) | Конструктор | ні |
| [state](jane_telegram_collector.stores.md#jane_telegram_collectorstoressqliteidempotencystorestate) | Поле екземпляра | ні |
| [db](../../../../jane-kit/reference/types/generated/jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystoredb) | Поле екземпляра | так |
| [owner](../../../../jane-kit/reference/types/generated/jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystoreowner) | Поле екземпляра | так |
| [lease_s](../../../../jane-kit/reference/types/generated/jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystorelease_s) | Поле екземпляра | так |
| [table](../../../../jane-kit/reference/types/generated/jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystoretable) | Поле екземпляра | так |
| [migrate](../../../../jane-kit/reference/types/generated/jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystoremigrate) | Метод | так |
| [begin_sync](../../../../jane-kit/reference/types/generated/jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystorebegin_sync) | Метод | так |
| [complete_sync](../../../../jane-kit/reference/types/generated/jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystorecomplete_sync) | Метод | так |
| [release_sync](../../../../jane-kit/reference/types/generated/jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystorerelease_sync) | Метод | так |
| [heartbeat_sync](../../../../jane-kit/reference/types/generated/jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystoreheartbeat_sync) | Метод | так |
| [begin](../../../../jane-kit/reference/types/generated/jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystorebegin) | Метод | так |
| [complete](../../../../jane-kit/reference/types/generated/jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystorecomplete) | Метод | так |
| [release](../../../../jane-kit/reference/types/generated/jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystorerelease) | Метод | так |
| [heartbeat](../../../../jane-kit/reference/types/generated/jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystoreheartbeat) | Метод | так |

## jane_telegram_collector.stores.SqliteIdempotencyStore.__init__

**Конструктор.** Код: [services/telegram-collector/src/jane_telegram_collector/stores.py:33](../../../../../../services/telegram-collector/src/jane_telegram_collector/stores.py#L33).

```python
def __init__(self, state: StateStore, instance_id: str, in_progress_lease_s: float) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `state` | `StateStore` | `—` | positional-or-keyword |
| `instance_id` | `str` | `—` | positional-or-keyword |
| `in_progress_lease_s` | `float` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.stores.SqliteIdempotencyStore.state

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/stores.py:37](../../../../../../services/telegram-collector/src/jane_telegram_collector/stores.py#L37).

```python
self.state = state
```
