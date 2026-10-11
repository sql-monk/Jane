# jane_registry.auth

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_registry.auth.ALL_SCOPES](#jane_registryauthall_scopes)
- [jane_registry.auth.ACTORS](#jane_registryauthactors)
- [jane_registry.auth.Principal](#jane_registryauthprincipal)
- [jane_registry.auth.Principal.__init__](#jane_registryauthprincipal__init__)
- [jane_registry.auth.Principal.name](#jane_registryauthprincipalname)
- [jane_registry.auth.Principal.scopes](#jane_registryauthprincipalscopes)
- [jane_registry.auth.Principal.actor](#jane_registryauthprincipalactor)
- [jane_registry.auth.check_actors](#jane_registryauthcheck_actors)
- [jane_registry.auth.Authenticator](#jane_registryauthauthenticator)
- [jane_registry.auth.Authenticator.__init__](#jane_registryauthauthenticator__init__)
- [jane_registry.auth.Authenticator.mode](#jane_registryauthauthenticatormode)
- [jane_registry.auth.Authenticator.principal](#jane_registryauthauthenticatorprincipal)
- [jane_registry.auth.Authenticator.require](#jane_registryauthauthenticatorrequire)

## jane_registry.auth.ALL_SCOPES

**Константа.** Код: [services/registry/src/jane_registry/auth.py:28](../../../../../../services/registry/src/jane_registry/auth.py#L28).

```python
ALL_SCOPES = frozenset({'registry:read', 'registry:write', 'registry:approve'})
```

## jane_registry.auth.ACTORS

**Константа.** Код: [services/registry/src/jane_registry/auth.py:29](../../../../../../services/registry/src/jane_registry/auth.py#L29).

```python
ACTORS = frozenset({'human', 'llm', 'import'})
```

## jane_registry.auth.Principal

**Клас.** Код: [services/registry/src/jane_registry/auth.py:33](../../../../../../services/registry/src/jane_registry/auth.py#L33).

```python
class Principal:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_registry.auth.md#jane_registryauthprincipalname) | Поле | ні |
| [scopes](jane_registry.auth.md#jane_registryauthprincipalscopes) | Поле | ні |
| [actor](jane_registry.auth.md#jane_registryauthprincipalactor) | Поле | ні |
| [__init__](jane_registry.auth.md#jane_registryauthprincipal__init__) | Конструктор dataclass | ні |

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_service_ops.py:338](../../../../../../services/registry/tests/test_service_ops.py#L338).

```python
who = Principal("tester", frozenset({"registry:write"}))
```

## jane_registry.auth.Principal.__init__

**Конструктор dataclass.** Код: [services/registry/src/jane_registry/auth.py:33](../../../../../../services/registry/src/jane_registry/auth.py#L33).

```python
def __init__(self, name: str, scopes: frozenset[str], actor: str = 'human') -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `name` | `str` | `—` | positional-or-keyword |
| `scopes` | `frozenset[str]` | `—` | positional-or-keyword |
| `actor` | `str` | `'human'` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_service_ops.py:338](../../../../../../services/registry/tests/test_service_ops.py#L338).

```python
who = Principal("tester", frozenset({"registry:write"}))
```

## jane_registry.auth.Principal.name

**Поле.** Код: [services/registry/src/jane_registry/auth.py:34](../../../../../../services/registry/src/jane_registry/auth.py#L34).

```python
name: str
```

Доступ: читання — так; запис — ні.

## jane_registry.auth.Principal.scopes

**Поле.** Код: [services/registry/src/jane_registry/auth.py:35](../../../../../../services/registry/src/jane_registry/auth.py#L35).

```python
scopes: frozenset[str]
```

Доступ: читання — так; запис — ні.

## jane_registry.auth.Principal.actor

**Поле.** Код: [services/registry/src/jane_registry/auth.py:36](../../../../../../services/registry/src/jane_registry/auth.py#L36).

```python
actor: str = 'human'
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
``provenance.created_by`` of what this caller creates: ``human`` (default), ``llm`` (the assistant's
    key) or ``import``. An ``llm`` caller can only publish ``created_by: llm`` versions.
```

## jane_registry.auth.check_actors

**Функція.** Код: [services/registry/src/jane_registry/auth.py:41](../../../../../../services/registry/src/jane_registry/auth.py#L41).

```python
def check_actors(settings: AuthSettings) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `settings` | `AuthSettings` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Start-up check: ``actor`` of every configured key is one of :data:`ACTORS`.
```

## jane_registry.auth.Authenticator

**Клас.** Код: [services/registry/src/jane_registry/auth.py:51](../../../../../../services/registry/src/jane_registry/auth.py#L51).

```python
class Authenticator:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_registry.auth.md#jane_registryauthauthenticator__init__) | Конструктор | ні |
| [mode](jane_registry.auth.md#jane_registryauthauthenticatormode) | Поле екземпляра | ні |
| [principal](jane_registry.auth.md#jane_registryauthauthenticatorprincipal) | Метод | ні |
| [require](jane_registry.auth.md#jane_registryauthauthenticatorrequire) | Метод | ні |

### Опис із вихідного коду

```text
Scope dependencies of the routes; authentication itself is jane-kit's middleware (``create_app``).
```

## jane_registry.auth.Authenticator.__init__

**Конструктор.** Код: [services/registry/src/jane_registry/auth.py:54](../../../../../../services/registry/src/jane_registry/auth.py#L54).

```python
def __init__(self, settings: AuthSettings) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `settings` | `AuthSettings` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.auth.Authenticator.mode

**Поле екземпляра.** Код: [services/registry/src/jane_registry/auth.py:56](../../../../../../services/registry/src/jane_registry/auth.py#L56).

```python
self.mode = settings.auth_mode
```

## jane_registry.auth.Authenticator.principal

**Метод.** Код: [services/registry/src/jane_registry/auth.py:59](../../../../../../services/registry/src/jane_registry/auth.py#L59).

```python
def principal(request: Request) -> Principal:
```

Декоратори: `staticmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `request` | `Request` | `—` | positional-or-keyword |

Результат: `Principal`.

Явні `raise` у тілі: `Forbidden`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_registry.auth.Authenticator.require

**Метод.** Код: [services/registry/src/jane_registry/auth.py:67](../../../../../../services/registry/src/jane_registry/auth.py#L67).

```python
def require(self, scope: str) -> Callable[[Request], Coroutine[Any, Any, Principal]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `scope` | `str` | `—` | positional-or-keyword |

Результат: `Callable[[Request], Coroutine[Any, Any, Principal]]`.
