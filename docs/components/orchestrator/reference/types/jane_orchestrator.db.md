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
| Код | [db.py:278](../../../../../services/orchestrator/src/jane_orchestrator/db.py#L278) |

```python
class Database: ...
```

Connection pool over the orchestrator's DSN; rows are dicts.

#### Конструктор `Database.__init__`

```python
def __init__(self, dsn: str, *, max_size: int = 10, min_size: int = 1) -> None: ...
```

Код: [db.py:281](../../../../../services/orchestrator/src/jane_orchestrator/db.py#L281).

#### Метод `Database.open`

```python
def open(self) -> None: ...
```

Код: [db.py:291](../../../../../services/orchestrator/src/jane_orchestrator/db.py#L291).

#### Метод `Database.close`

```python
def close(self) -> None: ...
```

Код: [db.py:294](../../../../../services/orchestrator/src/jane_orchestrator/db.py#L294).

#### Метод `Database.tx`

```python
@contextmanager
def tx(self) -> Iterator[Any]: ...
```

A connection inside one transaction (commit on success, rollback on error).

Код: [db.py:298](../../../../../services/orchestrator/src/jane_orchestrator/db.py#L298).

#### Метод `Database.conn`

```python
@contextmanager
def conn(self) -> Iterator[Any]: ...
```

Код: [db.py:304](../../../../../services/orchestrator/src/jane_orchestrator/db.py#L304).

#### Метод `Database.migrate`

```python
def migrate(self) -> int: ...
```

Apply pending migrations; returns the schema version.

Код: [db.py:308](../../../../../services/orchestrator/src/jane_orchestrator/db.py#L308).

#### Метод `Database.ping`

```python
def ping(self) -> bool: ...
```

Код: [db.py:326](../../../../../services/orchestrator/src/jane_orchestrator/db.py#L326).

## Реекспорт

| Назва | Визначено в |
|---|---|
| `Jsonb` | `psycopg.types.json` |
