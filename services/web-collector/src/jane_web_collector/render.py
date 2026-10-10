"""JavaScript rendering of pages (``fetch.render_js`` of the collector rules) in headless Chromium (Playwright).

The page itself is never requested by the browser. :class:`~.fetcher.Fetcher` fetches it first, with every guarantee
of a plain fetch: scope and robots.txt before, each redirect hop re-checked, the outbound address policy, per-host
limits, retries, ``crawl.max_material_bytes``, the User-Agent and the credentials of a managed connection. Only a
2xx HTML answer is rendered: the first navigation of the browser page is answered with the fetched body
(``route.fulfill``), any later navigation of a top-level frame (a script redirect, a reload, a popup) is aborted, so
the DOM is the DOM of the URL that passed the checks.

Everything else the browser loads (scripts, XHR/fetch, styles, frames, WebSockets) goes through
:class:`EgressProxy` - an HTTP proxy on 127.0.0.1, one per page - which applies the fetch client's
:class:`~.egress.EgressPolicy` to every connection the same way :class:`~.egress.GuardedBackend` does: the host is
resolved once, every address is checked, the connection is opened to a checked address (no DNS rebinding). Playwright
sends loopback through the proxy as well (``<-loopback>``), service workers are blocked and WebRTC may use proxied
traffic only. Requests of the resource types in ``RENDER_BLOCK_RESOURCE_TYPES`` are not made at all. One page may
download ``collector.render_max_transfer_bytes``; the browser sends the collector's User-Agent and never the
connection credentials.

The material is the serialized DOM (doctype + ``document.documentElement.outerHTML``) once the wait condition is
reached or ``collector.render_timeout_ms`` has passed, encoded as UTF-8 (``<meta charset>`` says so), cut at
``crawl.max_material_bytes``. If rendering is off, Playwright is not installed or Chromium cannot start, the URL fails
with ``not_implemented`` and a message saying why - never a silent plain fetch.
"""

from __future__ import annotations

import asyncio
import contextlib
import importlib.util
import logging
import time
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal
from urllib.parse import urlsplit

from .egress import EgressDenied, EgressPolicy, Resolver, system_resolve
from .fetcher import FetchError, HttpResult
from .settings import ServiceLimits

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from playwright.async_api import Browser, Page, Playwright, Route

__all__ = ["EgressProxy", "RenderOptions", "Renderer", "renderable"]

log = logging.getLogger(__name__)

WaitUntil = Literal["domcontentloaded", "load", "networkidle"]
RENDERED_CONTENT_TYPE = "text/html; charset=utf-8"
RENDERED_DROPPED_HEADERS = frozenset({"content-type", "content-length", "etag"})
"""Headers of the fetched bytes that do not describe the rendered DOM."""
RENDERABLE_TYPES = frozenset({"text/html", "application/xhtml+xml"})
INSTALL_HINT = "install the 'render' extra of jane-web-collector and Chromium (playwright install chromium)"
CHROMIUM_ARGS = (
    # WebRTC must not open UDP to arbitrary addresses past the egress proxy
    "--force-webrtc-ip-handling-policy=disable_non_proxied_udp",
    "--webrtc-ip-handling-policy=disable_non_proxied_udp",
    "--disable-dev-shm-usage",  # small /dev/shm in containers
)
PER_CONTEXT_PROXY = "http://per-context"
"""Launch-level proxy placeholder: every context sets its own proxy (Chromium needs a launch proxy for that)."""
DIAGNOSTIC_MAX_CHARS = 4000
"""``DiagnosticMessage.message`` maxLength of the contract."""
HOP_BY_HOP = frozenset({"connection", "proxy-connection", "keep-alive", "proxy-authorization"})
DEFAULT_PORTS = {"http": 80, "https": 443, "ws": 80, "wss": 443}

