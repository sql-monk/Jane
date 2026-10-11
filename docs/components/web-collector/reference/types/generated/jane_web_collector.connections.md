# jane_web_collector.connections

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_web_collector.connections.header_value_safe](#jane_web_collectorconnectionsheader_value_safe)
- [jane_web_collector.connections.SUPPORTED_KINDS](#jane_web_collectorconnectionssupported_kinds)
- [jane_web_collector.connections.is_safe_rule_header](#jane_web_collectorconnectionsis_safe_rule_header)
- [jane_web_collector.connections.header_name_safe](#jane_web_collectorconnectionsheader_name_safe)
- [jane_web_collector.connections.ConnectionPolicy](#jane_web_collectorconnectionsconnectionpolicy)
- [jane_web_collector.connections.ConnectionPolicy.__init__](#jane_web_collectorconnectionsconnectionpolicy__init__)
- [jane_web_collector.connections.ConnectionPolicy.origin_allowlist](#jane_web_collectorconnectionsconnectionpolicyorigin_allowlist)
- [jane_web_collector.connections.ConnectionPolicy.origin_allowed](#jane_web_collectorconnectionsconnectionpolicyorigin_allowed)
- [jane_web_collector.connections.ConnectionPolicy.validate_refs](#jane_web_collectorconnectionsconnectionpolicyvalidate_refs)
- [jane_web_collector.connections.connection_etag](#jane_web_collectorconnectionsconnection_etag)
- [jane_web_collector.connections.check_params](#jane_web_collectorconnectionscheck_params)
- [jane_web_collector.connections.auth_headers](#jane_web_collectorconnectionsauth_headers)

## jane_web_collector.connections.header_value_safe

**Повторний експорт.** Код: [services/web-collector/src/jane_web_collector/connections.py:23](../../../../../../services/web-collector/src/jane_web_collector/connections.py#L23).

```python
from jane_kit.rules import header_value_safe as header_value_safe
```

Повторний експорт: [jane_kit.rules.header_value_safe](../../../../jane-kit/reference/types/generated/jane_kit.rules.md#jane_kitrulesheader_value_safe).

## jane_web_collector.connections.SUPPORTED_KINDS

**Константа.** Код: [services/web-collector/src/jane_web_collector/connections.py:37](../../../../../../services/web-collector/src/jane_web_collector/connections.py#L37).

```python
SUPPORTED_KINDS = frozenset({'http'})
```

## jane_web_collector.connections.is_safe_rule_header

**Функція.** Код: [services/web-collector/src/jane_web_collector/connections.py:47](../../../../../../services/web-collector/src/jane_web_collector/connections.py#L47).

```python
def is_safe_rule_header(name: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `name` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

### Опис із вихідного коду

```text
Only these non-credential headers may come from a source-controlled rules package.
```

## jane_web_collector.connections.header_name_safe

**Функція.** Код: [services/web-collector/src/jane_web_collector/connections.py:52](../../../../../../services/web-collector/src/jane_web_collector/connections.py#L52).

```python
def header_name_safe(value: object) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `object` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_web_collector.connections.ConnectionPolicy

**Клас.** Код: [services/web-collector/src/jane_web_collector/connections.py:57](../../../../../../services/web-collector/src/jane_web_collector/connections.py#L57).

```python
class ConnectionPolicy(SecretPolicy):
```

Базові типи / інтерфейси: `SecretPolicy`.

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [origin_allowlist](jane_web_collector.connections.md#jane_web_collectorconnectionsconnectionpolicyorigin_allowlist) | Поле | ні |
| [origin_allowed](jane_web_collector.connections.md#jane_web_collectorconnectionsconnectionpolicyorigin_allowed) | Метод | ні |
| [validate_refs](jane_web_collector.connections.md#jane_web_collectorconnectionsconnectionpolicyvalidate_refs) | Метод | ні |
| [env_prefix](../../../../jane-kit/reference/types/generated/jane_kit.secrets.md#jane_kitsecretssecretpolicyenv_prefix) | Поле | так |
| [files_dir](../../../../jane-kit/reference/types/generated/jane_kit.secrets.md#jane_kitsecretssecretpolicyfiles_dir) | Поле | так |
| [secret_file](../../../../jane-kit/reference/types/generated/jane_kit.secrets.md#jane_kitsecretssecretpolicysecret_file) | Метод | так |
| [ref_error](../../../../jane-kit/reference/types/generated/jane_kit.secrets.md#jane_kitsecretssecretpolicyref_error) | Метод | так |
| [violations](../../../../jane-kit/reference/types/generated/jane_kit.secrets.md#jane_kitsecretssecretpolicyviolations) | Метод | так |
| [resolve](../../../../jane-kit/reference/types/generated/jane_kit.secrets.md#jane_kitsecretssecretpolicyresolve) | Метод | так |
| [__init__](jane_web_collector.connections.md#jane_web_collectorconnectionsconnectionpolicy__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
Operator-controlled secret and authenticated destination boundaries: jane-kit's shared secret policy
(R17: ``env:`` prefix, ``file:`` directory with pinned reading) and the exact origins a credential may go to.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_connection_policy.py:84](../../../../../../services/web-collector/tests/test_connection_policy.py#L84).

```python
policy = ConnectionPolicy(origin_allowlist=("https://source.test:443",))
```

Контекст і передумови: [services/web-collector/tests/test_connection_policy.py:116](../../../../../../services/web-collector/tests/test_connection_policy.py#L116).

```python
policy = ConnectionPolicy(origin_allowlist=("https://source.test",))
```

## jane_web_collector.connections.ConnectionPolicy.__init__

**Конструктор dataclass.** Код: [services/web-collector/src/jane_web_collector/connections.py:57](../../../../../../services/web-collector/src/jane_web_collector/connections.py#L57).

```python
def __init__(self, env_prefix: str = 'JANE_SECRET_', files_dir: Path | None = Path('/run/secrets'), origin_allowlist: tuple[str, ...] = ()) -> None:
```

Базові типи / інтерфейси: `SecretPolicy`.

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `env_prefix` | `str` | `'JANE_SECRET_'` | positional-or-keyword |
| `files_dir` | `Path \| None` | `Path('/run/secrets')` | positional-or-keyword |
| `origin_allowlist` | `tuple[str, ...]` | `()` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_connection_policy.py:84](../../../../../../services/web-collector/tests/test_connection_policy.py#L84).

```python
policy = ConnectionPolicy(origin_allowlist=("https://source.test:443",))
```

Контекст і передумови: [services/web-collector/tests/test_connection_policy.py:116](../../../../../../services/web-collector/tests/test_connection_policy.py#L116).

```python
policy = ConnectionPolicy(origin_allowlist=("https://source.test",))
```

## jane_web_collector.connections.ConnectionPolicy.origin_allowlist

**Поле.** Код: [services/web-collector/src/jane_web_collector/connections.py:61](../../../../../../services/web-collector/src/jane_web_collector/connections.py#L61).

```python
origin_allowlist: tuple[str, ...] = ()
```

Доступ: читання — так; запис — ні.

## jane_web_collector.connections.ConnectionPolicy.origin_allowed

**Метод.** Код: [services/web-collector/src/jane_web_collector/connections.py:71](../../../../../../services/web-collector/src/jane_web_collector/connections.py#L71).

```python
def origin_allowed(self, url: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_connection_policy.py:85](../../../../../../services/web-collector/tests/test_connection_policy.py#L85).

```python
assert policy.origin_allowed("https://source.test/product/1")
```

Контекст і передумови: [services/web-collector/tests/test_connection_policy.py:93](../../../../../../services/web-collector/tests/test_connection_policy.py#L93).

```python
assert not policy.origin_allowed(url)
```

## jane_web_collector.connections.ConnectionPolicy.validate_refs

**Метод.** Код: [services/web-collector/src/jane_web_collector/connections.py:74](../../../../../../services/web-collector/src/jane_web_collector/connections.py#L74).

```python
def validate_refs(self, body: Mapping[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `body` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_web_collector.connections.connection_etag

**Функція.** Код: [services/web-collector/src/jane_web_collector/connections.py:80](../../../../../../services/web-collector/src/jane_web_collector/connections.py#L80).

```python
def connection_etag(body: Mapping[str, Any]) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `body` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `str`.

## jane_web_collector.connections.check_params

**Функція.** Код: [services/web-collector/src/jane_web_collector/connections.py:101](../../../../../../services/web-collector/src/jane_web_collector/connections.py#L101).

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
Reject non-http kinds and secret-looking values in ``params`` (``secret_detected``).
```

## jane_web_collector.connections.auth_headers

**Функція.** Код: [services/web-collector/src/jane_web_collector/connections.py:127](../../../../../../services/web-collector/src/jane_web_collector/connections.py#L127).

```python
def auth_headers(connection: Mapping[str, Any], policy: ConnectionPolicy) -> dict[str, str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `connection` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `policy` | `ConnectionPolicy` | `—` | positional-or-keyword |

Результат: `dict[str, str]`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_connection_policy.py:71](../../../../../../services/web-collector/tests/test_connection_policy.py#L71).

```python
auth_headers(
            {
                **_connection("env:JANE_SECRET_SITE_TOKEN"),
                "secret_refs": {
                    "token": "env:JANE_SECRET_SITE_TOKEN",
                    "extra": "env:JANE_WEB_COLLECTOR_REGISTRY_URL",
                },
            },
            policy,
        )
```
