# Модуль `jane_storage.policy`

> Згенеровано `scripts/docs_reference.py` з [services/storage/src/jane_storage/policy.py](../../../../../services/storage/src/jane_storage/policy.py). Не редагуйте вручну.

Secret policy of storage connections (coordinator decision, same as WP-10 ``llm`` and WP-04 ``telegram-collector``).

A connection decides *where* a resolved secret goes: the adapter logs in to ``params.host`` / ``params.endpoint`` with it, and connections arrive through ``PUT /v1/connections/{id}``. So this executor restricts both ends:

* ``env:VAR`` — only variables starting with ``JANE_STORAGE_SECRET_ENV_PREFIX`` (default ``JANE_SECRET_``), so not ``PGPASSWORD`` or another service's configuration;
* ``file:<path>`` — only inside ``JANE_STORAGE_SECRET_FILES_DIR`` (default ``/run/secrets``); the path is resolved first (``..`` and symlinks do not escape) and the resolved file is read through pinned path components; ``vault:`` is disabled (both: jane-kit's shared :class:`jane_kit.secrets.SecretPolicy`, R17);
* every network address the adapter of the connection contacts — only hosts from ``JANE_STORAGE_CONNECTION_HOST_ALLOWLIST`` (``hostname`` = any port, ``hostname:port`` = that port; default empty, so every connection with a network address is rejected). :data:`KIND_ADDRESSES` knows the address parameters of the built-in adapters, including their defaults (``localhost``, the actual botocore S3 bucket host) and hosts inside URIs; :data:`GENERIC_ADDRESS_KEYS` are checked for every kind, so an adapter unknown to the core cannot take a host from them unchecked.

Values that URL parsers read differently (userinfo ``@``, backslashes, whitespace, control characters, percent-encoding in the host, trailing dots, IPv6 literals, Unix socket paths) are rejected instead of being "normalized".

## Зміст

- [Клас `Address`](#клас-address)
- [Клас `AddressError`](#клас-addresserror)
- [Клас `ConnectionPolicy`](#клас-connectionpolicy)
- [Клас `KindAddresses`](#клас-kindaddresses)
- [Функція `network_addresses`](#функція-network_addresses)
- [Функція `redact`](#функція-redact)
- [Функція `service_url`](#функція-service_url)

## Класи

### Клас `Address`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_storage.policy` |
| Код | [policy.py:72](../../../../../services/storage/src/jane_storage/policy.py#L72) |

```python
@dataclass(frozen=True)
class Address: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `pointer` | `str` | — | читання | JSON Pointer of the parameter in the Connection (``/params/host``). |
| `host` | `str` | — | читання |  |
| `port` | `int \| None` | — | читання | Effective port (explicit or the adapter's default); ``None`` when it is not known. |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `AddressError`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_storage.policy` |
| Успадкування | `ValueError` |
| Код | [policy.py:63](../../../../../services/storage/src/jane_storage/policy.py#L63) |

```python
class AddressError(ValueError): ...
```

A network-address parameter whose host cannot be determined safely.

#### Конструктор `AddressError.__init__`

```python
def __init__(self, pointer: str, message: str) -> None: ...
```

Код: [policy.py:66](../../../../../services/storage/src/jane_storage/policy.py#L66).

### Клас `ConnectionPolicy`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_storage.policy` |
| Успадкування | `SecretPolicy` |
| Код | [policy.py:307](../../../../../services/storage/src/jane_storage/policy.py#L307) |

```python
@dataclass(frozen=True)
class ConnectionPolicy(SecretPolicy): ...
```

jane-kit's shared secret policy (R17: ``env:`` prefix, ``file:`` directory with pinned reading, ``vault:`` refused) plus the network addresses a connection's adapter may contact.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `host_allowlist` | `Sequence[str]` | `()` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `ConnectionPolicy.host_allowed`

```python
def host_allowed(self, address: Address) -> bool: ...
```

Код: [policy.py:318](../../../../../services/storage/src/jane_storage/policy.py#L318).

#### Метод `ConnectionPolicy.host_violations`

```python
def host_violations(self, kind: str, params: Mapping[str, Any]) -> list[FieldError]: ...
```

Код: [policy.py:321](../../../../../services/storage/src/jane_storage/policy.py#L321).

#### Метод `ConnectionPolicy.violations`

```python
def violations(self, doc: Any, pointer: str = '/secret_refs') -> list[FieldError]: ...
```

Policy violations of a Connection document (empty: allowed).

Код: [policy.py:335](../../../../../services/storage/src/jane_storage/policy.py#L335).

### Клас `KindAddresses`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_storage.policy` |
| Код | [policy.py:239](../../../../../services/storage/src/jane_storage/policy.py#L239) |

```python
@dataclass(frozen=True)
class KindAddresses: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `keys` | `frozenset[str]` | — | читання | Parameters this rule interprets (the generic check skips them). |
| `addresses` | `Callable[[Mapping[str, Any]], list[Address]]` | — | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

## Функції

### Функція `network_addresses`

```python
def network_addresses(
    kind: str,
    params: Mapping[str, Any],
) -> tuple[list[Address], list[AddressError]]: ...
```

Every host the adapter of ``kind`` would contact for these ``params`` + parameters that cannot be read.

Код: [policy.py:285](../../../../../services/storage/src/jane_storage/policy.py#L285).

### Функція `redact`

```python
def redact(text: str, values: Iterable[str]) -> str: ...
```

``text`` with every secret value replaced by ``***`` (longest first).

Код: [policy.py:346](../../../../../services/storage/src/jane_storage/policy.py#L346).

### Функція `service_url`

```python
def service_url(value: object, pointer: str) -> Address: ...
```

Address of a Jane service URL configured by the operator (``JANE_STORAGE_REGISTRY_URL``): ``http(s)://host[:port][/path]`` with the same strict parsing as connection addresses, one host, no userinfo, query or fragment.

Винятки в коді функції: `AddressError`.

Код: [policy.py:115](../../../../../services/storage/src/jane_storage/policy.py#L115).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `GENERIC_ADDRESS_KEYS` | — | `('host', 'hosts', 'hostname', 'server', 'address', 'endpoint', 'endpoint_url', '` | Host-like parameters checked for every kind (``hostname[:port]``, ``scheme://host[:port]…`` or a list). |
| `HOST_NOT_ALLOWED` | — | `'host_not_allowed'` |  |
| `KIND_ADDRESSES` | `Mapping[str, KindAddresses]` | `{'filesystem': KindAddresses(frozenset(), lambda _params: []), 'postgresql': Kin` | Network addresses of the built-in adapters (``services/storage/adapters/*``, README of each adapter). |

## Реекспорт

| Назва | Визначено в |
|---|---|
| `SECRET_REF_NOT_ALLOWED` | `jane_kit.secrets` |
| `parse_host_port` | `jane_kit.secrets` |