SNAPSHOT_JS = """() => {
  for (const m of document.querySelectorAll('meta[charset]')) m.setAttribute('charset', 'utf-8');
  for (const m of document.querySelectorAll('meta[http-equiv]')) {
    if ((m.getAttribute('http-equiv') || '').toLowerCase() === 'content-type') {
      m.setAttribute('content', 'text/html; charset=utf-8');
    }
  }
  const dt = document.doctype;
  const doctype = dt ? new XMLSerializer().serializeToString(dt) + '\\n' : '';
  return doctype + (document.documentElement ? document.documentElement.outerHTML : '');
}"""


def renderable(result: HttpResult) -> bool:
    """A 2xx HTML answer: the only kind of fetched document that is rendered."""
    return 200 <= result.status < 300 and result.media_type in RENDERABLE_TYPES


def _first_line(exc: BaseException) -> str:
    text = str(exc).strip().splitlines()
    return (text[0] if text else type(exc).__name__)[:300]


def _clip(text: str) -> str:
    return text if len(text) <= DIAGNOSTIC_MAX_CHARS else text[: DIAGNOSTIC_MAX_CHARS - 1] + "…"


def _split_authority(authority: str, default_port: int) -> tuple[str, int]:
    parts = urlsplit("//" + authority)
    if not parts.hostname:
        raise ValueError(f"no host in {authority!r}")
    return parts.hostname, parts.port or default_port


class _Refused(Exception):
    """The proxy does not open more connections (the transfer budget of the page is spent)."""


