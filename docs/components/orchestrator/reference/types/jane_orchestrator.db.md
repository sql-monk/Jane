# Модуль `jane_orchestrator.db`

> Згенеровано `scripts/docs_reference.py` з [services/orchestrator/src/jane_orchestrator/db.py](../../../../../services/orchestrator/src/jane_orchestrator/db.py). Не редагуйте вручну.

The orchestrator's own PostgreSQL database: connection pool and schema migrations.

The work queue uses ``SELECT … FOR UPDATE SKIP LOCKED`` (plan.md §2); no other broker. Migrations are idempotent and serialized with an advisory lock, so several instances may start at once.

## Класи

### Клас `Database`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_orchestrator.db` |
| Код | [db.py:297](../../../../../services/orchestrator/src/jane_orchestrator/db.py#L297) |

```python
class Database: ...
```

Connection pool over the orchestrator's DSN; rows are dicts.

#### Конструктор `Database.__init__`

```python
def __init__(self, dsn: str, *, max_size: int = 10, min_size: int = 1) -> None: ...
```

Код: [db.py:300](../../../../../services/orchestrator/src/jane_orchestrator/db.py#L300).

#### Метод `Database.open`

```python
def open(self) -> None: ...
```

Код: [db.py:310](../../../../../services/orchestrator/src/jane_orchestrator/db.py#L310).

#### Метод `Database.close`

```python
def close(self) -> None: ...
```

Код: [db.py:313](../../../../../services/orchestrator/src/jane_orchestrator/db.py#L313).

#### Метод `Database.tx`

```python
@contextmanager
def tx(self) -> Iterator[Any]: ...
```

A connection inside one transaction (commit on success, rollback on error).

Код: [db.py:317](../../../../../services/orchestrator/src/jane_orchestrator/db.py#L317).

#### Метод `Database.conn`

```python
@contextmanager
def conn(self) -> Iterator[Any]: ...
```

Код: [db.py:323](../../../../../services/orchestrator/src/jane_orchestrator/db.py#L323).

#### Метод `Database.migrate`

```python
def migrate(self) -> int: ...
```

Apply pending migrations; returns the schema version.

Код: [db.py:327](../../../../../services/orchestrator/src/jane_orchestrator/db.py#L327).

#### Метод `Database.ping`

```python
def ping(self) -> bool: ...
```

Код: [db.py:345](../../../../../services/orchestrator/src/jane_orchestrator/db.py#L345).

## Реекспорт

| Назва | Визначено в |
|---|---|
| `Jsonb` | `psycopg.types.json` |
