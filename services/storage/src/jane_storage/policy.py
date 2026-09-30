"""Secret policy of storage connections (coordinator decision, same as WP-10 ``llm`` and WP-04
``telegram-collector``).

A connection decides *where* a resolved secret goes: the adapter logs in to ``params.host`` /
``params.endpoint`` with it, and connections arrive through ``PUT /v1/connections/{id}``. So this executor
restricts both ends:

* ``env:VAR`` — only variables starting with ``JANE_STORAGE_SECRET_ENV_PREFIX`` (default ``JANE_SECRET_``),
  so not ``PGPASSWORD`` or another service's configuration;
* ``file:<path>`` — only inside ``JANE_STORAGE_SECRET_FILES_DIR`` (default ``/run/secrets``); the path is
  resolved first (``..`` and symlinks do not escape) and the resolved file is the one read; ``vault:`` is
  disabled;
* every network address the adapter of the connection contacts — only hosts from
  ``JANE_STORAGE_CONNECTION_HOST_ALLOWLIST`` (``hostname`` = any port, ``hostname:port`` = that port; default
  empty, so every connection with a network address is rejected). :data:`KIND_ADDRESSES` knows the address
  parameters of the built-in adapters, including their defaults (``localhost``, the AWS regional endpoint) and
  hosts inside URIs; :data:`GENERIC_ADDRESS_KEYS` are checked for every kind, so an adapter unknown to the
  core cannot take a host from them unchecked.

Values that URL parsers read differently (userinfo ``@``, backslashes, whitespace, control characters,
percent-encoding in the host, trailing dots, IPv6 literals, Unix socket paths) are rejected instead of being
"normalized".
"""

from __future__ import annotations

import os
import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jane_kit.errors import FieldError

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
]

SECRET_REF_NOT_ALLOWED = "secret_ref_not_allowed"  # noqa: S105 - an error code, not a secret
HOST_NOT_ALLOWED = "host_not_allowed"

_LABEL = r"(?!-)[A-Za-z0-9_-]{1,63}(?<!-)"
_HOST_PORT = re.compile(rf"(?P<host>{_LABEL}(?:\.{_LABEL})*)(?::(?P<port>[0-9]{{1,5}}))?", re.ASCII)
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


def parse_host_port(value: object) -> tuple[str, int | None] | None:
    """Strict ``hostname[:port]`` → ``(lower-case host, port)``; anything else → ``None``."""
    if not isinstance(value, str) or len(value) > 300:
        return None
    m = _HOST_PORT.fullmatch(value)
    if m is None or len(m.group("host")) > 253:
        return None
    if m.group("port") is None:
        return m.group("host").lower(), None
    port = int(m.group("port"))
    if not 0 < port < 65536:
        return None
    return m.group("host").lower(), port


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


def _s3(params: Mapping[str, Any]) -> list[Address]:
    """``params.endpoint``; without it AWS: ``https://s3.<region>.amazonaws.com`` (region default ``us-east-1``).
    Virtual-hosted addressing contacts ``<bucket>.<endpoint host>``, a subdomain of the checked host."""
    if params.get("endpoint"):
        return _endpoint(params)
    region = params.get("region") or "us-east-1"
    if not isinstance(region, str) or not _REGION.fullmatch(region):
        raise AddressError("/params/region", "must be an AWS region name")
    return [Address("/params/region", f"s3.{region}.amazonaws.com", 443)]


def _minio(params: Mapping[str, Any]) -> list[Address]:
    """``params.endpoint`` (the adapter refuses to open without one)."""
    return _endpoint(params) if params.get("endpoint") else []


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


def _allow_entry(entry: str) -> tuple[str, int | None]:
    parsed = parse_host_port(entry.strip()) if isinstance(entry, str) else None
    if parsed is None:
        raise ValueError(f"host allowlist entry {entry!r} must be hostname or hostname:port")
    return parsed


@dataclass(frozen=True)
class ConnectionPolicy:
    env_prefix: str = "JANE_SECRET_"
    files_dir: Path | None = Path("/run/secrets")
    host_allowlist: Sequence[str] = ()
    _allowed: frozenset[tuple[str, int | None]] = field(init=False, repr=False, default=frozenset())

    def __post_init__(self) -> None:
        object.__setattr__(self, "_allowed", frozenset(_allow_entry(e) for e in self.host_allowlist))

    # ------------------------------------------------------------------------------ secret_refs
    def secret_file(self, ref: str) -> Path | None:
        """Resolved path of an allowed ``file:`` reference (``None`` if not allowed)."""
        if self.files_dir is None or not ref.startswith("file:") or not ref[5:]:
            return None
        try:
            path = Path(ref[5:]).resolve()
            base = self.files_dir.resolve()
        except (OSError, RuntimeError, ValueError):
            return None
        return path if path.is_relative_to(base) and path != base else None

    def ref_error(self, ref: str) -> str | None:
        """Why a secret reference is not allowed (``None`` if allowed)."""
        if ref.startswith("env:"):
            name = ref[4:]
            if not self.env_prefix or not name.startswith(self.env_prefix) or name == self.env_prefix:
                return f"env: references must name variables starting with {self.env_prefix!r}"
            return None
        if ref.startswith("file:"):
            if self.files_dir is None:
                return "file: references are disabled"
            if self.secret_file(ref) is None:
                return f"file: references must point to a file inside {self.files_dir}"
            return None
        if ref.startswith("vault:"):
            return "vault: references are not configured in this service"
        return "unknown secret reference scheme"

    def resolve(self, ref: str, environ: Mapping[str, str] | None = None) -> str | None:
        """Value of an allowed ``env:VAR`` / ``file:<path>``; ``None`` if missing, empty or not allowed."""
        if self.ref_error(ref) is not None:
            return None
        if ref.startswith("env:"):
            env = os.environ if environ is None else environ
            return env.get(ref[4:]) or None
        path = self.secret_file(ref)
        if path is None:
            return None
        try:
            return path.read_text(encoding="utf-8").strip() or None
        except (OSError, UnicodeDecodeError):
            return None

    # ------------------------------------------------------------------------------ hosts
    def host_allowed(self, address: Address) -> bool:
        return (address.host, None) in self._allowed or (
            address.port is not None and (address.host, address.port) in self._allowed
        )

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

    def violations(self, doc: Mapping[str, Any]) -> list[FieldError]:
        """Policy violations of a Connection document (empty: allowed)."""
        errors = []
        refs = doc.get("secret_refs") or {}
        if not isinstance(refs, Mapping):
            errors.append(
                FieldError(pointer="/secret_refs", code=SECRET_REF_NOT_ALLOWED, message="must be an object")
            )
            refs = {}
        for name, ref in refs.items():
            if msg := self.ref_error(str(ref)):
                errors.append(
                    FieldError(pointer=f"/secret_refs/{name}", code=SECRET_REF_NOT_ALLOWED, message=msg)
                )
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
