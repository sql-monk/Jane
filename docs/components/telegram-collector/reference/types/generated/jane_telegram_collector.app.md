# jane_telegram_collector.app

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_telegram_collector.app.log](#jane_telegram_collectorapplog)
- [jane_telegram_collector.app.CURSOR_RE](#jane_telegram_collectorappcursor_re)
- [jane_telegram_collector.app.TERMINAL](#jane_telegram_collectorappterminal)
- [jane_telegram_collector.app.state_store_busy](#jane_telegram_collectorappstate_store_busy)
- [jane_telegram_collector.app.build_app](#jane_telegram_collectorappbuild_app)

## jane_telegram_collector.app.log

**Змінна.** Код: [services/telegram-collector/src/jane_telegram_collector/app.py:42](../../../../../../services/telegram-collector/src/jane_telegram_collector/app.py#L42).

```python
log = logging.getLogger(__name__)
```

## jane_telegram_collector.app.CURSOR_RE

**Константа.** Код: [services/telegram-collector/src/jane_telegram_collector/app.py:44](../../../../../../services/telegram-collector/src/jane_telegram_collector/app.py#L44).

```python
CURSOR_RE = re.compile('^c_(\\d{1,18})$')
```

## jane_telegram_collector.app.TERMINAL

**Константа.** Код: [services/telegram-collector/src/jane_telegram_collector/app.py:45](../../../../../../services/telegram-collector/src/jane_telegram_collector/app.py#L45).

```python
TERMINAL = {'succeeded', 'failed', 'cancelled'}
```

## jane_telegram_collector.app.state_store_busy

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/app.py:67](../../../../../../services/telegram-collector/src/jane_telegram_collector/app.py#L67).

```python
def state_store_busy(exc: BaseException) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `exc` | `BaseException` | `—` | positional-or-keyword |

Результат: `bool`.

### Опис із вихідного коду

```text
SQLite could not take its lock within ``STATE_BUSY_TIMEOUT_MS`` (another instance holds it).
```

## jane_telegram_collector.app.build_app

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/app.py:73](../../../../../../services/telegram-collector/src/jane_telegram_collector/app.py#L73).

```python
def build_app(settings: Settings | None=None) -> FastAPI:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `settings` | `Settings \| None` | `None` | positional-or-keyword |

Результат: `FastAPI`.

### Приклади з тестів

Контекст і передумови: [services/telegram-collector/tests/conftest.py:49](../../../../../../services/telegram-collector/tests/conftest.py#L49).

```python
build_app(settings)
```

Контекст і передумови: [services/telegram-collector/tests/test_auth.py:24](../../../../../../services/telegram-collector/tests/test_auth.py#L24).

```python
build_app(s)
```
