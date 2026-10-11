# Модуль `jane_telegram_collector.connections`

> Згенеровано `scripts/docs_reference.py` з [services/telegram-collector/src/jane_telegram_collector/connections.py](../../../../../services/telegram-collector/src/jane_telegram_collector/connections.py). Не редагуйте вручну.

Managed connections (``/v1/connections``, ADR-0006): the Telegram account the collector works as.

Only ``kind=telegram_account`` is accepted. Secret values never pass the API: ``secret_refs`` point into this service's environment and are resolved right before a client is opened (kept only in memory).

Secret policy (coordinator decision, same as WP-10 ``services/llm``): a connection decides *where* a resolved secret goes, so the collector restricts it:

* ``env:VAR`` — only variables starting with ``JANE_TELEGRAM_COLLECTOR_SECRET_ENV_PREFIX`` (default ``JANE_SECRET_``);
* ``file:<path>`` — only inside ``JANE_TELEGRAM_COLLECTOR_SECRET_FILES_DIR`` (default ``/run/secrets``; the path is resolved first, so ``..`` does not escape); ``vault:`` is disabled;
* host-like ``params`` (``server``, ``host``, ``proxy_host``, ``proxy``, ``api_base``, ``dc_address``) — only hosts from ``JANE_TELEGRAM_COLLECTOR_TELEGRAM_HOST_ALLOWLIST`` (default empty: such params are rejected).

Violations: 422 on ``PUT /v1/connections``; a connection stored bypassing the API gets no secrets and is rejected (422) when a collection or fetch would use it.

## Зміст

- [Клас `ConnectionPolicy`](#клас-connectionpolicy)
- [Функція `check_params`](#функція-check_params)
- [Функція `connection_etag`](#функція-connection_etag)
- [Функція `parse_host`](#функція-parse_host)
- [Функція `resolve_account`](#функція-resolve_account)
- [Функція `resolved_map`](#функція-resolved_map)

## Класи

### Клас `ConnectionPolicy`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_telegram_collector.connections` |
| Успадкування | `SecretPolicy` |
| Код | [connections.py:78](../../../../../services/telegram-collector/src/jane_telegram_collector/connections.py#L78) |

```python
@dataclass(frozen=True)
class ConnectionPolicy(SecretPolicy): ...
```

jane-kit's shared secret policy (R17: ``env:`` prefix, ``file:`` directory with pinned reading, ``vault:`` refused) plus the allowed hosts of host-like ``params``.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `host_allowlist` | `Sequence[str]` | `()` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `ConnectionPolicy.host_error`

```python
def host_error(self, value: Any) -> str | None: ...
```

Код: [connections.py:84](../../../../../services/telegram-collector/src/jane_telegram_collector/connections.py#L84).

#### Метод `ConnectionPolicy.violations`

```python
def violations(self, doc: Any, pointer: str = '/secret_refs') -> list[FieldError]: ...
```

Violations of a Connection document: its ``secret_refs`` and host-like ``params``.

Код: [connections.py:95](../../../../../services/telegram-collector/src/jane_telegram_collector/connections.py#L95).

## Функції

### Функція `check_params`

```python
def check_params(body: Mapping[str, Any], policy: ConnectionPolicy) -> None: ...
```

Reject other kinds, secret-looking ``params`` (``secret_detected``) and policy violations (422).

Винятки в коді функції: `ValidationFailed`, `JaneError`.

Код: [connections.py:126](../../../../../services/telegram-collector/src/jane_telegram_collector/connections.py#L126).

### Функція `connection_etag`

```python
def connection_etag(body: Mapping[str, Any]) -> str: ...
```

Код: [connections.py:105](../../../../../services/telegram-collector/src/jane_telegram_collector/connections.py#L105).

### Функція `parse_host`

```python
def parse_host(value: object) -> tuple[str, int | None] | None: ...
```

Strict ``hostname[:port]`` or ``scheme://hostname[:port]`` -> ``(host, port)``; anything else -> ``None``.

No userinfo (``@``), backslashes, paths, queries, whitespace or control characters: URL parsers disagree on such values (``evil.test<backslash>@allowed.test``), so they are rejected instead of being "normalized".

Код: [connections.py:60](../../../../../services/telegram-collector/src/jane_telegram_collector/connections.py#L60).

### Функція `resolve_account`

```python
def resolve_account(
    connection: Mapping[str, Any] | None,
    pointer: str,
    policy: ConnectionPolicy,
) -> ResolvedAccount: ...
```

Resolve every ``secret_ref``; a policy violation or an unresolvable reference is a configuration error (422).

Винятки в коді функції: `ValidationFailed`.

Код: [connections.py:151](../../../../../services/telegram-collector/src/jane_telegram_collector/connections.py#L151).

### Функція `resolved_map`

```python
def resolved_map(connection: Mapping[str, Any], policy: ConnectionPolicy) -> dict[str, bool]: ...
```

Код: [connections.py:145](../../../../../services/telegram-collector/src/jane_telegram_collector/connections.py#L145).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `HOST_PARAMS` | — | `('server', 'host', 'proxy_host', 'proxy', 'api_base', 'dc_address')` |  |
| `SUPPORTED_KINDS` | — | `frozenset({'telegram_account'})` |  |
