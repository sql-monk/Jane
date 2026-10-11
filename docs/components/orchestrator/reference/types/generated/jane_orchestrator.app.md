# jane_orchestrator.app

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_orchestrator.app.log](#jane_orchestratorapplog)
- [jane_orchestrator.app.T](#jane_orchestratorappt)
- [jane_orchestrator.app.ADMIN](#jane_orchestratorappadmin)
- [jane_orchestrator.app.READ](#jane_orchestratorappread)
- [jane_orchestrator.app.WRITE](#jane_orchestratorappwrite)
- [jane_orchestrator.app.build_app](#jane_orchestratorappbuild_app)

## jane_orchestrator.app.log

**Змінна.** Код: [services/orchestrator/src/jane_orchestrator/app.py:39](../../../../../../services/orchestrator/src/jane_orchestrator/app.py#L39).

```python
log = logging.getLogger(__name__)
```

## jane_orchestrator.app.T

**Константа.** Код: [services/orchestrator/src/jane_orchestrator/app.py:40](../../../../../../services/orchestrator/src/jane_orchestrator/app.py#L40).

```python
T = TypeVar('T')
```

## jane_orchestrator.app.ADMIN

**Константа.** Код: [services/orchestrator/src/jane_orchestrator/app.py:42](../../../../../../services/orchestrator/src/jane_orchestrator/app.py#L42).

```python
READ, WRITE, ADMIN = ('orchestrator:read', 'orchestrator:write', 'orchestrator:admin')
```

## jane_orchestrator.app.READ

**Константа.** Код: [services/orchestrator/src/jane_orchestrator/app.py:42](../../../../../../services/orchestrator/src/jane_orchestrator/app.py#L42).

```python
READ, WRITE, ADMIN = ('orchestrator:read', 'orchestrator:write', 'orchestrator:admin')
```

## jane_orchestrator.app.WRITE

**Константа.** Код: [services/orchestrator/src/jane_orchestrator/app.py:42](../../../../../../services/orchestrator/src/jane_orchestrator/app.py#L42).

```python
READ, WRITE, ADMIN = ('orchestrator:read', 'orchestrator:write', 'orchestrator:admin')
```

## jane_orchestrator.app.build_app

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/app.py:45](../../../../../../services/orchestrator/src/jane_orchestrator/app.py#L45).

```python
def build_app(settings: Settings | None=None) -> FastAPI:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `settings` | `Settings \| None` | `None` | positional-or-keyword |

Результат: `FastAPI`.

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/conftest.py:86](../../../../../../services/orchestrator/tests/conftest.py#L86).

```python
client = TestClient(build_app(settings))
```
