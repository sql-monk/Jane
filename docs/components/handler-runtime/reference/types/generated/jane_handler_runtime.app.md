# jane_handler_runtime.app

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_handler_runtime.app.log](#jane_handler_runtimeapplog)
- [jane_handler_runtime.app.build_state](#jane_handler_runtimeappbuild_state)
- [jane_handler_runtime.app.build_app](#jane_handler_runtimeappbuild_app)

## jane_handler_runtime.app.log

**Змінна.** Код: [services/handler-runtime/src/jane_handler_runtime/app.py:47](../../../../../../services/handler-runtime/src/jane_handler_runtime/app.py#L47).

```python
log = logging.getLogger(__name__)
```

## jane_handler_runtime.app.build_state

**Функція.** Код: [services/handler-runtime/src/jane_handler_runtime/app.py:84](../../../../../../services/handler-runtime/src/jane_handler_runtime/app.py#L84).

```python
def build_state(settings: Settings, runtime: Runtime) -> ServiceState:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `settings` | `Settings` | `—` | positional-or-keyword |
| `runtime` | `Runtime` | `—` | positional-or-keyword |

Результат: `ServiceState`.

### Опис із вихідного коду

```text
PostgreSQL state when ``state_dsn`` is set (several instances), else in-memory (one instance).
```

## jane_handler_runtime.app.build_app

**Функція.** Код: [services/handler-runtime/src/jane_handler_runtime/app.py:96](../../../../../../services/handler-runtime/src/jane_handler_runtime/app.py#L96).

```python
def build_app(settings: Settings | None=None, runtime: Runtime | None=None, state: ServiceState | None=None) -> FastAPI:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `settings` | `Settings \| None` | `None` | positional-or-keyword |
| `runtime` | `Runtime \| None` | `None` | positional-or-keyword |
| `state` | `ServiceState \| None` | `None` | positional-or-keyword |

Результат: `FastAPI`.

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_app.py:26](../../../../../../services/handler-runtime/tests/test_app.py#L26).

```python
build_app(subprocess_settings)
```

Контекст і передумови: [services/handler-runtime/tests/test_app.py:291](../../../../../../services/handler-runtime/tests/test_app.py#L291).

```python
build_app(settings, runtime)
```
