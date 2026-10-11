# jane_kit.logs

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_kit.logs.current_context](#jane_kitlogscurrent_context)
- [jane_kit.logs.bind_context](#jane_kitlogsbind_context)
- [jane_kit.logs.JsonFormatter](#jane_kitlogsjsonformatter)
- [jane_kit.logs.JsonFormatter.__init__](#jane_kitlogsjsonformatter__init__)
- [jane_kit.logs.JsonFormatter.service](#jane_kitlogsjsonformatterservice)
- [jane_kit.logs.JsonFormatter.instance](#jane_kitlogsjsonformatterinstance)
- [jane_kit.logs.JsonFormatter.format](#jane_kitlogsjsonformatterformat)
- [jane_kit.logs.configure_logging](#jane_kitlogsconfigure_logging)
- [jane_kit.logs.get_logger](#jane_kitlogsget_logger)

## jane_kit.logs.current_context

**Функція.** Код: [libs/jane-kit/src/jane_kit/logs.py:31](../../../../../../libs/jane-kit/src/jane_kit/logs.py#L31).

```python
def current_context() -> dict[str, Any]:
```

Результат: `dict[str, Any]`.

## jane_kit.logs.bind_context

**Функція.** Код: [libs/jane-kit/src/jane_kit/logs.py:36](../../../../../../libs/jane-kit/src/jane_kit/logs.py#L36).

```python
def bind_context(**values: Any) -> Iterator[None]:
```

Декоратори: `contextmanager`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `values` | `Any` | `—` | var-keyword |

Результат: `Iterator[None]`.

### Опис із вихідного коду

```text
Add fields to every log record emitted inside the block (and in tasks spawned from it).
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_clients.py:55](../../../../../../libs/jane-kit/tests/test_clients.py#L55).

```python
bind_context(trace_id="4bf92f3577b34da6a3ce929d0e0e4736", request_id="req-7")
```

Контекст і передумови: [libs/jane-kit/tests/test_service.py:167](../../../../../../libs/jane-kit/tests/test_service.py#L167).

```python
bind_context(trace_id="t-1", job_id="j-1")
```

## jane_kit.logs.JsonFormatter

**Клас.** Код: [libs/jane-kit/src/jane_kit/logs.py:45](../../../../../../libs/jane-kit/src/jane_kit/logs.py#L45).

```python
class JsonFormatter(logging.Formatter):
```

Базові типи / інтерфейси: `logging.Formatter`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_kit.logs.md#jane_kitlogsjsonformatter__init__) | Конструктор | ні |
| [service](jane_kit.logs.md#jane_kitlogsjsonformatterservice) | Поле екземпляра | ні |
| [instance](jane_kit.logs.md#jane_kitlogsjsonformatterinstance) | Поле екземпляра | ні |
| [format](jane_kit.logs.md#jane_kitlogsjsonformatterformat) | Метод | ні |

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_service.py:162](../../../../../../libs/jane-kit/tests/test_service.py#L162).

```python
handler.setFormatter(JsonFormatter("svc", "i-1"))
```

## jane_kit.logs.JsonFormatter.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/logs.py:46](../../../../../../libs/jane-kit/src/jane_kit/logs.py#L46).

```python
def __init__(self, service: str, instance: str | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `service` | `str` | `—` | positional-or-keyword |
| `instance` | `str \| None` | `None` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_service.py:162](../../../../../../libs/jane-kit/tests/test_service.py#L162).

```python
handler.setFormatter(JsonFormatter("svc", "i-1"))
```

## jane_kit.logs.JsonFormatter.service

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/logs.py:48](../../../../../../libs/jane-kit/src/jane_kit/logs.py#L48).

```python
self.service = service
```

## jane_kit.logs.JsonFormatter.instance

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/logs.py:49](../../../../../../libs/jane-kit/src/jane_kit/logs.py#L49).

```python
self.instance = instance
```

## jane_kit.logs.JsonFormatter.format

**Метод.** Код: [libs/jane-kit/src/jane_kit/logs.py:51](../../../../../../libs/jane-kit/src/jane_kit/logs.py#L51).

```python
def format(self, record: logging.LogRecord) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `record` | `logging.LogRecord` | `—` | positional-or-keyword |

Результат: `str`.

## jane_kit.logs.configure_logging

**Функція.** Код: [libs/jane-kit/src/jane_kit/logs.py:77](../../../../../../libs/jane-kit/src/jane_kit/logs.py#L77).

```python
def configure_logging(service: str, level: str | int='INFO', fmt: Literal['json', 'console']='json', instance: str | None=None, stream: Any=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `service` | `str` | `—` | positional-or-keyword |
| `level` | `str \| int` | `'INFO'` | positional-or-keyword |
| `fmt` | `Literal['json', 'console']` | `'json'` | positional-or-keyword |
| `instance` | `str \| None` | `None` | positional-or-keyword |
| `stream` | `Any` | `None` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Configure the root logger once per process (idempotent; replaces previous handlers).
```

## jane_kit.logs.get_logger

**Функція.** Код: [libs/jane-kit/src/jane_kit/logs.py:103](../../../../../../libs/jane-kit/src/jane_kit/logs.py#L103).

```python
def get_logger(name: str) -> logging.Logger:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `name` | `str` | `—` | positional-or-keyword |

Результат: `logging.Logger`.
