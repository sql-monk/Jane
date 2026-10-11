# jane_web_collector.egress

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_web_collector.egress.Resolver](#jane_web_collectoregressresolver)
- [jane_web_collector.egress.EgressDenied](#jane_web_collectoregressegressdenied)
- [jane_web_collector.egress.EgressDenied.__init__](#jane_web_collectoregressegressdenied__init__)
- [jane_web_collector.egress.EgressDenied.host](#jane_web_collectoregressegressdeniedhost)
- [jane_web_collector.egress.EgressDenied.address](#jane_web_collectoregressegressdeniedaddress)
- [jane_web_collector.egress.EgressDenied.reason](#jane_web_collectoregressegressdeniedreason)
- [jane_web_collector.egress.EgressPolicy](#jane_web_collectoregressegresspolicy)
- [jane_web_collector.egress.EgressPolicy.__init__](#jane_web_collectoregressegresspolicy__init__)
- [jane_web_collector.egress.EgressPolicy.deny_link_local](#jane_web_collectoregressegresspolicydeny_link_local)
- [jane_web_collector.egress.EgressPolicy.deny_private](#jane_web_collectoregressegresspolicydeny_private)
- [jane_web_collector.egress.EgressPolicy.reason](#jane_web_collectoregressegresspolicyreason)
- [jane_web_collector.egress.EgressPolicy.check](#jane_web_collectoregressegresspolicycheck)
- [jane_web_collector.egress.system_resolve](#jane_web_collectoregresssystem_resolve)
- [jane_web_collector.egress.GuardedBackend](#jane_web_collectoregressguardedbackend)
- [jane_web_collector.egress.GuardedBackend.__init__](#jane_web_collectoregressguardedbackend__init__)
- [jane_web_collector.egress.GuardedBackend.policy](#jane_web_collectoregressguardedbackendpolicy)
- [jane_web_collector.egress.GuardedBackend.resolver](#jane_web_collectoregressguardedbackendresolver)
- [jane_web_collector.egress.GuardedBackend.inner](#jane_web_collectoregressguardedbackendinner)
- [jane_web_collector.egress.GuardedBackend.connect_tcp](#jane_web_collectoregressguardedbackendconnect_tcp)
- [jane_web_collector.egress.GuardedBackend.connect_unix_socket](#jane_web_collectoregressguardedbackendconnect_unix_socket)
- [jane_web_collector.egress.GuardedBackend.sleep](#jane_web_collectoregressguardedbackendsleep)
- [jane_web_collector.egress.GuardedTransport](#jane_web_collectoregressguardedtransport)
- [jane_web_collector.egress.GuardedTransport.__init__](#jane_web_collectoregressguardedtransport__init__)

## jane_web_collector.egress.Resolver

**Змінна.** Код: [services/web-collector/src/jane_web_collector/egress.py:59](../../../../../../services/web-collector/src/jane_web_collector/egress.py#L59).

```python
Resolver = Callable[[str, int], Awaitable[list[str]]]
```

### Опис із вихідного коду

```text
``(host, port) -> addresses`` in the order to try them.
```

## jane_web_collector.egress.EgressDenied

**Клас.** Код: [services/web-collector/src/jane_web_collector/egress.py:63](../../../../../../services/web-collector/src/jane_web_collector/egress.py#L63).

```python
class EgressDenied(Exception):
```

Базові типи / інтерфейси: `Exception`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_web_collector.egress.md#jane_web_collectoregressegressdenied__init__) | Конструктор | ні |
| [host](jane_web_collector.egress.md#jane_web_collectoregressegressdeniedhost) | Поле екземпляра | ні |
| [address](jane_web_collector.egress.md#jane_web_collectoregressegressdeniedaddress) | Поле екземпляра | ні |
| [reason](jane_web_collector.egress.md#jane_web_collectoregressegressdeniedreason) | Поле екземпляра | ні |

### Опис із вихідного коду

```text
The destination address is forbidden by the outbound address policy.
```

## jane_web_collector.egress.EgressDenied.__init__

**Конструктор.** Код: [services/web-collector/src/jane_web_collector/egress.py:66](../../../../../../services/web-collector/src/jane_web_collector/egress.py#L66).

```python
def __init__(self, host: str, address: str, reason: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `host` | `str` | `—` | positional-or-keyword |
| `address` | `str` | `—` | positional-or-keyword |
| `reason` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.egress.EgressDenied.host

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/egress.py:68](../../../../../../services/web-collector/src/jane_web_collector/egress.py#L68).

```python
self.host = host
```

## jane_web_collector.egress.EgressDenied.address

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/egress.py:69](../../../../../../services/web-collector/src/jane_web_collector/egress.py#L69).

```python
self.address = address
```

## jane_web_collector.egress.EgressDenied.reason

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/egress.py:70](../../../../../../services/web-collector/src/jane_web_collector/egress.py#L70).

```python
self.reason = reason
```

## jane_web_collector.egress.EgressPolicy

**Клас.** Код: [services/web-collector/src/jane_web_collector/egress.py:86](../../../../../../services/web-collector/src/jane_web_collector/egress.py#L86).

```python
class EgressPolicy:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [deny_link_local](jane_web_collector.egress.md#jane_web_collectoregressegresspolicydeny_link_local) | Поле | ні |
| [deny_private](jane_web_collector.egress.md#jane_web_collectoregressegresspolicydeny_private) | Поле | ні |
| [reason](jane_web_collector.egress.md#jane_web_collectoregressegresspolicyreason) | Метод | ні |
| [check](jane_web_collector.egress.md#jane_web_collectoregressegresspolicycheck) | Метод | ні |
| [__init__](jane_web_collector.egress.md#jane_web_collectoregressegresspolicy__init__) | Конструктор dataclass | ні |

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_egress_policy.py:67](../../../../../../services/web-collector/tests/test_egress_policy.py#L67).

```python
assert Settings().egress_policy() == EgressPolicy(deny_link_local=True, deny_private=False)
```

Контекст і передумови: [services/web-collector/tests/test_egress_policy.py:70](../../../../../../services/web-collector/tests/test_egress_policy.py#L70).

```python
assert Settings().egress_policy() == EgressPolicy(deny_link_local=False, deny_private=True)
```

## jane_web_collector.egress.EgressPolicy.__init__

**Конструктор dataclass.** Код: [services/web-collector/src/jane_web_collector/egress.py:86](../../../../../../services/web-collector/src/jane_web_collector/egress.py#L86).

```python
def __init__(self, deny_link_local: bool = True, deny_private: bool = False) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `deny_link_local` | `bool` | `True` | positional-or-keyword |
| `deny_private` | `bool` | `False` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_egress_policy.py:67](../../../../../../services/web-collector/tests/test_egress_policy.py#L67).

```python
assert Settings().egress_policy() == EgressPolicy(deny_link_local=True, deny_private=False)
```

Контекст і передумови: [services/web-collector/tests/test_egress_policy.py:70](../../../../../../services/web-collector/tests/test_egress_policy.py#L70).

```python
assert Settings().egress_policy() == EgressPolicy(deny_link_local=False, deny_private=True)
```

## jane_web_collector.egress.EgressPolicy.deny_link_local

**Поле.** Код: [services/web-collector/src/jane_web_collector/egress.py:87](../../../../../../services/web-collector/src/jane_web_collector/egress.py#L87).

```python
deny_link_local: bool = True
```

Доступ: читання — так; запис — ні.

## jane_web_collector.egress.EgressPolicy.deny_private

**Поле.** Код: [services/web-collector/src/jane_web_collector/egress.py:88](../../../../../../services/web-collector/src/jane_web_collector/egress.py#L88).

```python
deny_private: bool = False
```

Доступ: читання — так; запис — ні.

## jane_web_collector.egress.EgressPolicy.reason

**Метод.** Код: [services/web-collector/src/jane_web_collector/egress.py:90](../../../../../../services/web-collector/src/jane_web_collector/egress.py#L90).

```python
def reason(self, address: str | IPAddress) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `address` | `str \| IPAddress` | `—` | positional-or-keyword |

Результат: `str | None`.

### Опис із вихідного коду

```text
Why ``address`` is forbidden, or ``None`` if a connection to it is allowed.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_egress_policy.py:59](../../../../../../services/web-collector/tests/test_egress_policy.py#L59).

```python
return "allowed" if policy.reason(address) is None else "denied"
```

## jane_web_collector.egress.EgressPolicy.check

**Метод.** Код: [services/web-collector/src/jane_web_collector/egress.py:99](../../../../../../services/web-collector/src/jane_web_collector/egress.py#L99).

```python
def check(self, host: str, addresses: Iterable[str]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `host` | `str` | `—` | positional-or-keyword |
| `addresses` | `Iterable[str]` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `EgressDenied`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_web_collector.egress.system_resolve

**Функція.** Код: [services/web-collector/src/jane_web_collector/egress.py:106](../../../../../../services/web-collector/src/jane_web_collector/egress.py#L106).

```python
async def system_resolve(host: str, port: int) -> list[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `host` | `str` | `—` | positional-or-keyword |
| `port` | `int` | `—` | positional-or-keyword |

Результат: `list[str]`.

### Опис із вихідного коду

```text
Addresses of ``host`` from the system resolver, without duplicates, in ``getaddrinfo`` order.
```

## jane_web_collector.egress.GuardedBackend

**Клас.** Код: [services/web-collector/src/jane_web_collector/egress.py:117](../../../../../../services/web-collector/src/jane_web_collector/egress.py#L117).

```python
class GuardedBackend(httpcore.AsyncNetworkBackend):
```

Базові типи / інтерфейси: `httpcore.AsyncNetworkBackend`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_web_collector.egress.md#jane_web_collectoregressguardedbackend__init__) | Конструктор | ні |
| [policy](jane_web_collector.egress.md#jane_web_collectoregressguardedbackendpolicy) | Поле екземпляра | ні |
| [resolver](jane_web_collector.egress.md#jane_web_collectoregressguardedbackendresolver) | Поле екземпляра | ні |
| [inner](jane_web_collector.egress.md#jane_web_collectoregressguardedbackendinner) | Поле екземпляра | ні |
| [connect_tcp](jane_web_collector.egress.md#jane_web_collectoregressguardedbackendconnect_tcp) | Метод | ні |
| [connect_unix_socket](jane_web_collector.egress.md#jane_web_collectoregressguardedbackendconnect_unix_socket) | Метод | ні |
| [sleep](jane_web_collector.egress.md#jane_web_collectoregressguardedbackendsleep) | Метод | ні |

### Опис із вихідного коду

```text
Network backend that resolves, checks and connects to a checked address (see the module docstring).
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_egress_policy.py:114](../../../../../../services/web-collector/tests/test_egress_policy.py#L114).

```python
transport = GuardedTransport(httpx.Limits(), GuardedBackend(EgressPolicy(), resolver=dns, inner=inner))
```

Контекст і передумови: [services/web-collector/tests/test_egress_policy.py:132](../../../../../../services/web-collector/tests/test_egress_policy.py#L132).

```python
transport = GuardedTransport(httpx.Limits(), GuardedBackend(EgressPolicy(deny_private=True)))
```

## jane_web_collector.egress.GuardedBackend.__init__

**Конструктор.** Код: [services/web-collector/src/jane_web_collector/egress.py:120](../../../../../../services/web-collector/src/jane_web_collector/egress.py#L120).

```python
def __init__(self, policy: EgressPolicy, *, resolver: Resolver=system_resolve, inner: httpcore.AsyncNetworkBackend | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `policy` | `EgressPolicy` | `—` | positional-or-keyword |
| `resolver` | `Resolver` | `system_resolve` | keyword-only |
| `inner` | `httpcore.AsyncNetworkBackend \| None` | `None` | keyword-only |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_egress_policy.py:114](../../../../../../services/web-collector/tests/test_egress_policy.py#L114).

```python
transport = GuardedTransport(httpx.Limits(), GuardedBackend(EgressPolicy(), resolver=dns, inner=inner))
```

Контекст і передумови: [services/web-collector/tests/test_egress_policy.py:132](../../../../../../services/web-collector/tests/test_egress_policy.py#L132).

```python
transport = GuardedTransport(httpx.Limits(), GuardedBackend(EgressPolicy(deny_private=True)))
```

## jane_web_collector.egress.GuardedBackend.policy

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/egress.py:127](../../../../../../services/web-collector/src/jane_web_collector/egress.py#L127).

```python
self.policy = policy
```

## jane_web_collector.egress.GuardedBackend.resolver

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/egress.py:128](../../../../../../services/web-collector/src/jane_web_collector/egress.py#L128).

```python
self.resolver = resolver
```

## jane_web_collector.egress.GuardedBackend.inner

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/egress.py:129](../../../../../../services/web-collector/src/jane_web_collector/egress.py#L129).

```python
self.inner = inner or httpcore.AnyIOBackend()
```

## jane_web_collector.egress.GuardedBackend.connect_tcp

**Метод.** Код: [services/web-collector/src/jane_web_collector/egress.py:131](../../../../../../services/web-collector/src/jane_web_collector/egress.py#L131).

```python
async def connect_tcp(self, host: str, port: int, timeout: float | None=None, local_address: str | None=None, socket_options: typing.Iterable[httpcore.SOCKET_OPTION] | None=None) -> httpcore.AsyncNetworkStream:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `host` | `str` | `—` | positional-or-keyword |
| `port` | `int` | `—` | positional-or-keyword |
| `timeout` | `float \| None` | `None` | positional-or-keyword |
| `local_address` | `str \| None` | `None` | positional-or-keyword |
| `socket_options` | `typing.Iterable[httpcore.SOCKET_OPTION] \| None` | `None` | positional-or-keyword |

Результат: `httpcore.AsyncNetworkStream`.

Явні `raise` у тілі: `httpcore.ConnectError`, `httpcore.ConnectTimeout`, `last`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_web_collector.egress.GuardedBackend.connect_unix_socket

**Метод.** Код: [services/web-collector/src/jane_web_collector/egress.py:160](../../../../../../services/web-collector/src/jane_web_collector/egress.py#L160).

```python
async def connect_unix_socket(self, path: str, timeout: float | None=None, socket_options: typing.Iterable[httpcore.SOCKET_OPTION] | None=None) -> httpcore.AsyncNetworkStream:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `path` | `str` | `—` | positional-or-keyword |
| `timeout` | `float \| None` | `None` | positional-or-keyword |
| `socket_options` | `typing.Iterable[httpcore.SOCKET_OPTION] \| None` | `None` | positional-or-keyword |

Результат: `httpcore.AsyncNetworkStream`.

Явні `raise` у тілі: `httpcore.ConnectError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_web_collector.egress.GuardedBackend.sleep

**Метод.** Код: [services/web-collector/src/jane_web_collector/egress.py:168](../../../../../../services/web-collector/src/jane_web_collector/egress.py#L168).

```python
async def sleep(self, seconds: float) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `seconds` | `float` | `—` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.egress.GuardedTransport

**Клас.** Код: [services/web-collector/src/jane_web_collector/egress.py:172](../../../../../../services/web-collector/src/jane_web_collector/egress.py#L172).

```python
class GuardedTransport(httpx.AsyncHTTPTransport):
```

Базові типи / інтерфейси: `httpx.AsyncHTTPTransport`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_web_collector.egress.md#jane_web_collectoregressguardedtransport__init__) | Конструктор | ні |

### Опис із вихідного коду

```text
``httpx.AsyncHTTPTransport`` whose connections go through :class:`GuardedBackend`.

httpx has no public parameter for the network backend, so the connection pool is rebuilt with the same
settings the base class uses (no proxy, ``trust_env=False``) plus the guarded backend.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_egress_policy.py:114](../../../../../../services/web-collector/tests/test_egress_policy.py#L114).

```python
transport = GuardedTransport(httpx.Limits(), GuardedBackend(EgressPolicy(), resolver=dns, inner=inner))
```

Контекст і передумови: [services/web-collector/tests/test_egress_policy.py:132](../../../../../../services/web-collector/tests/test_egress_policy.py#L132).

```python
transport = GuardedTransport(httpx.Limits(), GuardedBackend(EgressPolicy(deny_private=True)))
```

## jane_web_collector.egress.GuardedTransport.__init__

**Конструктор.** Код: [services/web-collector/src/jane_web_collector/egress.py:179](../../../../../../services/web-collector/src/jane_web_collector/egress.py#L179).

```python
def __init__(self, limits: httpx.Limits, backend: GuardedBackend) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `limits` | `httpx.Limits` | `—` | positional-or-keyword |
| `backend` | `GuardedBackend` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_egress_policy.py:114](../../../../../../services/web-collector/tests/test_egress_policy.py#L114).

```python
transport = GuardedTransport(httpx.Limits(), GuardedBackend(EgressPolicy(), resolver=dns, inner=inner))
```

Контекст і передумови: [services/web-collector/tests/test_egress_policy.py:132](../../../../../../services/web-collector/tests/test_egress_policy.py#L132).

```python
transport = GuardedTransport(httpx.Limits(), GuardedBackend(EgressPolicy(deny_private=True)))
```
