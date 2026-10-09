"""Secret policy of storage connections (coordinator decision, same as WP-10 ``llm`` and WP-04
``telegram-collector``).

A connection decides *where* a resolved secret goes: the adapter logs in to ``params.host`` /
``params.endpoint`` with it, and connections arrive through ``PUT /v1/connections/{id}``. So this executor
restricts both ends:

* ``env:VAR`` — only variables starting with ``JANE_STORAGE_SECRET_ENV_PREFIX`` (default ``JANE_SECRET_``),
  so not ``PGPASSWORD`` or another service's configuration;
* ``file:<path>`` — only inside ``JANE_STORAGE_SECRET_FILES_DIR`` (default ``/run/secrets``); the path is
  resolved first (``..`` and symlinks do not escape) and the resolved file is read through pinned path
  components; ``vault:`` is disabled (both: jane-kit's shared :class:`jane_kit.secrets.SecretPolicy`, R17);
* every network address the adapter of the connection contacts — only hosts from
  ``JANE_STORAGE_CONNECTION_HOST_ALLOWLIST`` (``hostname`` = any port, ``hostname:port`` = that port; default
  empty, so every connection with a network address is rejected). :data:`KIND_ADDRESSES` knows the address
  parameters of the built-in adapters, including their defaults (``localhost``, the actual botocore S3 bucket host) and
  hosts inside URIs; :data:`GENERIC_ADDRESS_KEYS` are checked for every kind, so an adapter unknown to the
  core cannot take a host from them unchecked.

Values that URL parsers read differently (userinfo ``@``, backslashes, whitespace, control characters,
percent-encoding in the host, trailing dots, IPv6 literals, Unix socket paths) are rejected instead of being
"normalized".
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from jane_kit.errors import FieldError
from jane_kit.secrets import SECRET_REF_NOT_ALLOWED, HostAllowlist, SecretPolicy, parse_host_port

__all__ = [
    "GENERIC_ADDRESS_KEYS",
    "HOST_NOT_ALLOWED",
    "KIND_ADDRESSES",
    "SECRET_REF_NOT_ALLOWED",
    "Address",
    "AddressError",
    "ConnectionPolicy",
    "KindAddresses",
    "network_addresses",
    "parse_host_port",
    "redact",
    "service_url",
]

HOST_NOT_ALLOWED = "host_not_allowed"

_URL = re.compile(
    r"(?P<scheme>[A-Za-z][A-Za-z0-9+.-]{0,31})://(?P<authority>[^/?#]*)(?P<rest>[/?#].*)?",
    re.ASCII | re.DOTALL,
)
_UNSAFE = re.compile(r"[^\x21-\x7e]|[\\@]")
"""Anything but printable ASCII, a backslash or userinfo: parsers disagree on such URLs."""
_REGION = re.compile(r"(?!-)[a-z0-9-]{1,63}(?<!-)", re.ASCII)
_DEFAULT_PORTS = {"http": 80, "https": 443, "mongodb": 27017}
_MAX_VALUE = 2048


class AddressError(ValueError):
    """A network-address parameter whose host cannot be determined safely."""

    def __init__(self, pointer: str, message: str) -> None:
        super().__init__(message)
        self.pointer = pointer


@dataclass(frozen=True)
class Address:
    pointer: str
    """JSON Pointer of the parameter in the Connection (``/params/host``)."""
    host: str
    port: int | None
    """Effective port (explicit or the adapter's default); ``None`` when it is not known."""

    def __str__(self) -> str:
        return self.host if self.port is None else f"{self.host}:{self.port}"


def _host(value: object, pointer: str, default_port: int | None) -> Address:
    parsed = parse_host_port(value)
    if parsed is None:
        raise AddressError(pointer, "must be a plain hostname or hostname:port")
    host, port = parsed
    return Address(pointer, host, default_port if port is None else port)


def _url(
    value: object,
    pointer: str,
    *,
    schemes: frozenset[str] | None,
    default_port: int | None = None,
    multi_host: bool = False,
) -> list[Address]:
    """Hosts of ``scheme://host[:port][,host[:port]…][/path][?query]`` (no userinfo)."""
    if not isinstance(value, str) or len(value) > _MAX_VALUE or _UNSAFE.search(value):
        raise AddressError(pointer, "must be a URL without userinfo, whitespace or backslashes")
    m = _URL.fullmatch(value)
    if m is None:
        raise AddressError(pointer, "must be a URL scheme://host[:port]")
    scheme = m.group("scheme").lower()
    if schemes is not None and scheme not in schemes:
        raise AddressError(pointer, f"URL scheme must be one of {sorted(schemes)}")
    hosts = m.group("authority").split(",")
    if len(hosts) > 1 and not multi_host:
        raise AddressError(pointer, "must name a single host")
    port = _DEFAULT_PORTS.get(scheme) if default_port is None else default_port
    return [_host(h, pointer, port) for h in hosts]


def service_url(value: object, pointer: str) -> Address:
    """Address of a Jane service URL configured by the operator (``JANE_STORAGE_REGISTRY_URL``):
    ``http(s)://host[:port][/path]`` with the same strict parsing as connection addresses, one host, no userinfo,
    query or fragment."""
    (address,) = _url(value, pointer, schemes=frozenset({"http", "https"}))
    m = _URL.fullmatch(str(value))
    if m is not None and m.group("rest") and ("?" in m.group("rest") or "#" in m.group("rest")):
        raise AddressError(pointer, "must not have a query or a fragment")
    return address


def _port(params: Mapping[str, Any], default: int) -> int:
    value = params.get("port", default)
    if isinstance(value, bool):
        raise AddressError("/params/port", "must be an integer 1..65535")
    try:
        port = int(value)
    except (TypeError, ValueError):
        raise AddressError("/params/port", "must be an integer 1..65535") from None
    if not 0 < port < 65536:
        raise AddressError("/params/port", "must be an integer 1..65535")
    return port


def _database(default_port: int) -> Callable[[Mapping[str, Any]], list[Address]]:
    """``params.host`` (the adapters default to ``localhost``) + ``params.port``."""

    def addresses(params: Mapping[str, Any]) -> list[Address]:
        return [_host(params.get("host", "localhost"), "/params/host", _port(params, default_port))]

    return addresses


def _mongodb(params: Mapping[str, Any]) -> list[Address]:
    """``params.host`` is passed to the driver as is: ``hostname[:port]`` or a ``mongodb://`` /
    ``mongodb+srv://`` connection string whose hosts are all checked."""
    port = _port(params, 27017)
    host = params.get("host", "localhost")
    if not (isinstance(host, str) and "://" in host):
        return [_host(host, "/params/host", port)]
    if host[:14].lower() == "mongodb+srv://":
        # DNS SRV/TXT records of the named host define the servers: the named host must be allowed itself
        found = _url(host, "/params/host", schemes=frozenset({"mongodb+srv"}))
        if found[0].port is not None:
            raise AddressError("/params/host", "mongodb+srv:// must not name a port")
        return found
    return _url(host, "/params/host", schemes=frozenset({"mongodb"}), default_port=port, multi_host=True)


def _endpoint(params: Mapping[str, Any]) -> list[Address]:
    return _url(params["endpoint"], "/params/endpoint", schemes=frozenset({"http", "https"}))


class _S3HostCaptured(Exception):
    def __init__(self, url: str) -> None:
        self.url = url


def _s3_request_address(params: Mapping[str, Any], *, default_style: str) -> Address:
    """Resolve botocore's real bucket URL without allowing the probe to use the network."""
    import boto3  # type: ignore[import-untyped]
    from botocore.config import Config  # type: ignore[import-untyped]

    endpoint = params.get("endpoint") or None
    pointer = "/params/endpoint" if endpoint else "/params/region"
    if endpoint:
        _endpoint(params)  # strict URL validation before botocore sees untrusted input
    region = params.get("region") or "us-east-1"
    if not isinstance(region, str) or not _REGION.fullmatch(region):
        raise AddressError("/params/region", "must be an AWS region name")
    style = params.get("addressing_style", default_style)
    if style not in {"auto", "path", "virtual"}:
        raise AddressError("/params/addressing_style", "must be auto, path or virtual")
    bucket = params.get("bucket")
    if not isinstance(bucket, str) or not bucket:
        raise AddressError("/params/bucket", "must name a bucket")

    def capture(request: Any, **_kwargs: Any) -> None:
        raise _S3HostCaptured(str(request.url))

    def block_network(*_args: Any, **_kwargs: Any) -> None:
        raise RuntimeError("S3 policy probe may not use the network")

    try:
        client = boto3.session.Session().client(
            "s3",
            endpoint_url=endpoint,
            region_name=region,
            aws_access_key_id="policy-probe",
            aws_secret_access_key="policy-probe",  # noqa: S106 - never sent; HTTP transport is disabled
            config=Config(s3={"addressing_style": style}, retries={"total_max_attempts": 1}),
        )
        try:
            client._endpoint.http_session.send = block_network  # fail-closed probe
            client.meta.events.register_first("before-send.s3", capture)
            try:
                client.head_bucket(Bucket=bucket)
            except _S3HostCaptured as captured:
                addresses = _url(captured.url, pointer, schemes=frozenset({"http", "https"}))
                return addresses[0]
            raise AddressError(pointer, "cannot determine S3 request host")
        finally:
            client.close()
    except AddressError:
        raise
    except Exception:
        raise AddressError(pointer, "cannot determine S3 request host") from None


def _s3(params: Mapping[str, Any]) -> list[Address]:
    """Actual botocore bucket host for AWS or a custom endpoint (never a guessed regional host)."""
    if params.get("endpoint") and params.get("addressing_style", "auto") != "path":
        raise AddressError("/params/addressing_style", "custom S3 endpoint requires path addressing")
    return [_s3_request_address(params, default_style="auto")]


def _minio(params: Mapping[str, Any]) -> list[Address]:
    """``params.endpoint`` (the adapter refuses to open without one)."""
    if params.get("endpoint") and params.get("addressing_style", "path") != "path":
        raise AddressError("/params/addressing_style", "custom MinIO endpoint requires path addressing")
    return [_s3_request_address(params, default_style="path")] if params.get("endpoint") else []


@dataclass(frozen=True)
class KindAddresses:
    keys: frozenset[str]
    """Parameters this rule interprets (the generic check skips them)."""
    addresses: Callable[[Mapping[str, Any]], list[Address]]


KIND_ADDRESSES: Mapping[str, KindAddresses] = {
    "filesystem": KindAddresses(frozenset(), lambda _params: []),
    "postgresql": KindAddresses(frozenset({"host", "port"}), _database(5432)),
    "sqlserver": KindAddresses(frozenset({"host", "port"}), _database(1433)),
    "mongodb": KindAddresses(frozenset({"host", "port"}), _mongodb),
    "s3": KindAddresses(frozenset({"endpoint", "region"}), _s3),
    "minio": KindAddresses(frozenset({"endpoint"}), _minio),
}
"""Network addresses of the built-in adapters (``services/storage/adapters/*``, README of each adapter)."""

GENERIC_ADDRESS_KEYS = (
    "host",
    "hosts",
    "hostname",
    "server",
    "address",
    "endpoint",
    "endpoint_url",
    "url",
    "uri",
    "dsn",
    "connection_string",
    "base_url",
    "api_base",
)
"""Host-like parameters checked for every kind (``hostname[:port]``, ``scheme://host[:port]…`` or a list)."""


def _generic(key: str, value: object) -> list[Address]:
    pointer = f"/params/{key}"
    items = value if isinstance(value, list) else [value]
    out: list[Address] = []
    for item in items:
        if isinstance(item, str) and "://" in item:
            out += _url(item, pointer, schemes=None, multi_host=True)
        else:
            out.append(_host(item, pointer, None))
    return out


def network_addresses(kind: str, params: Mapping[str, Any]) -> tuple[list[Address], list[AddressError]]:
    """Every host the adapter of ``kind`` would contact for these ``params`` + parameters that cannot be read."""
    found: list[Address] = []
    problems: list[AddressError] = []
    rule = KIND_ADDRESSES.get(kind)
    handled: frozenset[str] = frozenset()
    if rule is not None:
        handled = rule.keys
        try:
            found += rule.addresses(params)
        except AddressError as exc:
            problems.append(exc)
    for key in GENERIC_ADDRESS_KEYS:
        if key in params and key not in handled:
            try:
                found += _generic(key, params[key])
            except AddressError as exc:
                problems.append(exc)
    return found, problems


@dataclass(frozen=True)
class ConnectionPolicy(SecretPolicy):
    """jane-kit's shared secret policy (R17: ``env:`` prefix, ``file:`` directory with pinned reading, ``vault:``
    refused) plus the network addresses a connection's adapter may contact."""

    host_allowlist: Sequence[str] = ()
    _allowed: HostAllowlist = field(init=False, repr=False, default=HostAllowlist())

    def __post_init__(self) -> None:
        object.__setattr__(self, "_allowed", HostAllowlist(tuple(self.host_allowlist)))

    # ------------------------------------------------------------------------------ hosts
    def host_allowed(self, address: Address) -> bool:
        return self._allowed.allows(address.host, address.port)

    def host_violations(self, kind: str, params: Mapping[str, Any]) -> list[FieldError]:
        found, problems = network_addresses(kind, params)
        errors = [FieldError(pointer=p.pointer, code=HOST_NOT_ALLOWED, message=str(p)) for p in problems]
        for address in found:
            if not self.host_allowed(address):
                errors.append(
                    FieldError(
                        pointer=address.pointer,
                        code=HOST_NOT_ALLOWED,
                        message=f"host {address} is not in JANE_STORAGE_CONNECTION_HOST_ALLOWLIST",
                    )
                )
        return errors

    def violations(self, doc: Any, pointer: str = "/secret_refs") -> list[FieldError]:
        """Policy violations of a Connection document (empty: allowed)."""
        doc = doc if isinstance(doc, Mapping) else {}
        errors = super().violations(doc.get("secret_refs") or {}, pointer)
        params = doc.get("params") or {}
        if not isinstance(params, Mapping):
            params = {}
        errors += self.host_violations(str(doc.get("kind", "")), params)
        return errors


def redact(text: str, values: Iterable[str]) -> str:
    """``text`` with every secret value replaced by ``***`` (longest first)."""
    for value in sorted({v for v in values if v}, key=len, reverse=True):
        text = text.replace(value, "***")
    return text
