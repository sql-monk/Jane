# Модуль `jane_web_collector.egress`

> Згенеровано `scripts/docs_reference.py` з [services/web-collector/src/jane_web_collector/egress.py](../../../../../services/web-collector/src/jane_web_collector/egress.py). Не редагуйте вручну.

Outbound address policy of the fetch client (protection against SSRF).

A collection or ``POST /v1/fetches`` must not turn the collector into a proxy to the cloud metadata service or to internal services. Every TCP connection of the fetch client goes through :class:`GuardedBackend`:

1. the host name is resolved once (``getaddrinfo``);
2. **every** resolved address is checked by :class:`EgressPolicy` - one forbidden address denies the host;
3. the connection is opened to an address that was checked (TLS still verifies the original host name), so a DNS answer that changes between the check and the connection (DNS rebinding) cannot bypass the policy.

The check is made at connection time, so it covers the first request, every redirect hop (a new host is a new connection; the redirect target is also re-checked by scope and robots.txt before it is requested), ``robots.txt`` and sitemap/strategy fetches alike. A denial is :class:`EgressDenied`; the fetcher turns it into ``access_denied_by_policy`` (403 for ``POST /v1/fetches``, an error of the URL in a collection).

Policy (``Settings.egress_*``, README "Політика вихідних адрес"):

* ``deny_link_local`` (default **on**): link-local ``169.254.0.0/16`` (cloud metadata ``169.254.169.254``), ``fe80::/10`` and the AWS IPv6 metadata address ``fd00:ec2::254``;
* ``deny_private`` (default off): every address that is not globally reachable - loopback, RFC 1918, ``fc00::/7``, CGNAT ``100.64.0.0/10``, ``0.0.0.0/8``, documentation and reserved ranges - and multicast. Off by default because the dev/e2e test site lives in a private Docker network.

IPv4 addresses embedded in IPv6 (``::ffff:a.b.c.d``, NAT64 ``64:ff9b::/96``, 6to4 ``2002::/16``) are checked as the IPv4 address they lead to.

## Зміст

- [Клас `EgressDenied`](#клас-egressdenied)
- [Клас `EgressPolicy`](#клас-egresspolicy)
- [Клас `GuardedBackend`](#клас-guardedbackend)
- [Клас `GuardedTransport`](#клас-guardedtransport)
- [Функція `system_resolve`](#функція-system_resolve)

## Класи

### Клас `EgressDenied`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_web_collector.egress` |
| Успадкування | `Exception` |
| Код | [egress.py:63](../../../../../services/web-collector/src/jane_web_collector/egress.py#L63) |

```python
class EgressDenied(Exception): ...
```

The destination address is forbidden by the outbound address policy.

#### Конструктор `EgressDenied.__init__`

```python
def __init__(self, host: str, address: str, reason: str) -> None: ...
```

Код: [egress.py:66](../../../../../services/web-collector/src/jane_web_collector/egress.py#L66).

### Клас `EgressPolicy`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_web_collector.egress` |
| Код | [egress.py:86](../../../../../services/web-collector/src/jane_web_collector/egress.py#L86) |

```python
@dataclass(frozen=True)
class EgressPolicy: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `deny_link_local` | `bool` | `True` | читання |  |
| `deny_private` | `bool` | `False` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `EgressPolicy.reason`

```python
def reason(self, address: str | IPAddress) -> str | None: ...
```

Why ``address`` is forbidden, or ``None`` if a connection to it is allowed.

Код: [egress.py:90](../../../../../services/web-collector/src/jane_web_collector/egress.py#L90).

#### Метод `EgressPolicy.check`

```python
def check(self, host: str, addresses: Iterable[str]) -> None: ...
```

Винятки в коді методу: `EgressDenied`.

Код: [egress.py:99](../../../../../services/web-collector/src/jane_web_collector/egress.py#L99).

### Клас `GuardedBackend`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.egress` |
| Успадкування | `httpcore.AsyncNetworkBackend` |
| Код | [egress.py:117](../../../../../services/web-collector/src/jane_web_collector/egress.py#L117) |

```python
class GuardedBackend(httpcore.AsyncNetworkBackend): ...
```

Network backend that resolves, checks and connects to a checked address (see the module docstring).

#### Конструктор `GuardedBackend.__init__`

```python
def __init__(
    self,
    policy: EgressPolicy,
    *,
    resolver: Resolver = system_resolve,
    inner: httpcore.AsyncNetworkBackend | None = None,
) -> None: ...
```

Код: [egress.py:120](../../../../../services/web-collector/src/jane_web_collector/egress.py#L120).

#### Метод `GuardedBackend.connect_tcp`

```python
async def connect_tcp(
    self,
    host: str,
    port: int,
    timeout: float | None = None,
    local_address: str | None = None,
    socket_options: typing.Iterable[httpcore.SOCKET_OPTION] | None = None,
) -> httpcore.AsyncNetworkStream: ...
```

Код: [egress.py:131](../../../../../services/web-collector/src/jane_web_collector/egress.py#L131).

#### Метод `GuardedBackend.connect_unix_socket`

```python
async def connect_unix_socket(
    self,
    path: str,
    timeout: float | None = None,
    socket_options: typing.Iterable[httpcore.SOCKET_OPTION] | None = None,
) -> httpcore.AsyncNetworkStream: ...
```

Код: [egress.py:160](../../../../../services/web-collector/src/jane_web_collector/egress.py#L160).

#### Метод `GuardedBackend.sleep`

```python
async def sleep(self, seconds: float) -> None: ...
```

Код: [egress.py:168](../../../../../services/web-collector/src/jane_web_collector/egress.py#L168).

### Клас `GuardedTransport`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.egress` |
| Успадкування | `httpx.AsyncHTTPTransport` |
| Код | [egress.py:172](../../../../../services/web-collector/src/jane_web_collector/egress.py#L172) |

```python
class GuardedTransport(httpx.AsyncHTTPTransport): ...
```

``httpx.AsyncHTTPTransport`` whose connections go through :class:`GuardedBackend`.

httpx has no public parameter for the network backend, so the connection pool is rebuilt with the same settings the base class uses (no proxy, ``trust_env=False``) plus the guarded backend.

#### Конструктор `GuardedTransport.__init__`

```python
def __init__(self, limits: httpx.Limits, backend: GuardedBackend) -> None: ...
```

Код: [egress.py:179](../../../../../services/web-collector/src/jane_web_collector/egress.py#L179).

## Функції

### Функція `system_resolve`

```python
async def system_resolve(host: str, port: int) -> list[str]: ...
```

Addresses of ``host`` from the system resolver, without duplicates, in ``getaddrinfo`` order.

Код: [egress.py:106](../../../../../services/web-collector/src/jane_web_collector/egress.py#L106).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `Resolver` | — | `Callable[[str, int], Awaitable[list[str]]]` | ``(host, port) -> addresses`` in the order to try them. |
