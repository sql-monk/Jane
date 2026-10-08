"""Outbound address policy of the fetch client (protection against SSRF).

A collection or ``POST /v1/fetches`` must not turn the collector into a proxy to the cloud metadata service
or to internal services. Every TCP connection of the fetch client goes through :class:`GuardedBackend`:

1. the host name is resolved once (``getaddrinfo``);
2. **every** resolved address is checked by :class:`EgressPolicy` - one forbidden address denies the host;
3. the connection is opened to an address that was checked (TLS still verifies the original host name), so
   a DNS answer that changes between the check and the connection (DNS rebinding) cannot bypass the policy.

The check is made at connection time, so it covers the first request, every redirect hop (a new host is a
new connection; the redirect target is also re-checked by scope and robots.txt before it is requested),
``robots.txt`` and sitemap/strategy fetches alike. A denial is :class:`EgressDenied`; the fetcher turns it
into ``access_denied_by_policy`` (403 for ``POST /v1/fetches``, an error of the URL in a collection).

Policy (``Settings.egress_*``, README "Політика вихідних адрес"):

* ``deny_link_local`` (default **on**): link-local ``169.254.0.0/16`` (cloud metadata ``169.254.169.254``),
  ``fe80::/10`` and the AWS IPv6 metadata address ``fd00:ec2::254``;
* ``deny_private`` (default off): every address that is not globally reachable - loopback, RFC 1918,
  ``fc00::/7``, CGNAT ``100.64.0.0/10``, ``0.0.0.0/8``, documentation and reserved ranges - and multicast.
  Off by default because the dev/e2e test site lives in a private Docker network.

IPv4 addresses embedded in IPv6 (``::ffff:a.b.c.d``, NAT64 ``64:ff9b::/96``, 6to4 ``2002::/16``) are
checked as the IPv4 address they lead to.
"""

from __future__ import annotations

import ipaddress
import socket
import typing
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass

import anyio
import httpcore
import httpx

__all__ = [
    "EgressDenied",
    "EgressPolicy",
    "GuardedBackend",
    "GuardedTransport",
    "Resolver",
    "system_resolve",
]

IPAddress = ipaddress.IPv4Address | ipaddress.IPv6Address

METADATA_NETWORKS = (
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("fe80::/10"),
    ipaddress.ip_network("fd00:ec2::254/128"),
)
"""Denied with ``deny_link_local``: link-local ranges (cloud metadata) and the AWS IPv6 metadata address."""
NAT64 = ipaddress.ip_network("64:ff9b::/96")

Resolver = Callable[[str, int], Awaitable[list[str]]]
"""``(host, port) -> addresses`` in the order to try them."""


class EgressDenied(Exception):
    """The destination address is forbidden by the outbound address policy."""

    def __init__(self, host: str, address: str, reason: str) -> None:
        super().__init__(f"{host} resolves to {address}: {reason} (egress policy)")
        self.host = host
        self.address = address
        self.reason = reason


def _effective(ip: IPAddress) -> IPAddress:
    """The IPv4 address an IPv6 address leads to (mapped, NAT64, 6to4), or the address itself."""
    if isinstance(ip, ipaddress.IPv6Address):
        if ip.ipv4_mapped is not None:
            return ip.ipv4_mapped
        if ip in NAT64:
            return ipaddress.IPv4Address(int(ip) & 0xFFFFFFFF)
        if ip.sixtofour is not None:
            return ip.sixtofour
    return ip


@dataclass(frozen=True)
class EgressPolicy:
    deny_link_local: bool = True
    deny_private: bool = False

    def reason(self, address: str | IPAddress) -> str | None:
        """Why ``address`` is forbidden, or ``None`` if a connection to it is allowed."""
        ip = _effective(ipaddress.ip_address(address) if isinstance(address, str) else address)
        if self.deny_link_local and (ip.is_link_local or any(ip in net for net in METADATA_NETWORKS)):
            return "link-local or cloud metadata address"
        if self.deny_private and (not ip.is_global or ip.is_multicast):
            return "private, loopback or other non-public address"
        return None

    def check(self, host: str, addresses: Iterable[str]) -> None:
        for address in addresses:
            reason = self.reason(address)
            if reason is not None:
                raise EgressDenied(host, address, reason)


async def system_resolve(host: str, port: int) -> list[str]:
    """Addresses of ``host`` from the system resolver, without duplicates, in ``getaddrinfo`` order."""
    infos = await anyio.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    out: list[str] = []
    for *_, sockaddr in infos:
        address = str(sockaddr[0])
        if address not in out:
            out.append(address)
    return out


class GuardedBackend(httpcore.AsyncNetworkBackend):
    """Network backend that resolves, checks and connects to a checked address (see the module docstring)."""

    def __init__(
        self,
        policy: EgressPolicy,
        *,
        resolver: Resolver = system_resolve,
        inner: httpcore.AsyncNetworkBackend | None = None,
    ) -> None:
        self.policy = policy
        self.resolver = resolver
        self.inner = inner or httpcore.AnyIOBackend()

    async def connect_tcp(
        self,
        host: str,
        port: int,
        timeout: float | None = None,  # noqa: ASYNC109 - httpcore.AsyncNetworkBackend signature
        local_address: str | None = None,
        socket_options: typing.Iterable[httpcore.SOCKET_OPTION] | None = None,
    ) -> httpcore.AsyncNetworkStream:
        try:
            with anyio.fail_after(timeout):
                addresses = await self.resolver(host, port)
        except TimeoutError as exc:
            raise httpcore.ConnectTimeout(f"resolving {host} timed out") from exc
        except OSError as exc:
            raise httpcore.ConnectError(f"cannot resolve {host}: {exc}") from exc
        if not addresses:
            raise httpcore.ConnectError(f"cannot resolve {host}: no addresses")
        self.policy.check(host, addresses)
        last: Exception | None = None
        for address in addresses:
            try:
                return await self.inner.connect_tcp(
                    address, port, timeout=timeout, local_address=local_address, socket_options=socket_options
                )
            except (httpcore.ConnectError, httpcore.ConnectTimeout) as exc:
                last = exc
        assert last is not None
        raise last

    async def connect_unix_socket(
        self,
        path: str,
        timeout: float | None = None,  # noqa: ASYNC109 - httpcore.AsyncNetworkBackend signature
        socket_options: typing.Iterable[httpcore.SOCKET_OPTION] | None = None,
    ) -> httpcore.AsyncNetworkStream:
        raise httpcore.ConnectError("unix sockets are not used by the fetch client")

    async def sleep(self, seconds: float) -> None:
        await self.inner.sleep(seconds)


class GuardedTransport(httpx.AsyncHTTPTransport):
    """``httpx.AsyncHTTPTransport`` whose connections go through :class:`GuardedBackend`.

    httpx has no public parameter for the network backend, so the connection pool is rebuilt with the same
    settings the base class uses (no proxy, ``trust_env=False``) plus the guarded backend.
    """

    def __init__(self, limits: httpx.Limits, backend: GuardedBackend) -> None:
        super().__init__(limits=limits, trust_env=False)
        self._pool = httpcore.AsyncConnectionPool(
            ssl_context=httpx.create_ssl_context(trust_env=False),
            max_connections=limits.max_connections,
            max_keepalive_connections=limits.max_keepalive_connections,
            keepalive_expiry=limits.keepalive_expiry,
            network_backend=backend,
        )
