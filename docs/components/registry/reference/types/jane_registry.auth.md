# Модуль `jane_registry.auth`

> Згенеровано `scripts/docs_reference.py` з [services/registry/src/jane_registry/auth.py](../../../../../services/registry/src/jane_registry/auth.py). Не редагуйте вручну.

Authentication and scopes (ADR-0005): ``Authorization: Bearer <token>``, implemented by ``jane_kit.auth``.

* ``auth_mode=none`` - every caller has every scope (local tests on loopback; the service logs a warning);
* ``auth_mode=api_key`` - keys from ``JANE_REGISTRY_API_KEYS`` (JSON) and/or ``JANE_REGISTRY_API_KEYS_FILE``: ``[{"name", "sha256" | "secret_ref", "scopes", "actor"}]`` - only hashes are kept (``secret_ref`` = ``env:VAR``/``file:/path`` is resolved once at start and hashed);
* ``auth_mode=jwt`` - RS256/ES256 tokens of an identity provider (``JANE_REGISTRY_JWT_*``); scopes from the ``scope`` claim, the actor from the ``actor`` claim (``human`` when absent).

Scopes (``jane_kit.auth_scopes.REGISTRY``, checked for every route): ``registry:read`` (GET), ``registry:write`` (create, publish, fork, test results, upstream ports, package settings), ``registry:approve`` (``POST .../status``).

## Класи

### Клас `Authenticator`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.auth` |
| Код | [auth.py:51](../../../../../services/registry/src/jane_registry/auth.py#L51) |

```python
class Authenticator: ...
```

Scope dependencies of the routes; authentication itself is jane-kit's middleware (``create_app``).

#### Конструктор `Authenticator.__init__`

```python
def __init__(self, settings: AuthSettings) -> None: ...
```

Код: [auth.py:54](../../../../../services/registry/src/jane_registry/auth.py#L54).

#### Метод `Authenticator.principal`

```python
@staticmethod
def principal(request: Request) -> Principal: ...
```

Винятки в коді методу: `Forbidden`.

Код: [auth.py:59](../../../../../services/registry/src/jane_registry/auth.py#L59).

#### Метод `Authenticator.require`

```python
def require(self, scope: str) -> Callable[[Request], Coroutine[Any, Any, Principal]]: ...
```

Винятки в коді методу: `Forbidden`.

Код: [auth.py:67](../../../../../services/registry/src/jane_registry/auth.py#L67).

### Клас `Principal`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_registry.auth` |
| Код | [auth.py:33](../../../../../services/registry/src/jane_registry/auth.py#L33) |

```python
@dataclass(frozen=True)
class Principal: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `name` | `str` | — | читання |  |
| `scopes` | `frozenset[str]` | — | читання |  |
| `actor` | `str` | `'human'` | читання | ``provenance.created_by`` of what this caller creates: ``human`` (default), ``llm`` (the assistant's key) or ``import``. An ``llm`` caller can only publish ``created_by: llm`` versions. |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

## Функції

### Функція `check_actors`

```python
def check_actors(settings: AuthSettings) -> None: ...
```

Start-up check: ``actor`` of every configured key is one of :data:`ACTORS`.

Винятки в коді функції: `ValueError`.

Код: [auth.py:41](../../../../../services/registry/src/jane_registry/auth.py#L41).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `ACTORS` | — | `frozenset({'human', 'llm', 'import'})` |  |
| `ALL_SCOPES` | — | `frozenset({'registry:read', 'registry:write', 'registry:approve'})` |  |
