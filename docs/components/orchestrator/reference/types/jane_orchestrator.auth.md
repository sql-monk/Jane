# Модуль `jane_orchestrator.auth`

> Згенеровано `scripts/docs_reference.py` з [services/orchestrator/src/jane_orchestrator/auth.py](../../../../../services/orchestrator/src/jane_orchestrator/auth.py). Не редагуйте вручну.

Bearer authentication (ADR-0005) of the orchestrator, implemented by ``jane_kit.auth``.

Modes ``none`` (local tests on loopback), ``api_key`` (``JANE_ORCHESTRATOR_API_KEYS`` / ``JANE_ORCHESTRATOR_API_KEYS_FILE``: ``[{"name", "sha256" | "secret_ref", "scopes"}]``, only hashes kept) and ``jwt`` (``JANE_ORCHESTRATOR_JWT_*``). jane-kit's middleware authenticates every request (401) and checks the scope table ``jane_kit.auth_scopes.ORCHESTRATOR`` (403); the handlers call :func:`caller` for the principal's name (audit, ``requested_by``). Scopes: ``orchestrator:read`` (GET), ``orchestrator:write`` (changes, runs), ``orchestrator:admin`` (platform limits, connections; also grants read and write).

## Класи

### Клас `Principal`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_orchestrator.auth` |
| Код | [auth.py:27](../../../../../services/orchestrator/src/jane_orchestrator/auth.py#L27) |

```python
@dataclass(frozen=True)
class Principal: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `name` | `str` | — | читання |  |
| `scopes` | `frozenset[str]` | — | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `Principal.require`

```python
def require(self, scope: str) -> None: ...
```

Винятки в коді методу: `Forbidden`.

Код: [auth.py:31](../../../../../services/orchestrator/src/jane_orchestrator/auth.py#L31).

## Функції

### Функція `caller`

```python
def caller(request: Request, scope: str) -> Principal: ...
```

The authenticated caller of this request with ``scope`` (or ``orchestrator:admin``).

Код: [auth.py:36](../../../../../services/orchestrator/src/jane_orchestrator/auth.py#L36).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `ADMIN` | — | `'orchestrator:admin'` |  |
| `ALL_SCOPES` | — | `frozenset({'orchestrator:read', 'orchestrator:write', ADMIN})` |  |
