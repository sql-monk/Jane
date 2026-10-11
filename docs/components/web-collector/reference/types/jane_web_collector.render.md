# Модуль `jane_web_collector.render`

> Згенеровано `scripts/docs_reference.py` з [services/web-collector/src/jane_web_collector/render.py](../../../../../services/web-collector/src/jane_web_collector/render.py). Не редагуйте вручну.

Browser document transport and JavaScript rendering in headless Chromium (Playwright).

``fetch.transport=browser`` fetches each document with Chromium's network stack and JavaScript disabled. Response-stage interception prevents automatic redirects, so the outer Fetcher checks every next hop. Subresources are blocked; the material contains the original response bytes. Connections use EgressProxy.

For ``fetch.render_js`` the page has already been fetched. :class:`~.fetcher.Fetcher` fetches it first, with every guarantee of a plain fetch: scope and robots.txt before, each redirect hop re-checked, the outbound address policy, per-host limits, retries, ``crawl.max_material_bytes``, the User-Agent and the credentials of a managed connection. Only a 2xx HTML answer is rendered: the first navigation of the browser page is answered with the fetched body (``route.fulfill``), any later navigation of a top-level frame (a script redirect, a meta refresh, a reload, a popup) is answered ``204 No Content`` - the navigation does not happen and the document stays - so the DOM is the DOM of the URL that passed the checks.

Everything else the browser loads (scripts, XHR/fetch, styles, frames, WebSockets) goes through :class:`EgressProxy` - an HTTP proxy on 127.0.0.1, one per page - which applies the fetch client's :class:`~.egress.EgressPolicy` to every connection the same way :class:`~.egress.GuardedBackend` does: the host is resolved once, every address is checked, the connection is opened to a checked address (no DNS rebinding). On top of that (``RENDER_DENY_PRIVATE``, default on) a non-public address is refused unless the host is the page's own or in the rules' ``scope.allowed_domains``: a page script cannot reach internal services the caller did not choose. Playwright sends loopback through the proxy as well (``<-loopback>``), service workers are blocked and WebRTC may use proxied traffic only. Requests of the resource types in ``RENDER_BLOCK_RESOURCE_TYPES`` are not made at all. One page may download ``collector.render_max_transfer_bytes``; the browser sends the collector's User-Agent and never the connection credentials.

The material is the serialized DOM (doctype + ``document.documentElement.outerHTML``) once the wait condition is reached or ``collector.render_timeout_ms`` has passed, encoded as UTF-8 (``<meta charset>`` says so), cut at ``crawl.max_material_bytes`` - already in the page, so a huge DOM never crosses to the collector whole. Starting Chromium and closing pages are bounded too (``collector.render_launch_timeout_ms`` / ``render_close_timeout_ms``). If rendering is off, Playwright is not installed or Chromium cannot start, the URL fails with ``not_implemented`` and a message saying why - never a silent plain fetch.

## Зміст

