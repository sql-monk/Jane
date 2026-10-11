# Модуль `jane_web_collector.fetcher`

> Згенеровано `scripts/docs_reference.py` з [services/web-collector/src/jane_web_collector/fetcher.py](../../../../../services/web-collector/src/jane_web_collector/fetcher.py). Не редагуйте вручну.

HTTP fetching with per-host limits, retries, manual redirects, size limits and conditional requests.

Every hop of a redirect chain goes through ``check_hop`` (scope, exclusions, robots.txt), so a redirect cannot lead the crawler out of bounds; every connection (first request and each hop) is checked by the outbound address policy after DNS resolution (:mod:`.egress`). All numbers come from :class:`~.settings.ServiceLimits`. Per-host limits are shared by the whole process (:mod:`.host_limits`); a fetcher uses them through its run's session.

## Зміст

- [Клас `FetchError`](#клас-fetcherror)
- [Клас `Fetcher`](#клас-fetcher)
- [Клас `HttpResult`](#клас-httpresult)
- [Функція `build_client`](#функція-build_client)

## Класи

### Клас `FetchError`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_web_collector.fetcher` |
| Успадкування | `Exception` |
| Код | [fetcher.py:45](../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L45) |

```python
class FetchError(Exception): ...
```

A URL could not be fetched (network, HTTP error after retries, policy).

#### Конструктор `FetchError.__init__`

```python
def __init__(
    self,
    code: str,
    message: str,
    *,
    http_status: int | None = None,
    attempts: int = 1,
    retry_after_seconds: int | None = None,
) -> None: ...
```

Код: [fetcher.py:48](../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L48).

### Клас `Fetcher`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.fetcher` |
| Код | [fetcher.py:124](../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L124) |

```python
class Fetcher: ...
```

#### Конструктор `Fetcher.__init__`

```python
def __init__(
    self,
    client: httpx.AsyncClient,
    limits: ServiceLimits,
    limiter: HostSession,
    *,
    user_agent: str,
    headers: Mapping[str, str] | None = None,
    auth_headers: Mapping[str, str] | None = None,
    connection_policy: ConnectionPolicy | None = None,
    crawl_delay_for: DelayFor | None = None,
) -> None: ...
```

Винятки в коді методу: `ValidationFailed`.

Код: [fetcher.py:125](../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L125).

#### Метод `Fetcher.get`

```python
async def get(
    self,
    url: str,
    *,
    check_hop: HopCheck | None = None,
    conditional: Mapping[str, str] | None = None,
    max_bytes: int | None = None,
    timeouts: Timeouts | None = None,
    method: str = 'GET',
    json_body: bytes | None = None,
) -> HttpResult: ...
```

GET (or a POST of ``json_body`` with ``Content-Type: application/json``) with retries and redirects. A POST is never conditional; after a 307/308 redirect it is repeated with its body, after 301/302/303 the chain continues with GET. Raises :class:`FetchError`; policy callbacks may raise their own.

Винятки в коді методу: `FetchError`.

Код: [fetcher.py:208](../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L208).

#### Метод `Fetcher.auth_headers_for`

```python
def auth_headers_for(self, current: str, original: str) -> dict[str, str]: ...
```

Credentials only for the original host (never leak them to a redirect target on another host).

Винятки в коді методу: `FetchError`.

Код: [fetcher.py:265](../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L265).

### Клас `HttpResult`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_web_collector.fetcher` |
| Код | [fetcher.py:66](../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L66) |

```python
@dataclass
class HttpResult: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `url` | `str` | — | читання й запис |  |
| `final_url` | `str` | — | читання й запис |  |
| `status` | `int` | — | читання й запис |  |
| `headers` | `dict[str, str]` | — | читання й запис |  |
| `body` | `bytes` | — | читання й запис |  |
| `fetched_at` | `datetime` | — | читання й запис |  |
| `truncated` | `bool` | `False` | читання й запис |  |
| `redirects` | `list[str]` | `field(default_factory=list)` | читання й запис |  |
| `attempts` | `int` | `1` | читання й запис |  |
| `diagnostics` | `list[dict[str, str]]` | `field(default_factory=list)` | читання й запис | Material diagnostics of this result besides ``truncated`` (e.g. how the page was rendered). |
| `network_bytes` | `int \| None` | `None` | читання й запис | Bytes downloaded for this result when they differ from ``len(body)`` (a rendered page: the document and everything the browser loaded); counts towards ``crawl.max_bytes_per_run``. |
| `media_type` | `str` | — | читання (властивість) |  |
| `charset` | `str \| None` | — | читання (властивість) |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

## Функції

### Функція `build_client`

```python
def build_client(
    limits: ServiceLimits,
    egress: EgressPolicy | None = None,
    *,
    resolver: Resolver = system_resolve,
) -> httpx.AsyncClient: ...
```

The fetch client; every connection is checked by ``egress`` (default: link-local denied).

Код: [fetcher.py:95](../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L95).
