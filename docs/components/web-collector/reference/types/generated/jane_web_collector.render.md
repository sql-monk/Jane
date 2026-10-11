# jane_web_collector.render

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_web_collector.render.renderable](#jane_web_collectorrenderrenderable)
- [jane_web_collector.render.EgressProxy](#jane_web_collectorrenderegressproxy)
- [jane_web_collector.render.EgressProxy.__init__](#jane_web_collectorrenderegressproxy__init__)
- [jane_web_collector.render.EgressProxy.policy](#jane_web_collectorrenderegressproxypolicy)
- [jane_web_collector.render.EgressProxy.private_allowed](#jane_web_collectorrenderegressproxyprivate_allowed)
- [jane_web_collector.render.EgressProxy.resolver](#jane_web_collectorrenderegressproxyresolver)
- [jane_web_collector.render.EgressProxy.connect_timeout_s](#jane_web_collectorrenderegressproxyconnect_timeout_s)
- [jane_web_collector.render.EgressProxy.max_bytes](#jane_web_collectorrenderegressproxymax_bytes)
- [jane_web_collector.render.EgressProxy.denied](#jane_web_collectorrenderegressproxydenied)
- [jane_web_collector.render.EgressProxy.connections](#jane_web_collectorrenderegressproxyconnections)
- [jane_web_collector.render.EgressProxy.transferred](#jane_web_collectorrenderegressproxytransferred)
- [jane_web_collector.render.EgressProxy.budget_exceeded](#jane_web_collectorrenderegressproxybudget_exceeded)
- [jane_web_collector.render.EgressProxy.url](#jane_web_collectorrenderegressproxyurl)
- [jane_web_collector.render.EgressProxy.start](#jane_web_collectorrenderegressproxystart)
- [jane_web_collector.render.EgressProxy.aclose](#jane_web_collectorrenderegressproxyaclose)
- [jane_web_collector.render.EgressProxy.precheck](#jane_web_collectorrenderegressproxyprecheck)
- [jane_web_collector.render.EgressProxy.check](#jane_web_collectorrenderegressproxycheck)
- [jane_web_collector.render.RenderOptions](#jane_web_collectorrenderrenderoptions)
- [jane_web_collector.render.RenderOptions.__init__](#jane_web_collectorrenderrenderoptions__init__)
- [jane_web_collector.render.RenderOptions.enabled](#jane_web_collectorrenderrenderoptionsenabled)
- [jane_web_collector.render.RenderOptions.wait_until](#jane_web_collectorrenderrenderoptionswait_until)
- [jane_web_collector.render.RenderOptions.block_resource_types](#jane_web_collectorrenderrenderoptionsblock_resource_types)
- [jane_web_collector.render.RenderOptions.executable](#jane_web_collectorrenderrenderoptionsexecutable)
- [jane_web_collector.render.RenderOptions.deny_private](#jane_web_collectorrenderrenderoptionsdeny_private)
- [jane_web_collector.render.Renderer](#jane_web_collectorrenderrenderer)
- [jane_web_collector.render.Renderer.__init__](#jane_web_collectorrenderrenderer__init__)
- [jane_web_collector.render.Renderer.options](#jane_web_collectorrenderrendereroptions)
- [jane_web_collector.render.Renderer.policy](#jane_web_collectorrenderrendererpolicy)
- [jane_web_collector.render.Renderer.resolver](#jane_web_collectorrenderrendererresolver)
- [jane_web_collector.render.Renderer.launch_timeout_ms](#jane_web_collectorrenderrendererlaunch_timeout_ms)
- [jane_web_collector.render.Renderer.close_timeout_s](#jane_web_collectorrenderrendererclose_timeout_s)
- [jane_web_collector.render.Renderer.last_error](#jane_web_collectorrenderrendererlast_error)
- [jane_web_collector.render.Renderer.unavailable_reason](#jane_web_collectorrenderrendererunavailable_reason)
- [jane_web_collector.render.Renderer.capabilities](#jane_web_collectorrenderrenderercapabilities)
- [jane_web_collector.render.Renderer.aclose](#jane_web_collectorrenderrendereraclose)
- [jane_web_collector.render.Renderer.render](#jane_web_collectorrenderrendererrender)

## jane_web_collector.render.renderable

**Функція.** Код: [services/web-collector/src/jane_web_collector/render.py:96](../../../../../../services/web-collector/src/jane_web_collector/render.py#L96).

```python
def renderable(result: HttpResult) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `result` | `HttpResult` | `—` | positional-or-keyword |

Результат: `bool`.

### Опис із вихідного коду

```text
A 2xx HTML answer: the only kind of fetched document that is rendered.
```

## jane_web_collector.render.EgressProxy

**Клас.** Код: [services/web-collector/src/jane_web_collector/render.py:121](../../../../../../services/web-collector/src/jane_web_collector/render.py#L121).

```python
class EgressProxy:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_web_collector.render.md#jane_web_collectorrenderegressproxy__init__) | Конструктор | ні |
| [policy](jane_web_collector.render.md#jane_web_collectorrenderegressproxypolicy) | Поле екземпляра | ні |
| [private_allowed](jane_web_collector.render.md#jane_web_collectorrenderegressproxyprivate_allowed) | Поле екземпляра | ні |
| [resolver](jane_web_collector.render.md#jane_web_collectorrenderegressproxyresolver) | Поле екземпляра | ні |
| [connect_timeout_s](jane_web_collector.render.md#jane_web_collectorrenderegressproxyconnect_timeout_s) | Поле екземпляра | ні |
| [max_bytes](jane_web_collector.render.md#jane_web_collectorrenderegressproxymax_bytes) | Поле екземпляра | ні |
| [denied](jane_web_collector.render.md#jane_web_collectorrenderegressproxydenied) | Поле екземпляра | ні |
| [connections](jane_web_collector.render.md#jane_web_collectorrenderegressproxyconnections) | Поле екземпляра | ні |
| [transferred](jane_web_collector.render.md#jane_web_collectorrenderegressproxytransferred) | Поле екземпляра | ні |
| [budget_exceeded](jane_web_collector.render.md#jane_web_collectorrenderegressproxybudget_exceeded) | Поле екземпляра | ні |
| [url](jane_web_collector.render.md#jane_web_collectorrenderegressproxyurl) | Поле екземпляра | ні |
| [start](jane_web_collector.render.md#jane_web_collectorrenderegressproxystart) | Метод | ні |
| [aclose](jane_web_collector.render.md#jane_web_collectorrenderegressproxyaclose) | Метод | ні |
| [precheck](jane_web_collector.render.md#jane_web_collectorrenderegressproxyprecheck) | Метод | ні |
| [check](jane_web_collector.render.md#jane_web_collectorrenderegressproxycheck) | Метод | ні |

### Опис із вихідного коду

```text
HTTP proxy for one browser page: the outbound address policy for every connection (see the module docstring).

``CONNECT host:port`` (HTTPS, WebSocket) becomes a tunnel; an absolute-form request (plain HTTP) is forwarded
in origin form with ``Connection: close``. A denied destination is listed in :attr:`denied`; the browser gets
a failed tunnel (403 to ``CONNECT``) or a closed connection (plain HTTP), never a response it could read as the
site's.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:133](../../../../../../services/web-collector/tests/test_render_js.py#L133).

```python
proxy = EgressProxy(EgressPolicy(), resolver=dns, connect_timeout_s=5, max_bytes=10_000)
```

## jane_web_collector.render.EgressProxy.__init__

**Конструктор.** Код: [services/web-collector/src/jane_web_collector/render.py:129](../../../../../../services/web-collector/src/jane_web_collector/render.py#L129).

```python
def __init__(self, policy: EgressPolicy, *, resolver: Resolver=system_resolve, connect_timeout_s: float, max_bytes: int, private_allowed: Callable[[str], bool] | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `policy` | `EgressPolicy` | `—` | positional-or-keyword |
| `resolver` | `Resolver` | `system_resolve` | keyword-only |
| `connect_timeout_s` | `float` | `—` | keyword-only |
| `max_bytes` | `int` | `—` | keyword-only |
| `private_allowed` | `Callable[[str], bool] \| None` | `None` | keyword-only |

Результат: `None`.

### Опис із вихідного коду

```text
``private_allowed``: with it, a non-public address is refused unless this says yes for the host (the
page's own host and ``scope.allowed_domains``, ``RENDER_DENY_PRIVATE``); ``policy`` applies to every host.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:133](../../../../../../services/web-collector/tests/test_render_js.py#L133).

```python
proxy = EgressProxy(EgressPolicy(), resolver=dns, connect_timeout_s=5, max_bytes=10_000)
```

## jane_web_collector.render.EgressProxy.policy

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/render.py:140](../../../../../../services/web-collector/src/jane_web_collector/render.py#L140).

```python
self.policy = policy
```

## jane_web_collector.render.EgressProxy.private_allowed

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/render.py:141](../../../../../../services/web-collector/src/jane_web_collector/render.py#L141).

```python
self.private_allowed = private_allowed
```

## jane_web_collector.render.EgressProxy.resolver

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/render.py:142](../../../../../../services/web-collector/src/jane_web_collector/render.py#L142).

```python
self.resolver = resolver
```

## jane_web_collector.render.EgressProxy.connect_timeout_s

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/render.py:143](../../../../../../services/web-collector/src/jane_web_collector/render.py#L143).

```python
self.connect_timeout_s = connect_timeout_s
```

## jane_web_collector.render.EgressProxy.max_bytes

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/render.py:144](../../../../../../services/web-collector/src/jane_web_collector/render.py#L144).

```python
self.max_bytes = max_bytes
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:151](../../../../../../services/web-collector/tests/test_render_js.py#L151).

```python
proxy.max_bytes = 10
```

## jane_web_collector.render.EgressProxy.denied

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/render.py:145](../../../../../../services/web-collector/src/jane_web_collector/render.py#L145).

```python
self.denied: list[str] = []
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:147](../../../../../../services/web-collector/tests/test_render_js.py#L147).

```python
assert len(proxy.denied) == 2 and all("169.254.169.254" in d for d in proxy.denied)
```

## jane_web_collector.render.EgressProxy.connections

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/render.py:146](../../../../../../services/web-collector/src/jane_web_collector/render.py#L146).

```python
self.connections = 0
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:141](../../../../../../services/web-collector/tests/test_render_js.py#L141).

```python
assert site.requests[testsite.JS_PRICE_DATA] == 1 and proxy.connections == 1
```

Контекст і передумови: [services/web-collector/tests/test_render_js.py:155](../../../../../../services/web-collector/tests/test_render_js.py#L155).

```python
assert status.startswith("HTTP/1.1 403") and proxy.connections == 2
```

## jane_web_collector.render.EgressProxy.transferred

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/render.py:147](../../../../../../services/web-collector/src/jane_web_collector/render.py#L147).

```python
self.transferred = 0
```

## jane_web_collector.render.EgressProxy.budget_exceeded

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/render.py:148](../../../../../../services/web-collector/src/jane_web_collector/render.py#L148).

```python
self.budget_exceeded = False
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:153](../../../../../../services/web-collector/tests/test_render_js.py#L153).

```python
assert proxy.budget_exceeded
```

## jane_web_collector.render.EgressProxy.url

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/render.py:149](../../../../../../services/web-collector/src/jane_web_collector/render.py#L149).

```python
self.url = ''
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:569](../../../../../../services/web-collector/tests/test_render_js.py#L569).

```python
reader, writer = await asyncio.open_connection("127.0.0.1", int(proxy.url.rsplit(":", 1)[1]))
```

## jane_web_collector.render.EgressProxy.start

**Метод.** Код: [services/web-collector/src/jane_web_collector/render.py:155](../../../../../../services/web-collector/src/jane_web_collector/render.py#L155).

```python
async def start(self) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:134](../../../../../../services/web-collector/tests/test_render_js.py#L134).

```python
await proxy.start()
```

## jane_web_collector.render.EgressProxy.aclose

**Метод.** Код: [services/web-collector/src/jane_web_collector/render.py:161](../../../../../../services/web-collector/src/jane_web_collector/render.py#L161).

```python
async def aclose(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:157](../../../../../../services/web-collector/tests/test_render_js.py#L157).

```python
await proxy.aclose()
```

## jane_web_collector.render.EgressProxy.precheck

**Метод.** Код: [services/web-collector/src/jane_web_collector/render.py:173](../../../../../../services/web-collector/src/jane_web_collector/render.py#L173).

```python
async def precheck(self, url: str) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |

Результат: `str | None`.

### Опис із вихідного коду

```text
Why the outbound policy refuses ``url`` (``None``: allowed, or left to the proxy). The page router aborts
a refused request with its URL before the browser connects; the proxy still checks every connection, so a
DNS answer that changes after this check changes nothing. One resolution per host and port of a page.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:148](../../../../../../services/web-collector/tests/test_render_js.py#L148).

```python
assert await proxy.precheck("https://metadata.example.test/x") is not None
```

Контекст і передумови: [services/web-collector/tests/test_render_js.py:149](../../../../../../services/web-collector/tests/test_render_js.py#L149).

```python
assert await proxy.precheck(site.url("/")) is None
```

## jane_web_collector.render.EgressProxy.check

**Метод.** Код: [services/web-collector/src/jane_web_collector/render.py:198](../../../../../../services/web-collector/src/jane_web_collector/render.py#L198).

```python
def check(self, host: str, addresses: list[str]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `host` | `str` | `—` | positional-or-keyword |
| `addresses` | `list[str]` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `EgressDenied`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
The policy of the fetch client, then (``RENDER_DENY_PRIVATE``) no non-public address for a host that is
neither the page's own nor in ``scope.allowed_domains``: a page script must not reach internal services the
caller did not choose. Raises :class:`~.egress.EgressDenied`.
```

## jane_web_collector.render.RenderOptions

**Клас.** Код: [services/web-collector/src/jane_web_collector/render.py:349](../../../../../../services/web-collector/src/jane_web_collector/render.py#L349).

```python
class RenderOptions:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [enabled](jane_web_collector.render.md#jane_web_collectorrenderrenderoptionsenabled) | Поле | ні |
| [wait_until](jane_web_collector.render.md#jane_web_collectorrenderrenderoptionswait_until) | Поле | ні |
| [block_resource_types](jane_web_collector.render.md#jane_web_collectorrenderrenderoptionsblock_resource_types) | Поле | ні |
| [executable](jane_web_collector.render.md#jane_web_collectorrenderrenderoptionsexecutable) | Поле | ні |
| [deny_private](jane_web_collector.render.md#jane_web_collectorrenderrenderoptionsdeny_private) | Поле | ні |
| [__init__](jane_web_collector.render.md#jane_web_collectorrenderrenderoptions__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
Service-level rendering settings (``JANE_WEB_COLLECTOR_RENDER_*``).
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:221](../../../../../../services/web-collector/tests/test_render_js.py#L221).

```python
renderer = Renderer(RenderOptions(), EgressPolicy(deny_private=True), max_pages=1)
```

Контекст і передумови: [services/web-collector/tests/test_render_js.py:241](../../../../../../services/web-collector/tests/test_render_js.py#L241).

```python
renderer = Renderer(
        RenderOptions(), EgressPolicy(), max_pages=1, resolver=fake_dns({"shop.example.test": ["127.0.0.1"]})
    )
```

## jane_web_collector.render.RenderOptions.__init__

**Конструктор dataclass.** Код: [services/web-collector/src/jane_web_collector/render.py:349](../../../../../../services/web-collector/src/jane_web_collector/render.py#L349).

```python
def __init__(self, enabled: bool = True, wait_until: WaitUntil = 'networkidle', block_resource_types: tuple[str, ...] = ('image', 'media', 'font'), executable: Path | None = None, deny_private: bool = True) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `enabled` | `bool` | `True` | positional-or-keyword |
| `wait_until` | `WaitUntil` | `'networkidle'` | positional-or-keyword |
| `block_resource_types` | `tuple[str, ...]` | `('image', 'media', 'font')` | positional-or-keyword |
| `executable` | `Path \| None` | `None` | positional-or-keyword |
| `deny_private` | `bool` | `True` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:221](../../../../../../services/web-collector/tests/test_render_js.py#L221).

```python
renderer = Renderer(RenderOptions(), EgressPolicy(deny_private=True), max_pages=1)
```

Контекст і передумови: [services/web-collector/tests/test_render_js.py:241](../../../../../../services/web-collector/tests/test_render_js.py#L241).

```python
renderer = Renderer(
        RenderOptions(), EgressPolicy(), max_pages=1, resolver=fake_dns({"shop.example.test": ["127.0.0.1"]})
    )
```

## jane_web_collector.render.RenderOptions.enabled

**Поле.** Код: [services/web-collector/src/jane_web_collector/render.py:352](../../../../../../services/web-collector/src/jane_web_collector/render.py#L352).

```python
enabled: bool = True
```

Доступ: читання — так; запис — ні.

## jane_web_collector.render.RenderOptions.wait_until

**Поле.** Код: [services/web-collector/src/jane_web_collector/render.py:353](../../../../../../services/web-collector/src/jane_web_collector/render.py#L353).

```python
wait_until: WaitUntil = 'networkidle'
```

Доступ: читання — так; запис — ні.

## jane_web_collector.render.RenderOptions.block_resource_types

**Поле.** Код: [services/web-collector/src/jane_web_collector/render.py:354](../../../../../../services/web-collector/src/jane_web_collector/render.py#L354).

```python
block_resource_types: tuple[str, ...] = ('image', 'media', 'font')
```

Доступ: читання — так; запис — ні.

## jane_web_collector.render.RenderOptions.executable

**Поле.** Код: [services/web-collector/src/jane_web_collector/render.py:355](../../../../../../services/web-collector/src/jane_web_collector/render.py#L355).

```python
executable: Path | None = None
```

Доступ: читання — так; запис — ні.

## jane_web_collector.render.RenderOptions.deny_private

**Поле.** Код: [services/web-collector/src/jane_web_collector/render.py:356](../../../../../../services/web-collector/src/jane_web_collector/render.py#L356).

```python
deny_private: bool = True
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
``RENDER_DENY_PRIVATE``: browser requests reach non-public addresses only for the page's own host and
    ``scope.allowed_domains``.
```

## jane_web_collector.render.Renderer

**Клас.** Код: [services/web-collector/src/jane_web_collector/render.py:371](../../../../../../services/web-collector/src/jane_web_collector/render.py#L371).

```python
class Renderer:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_web_collector.render.md#jane_web_collectorrenderrenderer__init__) | Конструктор | ні |
| [options](jane_web_collector.render.md#jane_web_collectorrenderrendereroptions) | Поле екземпляра | ні |
| [policy](jane_web_collector.render.md#jane_web_collectorrenderrendererpolicy) | Поле екземпляра | ні |
| [resolver](jane_web_collector.render.md#jane_web_collectorrenderrendererresolver) | Поле екземпляра | ні |
| [launch_timeout_ms](jane_web_collector.render.md#jane_web_collectorrenderrendererlaunch_timeout_ms) | Поле екземпляра | ні |
| [close_timeout_s](jane_web_collector.render.md#jane_web_collectorrenderrendererclose_timeout_s) | Поле екземпляра | ні |
| [last_error](jane_web_collector.render.md#jane_web_collectorrenderrendererlast_error) | Поле екземпляра | ні |
| [unavailable_reason](jane_web_collector.render.md#jane_web_collectorrenderrendererunavailable_reason) | Метод | ні |
| [capabilities](jane_web_collector.render.md#jane_web_collectorrenderrenderercapabilities) | Метод | ні |
| [aclose](jane_web_collector.render.md#jane_web_collectorrenderrendereraclose) | Метод | ні |
| [render](jane_web_collector.render.md#jane_web_collectorrenderrendererrender) | Метод | ні |

### Опис із вихідного коду

```text
Headless Chromium shared by every collection and fetch of the process, started on first use.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:221](../../../../../../services/web-collector/tests/test_render_js.py#L221).

```python
renderer = Renderer(RenderOptions(), EgressPolicy(deny_private=True), max_pages=1)
```

Контекст і передумови: [services/web-collector/tests/test_render_js.py:241](../../../../../../services/web-collector/tests/test_render_js.py#L241).

```python
renderer = Renderer(
        RenderOptions(), EgressPolicy(), max_pages=1, resolver=fake_dns({"shop.example.test": ["127.0.0.1"]})
    )
```

## jane_web_collector.render.Renderer.__init__

**Конструктор.** Код: [services/web-collector/src/jane_web_collector/render.py:374](../../../../../../services/web-collector/src/jane_web_collector/render.py#L374).

```python
def __init__(self, options: RenderOptions, policy: EgressPolicy, *, max_pages: int, resolver: Resolver=system_resolve, launch_timeout_ms: int | None=None, close_timeout_ms: int | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `options` | `RenderOptions` | `—` | positional-or-keyword |
| `policy` | `EgressPolicy` | `—` | positional-or-keyword |
| `max_pages` | `int` | `—` | keyword-only |
| `resolver` | `Resolver` | `system_resolve` | keyword-only |
| `launch_timeout_ms` | `int \| None` | `None` | keyword-only |
| `close_timeout_ms` | `int \| None` | `None` | keyword-only |

Результат: `None`.

### Опис із вихідного коду

```text
``launch_timeout_ms`` / ``close_timeout_ms``: ``collector.render_launch_timeout_ms`` /
``collector.render_close_timeout_ms`` (their defaults when not given).
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:221](../../../../../../services/web-collector/tests/test_render_js.py#L221).

```python
renderer = Renderer(RenderOptions(), EgressPolicy(deny_private=True), max_pages=1)
```

Контекст і передумови: [services/web-collector/tests/test_render_js.py:241](../../../../../../services/web-collector/tests/test_render_js.py#L241).

```python
renderer = Renderer(
        RenderOptions(), EgressPolicy(), max_pages=1, resolver=fake_dns({"shop.example.test": ["127.0.0.1"]})
    )
```

## jane_web_collector.render.Renderer.options

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/render.py:387](../../../../../../services/web-collector/src/jane_web_collector/render.py#L387).

```python
self.options = options
```

## jane_web_collector.render.Renderer.policy

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/render.py:388](../../../../../../services/web-collector/src/jane_web_collector/render.py#L388).

```python
self.policy = policy
```

## jane_web_collector.render.Renderer.resolver

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/render.py:389](../../../../../../services/web-collector/src/jane_web_collector/render.py#L389).

```python
self.resolver = resolver
```

## jane_web_collector.render.Renderer.launch_timeout_ms

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/render.py:390](../../../../../../services/web-collector/src/jane_web_collector/render.py#L390).

```python
self.launch_timeout_ms = launch_timeout_ms or defaults.render_launch_timeout_ms
```

## jane_web_collector.render.Renderer.close_timeout_s

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/render.py:391](../../../../../../services/web-collector/src/jane_web_collector/render.py#L391).

```python
self.close_timeout_s = (close_timeout_ms or defaults.render_close_timeout_ms) / 1000
```

## jane_web_collector.render.Renderer.last_error

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/render.py:398](../../../../../../services/web-collector/src/jane_web_collector/render.py#L398).

```python
self.last_error: str | None = None
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:406](../../../../../../services/web-collector/tests/test_render_js.py#L406).

```python
assert "after crash" in out.body.decode("utf-8") and renderer.last_error is None
```

## jane_web_collector.render.Renderer.unavailable_reason

**Метод.** Код: [services/web-collector/src/jane_web_collector/render.py:401](../../../../../../services/web-collector/src/jane_web_collector/render.py#L401).

```python
def unavailable_reason(self) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str | None`.

### Опис із вихідного коду

```text
Why rendering cannot work here, known without starting the browser.
```

## jane_web_collector.render.Renderer.capabilities

**Метод.** Код: [services/web-collector/src/jane_web_collector/render.py:409](../../../../../../services/web-collector/src/jane_web_collector/render.py#L409).

```python
def capabilities(self) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
``/v1/info`` capabilities: ``render_js`` and, when it is false, why.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:424](../../../../../../services/web-collector/tests/test_render_js.py#L424).

```python
assert renderer.capabilities()["render_js"] is False
```

## jane_web_collector.render.Renderer.aclose

**Метод.** Код: [services/web-collector/src/jane_web_collector/render.py:414](../../../../../../services/web-collector/src/jane_web_collector/render.py#L414).

```python
async def aclose(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:225](../../../../../../services/web-collector/tests/test_render_js.py#L225).

```python
await renderer.aclose()
```

Контекст і передумови: [services/web-collector/tests/test_render_js.py:247](../../../../../../services/web-collector/tests/test_render_js.py#L247).

```python
await renderer.aclose()
```

## jane_web_collector.render.Renderer.render

**Метод.** Код: [services/web-collector/src/jane_web_collector/render.py:467](../../../../../../services/web-collector/src/jane_web_collector/render.py#L467).

```python
async def render(self, result: HttpResult, *, user_agent: str, limits: ServiceLimits, accept_language: str | None=None, allowed_hosts: Callable[[str], bool] | None=None) -> HttpResult:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `result` | `HttpResult` | `—` | positional-or-keyword |
| `user_agent` | `str` | `—` | keyword-only |
| `limits` | `ServiceLimits` | `—` | keyword-only |
| `accept_language` | `str \| None` | `None` | keyword-only |
| `allowed_hosts` | `Callable[[str], bool] \| None` | `None` | keyword-only |

Результат: `HttpResult`.

### Опис із вихідного коду

```text
The fetched HTML ``result`` rendered by the browser: the same result with the serialized DOM as body.

``allowed_hosts``: hosts of ``scope.allowed_domains`` - with the page's own host the only ones the browser
may reach at a non-public address (``RENDER_DENY_PRIVATE``). Raises :class:`~.fetcher.FetchError`:
``not_implemented`` (no browser), ``timeout`` (the DOM could not be taken in time), ``internal_error`` (the
browser failed).
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:223](../../../../../../services/web-collector/tests/test_render_js.py#L223).

```python
out = await renderer.render(page, user_agent=RENDER_UA, limits=ServiceLimits())
```

Контекст і передумови: [services/web-collector/tests/test_render_js.py:245](../../../../../../services/web-collector/tests/test_render_js.py#L245).

```python
out = await renderer.render(page, user_agent=RENDER_UA, limits=ServiceLimits())
```