- [Клас `EgressProxy`](#клас-egressproxy)
- [Клас `RenderOptions`](#клас-renderoptions)
- [Клас `Renderer`](#клас-renderer)
- [Функція `renderable`](#функція-renderable)

## Класи

### Клас `EgressProxy`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.render` |
| Код | [render.py:128](../../../../../services/web-collector/src/jane_web_collector/render.py#L128) |

```python
class EgressProxy: ...
```

HTTP proxy for one browser page: the outbound address policy for every connection (see the module docstring).

``CONNECT host:port`` (HTTPS, WebSocket) becomes a tunnel; an absolute-form request (plain HTTP) is forwarded in origin form with ``Connection: close``. A denied destination is listed in :attr:`denied`; the browser gets a failed tunnel (403 to ``CONNECT``) or a closed connection (plain HTTP), never a response it could read as the site's.

#### Конструктор `EgressProxy.__init__`

```python
def __init__(
    self,
    policy: EgressPolicy,
    *,
    resolver: Resolver = system_resolve,
    connect_timeout_s: float,
    max_bytes: int,
    private_allowed: Callable[[str], bool] | None = None,
) -> None: ...
```

``private_allowed``: with it, a non-public address is refused unless this says yes for the host (the page's own host and ``scope.allowed_domains``, ``RENDER_DENY_PRIVATE``); ``policy`` applies to every host.

Код: [render.py:136](../../../../../services/web-collector/src/jane_web_collector/render.py#L136).

#### Метод `EgressProxy.start`

```python
async def start(self) -> str: ...
```

Код: [render.py:162](../../../../../services/web-collector/src/jane_web_collector/render.py#L162).

#### Метод `EgressProxy.aclose`

```python
async def aclose(self) -> None: ...
```

Код: [render.py:168](../../../../../services/web-collector/src/jane_web_collector/render.py#L168).

#### Метод `EgressProxy.precheck`

```python
async def precheck(self, url: str) -> str | None: ...
```

Why the outbound policy refuses ``url`` (``None``: allowed, or left to the proxy). The page router aborts a refused request with its URL before the browser connects; the proxy still checks every connection, so a DNS answer that changes after this check changes nothing. One resolution per host and port of a page.

Код: [render.py:180](../../../../../services/web-collector/src/jane_web_collector/render.py#L180).

#### Метод `EgressProxy.check`

```python
def check(self, host: str, addresses: list[str]) -> None: ...
```

The policy of the fetch client, then (``RENDER_DENY_PRIVATE``) no non-public address for a host that is neither the page's own nor in ``scope.allowed_domains``: a page script must not reach internal services the caller did not choose. Raises :class:`~.egress.EgressDenied`.

Винятки в коді методу: `EgressDenied`.

Код: [render.py:205](../../../../../services/web-collector/src/jane_web_collector/render.py#L205).

### Клас `RenderOptions`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_web_collector.render` |
| Код | [render.py:356](../../../../../services/web-collector/src/jane_web_collector/render.py#L356) |

```python
@dataclass(frozen=True)
class RenderOptions: ...
```

Service-level rendering settings (``JANE_WEB_COLLECTOR_RENDER_*``).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `enabled` | `bool` | `True` | читання |  |
| `wait_until` | `WaitUntil` | `'networkidle'` | читання |  |
| `block_resource_types` | `tuple[str, ...]` | `('image', 'media', 'font')` | читання |  |
| `executable` | `Path \| None` | `None` | читання |  |
| `deny_private` | `bool` | `True` | читання | ``RENDER_DENY_PRIVATE``: browser requests reach non-public addresses only for the page's own host and ``scope.allowed_domains``. |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `Renderer`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.render` |
| Код | [render.py:378](../../../../../services/web-collector/src/jane_web_collector/render.py#L378) |

```python
class Renderer: ...
```

Headless Chromium shared by every collection and fetch of the process, started on first use.

#### Конструктор `Renderer.__init__`

```python
def __init__(
    self,
    options: RenderOptions,
    policy: EgressPolicy,
    *,
    max_pages: int,
    resolver: Resolver = system_resolve,
    launch_timeout_ms: int | None = None,
    close_timeout_ms: int | None = None,
) -> None: ...
```

``launch_timeout_ms`` / ``close_timeout_ms``: ``collector.render_launch_timeout_ms`` / ``collector.render_close_timeout_ms`` (their defaults when not given).

Код: [render.py:381](../../../../../services/web-collector/src/jane_web_collector/render.py#L381).

#### Метод `Renderer.unavailable_reason`

```python
def unavailable_reason(self) -> str | None: ...
```

Why rendering cannot work here, known without starting the browser.

Код: [render.py:408](../../../../../services/web-collector/src/jane_web_collector/render.py#L408).

#### Метод `Renderer.capabilities`

```python
def capabilities(self) -> dict[str, Any]: ...
```

``/v1/info`` capabilities: ``render_js`` and, when it is false, why.

Код: [render.py:416](../../../../../services/web-collector/src/jane_web_collector/render.py#L416).

#### Метод `Renderer.aclose`

```python
async def aclose(self) -> None: ...
```

Код: [render.py:421](../../../../../services/web-collector/src/jane_web_collector/render.py#L421).

#### Метод `Renderer.fetch`

```python
async def fetch(
    self,
    url: str,
    *,
    headers: Mapping[str, str],
    max_bytes: int,
    limits: ServiceLimits,
    timeouts: Timeouts | None = None,
) -> tuple[int, dict[str, str], bytes, bool, int]: ...
```

Fetch one GET document with Chromium's network stack, without JavaScript.

Redirect targets and subresources never reach the network in this context. The outer Fetcher handles each redirect as a separate request after checking scope, robots and host limits. Every network connection uses the existing proxy with checked, pinned DNS addresses.

Винятки в коді методу: `EgressDenied`, `FetchError`.

Код: [render.py:493](../../../../../services/web-collector/src/jane_web_collector/render.py#L493).

#### Метод `Renderer.render`

```python
async def render(
    self,
    result: HttpResult,
    *,
    user_agent: str,
    limits: ServiceLimits,
    accept_language: str | None = None,
    allowed_hosts: Callable[[str], bool] | None = None,
) -> HttpResult: ...
```

The fetched HTML ``result`` rendered by the browser: the same result with the serialized DOM as body.

``allowed_hosts``: hosts of ``scope.allowed_domains`` - with the page's own host the only ones the browser may reach at a non-public address (``RENDER_DENY_PRIVATE``). Raises :class:`~.fetcher.FetchError`: ``not_implemented`` (no browser), ``timeout`` (the DOM could not be taken in time), ``internal_error`` (the browser failed).

Код: [render.py:639](../../../../../services/web-collector/src/jane_web_collector/render.py#L639).

## Функції

### Функція `renderable`

```python
def renderable(result: HttpResult) -> bool: ...
```

A 2xx HTML answer: the only kind of fetched document that is rendered.

Код: [render.py:103](../../../../../services/web-collector/src/jane_web_collector/render.py#L103).