class EgressProxy:
    """HTTP proxy for one browser page: the outbound address policy for every connection (see the module docstring).

    ``CONNECT host:port`` (HTTPS, WebSocket) becomes a tunnel; an absolute-form request (plain HTTP) is forwarded
    in origin form with ``Connection: close``. A denied destination is listed in :attr:`denied`; the browser gets
    a failed tunnel (403 to ``CONNECT``) or a closed connection (plain HTTP), never a response it could read as the
    site's."""

    def __init__(
        self,
        policy: EgressPolicy,
        *,
        resolver: Resolver = system_resolve,
        connect_timeout_s: float,
        max_bytes: int,
    ) -> None:
        self.policy = policy
        self.resolver = resolver
        self.connect_timeout_s = connect_timeout_s
        self.max_bytes = max_bytes
        self.denied: list[str] = []
        self.connections = 0
        self.transferred = 0
        self.budget_exceeded = False
        self.url = ""
        self._verdicts: dict[tuple[str, int], str | None] = {}
        self._server: asyncio.Server | None = None
        self._tasks: set[asyncio.Task[Any]] = set()
        self._writers: set[asyncio.StreamWriter] = set()

    async def start(self) -> str:
        self._server = await asyncio.start_server(self._serve, "127.0.0.1", 0)
        port = self._server.sockets[0].getsockname()[1]
        self.url = f"http://127.0.0.1:{port}"
        return self.url

    async def aclose(self) -> None:
        if self._server is not None:
            self._server.close()
        self._cut()
        for task in list(self._tasks):
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)

    def _cut(self) -> None:
        for writer in list(self._writers):
            writer.close()

    async def precheck(self, url: str) -> str | None:
        """Why the outbound policy refuses ``url`` (``None``: allowed, or left to the proxy). The page router aborts
        a refused request with its URL before the browser connects; the proxy still checks every connection, so a
        DNS answer that changes after this check changes nothing. One resolution per host and port of a page."""
        parts = urlsplit(url)
        scheme = parts.scheme.lower()
        if scheme not in DEFAULT_PORTS or not parts.hostname:
            return None
        try:
            key = (parts.hostname, parts.port or DEFAULT_PORTS[scheme])
        except ValueError:
            return None
        if key not in self._verdicts:
            verdict: str | None = None
            try:
                async with asyncio.timeout(self.connect_timeout_s):
                    addresses = await self.resolver(*key)
                self.policy.check(key[0], addresses)
            except EgressDenied as exc:
                verdict = str(exc)
            except (OSError, TimeoutError):
                pass  # unresolvable: the proxy fails the connection
            self._verdicts[key] = verdict
        return self._verdicts[key]

    async def _serve(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        task = asyncio.current_task()
        if task is not None:
            self._tasks.add(task)
        self._writers.add(writer)
        upstream: asyncio.StreamWriter | None = None
        try:
            try:
                head = await reader.readuntil(b"\r\n\r\n")
            except (asyncio.IncompleteReadError, asyncio.LimitOverrunError, ConnectionError):
                return
            lines = head[:-4].decode("latin-1").split("\r\n")
            request_line = lines[0].split(" ")
            if len(request_line) != 3:
                return await self._reply(writer, 400, "Bad Request")
            method, target, version = request_line
            tunnel = method.upper() == "CONNECT"
            try:
                if tunnel:
                    host, port = _split_authority(target, 443)
                else:
                    url = urlsplit(target)
                    if url.scheme.lower() != "http" or not url.hostname:
                        return await self._reply(writer, 400, "Bad Request")
                    host, port = url.hostname, url.port or 80
            except ValueError:
                return await self._reply(writer, 400, "Bad Request")
            try:
                up_reader, upstream = await self._connect(host, port)
            except EgressDenied as exc:
                self.denied.append(str(exc))
                return await self._refuse(writer, tunnel, 403, "Forbidden")
            except _Refused:
                return await self._refuse(writer, tunnel, 403, "Forbidden")
            except (OSError, TimeoutError):
                return await self._refuse(writer, tunnel, 502, "Bad Gateway")
            self._writers.add(upstream)
            if tunnel:
                writer.write(b"HTTP/1.1 200 Connection established\r\n\r\n")
                await writer.drain()
            else:
                path = (url.path or "/") + (f"?{url.query}" if url.query else "")
                kept = [h for h in lines[1:] if h and h.split(":", 1)[0].strip().lower() not in HOP_BY_HOP]
                request = f"{method} {path} {version}\r\n" + "".join(f"{h}\r\n" for h in kept)
                upstream.write((request + "Connection: close\r\n\r\n").encode("latin-1"))
            await self._relay(reader, writer, up_reader, upstream, rewrite_response=not tunnel)
        except (ConnectionError, asyncio.IncompleteReadError, asyncio.LimitOverrunError):
            return
        finally:
            for w in (writer, upstream):
                if w is not None:
                    w.close()
                    self._writers.discard(w)
            if task is not None:
                self._tasks.discard(task)

    async def _connect(self, host: str, port: int) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """Resolve once, check every address, connect to a checked one (as ``GuardedBackend.connect_tcp``)."""
        if self.budget_exceeded:
            raise _Refused
        async with asyncio.timeout(self.connect_timeout_s):
            addresses = await self.resolver(host, port)
            if not addresses:
                raise OSError(f"cannot resolve {host}: no addresses")
            self.policy.check(host, addresses)
            last: OSError | None = None
            for address in addresses:
                try:
                    streams = await asyncio.open_connection(address, port)
                except OSError as exc:
                    last = exc
                    continue
                self.connections += 1
                return streams
        assert last is not None
        raise last

    async def _relay(
        self,
        client_reader: asyncio.StreamReader,
        client: asyncio.StreamWriter,
        upstream_reader: asyncio.StreamReader,
        upstream: asyncio.StreamWriter,
        *,
        rewrite_response: bool,
    ) -> None:
        """Copy both ways until one side closes (a plain HTTP response is followed by ``Connection: close``)."""
        up = asyncio.create_task(self._pipe(client_reader, upstream, count=False))
        down = asyncio.create_task(self._pipe(upstream_reader, client, count=True, rewrite=rewrite_response))
        try:
            await asyncio.wait({up, down}, return_when=asyncio.FIRST_COMPLETED)
        finally:
            for t in (up, down):
                t.cancel()
            await asyncio.gather(up, down, return_exceptions=True)

    async def _pipe(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        *,
        count: bool,
        rewrite: bool = False,
    ) -> None:
        if rewrite:  # the browser must not reuse a connection that the proxy closes after this response
            head = await reader.readuntil(b"\r\n\r\n")
            if not self._count(len(head), count):
                return
            lines = head[:-4].decode("latin-1").split("\r\n")
            kept = [lines[0], *(h for h in lines[1:] if h.split(":", 1)[0].strip().lower() not in HOP_BY_HOP)]
            writer.write(("\r\n".join(kept) + "\r\nConnection: close\r\n\r\n").encode("latin-1"))
        while chunk := await reader.read(65536):
            if not self._count(len(chunk), count):
                return
            writer.write(chunk)
            await writer.drain()

    def _count(self, size: int, count: bool) -> bool:
        """Account downloaded bytes; past the budget every connection of the page is cut."""
        if not count:
            return True
        self.transferred += size
        if self.transferred > self.max_bytes:
            self.budget_exceeded = True
            self._cut()
            return False
        return True

    async def _refuse(self, writer: asyncio.StreamWriter, tunnel: bool, status: int, reason: str) -> None:
        """A failed tunnel for ``CONNECT``; for plain HTTP no answer at all (a network error, not a page)."""
        if tunnel:
            await self._reply(writer, status, reason)

    async def _reply(self, writer: asyncio.StreamWriter, status: int, reason: str) -> None:
        writer.write(f"HTTP/1.1 {status} {reason}\r\nContent-Length: 0\r\nConnection: close\r\n\r\n".encode())
        with contextlib.suppress(ConnectionError):
            await writer.drain()


@dataclass(frozen=True)
class RenderOptions:
    """Service-level rendering settings (``JANE_WEB_COLLECTOR_RENDER_*``)."""

    enabled: bool = True
    wait_until: WaitUntil = "networkidle"
    block_resource_types: tuple[str, ...] = ("image", "media", "font")
    executable: Path | None = None


@dataclass
class _PageLog:
    """What the router of one page did."""

    served: bool = False
    blocked_types: int = 0
    navigations: list[str] = field(default_factory=list)
    denied: list[str] = field(default_factory=list)


class Renderer:
    """Headless Chromium shared by every collection and fetch of the process, started on first use."""

    def __init__(
        self,
        options: RenderOptions,
        policy: EgressPolicy,
        *,
        max_pages: int,
        resolver: Resolver = system_resolve,
    ) -> None:
        self.options = options
        self.policy = policy
        self.resolver = resolver
        self._pages = asyncio.Semaphore(max_pages)
        self._lock = asyncio.Lock()
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self.last_error: str | None = None
        """Why the browser could not start the last time it was needed (cleared by a successful start)."""

    def unavailable_reason(self) -> str | None:
        """Why rendering cannot work here, known without starting the browser."""
        if not self.options.enabled:
            return "rendering is disabled (JANE_WEB_COLLECTOR_RENDER_ENABLED=false)"
        if importlib.util.find_spec("playwright") is None:
            return f"Playwright is not installed; {INSTALL_HINT}"
        return None

    def capabilities(self) -> dict[str, Any]:
        """``/v1/info`` capabilities: ``render_js`` and, when it is false, why."""
        reason = self.unavailable_reason() or self.last_error
        return {"render_js": reason is None, **({"render_js_unavailable": reason} if reason else {})}

    async def aclose(self) -> None:
        async with self._lock:
            await self._shutdown()

    async def _shutdown(self) -> None:
        browser, playwright = self._browser, self._playwright
        self._browser = self._playwright = None
        if browser is not None:
            with contextlib.suppress(Exception):
                await browser.close()
        if playwright is not None:
            with contextlib.suppress(Exception):
                await playwright.stop()

    async def _get_browser(self) -> Browser:
        async with self._lock:
            if self._browser is not None and self._browser.is_connected():
                return self._browser
            await self._shutdown()  # a browser that crashed or disconnected is started again
            reason = self.unavailable_reason()
            if reason is not None:
                raise FetchError("not_implemented", f"fetch.render_js: {reason}")
            from playwright.async_api import async_playwright

            try:
                self._playwright = await async_playwright().start()
                self._browser = await self._playwright.chromium.launch(
                    headless=True,
                    executable_path=self.options.executable,
                    proxy={"server": PER_CONTEXT_PROXY},
                    args=list(CHROMIUM_ARGS),
                )
            # Playwright's Error, a missing driver or browser, an event loop without subprocess support
            except Exception as exc:
                await self._shutdown()
                self.last_error = f"headless Chromium could not start: {_first_line(exc)}; {INSTALL_HINT}"
                log.warning("headless browser unavailable", extra={"error": self.last_error})
                raise FetchError("not_implemented", f"fetch.render_js: {self.last_error}") from None
            self.last_error = None
            log.info("headless browser started", extra={"browser_version": self._browser.version})
            return self._browser

    async def render(
        self,
        result: HttpResult,
        *,
        user_agent: str,
        limits: ServiceLimits,
        accept_language: str | None = None,
    ) -> HttpResult:
        """The fetched HTML ``result`` rendered by the browser: the same result with the serialized DOM as body.

        Raises :class:`~.fetcher.FetchError`: ``not_implemented`` (no browser), ``timeout`` (the DOM could not be
        taken in time), ``internal_error`` (the browser failed)."""
        async with self._pages:
            browser = await self._get_browser()
            proxy = EgressProxy(
                self.policy,
                resolver=self.resolver,
                connect_timeout_s=limits.timeouts.connect_timeout_ms / 1000,
                max_bytes=limits.collector.render_max_transfer_bytes,
            )
            await proxy.start()
            try:
                return await self._render(browser, proxy, result, user_agent, limits, accept_language)
            finally:
                await proxy.aclose()

    async def _render(
        self,
        browser: Browser,
        proxy: EgressProxy,
        result: HttpResult,
        user_agent: str,
        limits: ServiceLimits,
        accept_language: str | None,
    ) -> HttpResult:
        from playwright.async_api import Error as PlaywrightError
        from playwright.async_api import TimeoutError as PlaywrightTimeoutError

        timeout_ms = limits.collector.render_timeout_ms
        started = time.monotonic()
        deadline = started + timeout_ms / 1000
        page_log = _PageLog()
        incomplete: str | None = None
        try:
            context = await browser.new_context(
                user_agent=user_agent,
                proxy={"server": proxy.url},
                service_workers="block",
                accept_downloads=False,
                extra_http_headers={"Accept-Language": accept_language} if accept_language else None,
            )
        except PlaywrightError as exc:
            raise FetchError(
                "internal_error", f"render: browser context failed: {_first_line(exc)}"
            ) from None
        try:
            page = await context.new_page()
            await context.route("**/*", self._router(page, result, page_log, proxy))
            try:
                await page.goto(result.final_url, wait_until="commit", timeout=timeout_ms)
            except PlaywrightTimeoutError:
                raise FetchError(
                    "timeout",
                    f"render: the page did not open within collector.render_timeout_ms={timeout_ms}",
                ) from None
            try:
                await page.wait_for_load_state(self.options.wait_until, timeout=_left_ms(deadline))
            except PlaywrightTimeoutError:
                incomplete = (
                    f"'{self.options.wait_until}' not reached within collector.render_timeout_ms={timeout_ms}"
                )
            extra_ms = min(limits.collector.render_extra_wait_ms, _left_ms(deadline))
            if extra_ms > 0 and not incomplete:
                await asyncio.sleep(extra_ms / 1000)
            try:
                html = await asyncio.wait_for(page.evaluate(SNAPSHOT_JS), timeout_ms / 1000)
            except TimeoutError:
                raise FetchError(
                    "timeout",
                    f"render: the DOM was not taken within collector.render_timeout_ms={timeout_ms}",
                ) from None
        except PlaywrightError as exc:
            raise FetchError("internal_error", f"render failed: {_first_line(exc)}") from None
        finally:
            with contextlib.suppress(Exception):
                await context.close()
        elapsed_ms = int((time.monotonic() - started) * 1000)
        if not isinstance(html, str):
            raise FetchError("internal_error", "render: the page returned no DOM")
        return self._rendered(result, html, limits, proxy, page_log, incomplete, elapsed_ms)

    def _router(
        self, page: Page, result: HttpResult, page_log: _PageLog, proxy: EgressProxy
    ) -> Callable[[Route], Awaitable[None]]:
        blocked = frozenset(self.options.block_resource_types)
        document_headers = {"content-type": result.headers.get("content-type", RENDERED_CONTENT_TYPE)}
        if language := result.headers.get("content-language"):
            document_headers["content-language"] = language

        async def route(route: Route) -> None:
            request = route.request
            try:
                if request.is_navigation_request() and request.frame.parent_frame is None:
                    if not page_log.served and request.frame == page.main_frame:
                        page_log.served = True  # the fetched document; the browser never requests it
                        await route.fulfill(status=result.status, headers=document_headers, body=result.body)
                    else:  # a script redirect, reload or popup would replace the checked page
                        page_log.navigations.append(request.url)
                        await route.abort("blockedbyclient")
                    return
                if request.resource_type in blocked:
                    page_log.blocked_types += 1
                    await route.abort("blockedbyclient")
                    return
                if (reason := await proxy.precheck(request.url)) is not None:
                    page_log.denied.append(f"{request.url} ({reason})")
                    await route.abort("accessdenied")
                    return
                await route.continue_()  # through the egress proxy of this page
            except Exception:  # the page is closing, or the request cannot be routed: it must not hang
                log.debug("request not routed", extra={"url": request.url}, exc_info=True)
                with contextlib.suppress(Exception):
                    await route.abort("failed")

        return route

    def _rendered(
        self,
        result: HttpResult,
        html: str,
        limits: ServiceLimits,
        proxy: EgressProxy,
        page_log: _PageLog,
        incomplete: str | None,
        elapsed_ms: int,
    ) -> HttpResult:
        body = html.encode("utf-8")
        truncated = result.truncated
        max_bytes = limits.crawl.max_material_bytes
        if len(body) > max_bytes:
            body = body[:max_bytes].decode("utf-8", errors="ignore").encode("utf-8")
            truncated = True
        headers = {k: v for k, v in result.headers.items() if k not in RENDERED_DROPPED_HEADERS}
        headers["content-type"] = RENDERED_CONTENT_TYPE
        diagnostics = [
            {
                "level": "info",
                "code": "rendered",
                "message": (
                    f"rendered in headless Chromium (fetch.render_js): wait '{self.options.wait_until}', "
                    f"{elapsed_ms} ms, {proxy.connections} connection(s) and {proxy.transferred} bytes through "
                    f"the egress proxy, {page_log.blocked_types} request(s) of blocked types not made"
                ),
            }
        ]
        if incomplete:
            diagnostics.append({"level": "warning", "code": "render_incomplete", "message": incomplete})
        if page_log.denied or proxy.denied:
            denied = "; ".join(dict.fromkeys([*page_log.denied, *proxy.denied]))
            diagnostics.append(
                {
                    "level": "warning",
                    "code": "render_egress_denied",
                    "message": _clip(f"browser requests refused by the egress policy: {denied}"),
                }
            )
        if proxy.budget_exceeded:
            diagnostics.append(
                {
                    "level": "warning",
                    "code": "render_budget_exceeded",
                    "message": (
                        "the browser downloaded more than collector.render_max_transfer_bytes="
                        f"{proxy.max_bytes}; its connections were cut and the DOM taken as it was"
                    ),
                }
            )
        if page_log.navigations:
            targets = ", ".join(dict.fromkeys(page_log.navigations))
            diagnostics.append(
                {
                    "level": "info",
                    "code": "render_navigation_blocked",
                    "message": _clip(f"the page tried to navigate away (not followed): {targets}"),
                }
            )
        return replace(
            result,
            body=body,
            headers=headers,
            truncated=truncated,
            diagnostics=[*result.diagnostics, *diagnostics],
            network_bytes=len(result.body) + proxy.transferred,
        )


def _left_ms(deadline: float) -> int:
    """Milliseconds until ``deadline``, at least 1 (Playwright reads 0 as "no timeout")."""
    return max(1, int((deadline - time.monotonic()) * 1000))
