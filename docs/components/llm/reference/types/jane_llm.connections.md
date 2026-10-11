# Модуль `jane_llm.connections`

> Згенеровано `scripts/docs_reference.py` з [services/llm/src/jane_llm/connections.py](../../../../../services/llm/src/jane_llm/connections.py). Не редагуйте вручну.

Managed connections: secret reference policy and resolution, secret-like value detection (ADR-0006).

Secret values are resolved only here, in the service's own environment, and are never returned by the API, stored in the database or written to logs.

Because a connection decides *where* a resolved secret is sent (``params.api_base``), a connection must not be able to reference arbitrary process state or ship a secret to an arbitrary host. :class:`ConnectionPolicy` (from :class:`~jane_llm.settings.Settings`) restricts:

* ``env:`` references to variables with a configured prefix (default ``JANE_SECRET_``);
* ``file:`` references to files inside a configured directory (default ``/run/secrets``), read through pinned path components;
* ``params.api_base`` to a configured allowlist of exact origins (default the official provider hosts; no userinfo, backslashes or whitespace).

The secret part is jane-kit's shared :class:`jane_kit.secrets.SecretPolicy` (R17), the same as in storage and the collectors.

The policy is enforced when a connection is stored (422) **and** when it is resolved for a call.

## Зміст

- [Клас `ConnectionPolicy`](#клас-connectionpolicy)
- [Функція `resolve_ref`](#функція-resolve_ref)
- [Функція `find_secret_like`](#функція-find_secret_like)
- [Функція `resolve_connection`](#функція-resolve_connection)

## Класи

### Клас `ConnectionPolicy`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_llm.connections` |
| Успадкування | `SecretPolicy` |
| Код | [connections.py:54](../../../../../services/llm/src/jane_llm/connections.py#L54) |

```python
@dataclass(frozen=True)
class ConnectionPolicy(SecretPolicy): ...
```

jane-kit's secret policy plus the allowed origins of ``params.api_base``.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `api_base_allowlist` | `tuple[str, ...]` | `('https://api.anthropic.com',)` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `ConnectionPolicy.api_base_error`

```python
def api_base_error(self, api_base: Any) -> str | None: ...
```

Код: [connections.py:63](../../../../../services/llm/src/jane_llm/connections.py#L63).

#### Метод `ConnectionPolicy.violations`

```python
def violations(self, doc: Any, pointer: str = '/secret_refs') -> list[FieldError]: ...
```

Violations of a Connection document: its ``secret_refs`` and ``params.api_base``.

Код: [connections.py:73](../../../../../services/llm/src/jane_llm/connections.py#L73).

## Функції

### Функція `resolve_ref`

```python
def resolve_ref(ref: str, policy: ConnectionPolicy) -> str | None: ...
```

Value of an allowed ``env:VAR`` / ``file:<path>``; ``None`` if missing or not allowed.

Код: [connections.py:82](../../../../../services/llm/src/jane_llm/connections.py#L82).

### Функція `find_secret_like`

```python
def find_secret_like(params: dict[str, Any], prefix: str = '/params') -> list[FieldError]: ...
```

Pointers to values in ``params`` that look like secrets (they belong in ``secret_refs``).

Код: [connections.py:87](../../../../../services/llm/src/jane_llm/connections.py#L87).

### Функція `resolve_connection`

```python
def resolve_connection(
    doc: dict[str, Any],
    policy: ConnectionPolicy,
) -> tuple[ResolvedConnection, dict[str, bool]]: ...
```

Resolve ``secret_refs`` of a stored connection under ``policy``. Returns the connection and, per secret, whether it was resolved (for ``POST /v1/connections/{id}/test``). A connection whose ``api_base`` is not allowed gets no secrets at all.

Код: [connections.py:113](../../../../../services/llm/src/jane_llm/connections.py#L113).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `FAKE_SCRIPTS_KEY` | — | `'responses'` | Scripts of the ``fake`` provider may contain arbitrary text; exempt only when ``params.provider == "fake"``. |
