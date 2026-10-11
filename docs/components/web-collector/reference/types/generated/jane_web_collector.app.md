# jane_web_collector.app

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_web_collector.app.log](#jane_web_collectorapplog)
- [jane_web_collector.app.CURSOR_RE](#jane_web_collectorappcursor_re)
- [jane_web_collector.app.TERMINAL](#jane_web_collectorappterminal)
- [jane_web_collector.app.state_store_busy](#jane_web_collectorappstate_store_busy)
- [jane_web_collector.app.build_app](#jane_web_collectorappbuild_app)
- [jane_web_collector.app.rfc3339_ts](#jane_web_collectorapprfc3339_ts)
- [jane_web_collector.app.rfc3339_now](#jane_web_collectorapprfc3339_now)

## jane_web_collector.app.log

**Змінна.** Код: [services/web-collector/src/jane_web_collector/app.py:42](../../../../../../services/web-collector/src/jane_web_collector/app.py#L42).

```python
log = logging.getLogger(__name__)
```

## jane_web_collector.app.CURSOR_RE

**Константа.** Код: [services/web-collector/src/jane_web_collector/app.py:44](../../../../../../services/web-collector/src/jane_web_collector/app.py#L44).

```python
CURSOR_RE = re.compile('^c_(\\d{1,18})$')
```

## jane_web_collector.app.TERMINAL

**Константа.** Код: [services/web-collector/src/jane_web_collector/app.py:45](../../../../../../services/web-collector/src/jane_web_collector/app.py#L45).

```python
TERMINAL = {'succeeded', 'failed', 'cancelled'}
```

## jane_web_collector.app.state_store_busy

**Функція.** Код: [services/web-collector/src/jane_web_collector/app.py:63](../../../../../../services/web-collector/src/jane_web_collector/app.py#L63).

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

## jane_web_collector.app.build_app

**Функція.** Код: [services/web-collector/src/jane_web_collector/app.py:69](../../../../../../services/web-collector/src/jane_web_collector/app.py#L69).

```python
def build_app(settings: Settings | None=None) -> FastAPI:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `settings` | `Settings \| None` | `None` | positional-or-keyword |

Результат: `FastAPI`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/strategies/discovery/tests/conftest.py:117](../../../../../../services/web-collector/strategies/discovery/tests/conftest.py#L117).

```python
build_app(make_settings(tmp_path, discovery_path=PACKAGE_DIR))
```

Контекст і передумови: [services/web-collector/tests/conftest.py:97](../../../../../../services/web-collector/tests/conftest.py#L97).

```python
build_app(settings)
```

## jane_web_collector.app.rfc3339_ts

**Функція.** Код: [services/web-collector/src/jane_web_collector/app.py:353](../../../../../../services/web-collector/src/jane_web_collector/app.py#L353).

```python
def rfc3339_ts(ts: float) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `ts` | `float` | `—` | positional-or-keyword |

Результат: `str`.

## jane_web_collector.app.rfc3339_now

**Функція.** Код: [services/web-collector/src/jane_web_collector/app.py:357](../../../../../../services/web-collector/src/jane_web_collector/app.py#L357).

```python
def rfc3339_now() -> str:
```

Результат: `str`.
