# jane_web_collector.fetcher

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_web_collector.fetcher.FetchError](#jane_web_collectorfetcherfetcherror)
- [jane_web_collector.fetcher.FetchError.__init__](#jane_web_collectorfetcherfetcherror__init__)
- [jane_web_collector.fetcher.FetchError.code](#jane_web_collectorfetcherfetcherrorcode)
- [jane_web_collector.fetcher.FetchError.message](#jane_web_collectorfetcherfetcherrormessage)
- [jane_web_collector.fetcher.FetchError.http_status](#jane_web_collectorfetcherfetcherrorhttp_status)
- [jane_web_collector.fetcher.FetchError.attempts](#jane_web_collectorfetcherfetcherrorattempts)
- [jane_web_collector.fetcher.FetchError.retry_after_seconds](#jane_web_collectorfetcherfetcherrorretry_after_seconds)
- [jane_web_collector.fetcher.HttpResult](#jane_web_collectorfetcherhttpresult)
- [jane_web_collector.fetcher.HttpResult.__init__](#jane_web_collectorfetcherhttpresult__init__)
- [jane_web_collector.fetcher.HttpResult.url](#jane_web_collectorfetcherhttpresulturl)
- [jane_web_collector.fetcher.HttpResult.final_url](#jane_web_collectorfetcherhttpresultfinal_url)
- [jane_web_collector.fetcher.HttpResult.status](#jane_web_collectorfetcherhttpresultstatus)
- [jane_web_collector.fetcher.HttpResult.headers](#jane_web_collectorfetcherhttpresultheaders)
- [jane_web_collector.fetcher.HttpResult.body](#jane_web_collectorfetcherhttpresultbody)
- [jane_web_collector.fetcher.HttpResult.fetched_at](#jane_web_collectorfetcherhttpresultfetched_at)
- [jane_web_collector.fetcher.HttpResult.truncated](#jane_web_collectorfetcherhttpresulttruncated)
- [jane_web_collector.fetcher.HttpResult.redirects](#jane_web_collectorfetcherhttpresultredirects)
- [jane_web_collector.fetcher.HttpResult.attempts](#jane_web_collectorfetcherhttpresultattempts)
- [jane_web_collector.fetcher.HttpResult.diagnostics](#jane_web_collectorfetcherhttpresultdiagnostics)
- [jane_web_collector.fetcher.HttpResult.network_bytes](#jane_web_collectorfetcherhttpresultnetwork_bytes)
- [jane_web_collector.fetcher.HttpResult.media_type](#jane_web_collectorfetcherhttpresultmedia_type)
- [jane_web_collector.fetcher.HttpResult.charset](#jane_web_collectorfetcherhttpresultcharset)
- [jane_web_collector.fetcher.build_client](#jane_web_collectorfetcherbuild_client)
- [jane_web_collector.fetcher.Fetcher](#jane_web_collectorfetcherfetcher)
- [jane_web_collector.fetcher.Fetcher.__init__](#jane_web_collectorfetcherfetcher__init__)
- [jane_web_collector.fetcher.Fetcher.client](#jane_web_collectorfetcherfetcherclient)
- [jane_web_collector.fetcher.Fetcher.limits](#jane_web_collectorfetcherfetcherlimits)
- [jane_web_collector.fetcher.Fetcher.limiter](#jane_web_collectorfetcherfetcherlimiter)
- [jane_web_collector.fetcher.Fetcher.headers](#jane_web_collectorfetcherfetcherheaders)
- [jane_web_collector.fetcher.Fetcher.auth_headers](#jane_web_collectorfetcherfetcherauth_headers)
- [jane_web_collector.fetcher.Fetcher.connection_policy](#jane_web_collectorfetcherfetcherconnection_policy)
- [jane_web_collector.fetcher.Fetcher.crawl_delay_for](#jane_web_collectorfetcherfetchercrawl_delay_for)
- [jane_web_collector.fetcher.Fetcher.get](#jane_web_collectorfetcherfetcherget)
- [jane_web_collector.fetcher.Fetcher.auth_headers_for](#jane_web_collectorfetcherfetcherauth_headers_for)

## jane_web_collector.fetcher.FetchError

**Клас.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:45](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L45).

```python
class FetchError(Exception):
```

Базові типи / інтерфейси: `Exception`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_web_collector.fetcher.md#jane_web_collectorfetcherfetcherror__init__) | Конструктор | ні |
| [code](jane_web_collector.fetcher.md#jane_web_collectorfetcherfetcherrorcode) | Поле екземпляра | ні |
| [message](jane_web_collector.fetcher.md#jane_web_collectorfetcherfetcherrormessage) | Поле екземпляра | ні |
| [http_status](jane_web_collector.fetcher.md#jane_web_collectorfetcherfetcherrorhttp_status) | Поле екземпляра | ні |
| [attempts](jane_web_collector.fetcher.md#jane_web_collectorfetcherfetcherrorattempts) | Поле екземпляра | ні |
| [retry_after_seconds](jane_web_collector.fetcher.md#jane_web_collectorfetcherfetcherrorretry_after_seconds) | Поле екземпляра | ні |

### Опис із вихідного коду

```text
A URL could not be fetched (network, HTTP error after retries, policy).
```

## jane_web_collector.fetcher.FetchError.__init__

**Конструктор.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:48](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L48).

```python
def __init__(self, code: str, message: str, *, http_status: int | None=None, attempts: int=1, retry_after_seconds: int | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `code` | `str` | `—` | positional-or-keyword |
| `message` | `str` | `—` | positional-or-keyword |
| `http_status` | `int \| None` | `None` | keyword-only |
| `attempts` | `int` | `1` | keyword-only |
| `retry_after_seconds` | `int \| None` | `None` | keyword-only |

Результат: `None`.

## jane_web_collector.fetcher.FetchError.code

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:58](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L58).

```python
self.code = code
```

## jane_web_collector.fetcher.FetchError.message

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:59](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L59).

```python
self.message = message
```

## jane_web_collector.fetcher.FetchError.http_status

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:60](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L60).

```python
self.http_status = http_status
```

## jane_web_collector.fetcher.FetchError.attempts

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:61](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L61).

```python
self.attempts = attempts
```

## jane_web_collector.fetcher.FetchError.retry_after_seconds

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:62](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L62).

```python
self.retry_after_seconds = retry_after_seconds
```

## jane_web_collector.fetcher.HttpResult

**Клас.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:66](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L66).

```python
class HttpResult:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [url](jane_web_collector.fetcher.md#jane_web_collectorfetcherhttpresulturl) | Поле | ні |
| [final_url](jane_web_collector.fetcher.md#jane_web_collectorfetcherhttpresultfinal_url) | Поле | ні |
| [status](jane_web_collector.fetcher.md#jane_web_collectorfetcherhttpresultstatus) | Поле | ні |
| [headers](jane_web_collector.fetcher.md#jane_web_collectorfetcherhttpresultheaders) | Поле | ні |
| [body](jane_web_collector.fetcher.md#jane_web_collectorfetcherhttpresultbody) | Поле | ні |
| [fetched_at](jane_web_collector.fetcher.md#jane_web_collectorfetcherhttpresultfetched_at) | Поле | ні |
| [truncated](jane_web_collector.fetcher.md#jane_web_collectorfetcherhttpresulttruncated) | Поле | ні |
| [redirects](jane_web_collector.fetcher.md#jane_web_collectorfetcherhttpresultredirects) | Поле | ні |
| [attempts](jane_web_collector.fetcher.md#jane_web_collectorfetcherhttpresultattempts) | Поле | ні |
| [diagnostics](jane_web_collector.fetcher.md#jane_web_collectorfetcherhttpresultdiagnostics) | Поле | ні |
| [network_bytes](jane_web_collector.fetcher.md#jane_web_collectorfetcherhttpresultnetwork_bytes) | Поле | ні |
| [media_type](jane_web_collector.fetcher.md#jane_web_collectorfetcherhttpresultmedia_type) | Властивість | ні |
| [charset](jane_web_collector.fetcher.md#jane_web_collectorfetcherhttpresultcharset) | Властивість | ні |
| [__init__](jane_web_collector.fetcher.md#jane_web_collectorfetcherhttpresult__init__) | Конструктор dataclass | ні |

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:507](../../../../../../services/web-collector/tests/test_render_js.py#L507).

```python
return HttpResult(
        url=url,
        final_url=url,
        status=200,
        headers={"content-type": "text/html; charset=utf-8"},
        body=html.encode("utf-8"),
        fetched_at=datetime.now(UTC),
    )
```

Контекст і передумови: [services/web-collector/tests/test_render_js.py:557](../../../../../../services/web-collector/tests/test_render_js.py#L557).

```python
return HttpResult(
        url=url,
        final_url=url,
        status=r.status_code,
        headers={"content-type": r.headers["content-type"]},
        body=r.content,
        fetched_at=datetime.now(UTC),
    )
```

## jane_web_collector.fetcher.HttpResult.__init__

**Конструктор dataclass.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:66](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L66).

```python
def __init__(self, url: str, final_url: str, status: int, headers: dict[str, str], body: bytes, fetched_at: datetime, truncated: bool = False, redirects: list[str] = <factory list>, attempts: int = 1, diagnostics: list[dict[str, str]] = <factory list>, network_bytes: int | None = None) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `url` | `str` | `—` | positional-or-keyword |
| `final_url` | `str` | `—` | positional-or-keyword |
| `status` | `int` | `—` | positional-or-keyword |
| `headers` | `dict[str, str]` | `—` | positional-or-keyword |
| `body` | `bytes` | `—` | positional-or-keyword |
| `fetched_at` | `datetime` | `—` | positional-or-keyword |
| `truncated` | `bool` | `False` | positional-or-keyword |
| `redirects` | `list[str]` | `factory: list` | positional-or-keyword |
| `attempts` | `int` | `1` | positional-or-keyword |
| `diagnostics` | `list[dict[str, str]]` | `factory: list` | positional-or-keyword |
| `network_bytes` | `int \| None` | `None` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:507](../../../../../../services/web-collector/tests/test_render_js.py#L507).

```python
return HttpResult(
        url=url,
        final_url=url,
        status=200,
        headers={"content-type": "text/html; charset=utf-8"},
        body=html.encode("utf-8"),
        fetched_at=datetime.now(UTC),
    )
```

Контекст і передумови: [services/web-collector/tests/test_render_js.py:557](../../../../../../services/web-collector/tests/test_render_js.py#L557).

```python
return HttpResult(
        url=url,
        final_url=url,
        status=r.status_code,
        headers={"content-type": r.headers["content-type"]},
        body=r.content,
        fetched_at=datetime.now(UTC),
    )
```

## jane_web_collector.fetcher.HttpResult.url

**Поле.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:67](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L67).

```python
url: str
```

Доступ: читання — так; запис — так.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:240](../../../../../../services/web-collector/tests/test_render_js.py#L240).

```python
page.url = page.final_url = f"http://shop.example.test:{port}{testsite.JS_PRICE_PAGE}"
```

Контекст і передумови: [services/web-collector/tests/test_render_js.py:264](../../../../../../services/web-collector/tests/test_render_js.py#L264).

```python
page.url = page.final_url = f"http://shop.example.test:{port}{testsite.JS_PRICE_PAGE}"
```

## jane_web_collector.fetcher.HttpResult.final_url

**Поле.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:68](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L68).

```python
final_url: str
```

Доступ: читання — так; запис — так.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:240](../../../../../../services/web-collector/tests/test_render_js.py#L240).

```python
page.url = page.final_url = f"http://shop.example.test:{port}{testsite.JS_PRICE_PAGE}"
```

Контекст і передумови: [services/web-collector/tests/test_render_js.py:264](../../../../../../services/web-collector/tests/test_render_js.py#L264).

```python
page.url = page.final_url = f"http://shop.example.test:{port}{testsite.JS_PRICE_PAGE}"
```

## jane_web_collector.fetcher.HttpResult.status

**Поле.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:69](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L69).

```python
status: int
```

Доступ: читання — так; запис — так.

## jane_web_collector.fetcher.HttpResult.headers

**Поле.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:70](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L70).

```python
headers: dict[str, str]
```

Доступ: читання — так; запис — так.

## jane_web_collector.fetcher.HttpResult.body

**Поле.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:71](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L71).

```python
body: bytes
```

Доступ: читання — так; запис — так.

## jane_web_collector.fetcher.HttpResult.fetched_at

**Поле.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:72](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L72).

```python
fetched_at: datetime
```

Доступ: читання — так; запис — так.

## jane_web_collector.fetcher.HttpResult.truncated

**Поле.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:73](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L73).

```python
truncated: bool = False
```

Доступ: читання — так; запис — так.

## jane_web_collector.fetcher.HttpResult.redirects

**Поле.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:74](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L74).

```python
redirects: list[str] = field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

## jane_web_collector.fetcher.HttpResult.attempts

**Поле.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:75](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L75).

```python
attempts: int = 1
```

Доступ: читання — так; запис — так.

## jane_web_collector.fetcher.HttpResult.diagnostics

**Поле.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:76](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L76).

```python
diagnostics: list[dict[str, str]] = field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

### Опис із вихідного коду

```text
Material diagnostics of this result besides ``truncated`` (e.g. how the page was rendered).
```

## jane_web_collector.fetcher.HttpResult.network_bytes

**Поле.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:78](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L78).

```python
network_bytes: int | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Bytes downloaded for this result when they differ from ``len(body)`` (a rendered page: the document and
    everything the browser loaded); counts towards ``crawl.max_bytes_per_run``.
```

## jane_web_collector.fetcher.HttpResult.media_type

**Властивість.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:83](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L83).

```python
def media_type(self) -> str:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

Доступ: читання — так; запис — ні.

## jane_web_collector.fetcher.HttpResult.charset

**Властивість.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:87](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L87).

```python
def charset(self) -> str | None:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str | None`.

Доступ: читання — так; запис — ні.

## jane_web_collector.fetcher.build_client

**Функція.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:95](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L95).

```python
def build_client(limits: ServiceLimits, egress: EgressPolicy | None=None, *, resolver: Resolver=system_resolve) -> httpx.AsyncClient:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `limits` | `ServiceLimits` | `—` | positional-or-keyword |
| `egress` | `EgressPolicy \| None` | `None` | positional-or-keyword |
| `resolver` | `Resolver` | `system_resolve` | keyword-only |

Результат: `httpx.AsyncClient`.

### Опис із вихідного коду

```text
The fetch client; every connection is checked by ``egress`` (default: link-local denied).
```

## jane_web_collector.fetcher.Fetcher

**Клас.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:124](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L124).

```python
class Fetcher:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_web_collector.fetcher.md#jane_web_collectorfetcherfetcher__init__) | Конструктор | ні |
| [client](jane_web_collector.fetcher.md#jane_web_collectorfetcherfetcherclient) | Поле екземпляра | ні |
| [limits](jane_web_collector.fetcher.md#jane_web_collectorfetcherfetcherlimits) | Поле екземпляра | ні |
| [limiter](jane_web_collector.fetcher.md#jane_web_collectorfetcherfetcherlimiter) | Поле екземпляра | ні |
| [headers](jane_web_collector.fetcher.md#jane_web_collectorfetcherfetcherheaders) | Поле екземпляра | ні |
| [auth_headers](jane_web_collector.fetcher.md#jane_web_collectorfetcherfetcherauth_headers) | Поле екземпляра | ні |
| [connection_policy](jane_web_collector.fetcher.md#jane_web_collectorfetcherfetcherconnection_policy) | Поле екземпляра | ні |
| [crawl_delay_for](jane_web_collector.fetcher.md#jane_web_collectorfetcherfetchercrawl_delay_for) | Поле екземпляра | ні |
| [get](jane_web_collector.fetcher.md#jane_web_collectorfetcherfetcherget) | Метод | ні |
| [auth_headers_for](jane_web_collector.fetcher.md#jane_web_collectorfetcherfetcherauth_headers_for) | Метод | ні |

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_connection_policy.py:118](../../../../../../services/web-collector/tests/test_connection_policy.py#L118).

```python
fetcher = Fetcher(
            client,
            limits,
            HostLimiter(limits).session(limits),
            user_agent="JaneBot",
            auth_headers={"Authorization": "Bearer safe-token"},
            connection_policy=policy,
        )
```

Контекст і передумови: [services/web-collector/tests/test_connection_policy.py:191](../../../../../../services/web-collector/tests/test_connection_policy.py#L191).

```python
fetcher = Fetcher(
            http_client,
            limits,
            HostLimiter(limits).session(limits),
            user_agent="JaneBot",
            auth_headers={"Authorization": "Bearer safe-token"},
            connection_policy=policy,
        )
```

## jane_web_collector.fetcher.Fetcher.__init__

**Конструктор.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:125](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L125).

```python
def __init__(self, client: httpx.AsyncClient, limits: ServiceLimits, limiter: HostSession, *, user_agent: str, headers: Mapping[str, str] | None=None, auth_headers: Mapping[str, str] | None=None, connection_policy: ConnectionPolicy | None=None, crawl_delay_for: DelayFor | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `client` | `httpx.AsyncClient` | `—` | positional-or-keyword |
| `limits` | `ServiceLimits` | `—` | positional-or-keyword |
| `limiter` | `HostSession` | `—` | positional-or-keyword |
| `user_agent` | `str` | `—` | keyword-only |
| `headers` | `Mapping[str, str] \| None` | `None` | keyword-only |
| `auth_headers` | `Mapping[str, str] \| None` | `None` | keyword-only |
| `connection_policy` | `ConnectionPolicy \| None` | `None` | keyword-only |
| `crawl_delay_for` | `DelayFor \| None` | `None` | keyword-only |

Результат: `None`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_connection_policy.py:118](../../../../../../services/web-collector/tests/test_connection_policy.py#L118).

```python
fetcher = Fetcher(
            client,
            limits,
            HostLimiter(limits).session(limits),
            user_agent="JaneBot",
            auth_headers={"Authorization": "Bearer safe-token"},
            connection_policy=policy,
        )
```

Контекст і передумови: [services/web-collector/tests/test_connection_policy.py:191](../../../../../../services/web-collector/tests/test_connection_policy.py#L191).

```python
fetcher = Fetcher(
            http_client,
            limits,
            HostLimiter(limits).session(limits),
            user_agent="JaneBot",
            auth_headers={"Authorization": "Bearer safe-token"},
            connection_policy=policy,
        )
```

## jane_web_collector.fetcher.Fetcher.client

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:137](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L137).

```python
self.client = client
```

## jane_web_collector.fetcher.Fetcher.limits

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:138](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L138).

```python
self.limits = limits
```

## jane_web_collector.fetcher.Fetcher.limiter

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:139](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L139).

```python
self.limiter = limiter
```

## jane_web_collector.fetcher.Fetcher.headers

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:150](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L150).

```python
self.headers = {'User-Agent': user_agent, **source_headers}
```

## jane_web_collector.fetcher.Fetcher.auth_headers

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:151](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L151).

```python
self.auth_headers = dict(auth_headers or {})
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_connection_policy.py:203](../../../../../../services/web-collector/tests/test_connection_policy.py#L203).

```python
fetcher.auth_headers = {"Authorization": f"Bearer {secret}"}
```

## jane_web_collector.fetcher.Fetcher.connection_policy

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:152](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L152).

```python
self.connection_policy = connection_policy or ConnectionPolicy()
```

## jane_web_collector.fetcher.Fetcher.crawl_delay_for

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:153](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L153).

```python
self.crawl_delay_for = crawl_delay_for
```

## jane_web_collector.fetcher.Fetcher.get

**Метод.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:208](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L208).

```python
async def get(self, url: str, *, check_hop: HopCheck | None=None, conditional: Mapping[str, str] | None=None, max_bytes: int | None=None, timeouts: Timeouts | None=None, method: str='GET', json_body: bytes | None=None) -> HttpResult:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |
| `check_hop` | `HopCheck \| None` | `None` | keyword-only |
| `conditional` | `Mapping[str, str] \| None` | `None` | keyword-only |
| `max_bytes` | `int \| None` | `None` | keyword-only |
| `timeouts` | `Timeouts \| None` | `None` | keyword-only |
| `method` | `str` | `'GET'` | keyword-only |
| `json_body` | `bytes \| None` | `None` | keyword-only |

Результат: `HttpResult`.

Явні `raise` у тілі: `FetchError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
GET (or a POST of ``json_body`` with ``Content-Type: application/json``) with retries and redirects.
A POST is never conditional; after a 307/308 redirect it is repeated with its body, after 301/302/303 the
chain continues with GET. Raises :class:`FetchError`; policy callbacks may raise their own.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_connection_policy.py:130](../../../../../../services/web-collector/tests/test_connection_policy.py#L130).

```python
await fetcher.get("https://source.test/same")
```

Контекст і передумови: [services/web-collector/tests/test_connection_policy.py:136](../../../../../../services/web-collector/tests/test_connection_policy.py#L136).

```python
await fetcher.get("https://source.test/redirect")
```

## jane_web_collector.fetcher.Fetcher.auth_headers_for

**Метод.** Код: [services/web-collector/src/jane_web_collector/fetcher.py:265](../../../../../../services/web-collector/src/jane_web_collector/fetcher.py#L265).

```python
def auth_headers_for(self, current: str, original: str) -> dict[str, str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `current` | `str` | `—` | positional-or-keyword |
| `original` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, str]`.

Явні `raise` у тілі: `FetchError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Credentials only for the original host (never leak them to a redirect target on another host).
```
