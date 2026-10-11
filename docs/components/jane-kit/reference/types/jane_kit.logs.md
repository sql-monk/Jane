# Модуль `jane_kit.logs`

> Згенеровано `scripts/docs_reference.py` з [libs/jane-kit/src/jane_kit/logs.py](../../../../../libs/jane-kit/src/jane_kit/logs.py). Не редагуйте вручну.

Structured logging: one JSON object per line on stdout, with bound context.

Context (``request_id``, ``job_id``, ``source_id`` ...) is stored in a ``contextvars`` variable, so it follows asyncio tasks. ``extra={...}`` fields of a log call are added to the record.

## Зміст

- [Клас `JsonFormatter`](#клас-jsonformatter)
- [Функція `bind_context`](#функція-bind_context)
- [Функція `configure_logging`](#функція-configure_logging)
- [Функція `current_context`](#функція-current_context)
- [Функція `get_logger`](#функція-get_logger)

## Класи

### Клас `JsonFormatter`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.logs` |
| Успадкування | `logging.Formatter` |
| Код | [logs.py:45](../../../../../libs/jane-kit/src/jane_kit/logs.py#L45) |

```python
class JsonFormatter(logging.Formatter): ...
```

#### Конструктор `JsonFormatter.__init__`

```python
def __init__(self, service: str, instance: str | None = None) -> None: ...
```

Код: [logs.py:46](../../../../../libs/jane-kit/src/jane_kit/logs.py#L46).

#### Метод `JsonFormatter.format`

```python
def format(self, record: logging.LogRecord) -> str: ...
```

Код: [logs.py:51](../../../../../libs/jane-kit/src/jane_kit/logs.py#L51).

## Функції

### Функція `bind_context`

```python
@contextmanager
def bind_context(**values: Any) -> Iterator[None]: ...
```

Add fields to every log record emitted inside the block (and in tasks spawned from it).

Код: [logs.py:36](../../../../../libs/jane-kit/src/jane_kit/logs.py#L36).

### Функція `configure_logging`

```python
def configure_logging(
    service: str,
    level: str | int = 'INFO',
    fmt: Literal['json', 'console'] = 'json',
    instance: str | None = None,
    stream: Any = None,
) -> None: ...
```

Configure the root logger once per process (idempotent; replaces previous handlers).

Код: [logs.py:77](../../../../../libs/jane-kit/src/jane_kit/logs.py#L77).

### Функція `current_context`

```python
def current_context() -> dict[str, Any]: ...
```

Код: [logs.py:31](../../../../../libs/jane-kit/src/jane_kit/logs.py#L31).

### Функція `get_logger`

```python
def get_logger(name: str) -> logging.Logger: ...
```

Код: [logs.py:103](../../../../../libs/jane-kit/src/jane_kit/logs.py#L103).
