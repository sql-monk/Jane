# Модуль `jane_web_collector.connections`

> Згенеровано `scripts/docs_reference.py` з [services/web-collector/src/jane_web_collector/connections.py](../../../../../services/web-collector/src/jane_web_collector/connections.py). Не редагуйте вручну.

Managed connections (``/v1/connections``, ADR-0006) for sites that need HTTP authentication.

Only ``kind=http`` is used by the web collector. Secret values never pass the API: ``secret_refs`` point to ``env:VAR`` or ``file:<path>`` within operator-configured bounds (``vault:`` has no provider in v1 and is rejected). How the resolved secrets are applied (service convention for ``params``, documented in README):

* ``params.auth_scheme = "bearer"`` + ``secret_refs.token`` -> ``Authorization: Bearer <token>``;
* ``params.auth_scheme = "basic"`` + ``secret_refs.username`` / ``secret_refs.password``;
* ``params.auth_scheme = "header"`` + ``params.header_name`` + ``secret_refs.value``.

## Зміст

- [Клас `ConnectionPolicy`](#клас-connectionpolicy)
- [Функція `auth_headers`](#функція-auth_headers)
- [Функція `check_params`](#функція-check_params)
- [Функція `connection_etag`](#функція-connection_etag)
- [Функція `header_name_safe`](#функція-header_name_safe)
- [Функція `is_safe_rule_header`](#функція-is_safe_rule_header)

## Класи

### Клас `ConnectionPolicy`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_web_collector.connections` |
| Успадкування | `SecretPolicy` |
| Код | [connections.py:57](../../../../../services/web-collector/src/jane_web_collector/connections.py#L57) |

```python
@dataclass(frozen=True)
class ConnectionPolicy(SecretPolicy): ...
```

Operator-controlled secret and authenticated destination boundaries: jane-kit's shared secret policy (R17: ``env:`` prefix, ``file:`` directory with pinned reading) and the exact origins a credential may go to.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `origin_allowlist` | `tuple[str, ...]` | `()` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `ConnectionPolicy.origin_allowed`

```python
def origin_allowed(self, url: str) -> bool: ...
```

Код: [connections.py:71](../../../../../services/web-collector/src/jane_web_collector/connections.py#L71).

#### Метод `ConnectionPolicy.validate_refs`

```python
def validate_refs(self, body: Mapping[str, Any]) -> None: ...
```

Винятки в коді методу: `ValidationFailed`.

Код: [connections.py:74](../../../../../services/web-collector/src/jane_web_collector/connections.py#L74).

## Функції

### Функція `auth_headers`

```python
def auth_headers(connection: Mapping[str, Any], policy: ConnectionPolicy) -> dict[str, str]: ...
```

Винятки в коді функції: `ValidationFailed`.

Код: [connections.py:127](../../../../../services/web-collector/src/jane_web_collector/connections.py#L127).

### Функція `check_params`

```python
def check_params(body: Mapping[str, Any], policy: ConnectionPolicy) -> None: ...
```

Reject non-http kinds and secret-looking values in ``params`` (``secret_detected``).

Винятки в коді функції: `ValidationFailed`, `JaneError`.

Код: [connections.py:101](../../../../../services/web-collector/src/jane_web_collector/connections.py#L101).

### Функція `connection_etag`

```python
def connection_etag(body: Mapping[str, Any]) -> str: ...
```

Код: [connections.py:80](../../../../../services/web-collector/src/jane_web_collector/connections.py#L80).

### Функція `header_name_safe`

```python
def header_name_safe(value: object) -> bool: ...
```

Код: [connections.py:52](../../../../../services/web-collector/src/jane_web_collector/connections.py#L52).

### Функція `is_safe_rule_header`

```python
def is_safe_rule_header(name: str) -> bool: ...
```

Only these non-credential headers may come from a source-controlled rules package.

Код: [connections.py:47](../../../../../services/web-collector/src/jane_web_collector/connections.py#L47).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `SUPPORTED_KINDS` | — | `frozenset({'http'})` |  |

## Реекспорт

| Назва | Визначено в |
|---|---|
| `header_value_safe` | `jane_kit.rules` |
