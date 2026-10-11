# jane_telegram_collector.connections

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_telegram_collector.connections.SUPPORTED_KINDS](#jane_telegram_collectorconnectionssupported_kinds)
- [jane_telegram_collector.connections.HOST_PARAMS](#jane_telegram_collectorconnectionshost_params)
- [jane_telegram_collector.connections.parse_host](#jane_telegram_collectorconnectionsparse_host)
- [jane_telegram_collector.connections.ConnectionPolicy](#jane_telegram_collectorconnectionsconnectionpolicy)
- [jane_telegram_collector.connections.ConnectionPolicy.__init__](#jane_telegram_collectorconnectionsconnectionpolicy__init__)
- [jane_telegram_collector.connections.ConnectionPolicy.host_allowlist](#jane_telegram_collectorconnectionsconnectionpolicyhost_allowlist)
- [jane_telegram_collector.connections.ConnectionPolicy.host_error](#jane_telegram_collectorconnectionsconnectionpolicyhost_error)
- [jane_telegram_collector.connections.ConnectionPolicy.violations](#jane_telegram_collectorconnectionsconnectionpolicyviolations)
- [jane_telegram_collector.connections.connection_etag](#jane_telegram_collectorconnectionsconnection_etag)
- [jane_telegram_collector.connections.check_params](#jane_telegram_collectorconnectionscheck_params)
- [jane_telegram_collector.connections.resolved_map](#jane_telegram_collectorconnectionsresolved_map)
- [jane_telegram_collector.connections.resolve_account](#jane_telegram_collectorconnectionsresolve_account)

## jane_telegram_collector.connections.SUPPORTED_KINDS

**Константа.** Код: [services/telegram-collector/src/jane_telegram_collector/connections.py:44](../../../../../../services/telegram-collector/src/jane_telegram_collector/connections.py#L44).

```python
SUPPORTED_KINDS = frozenset({'telegram_account'})
```

## jane_telegram_collector.connections.HOST_PARAMS

**Константа.** Код: [services/telegram-collector/src/jane_telegram_collector/connections.py:45](../../../../../../services/telegram-collector/src/jane_telegram_collector/connections.py#L45).

```python
HOST_PARAMS = ('server', 'host', 'proxy_host', 'proxy', 'api_base', 'dc_address')
```

## jane_telegram_collector.connections.parse_host

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/connections.py:60](../../../../../../services/telegram-collector/src/jane_telegram_collector/connections.py#L60).

```python
def parse_host(value: object) -> tuple[str, int | None] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `object` | `—` | positional-or-keyword |

Результат: `tuple[str, int | None] | None`.

### Опис із вихідного коду

```text
Strict ``hostname[:port]`` or ``scheme://hostname[:port]`` -> ``(host, port)``; anything else -> ``None``.

No userinfo (``@``), backslashes, paths, queries, whitespace or control characters: URL parsers disagree
on such values (``evil.test<backslash>@allowed.test``), so they are rejected instead of being "normalized".
```

## jane_telegram_collector.connections.ConnectionPolicy

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/connections.py:78](../../../../../../services/telegram-collector/src/jane_telegram_collector/connections.py#L78).

```python
class ConnectionPolicy(SecretPolicy):
```

Базові типи / інтерфейси: `SecretPolicy`.

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [host_allowlist](jane_telegram_collector.connections.md#jane_telegram_collectorconnectionsconnectionpolicyhost_allowlist) | Поле | ні |
| [host_error](jane_telegram_collector.connections.md#jane_telegram_collectorconnectionsconnectionpolicyhost_error) | Метод | ні |
| [violations](jane_telegram_collector.connections.md#jane_telegram_collectorconnectionsconnectionpolicyviolations) | Метод | ні |
| [env_prefix](../../../../jane-kit/reference/types/generated/jane_kit.secrets.md#jane_kitsecretssecretpolicyenv_prefix) | Поле | так |
| [files_dir](../../../../jane-kit/reference/types/generated/jane_kit.secrets.md#jane_kitsecretssecretpolicyfiles_dir) | Поле | так |
| [secret_file](../../../../jane-kit/reference/types/generated/jane_kit.secrets.md#jane_kitsecretssecretpolicysecret_file) | Метод | так |
| [ref_error](../../../../jane-kit/reference/types/generated/jane_kit.secrets.md#jane_kitsecretssecretpolicyref_error) | Метод | так |
| [resolve](../../../../jane-kit/reference/types/generated/jane_kit.secrets.md#jane_kitsecretssecretpolicyresolve) | Метод | так |
| [__init__](jane_telegram_collector.connections.md#jane_telegram_collectorconnectionsconnectionpolicy__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
jane-kit's shared secret policy (R17: ``env:`` prefix, ``file:`` directory with pinned reading, ``vault:``
refused) plus the allowed hosts of host-like ``params``.
```

### Приклади з тестів

Контекст і передумови: [services/telegram-collector/tests/test_secret_files.py:31](../../../../../../services/telegram-collector/tests/test_secret_files.py#L31).

```python
policy = ConnectionPolicy(files_dir=secrets_dir)
```

Контекст і передумови: [services/telegram-collector/tests/test_secret_files.py:93](../../../../../../services/telegram-collector/tests/test_secret_files.py#L93).

```python
policy = ConnectionPolicy(files_dir=secrets_dir)
```

## jane_telegram_collector.connections.ConnectionPolicy.__init__

**Конструктор dataclass.** Код: [services/telegram-collector/src/jane_telegram_collector/connections.py:78](../../../../../../services/telegram-collector/src/jane_telegram_collector/connections.py#L78).

```python
def __init__(self, env_prefix: str = 'JANE_SECRET_', files_dir: Path | None = Path('/run/secrets'), host_allowlist: Sequence[str] = ()) -> None:
```

Базові типи / інтерфейси: `SecretPolicy`.

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `env_prefix` | `str` | `'JANE_SECRET_'` | positional-or-keyword |
| `files_dir` | `Path \| None` | `Path('/run/secrets')` | positional-or-keyword |
| `host_allowlist` | `Sequence[str]` | `()` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/telegram-collector/tests/test_secret_files.py:31](../../../../../../services/telegram-collector/tests/test_secret_files.py#L31).

```python
policy = ConnectionPolicy(files_dir=secrets_dir)
```

Контекст і передумови: [services/telegram-collector/tests/test_secret_files.py:93](../../../../../../services/telegram-collector/tests/test_secret_files.py#L93).

```python
policy = ConnectionPolicy(files_dir=secrets_dir)
```

## jane_telegram_collector.connections.ConnectionPolicy.host_allowlist

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/connections.py:82](../../../../../../services/telegram-collector/src/jane_telegram_collector/connections.py#L82).

```python
host_allowlist: Sequence[str] = ()
```

Доступ: читання — так; запис — ні.

## jane_telegram_collector.connections.ConnectionPolicy.host_error

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/connections.py:84](../../../../../../services/telegram-collector/src/jane_telegram_collector/connections.py#L84).

```python
def host_error(self, value: Any) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `value` | `Any` | `—` | positional-or-keyword |

Результат: `str | None`.

## jane_telegram_collector.connections.ConnectionPolicy.violations

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/connections.py:95](../../../../../../services/telegram-collector/src/jane_telegram_collector/connections.py#L95).

```python
def violations(self, doc: Any, pointer: str='/secret_refs') -> list[FieldError]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `doc` | `Any` | `—` | positional-or-keyword |
| `pointer` | `str` | `'/secret_refs'` | positional-or-keyword |

Результат: `list[FieldError]`.

### Опис із вихідного коду

```text
Violations of a Connection document: its ``secret_refs`` and host-like ``params``.
```

## jane_telegram_collector.connections.connection_etag

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/connections.py:105](../../../../../../services/telegram-collector/src/jane_telegram_collector/connections.py#L105).

```python
def connection_etag(body: Mapping[str, Any]) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `body` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `str`.

## jane_telegram_collector.connections.check_params

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/connections.py:126](../../../../../../services/telegram-collector/src/jane_telegram_collector/connections.py#L126).

```python
def check_params(body: Mapping[str, Any], policy: ConnectionPolicy) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `body` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `policy` | `ConnectionPolicy` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `JaneError`, `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Reject other kinds, secret-looking ``params`` (``secret_detected``) and policy violations (422).
```

## jane_telegram_collector.connections.resolved_map

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/connections.py:145](../../../../../../services/telegram-collector/src/jane_telegram_collector/connections.py#L145).

```python
def resolved_map(connection: Mapping[str, Any], policy: ConnectionPolicy) -> dict[str, bool]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `connection` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `policy` | `ConnectionPolicy` | `—` | positional-or-keyword |

Результат: `dict[str, bool]`.

## jane_telegram_collector.connections.resolve_account

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/connections.py:151](../../../../../../services/telegram-collector/src/jane_telegram_collector/connections.py#L151).

```python
def resolve_account(connection: Mapping[str, Any] | None, pointer: str, policy: ConnectionPolicy) -> ResolvedAccount:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `connection` | `Mapping[str, Any] \| None` | `—` | positional-or-keyword |
| `pointer` | `str` | `—` | positional-or-keyword |
| `policy` | `ConnectionPolicy` | `—` | positional-or-keyword |

Результат: `ResolvedAccount`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Resolve every ``secret_ref``; a policy violation or an unresolvable reference is a configuration error (422).
```
