# jane_orchestrator.auth

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_orchestrator.auth.ADMIN](#jane_orchestratorauthadmin)
- [jane_orchestrator.auth.ALL_SCOPES](#jane_orchestratorauthall_scopes)
- [jane_orchestrator.auth.Principal](#jane_orchestratorauthprincipal)
- [jane_orchestrator.auth.Principal.__init__](#jane_orchestratorauthprincipal__init__)
- [jane_orchestrator.auth.Principal.name](#jane_orchestratorauthprincipalname)
- [jane_orchestrator.auth.Principal.scopes](#jane_orchestratorauthprincipalscopes)
- [jane_orchestrator.auth.Principal.require](#jane_orchestratorauthprincipalrequire)
- [jane_orchestrator.auth.caller](#jane_orchestratorauthcaller)

## jane_orchestrator.auth.ADMIN

**Константа.** Код: [services/orchestrator/src/jane_orchestrator/auth.py:22](../../../../../../services/orchestrator/src/jane_orchestrator/auth.py#L22).

```python
ADMIN = 'orchestrator:admin'
```

## jane_orchestrator.auth.ALL_SCOPES

**Константа.** Код: [services/orchestrator/src/jane_orchestrator/auth.py:23](../../../../../../services/orchestrator/src/jane_orchestrator/auth.py#L23).

```python
ALL_SCOPES = frozenset({'orchestrator:read', 'orchestrator:write', ADMIN})
```

## jane_orchestrator.auth.Principal

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/auth.py:27](../../../../../../services/orchestrator/src/jane_orchestrator/auth.py#L27).

```python
class Principal:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_orchestrator.auth.md#jane_orchestratorauthprincipalname) | Поле | ні |
| [scopes](jane_orchestrator.auth.md#jane_orchestratorauthprincipalscopes) | Поле | ні |
| [require](jane_orchestrator.auth.md#jane_orchestratorauthprincipalrequire) | Метод | ні |
| [__init__](jane_orchestrator.auth.md#jane_orchestratorauthprincipal__init__) | Конструктор dataclass | ні |

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/orch_support.py:1099](../../../../../../services/orchestrator/tests/orch_support.py#L1099).

```python
return Principal(found.name, frozenset(found.scopes))
```

Контекст і передумови: [services/orchestrator/tests/orch_support.py:1092](../../../../../../services/orchestrator/tests/orch_support.py#L1092).

```python
return Principal("anonymous", ALL_SCOPES)
```

## jane_orchestrator.auth.Principal.__init__

**Конструктор dataclass.** Код: [services/orchestrator/src/jane_orchestrator/auth.py:27](../../../../../../services/orchestrator/src/jane_orchestrator/auth.py#L27).

```python
def __init__(self, name: str, scopes: frozenset[str]) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `name` | `str` | `—` | positional-or-keyword |
| `scopes` | `frozenset[str]` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/orch_support.py:1099](../../../../../../services/orchestrator/tests/orch_support.py#L1099).

```python
return Principal(found.name, frozenset(found.scopes))
```

Контекст і передумови: [services/orchestrator/tests/orch_support.py:1092](../../../../../../services/orchestrator/tests/orch_support.py#L1092).

```python
return Principal("anonymous", ALL_SCOPES)
```

## jane_orchestrator.auth.Principal.name

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/auth.py:28](../../../../../../services/orchestrator/src/jane_orchestrator/auth.py#L28).

```python
name: str
```

Доступ: читання — так; запис — ні.

## jane_orchestrator.auth.Principal.scopes

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/auth.py:29](../../../../../../services/orchestrator/src/jane_orchestrator/auth.py#L29).

```python
scopes: frozenset[str]
```

Доступ: читання — так; запис — ні.

## jane_orchestrator.auth.Principal.require

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/auth.py:31](../../../../../../services/orchestrator/src/jane_orchestrator/auth.py#L31).

```python
def require(self, scope: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `scope` | `str` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `Forbidden`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_orchestrator.auth.caller

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/auth.py:36](../../../../../../services/orchestrator/src/jane_orchestrator/auth.py#L36).

```python
def caller(request: Request, scope: str) -> Principal:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `request` | `Request` | `—` | positional-or-keyword |
| `scope` | `str` | `—` | positional-or-keyword |

Результат: `Principal`.

### Опис із вихідного коду

```text
The authenticated caller of this request with ``scope`` (or ``orchestrator:admin``).
```
