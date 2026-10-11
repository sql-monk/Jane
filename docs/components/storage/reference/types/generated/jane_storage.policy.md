# jane_storage.policy

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_storage.policy.SECRET_REF_NOT_ALLOWED](#jane_storagepolicysecret_ref_not_allowed)
- [jane_storage.policy.parse_host_port](#jane_storagepolicyparse_host_port)
- [jane_storage.policy.HOST_NOT_ALLOWED](#jane_storagepolicyhost_not_allowed)
- [jane_storage.policy.AddressError](#jane_storagepolicyaddresserror)
- [jane_storage.policy.AddressError.__init__](#jane_storagepolicyaddresserror__init__)
- [jane_storage.policy.AddressError.pointer](#jane_storagepolicyaddresserrorpointer)
- [jane_storage.policy.Address](#jane_storagepolicyaddress)
- [jane_storage.policy.Address.__init__](#jane_storagepolicyaddress__init__)
- [jane_storage.policy.Address.pointer](#jane_storagepolicyaddresspointer)
- [jane_storage.policy.Address.host](#jane_storagepolicyaddresshost)
- [jane_storage.policy.Address.port](#jane_storagepolicyaddressport)
- [jane_storage.policy.Address.__str__](#jane_storagepolicyaddress__str__)
- [jane_storage.policy.service_url](#jane_storagepolicyservice_url)
- [jane_storage.policy.KindAddresses](#jane_storagepolicykindaddresses)
- [jane_storage.policy.KindAddresses.__init__](#jane_storagepolicykindaddresses__init__)
- [jane_storage.policy.KindAddresses.keys](#jane_storagepolicykindaddresseskeys)
- [jane_storage.policy.KindAddresses.addresses](#jane_storagepolicykindaddressesaddresses)
- [jane_storage.policy.KIND_ADDRESSES](#jane_storagepolicykind_addresses)
- [jane_storage.policy.GENERIC_ADDRESS_KEYS](#jane_storagepolicygeneric_address_keys)
- [jane_storage.policy.network_addresses](#jane_storagepolicynetwork_addresses)
- [jane_storage.policy.ConnectionPolicy](#jane_storagepolicyconnectionpolicy)
- [jane_storage.policy.ConnectionPolicy.__init__](#jane_storagepolicyconnectionpolicy__init__)
- [jane_storage.policy.ConnectionPolicy.host_allowlist](#jane_storagepolicyconnectionpolicyhost_allowlist)
- [jane_storage.policy.ConnectionPolicy.host_allowed](#jane_storagepolicyconnectionpolicyhost_allowed)
- [jane_storage.policy.ConnectionPolicy.host_violations](#jane_storagepolicyconnectionpolicyhost_violations)
- [jane_storage.policy.ConnectionPolicy.violations](#jane_storagepolicyconnectionpolicyviolations)
- [jane_storage.policy.redact](#jane_storagepolicyredact)

## jane_storage.policy.SECRET_REF_NOT_ALLOWED

**Повторний експорт.** Код: [services/storage/src/jane_storage/policy.py:33](../../../../../../services/storage/src/jane_storage/policy.py#L33).

```python
from jane_kit.secrets import SECRET_REF_NOT_ALLOWED as SECRET_REF_NOT_ALLOWED
```

Повторний експорт: [jane_kit.secrets.SECRET_REF_NOT_ALLOWED](../../../../jane-kit/reference/types/generated/jane_kit.secrets.md#jane_kitsecretssecret_ref_not_allowed).

## jane_storage.policy.parse_host_port

**Повторний експорт.** Код: [services/storage/src/jane_storage/policy.py:33](../../../../../../services/storage/src/jane_storage/policy.py#L33).

```python
from jane_kit.secrets import parse_host_port as parse_host_port
```

Повторний експорт: [jane_kit.secrets.parse_host_port](../../../../jane-kit/reference/types/generated/jane_kit.secrets.md#jane_kitsecretsparse_host_port).

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_secret_policy.py:577](../../../../../../services/storage/tests/test_secret_policy.py#L577).

```python
assert parse_host_port("Postgres:5432") == ("postgres", 5432)
```

Контекст і передумови: [services/storage/tests/test_secret_policy.py:578](../../../../../../services/storage/tests/test_secret_policy.py#L578).

```python
assert parse_host_port("10.0.0.5") == ("10.0.0.5", None)
```

## jane_storage.policy.HOST_NOT_ALLOWED

**Константа.** Код: [services/storage/src/jane_storage/policy.py:50](../../../../../../services/storage/src/jane_storage/policy.py#L50).

```python
HOST_NOT_ALLOWED = 'host_not_allowed'
```

## jane_storage.policy.AddressError

**Клас.** Код: [services/storage/src/jane_storage/policy.py:63](../../../../../../services/storage/src/jane_storage/policy.py#L63).

```python
class AddressError(ValueError):
```

Базові типи / інтерфейси: `ValueError`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_storage.policy.md#jane_storagepolicyaddresserror__init__) | Конструктор | ні |
| [pointer](jane_storage.policy.md#jane_storagepolicyaddresserrorpointer) | Поле екземпляра | ні |

### Опис із вихідного коду

```text
A network-address parameter whose host cannot be determined safely.
```

## jane_storage.policy.AddressError.__init__

**Конструктор.** Код: [services/storage/src/jane_storage/policy.py:66](../../../../../../services/storage/src/jane_storage/policy.py#L66).

```python
def __init__(self, pointer: str, message: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `pointer` | `str` | `—` | positional-or-keyword |
| `message` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.policy.AddressError.pointer

**Поле екземпляра.** Код: [services/storage/src/jane_storage/policy.py:68](../../../../../../services/storage/src/jane_storage/policy.py#L68).

```python
self.pointer = pointer
```

## jane_storage.policy.Address

**Клас.** Код: [services/storage/src/jane_storage/policy.py:72](../../../../../../services/storage/src/jane_storage/policy.py#L72).

```python
class Address:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [pointer](jane_storage.policy.md#jane_storagepolicyaddresspointer) | Поле | ні |
| [host](jane_storage.policy.md#jane_storagepolicyaddresshost) | Поле | ні |
| [port](jane_storage.policy.md#jane_storagepolicyaddressport) | Поле | ні |
| [__str__](jane_storage.policy.md#jane_storagepolicyaddress__str__) | Метод | ні |
| [__init__](jane_storage.policy.md#jane_storagepolicyaddress__init__) | Конструктор dataclass | ні |

## jane_storage.policy.Address.__init__

**Конструктор dataclass.** Код: [services/storage/src/jane_storage/policy.py:72](../../../../../../services/storage/src/jane_storage/policy.py#L72).

```python
def __init__(self, pointer: str, host: str, port: int | None) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `pointer` | `str` | `—` | positional-or-keyword |
| `host` | `str` | `—` | positional-or-keyword |
| `port` | `int \| None` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.policy.Address.pointer

**Поле.** Код: [services/storage/src/jane_storage/policy.py:73](../../../../../../services/storage/src/jane_storage/policy.py#L73).

```python
pointer: str
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
JSON Pointer of the parameter in the Connection (``/params/host``).
```

## jane_storage.policy.Address.host

**Поле.** Код: [services/storage/src/jane_storage/policy.py:75](../../../../../../services/storage/src/jane_storage/policy.py#L75).

```python
host: str
```

Доступ: читання — так; запис — ні.

## jane_storage.policy.Address.port

**Поле.** Код: [services/storage/src/jane_storage/policy.py:76](../../../../../../services/storage/src/jane_storage/policy.py#L76).

```python
port: int | None
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
Effective port (explicit or the adapter's default); ``None`` when it is not known.
```

## jane_storage.policy.Address.__str__

**Метод.** Код: [services/storage/src/jane_storage/policy.py:79](../../../../../../services/storage/src/jane_storage/policy.py#L79).

```python
def __str__(self) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

## jane_storage.policy.service_url

**Функція.** Код: [services/storage/src/jane_storage/policy.py:115](../../../../../../services/storage/src/jane_storage/policy.py#L115).

```python
def service_url(value: object, pointer: str) -> Address:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `object` | `—` | positional-or-keyword |
| `pointer` | `str` | `—` | positional-or-keyword |

Результат: `Address`.

Явні `raise` у тілі: `AddressError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Address of a Jane service URL configured by the operator (``JANE_STORAGE_REGISTRY_URL``):
``http(s)://host[:port][/path]`` with the same strict parsing as connection addresses, one host, no userinfo,
query or fragment.
```

## jane_storage.policy.KindAddresses

**Клас.** Код: [services/storage/src/jane_storage/policy.py:239](../../../../../../services/storage/src/jane_storage/policy.py#L239).

```python
class KindAddresses:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [keys](jane_storage.policy.md#jane_storagepolicykindaddresseskeys) | Поле | ні |
| [addresses](jane_storage.policy.md#jane_storagepolicykindaddressesaddresses) | Поле | ні |
| [__init__](jane_storage.policy.md#jane_storagepolicykindaddresses__init__) | Конструктор dataclass | ні |

## jane_storage.policy.KindAddresses.__init__

**Конструктор dataclass.** Код: [services/storage/src/jane_storage/policy.py:239](../../../../../../services/storage/src/jane_storage/policy.py#L239).

```python
def __init__(self, keys: frozenset[str], addresses: Callable[[Mapping[str, Any]], list[Address]]) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `keys` | `frozenset[str]` | `—` | positional-or-keyword |
| `addresses` | `Callable[[Mapping[str, Any]], list[Address]]` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.policy.KindAddresses.keys

**Поле.** Код: [services/storage/src/jane_storage/policy.py:240](../../../../../../services/storage/src/jane_storage/policy.py#L240).

```python
keys: frozenset[str]
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
Parameters this rule interprets (the generic check skips them).
```

## jane_storage.policy.KindAddresses.addresses

**Поле.** Код: [services/storage/src/jane_storage/policy.py:242](../../../../../../services/storage/src/jane_storage/policy.py#L242).

```python
addresses: Callable[[Mapping[str, Any]], list[Address]]
```

Доступ: читання — так; запис — ні.

## jane_storage.policy.KIND_ADDRESSES

**Константа.** Код: [services/storage/src/jane_storage/policy.py:245](../../../../../../services/storage/src/jane_storage/policy.py#L245).

```python
KIND_ADDRESSES: Mapping[str, KindAddresses] = {'filesystem': KindAddresses(frozenset(), lambda _params: []), 'postgresql': KindAddresses(frozenset({'host', 'port'}), _database(5432)), 'sqlserver': KindAddresses(frozenset({'host', 'port'}), _database(1433)), 'mongodb': KindAddresses(frozenset({'host', 'port'}), _mongodb), 's3': KindAddresses(frozenset({'endpoint', 'region'}), _s3), 'minio': KindAddresses(frozenset({'endpoint'}), _minio)}
```

### Опис із вихідного коду

```text
Network addresses of the built-in adapters (``services/storage/adapters/*``, README of each adapter).
```

## jane_storage.policy.GENERIC_ADDRESS_KEYS

**Константа.** Код: [services/storage/src/jane_storage/policy.py:255](../../../../../../services/storage/src/jane_storage/policy.py#L255).

```python
GENERIC_ADDRESS_KEYS = ('host', 'hosts', 'hostname', 'server', 'address', 'endpoint', 'endpoint_url', 'url', 'uri', 'dsn', 'connection_string', 'base_url', 'api_base')
```

### Опис із вихідного коду

```text
Host-like parameters checked for every kind (``hostname[:port]``, ``scheme://host[:port]…`` or a list).
```

## jane_storage.policy.network_addresses

**Функція.** Код: [services/storage/src/jane_storage/policy.py:285](../../../../../../services/storage/src/jane_storage/policy.py#L285).

```python
def network_addresses(kind: str, params: Mapping[str, Any]) -> tuple[list[Address], list[AddressError]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `kind` | `str` | `—` | positional-or-keyword |
| `params` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `tuple[list[Address], list[AddressError]]`.

### Опис із вихідного коду

```text
Every host the adapter of ``kind`` would contact for these ``params`` + parameters that cannot be read.
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_secret_policy.py:504](../../../../../../services/storage/tests/test_secret_policy.py#L504).

```python
found, problems = network_addresses(kind, params)
```

Контекст і передумови: [services/storage/tests/test_secret_policy.py:539](../../../../../../services/storage/tests/test_secret_policy.py#L539).

```python
found, problems = network_addresses("s3", params)
```

## jane_storage.policy.ConnectionPolicy

**Клас.** Код: [services/storage/src/jane_storage/policy.py:307](../../../../../../services/storage/src/jane_storage/policy.py#L307).

```python
class ConnectionPolicy(SecretPolicy):
```

Базові типи / інтерфейси: `SecretPolicy`.

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [host_allowlist](jane_storage.policy.md#jane_storagepolicyconnectionpolicyhost_allowlist) | Поле | ні |
| [host_allowed](jane_storage.policy.md#jane_storagepolicyconnectionpolicyhost_allowed) | Метод | ні |
| [host_violations](jane_storage.policy.md#jane_storagepolicyconnectionpolicyhost_violations) | Метод | ні |
| [violations](jane_storage.policy.md#jane_storagepolicyconnectionpolicyviolations) | Метод | ні |
| [env_prefix](../../../../jane-kit/reference/types/generated/jane_kit.secrets.md#jane_kitsecretssecretpolicyenv_prefix) | Поле | так |
| [files_dir](../../../../jane-kit/reference/types/generated/jane_kit.secrets.md#jane_kitsecretssecretpolicyfiles_dir) | Поле | так |
| [secret_file](../../../../jane-kit/reference/types/generated/jane_kit.secrets.md#jane_kitsecretssecretpolicysecret_file) | Метод | так |
| [ref_error](../../../../jane-kit/reference/types/generated/jane_kit.secrets.md#jane_kitsecretssecretpolicyref_error) | Метод | так |
| [resolve](../../../../jane-kit/reference/types/generated/jane_kit.secrets.md#jane_kitsecretssecretpolicyresolve) | Метод | так |
| [__init__](jane_storage.policy.md#jane_storagepolicyconnectionpolicy__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
jane-kit's shared secret policy (R17: ``env:`` prefix, ``file:`` directory with pinned reading, ``vault:``
refused) plus the network addresses a connection's adapter may contact.
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_secret_policy.py:329](../../../../../../services/storage/tests/test_secret_policy.py#L329).

```python
policy = ConnectionPolicy(files_dir=secrets_dir)
```

Контекст і передумови: [services/storage/tests/test_secret_policy.py:597](../../../../../../services/storage/tests/test_secret_policy.py#L597).

```python
ConnectionPolicy(host_allowlist=("https://postgres",))
```

## jane_storage.policy.ConnectionPolicy.__init__

**Конструктор dataclass.** Код: [services/storage/src/jane_storage/policy.py:307](../../../../../../services/storage/src/jane_storage/policy.py#L307).

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

Контекст і передумови: [services/storage/tests/test_secret_policy.py:329](../../../../../../services/storage/tests/test_secret_policy.py#L329).

```python
policy = ConnectionPolicy(files_dir=secrets_dir)
```

Контекст і передумови: [services/storage/tests/test_secret_policy.py:597](../../../../../../services/storage/tests/test_secret_policy.py#L597).

```python
ConnectionPolicy(host_allowlist=("https://postgres",))
```

## jane_storage.policy.ConnectionPolicy.host_allowlist

**Поле.** Код: [services/storage/src/jane_storage/policy.py:311](../../../../../../services/storage/src/jane_storage/policy.py#L311).

```python
host_allowlist: Sequence[str] = ()
```

Доступ: читання — так; запис — ні.

## jane_storage.policy.ConnectionPolicy.host_allowed

**Метод.** Код: [services/storage/src/jane_storage/policy.py:318](../../../../../../services/storage/src/jane_storage/policy.py#L318).

```python
def host_allowed(self, address: Address) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `address` | `Address` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_storage.policy.ConnectionPolicy.host_violations

**Метод.** Код: [services/storage/src/jane_storage/policy.py:321](../../../../../../services/storage/src/jane_storage/policy.py#L321).

```python
def host_violations(self, kind: str, params: Mapping[str, Any]) -> list[FieldError]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `kind` | `str` | `—` | positional-or-keyword |
| `params` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `list[FieldError]`.

## jane_storage.policy.ConnectionPolicy.violations

**Метод.** Код: [services/storage/src/jane_storage/policy.py:335](../../../../../../services/storage/src/jane_storage/policy.py#L335).

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
Policy violations of a Connection document (empty: allowed).
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_secret_policy.py:457](../../../../../../services/storage/tests/test_secret_policy.py#L457).

```python
assert policy.violations(other("postgresql", {"host": "postgres"})) == []
```

Контекст і передумови: [services/storage/tests/test_secret_policy.py:458](../../../../../../services/storage/tests/test_secret_policy.py#L458).

```python
assert policy.violations(other("minio", {"endpoint": "https://minio:9443", "bucket": "bucket"})) == []
```

## jane_storage.policy.redact

**Функція.** Код: [services/storage/src/jane_storage/policy.py:346](../../../../../../services/storage/src/jane_storage/policy.py#L346).

```python
def redact(text: str, values: Iterable[str]) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `text` | `str` | `—` | positional-or-keyword |
| `values` | `Iterable[str]` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
``text`` with every secret value replaced by ``***`` (longest first).
```
