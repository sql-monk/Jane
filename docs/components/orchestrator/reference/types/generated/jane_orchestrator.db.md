# jane_orchestrator.db

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_orchestrator.db.Jsonb](#jane_orchestratordbjsonb)
- [jane_orchestrator.db.Database](#jane_orchestratordbdatabase)
- [jane_orchestrator.db.Database.__init__](#jane_orchestratordbdatabase__init__)
- [jane_orchestrator.db.Database.dsn](#jane_orchestratordbdatabasedsn)
- [jane_orchestrator.db.Database.pool](#jane_orchestratordbdatabasepool)
- [jane_orchestrator.db.Database.open](#jane_orchestratordbdatabaseopen)
- [jane_orchestrator.db.Database.close](#jane_orchestratordbdatabaseclose)
- [jane_orchestrator.db.Database.tx](#jane_orchestratordbdatabasetx)
- [jane_orchestrator.db.Database.conn](#jane_orchestratordbdatabaseconn)
- [jane_orchestrator.db.Database.migrate](#jane_orchestratordbdatabasemigrate)
- [jane_orchestrator.db.Database.ping](#jane_orchestratordbdatabaseping)

## jane_orchestrator.db.Jsonb

**Повторний експорт.** Код: [services/orchestrator/src/jane_orchestrator/db.py:15](../../../../../../services/orchestrator/src/jane_orchestrator/db.py#L15).

```python
from psycopg.types.json import Jsonb as Jsonb
```

Повторний експорт із `psycopg.types.json.Jsonb`.

## jane_orchestrator.db.Database

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/db.py:278](../../../../../../services/orchestrator/src/jane_orchestrator/db.py#L278).

```python
class Database:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_orchestrator.db.md#jane_orchestratordbdatabase__init__) | Конструктор | ні |
| [dsn](jane_orchestrator.db.md#jane_orchestratordbdatabasedsn) | Поле екземпляра | ні |
| [pool](jane_orchestrator.db.md#jane_orchestratordbdatabasepool) | Поле екземпляра | ні |
| [open](jane_orchestrator.db.md#jane_orchestratordbdatabaseopen) | Метод | ні |
| [close](jane_orchestrator.db.md#jane_orchestratordbdatabaseclose) | Метод | ні |
| [tx](jane_orchestrator.db.md#jane_orchestratordbdatabasetx) | Метод | ні |
| [conn](jane_orchestrator.db.md#jane_orchestratordbdatabaseconn) | Метод | ні |
| [migrate](jane_orchestrator.db.md#jane_orchestratordbdatabasemigrate) | Метод | ні |
| [ping](jane_orchestrator.db.md#jane_orchestratordbdatabaseping) | Метод | ні |

### Опис із вихідного коду

```text
Connection pool over the orchestrator's DSN; rows are dicts.
```

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_stored_raw.py:221](../../../../../../services/orchestrator/tests/test_stored_raw.py#L221).

```python
db = Database(db_dsn)
```

## jane_orchestrator.db.Database.__init__

**Конструктор.** Код: [services/orchestrator/src/jane_orchestrator/db.py:281](../../../../../../services/orchestrator/src/jane_orchestrator/db.py#L281).

```python
def __init__(self, dsn: str, *, max_size: int=10, min_size: int=1) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `dsn` | `str` | `—` | positional-or-keyword |
| `max_size` | `int` | `10` | keyword-only |
| `min_size` | `int` | `1` | keyword-only |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_stored_raw.py:221](../../../../../../services/orchestrator/tests/test_stored_raw.py#L221).

```python
db = Database(db_dsn)
```

## jane_orchestrator.db.Database.dsn

**Поле екземпляра.** Код: [services/orchestrator/src/jane_orchestrator/db.py:282](../../../../../../services/orchestrator/src/jane_orchestrator/db.py#L282).

```python
self.dsn = dsn
```

## jane_orchestrator.db.Database.pool

**Поле екземпляра.** Код: [services/orchestrator/src/jane_orchestrator/db.py:283](../../../../../../services/orchestrator/src/jane_orchestrator/db.py#L283).

```python
self.pool = ConnectionPool(dsn, min_size=min_size, max_size=max_size, kwargs={'row_factory': dict_row, 'autocommit': True}, open=False)
```

## jane_orchestrator.db.Database.open

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/db.py:291](../../../../../../services/orchestrator/src/jane_orchestrator/db.py#L291).

```python
def open(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_stored_raw.py:222](../../../../../../services/orchestrator/tests/test_stored_raw.py#L222).

```python
db.open()
```

## jane_orchestrator.db.Database.close

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/db.py:294](../../../../../../services/orchestrator/src/jane_orchestrator/db.py#L294).

```python
def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_stored_raw.py:234](../../../../../../services/orchestrator/tests/test_stored_raw.py#L234).

```python
db.close()
```

## jane_orchestrator.db.Database.tx

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/db.py:298](../../../../../../services/orchestrator/src/jane_orchestrator/db.py#L298).

```python
def tx(self) -> Iterator[Any]:
```

Декоратори: `contextmanager`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `Iterator[Any]`.

### Опис із вихідного коду

```text
A connection inside one transaction (commit on success, rollback on error).
```

## jane_orchestrator.db.Database.conn

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/db.py:304](../../../../../../services/orchestrator/src/jane_orchestrator/db.py#L304).

```python
def conn(self) -> Iterator[Any]:
```

Декоратори: `contextmanager`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `Iterator[Any]`.

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_stored_raw.py:226](../../../../../../services/orchestrator/tests/test_stored_raw.py#L226).

```python
db.conn()
```

## jane_orchestrator.db.Database.migrate

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/db.py:308](../../../../../../services/orchestrator/src/jane_orchestrator/db.py#L308).

```python
def migrate(self) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `int`.

### Опис із вихідного коду

```text
Apply pending migrations; returns the schema version.
```

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_stored_raw.py:224](../../../../../../services/orchestrator/tests/test_stored_raw.py#L224).

```python
assert db.migrate() == len(MIGRATIONS)
```

Контекст і передумови: [services/orchestrator/tests/test_stored_raw.py:225](../../../../../../services/orchestrator/tests/test_stored_raw.py#L225).

```python
assert db.migrate() == len(MIGRATIONS)
```

## jane_orchestrator.db.Database.ping

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/db.py:326](../../../../../../services/orchestrator/src/jane_orchestrator/db.py#L326).

```python
def ping(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.
