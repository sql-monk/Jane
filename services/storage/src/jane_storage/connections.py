"""Managed connections of the storage executor (ADR-0006) and the pool of opened adapters.

* Definitions (``connection.schema.json``: ``params`` + ``secret_refs``) come from a config file
  (``JANE_STORAGE_CONNECTIONS_FILE``, JSON/YAML: ``{"connections": [...]}``) and from
  ``PUT /v1/connections/{id}`` (the orchestrator syncs its registry; values are never secrets).
* ``secret_refs`` are resolved only here, in the executor's environment, under the secret policy
  (:mod:`jane_storage.policy`): ``env:`` only with the configured prefix, ``file:`` only inside the secrets
  directory, ``vault:`` disabled, and every network address of the connection from the host allowlist.
  ``PUT`` of a violating connection → 422 (``secret_ref_not_allowed`` / ``host_not_allowed``); a violating
  connection from the config file (or stored bypassing the API) is kept, but gets no secrets and is rejected
  (422) when used.
* :class:`AdapterPool` keeps one opened adapter per (connection, definition ETag, options) and closes
  adapters whose connection changed or was deleted. Adapter errors raised while opening are redacted: the
  resolved secret values of the connection never reach responses or logs.
"""

from __future__ import annotations

import asyncio
import builtins
import hashlib
import json
import logging
import re
from collections.abc import AsyncIterator, Iterable, Mapping, MutableMapping
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from jane_contracts.storage_adapter import AdapterError, ResolvedConnection, StorageAdapter
from jane_kit.errors import FieldError, JaneError, NotFound, ValidationFailed

from .adapters import UnknownAdapter, create_adapter
from .policy import ConnectionPolicy, redact

__all__ = ["AdapterPool", "ConnectionRegistry", "SecretUnresolved", "StoredConnection"]

log = logging.getLogger("jane_storage.connections")

_SECRET_NAME = re.compile(r"(pass(word)?|secret|token|api[_-]?key|private[_-]?key|credential)", re.I)
_SECRET_VALUE = re.compile(
    r"^(AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|[a-z]+://[^/\s:]+:[^@/\s]+@)", re.M
)


class SecretUnresolved(JaneError):
    """A secret reference cannot be resolved in this executor's environment."""

    code = "upstream_unavailable"


@dataclass(frozen=True)
class StoredConnection:
    document: dict[str, Any]
    etag: str

    @property
    def connection_id(self) -> str:
        return str(self.document["connection_id"])

    @property
    def kind(self) -> str:
        return str(self.document["kind"])


def _etag(doc: Mapping[str, Any]) -> str:
    return '"' + hashlib.sha256(json.dumps(doc, sort_keys=True).encode()).hexdigest()[:32] + '"'


def _secret_like(params: Mapping[str, Any], prefix: str = "/params") -> list[FieldError]:
    found = []
    for name, value in params.items():
        pointer = f"{prefix}/{name}"
        if isinstance(value, Mapping):
            found += _secret_like(value, pointer)
        elif isinstance(value, str) and (_SECRET_NAME.search(name) or _SECRET_VALUE.search(value)):
            found.append(FieldError(pointer=pointer, message="looks like a secret; use secret_refs"))
    return found


class ConnectionRegistry:
    def __init__(
        self,
        validator: Any = None,
        environ: Mapping[str, str] | None = None,
        policy: ConnectionPolicy | None = None,
    ) -> None:
        self._items: dict[str, StoredConnection] = {}
        self._resolved: dict[str, ResolvedConnection] = {}
        self._validator = validator
        self._environ = environ
        self.policy = policy if policy is not None else ConnectionPolicy()

    # -------------------------------------------------------------------------------- definitions
    def load_file(self, path: Path) -> int:
        """Connections of the config file. A policy violation does not stop the service (the connection is
        kept, gets no secrets and is rejected when used); other validation errors do."""
        text = path.read_text(encoding="utf-8")
        data = yaml.safe_load(text) if path.suffix.lower() in {".yaml", ".yml"} else json.loads(text)
        items = data.get("connections", []) if isinstance(data, Mapping) else data
        for doc in items:
            self.put(dict(doc), enforce_policy=False)
        return len(items)

    def validate(self, doc: Mapping[str, Any]) -> None:
        if self._validator is not None:
            errors = [
                FieldError(pointer="".join(f"/{p}" for p in e.path) or "/", message=e.message[:500])
                for e in self._validator.iter_errors(doc)
            ]
            if errors:
                raise ValidationFailed("invalid Connection", errors=errors)
        secrets = _secret_like(doc.get("params") or {})
        if secrets:
            raise JaneError("secret-like values in params", code="secret_detected", errors=secrets)

    def put(self, doc: dict[str, Any], *, enforce_policy: bool = True) -> tuple[StoredConnection, bool]:
        """Store a definition. ``enforce_policy`` (the API): a secret-policy violation → 422 and nothing is
        stored; otherwise (config file) the connection is stored with a warning and rejected when used."""
        self.validate(doc)
        cid = str(doc["connection_id"])
        violations = self.policy.violations(doc)
        if violations and enforce_policy:
            raise ValidationFailed(
                "connection violates the secret policy of this executor", errors=violations
            )
        if violations:
            log.warning(
                "connection violates the secret policy: it gets no secrets and is rejected when used",
                extra={
                    "connection_id": cid,
                    "violations": [f"{v.pointer} ({v.code}): {v.message}" for v in violations],
                },
            )
        created = cid not in self._items
        stored = StoredConnection(document=doc, etag=_etag(doc))
        self._items[cid] = stored
        return stored, created

    def add_resolved(self, conn: ResolvedConnection) -> StoredConnection:
        """Register an already resolved connection (embedding, tests of adapters)."""
        doc = {"connection_id": conn.connection_id, "kind": conn.kind, "params": dict(conn.params)}
        stored = StoredConnection(document=doc, etag=_etag({**doc, "resolved": True}))
        self._items[conn.connection_id] = stored
        self._resolved[conn.connection_id] = conn
        return stored

    def get(self, connection_id: str) -> StoredConnection:
        try:
            return self._items[connection_id]
        except KeyError:
            raise NotFound(f"connection {connection_id!r} is not known to this executor") from None

    def delete(self, connection_id: str) -> None:
        self.get(connection_id)
        del self._items[connection_id]
        self._resolved.pop(connection_id, None)

    def list(self) -> list[StoredConnection]:
        return [self._items[k] for k in sorted(self._items)]

    # -------------------------------------------------------------------------------- policy
    def policy_errors(self, connection_id: str) -> builtins.list[FieldError]:
        """Secret-policy violations of a stored connection (``add_resolved`` ones are the embedder's)."""
        stored = self.get(connection_id)
        if connection_id in self._resolved:
            return []
        return self.policy.violations(stored.document)

    def ensure_allowed(
        self, connection_id: str, *, pointer: str | None = None, parameter: str | None = None
    ) -> None:
        """422 (``secret_ref_not_allowed`` / ``host_not_allowed``) if the connection violates the policy."""
        errors = self.policy_errors(connection_id)
        if errors:
            raise ValidationFailed(
                f"connection {connection_id!r} violates the secret policy of this executor; it gets no secrets",
                errors=[
                    FieldError(
                        pointer=pointer,
                        parameter=parameter,
                        code=e.code,
                        message=f"connection {connection_id} {e.pointer}: {e.message}",
                    )
                    for e in errors
                ],
            )

    # -------------------------------------------------------------------------------- secrets
    def _resolve_ref(self, ref: str) -> str | None:
        """Value of an allowed reference (``None``: missing, empty or not allowed; ``vault:`` is disabled)."""
        return self.policy.resolve(str(ref), self._environ)

    def secrets_resolved(self, connection_id: str) -> dict[str, bool]:
        """Name → resolvable (never values); all ``False`` for a connection that violates the policy."""
        stored = self.get(connection_id)
        if connection_id in self._resolved:
            return dict.fromkeys(self._resolved[connection_id].secrets, True)
        refs = stored.document.get("secret_refs") or {}
        if self.policy_errors(connection_id):
            return dict.fromkeys(refs, False)
        return {name: self._resolve_ref(ref) is not None for name, ref in refs.items()}

    def secret_values(self, connection_id: str) -> builtins.list[str]:
        """Resolved values of the connection — only to redact error messages."""
        if connection_id in self._resolved:
            return list(self._resolved[connection_id].secrets.values())
        if connection_id not in self._items or self.policy_errors(connection_id):
            return []
        refs = self._items[connection_id].document.get("secret_refs") or {}
        return [v for ref in refs.values() if (v := self._resolve_ref(ref)) is not None]

    def resolve(self, connection_id: str) -> ResolvedConnection:
        stored = self.get(connection_id)
        if connection_id in self._resolved:
            return self._resolved[connection_id]
        self.ensure_allowed(connection_id)
        values: dict[str, str] = {}
        missing = []
        for name, ref in (stored.document.get("secret_refs") or {}).items():
            value = self._resolve_ref(ref)
            if value is None:
                missing.append(name)
            else:
                values[name] = value
        if missing:
            raise SecretUnresolved(
                f"connection {connection_id!r}: secret(s) {sorted(missing)} cannot be resolved in this executor",
                retryable=False,
            )
        return ResolvedConnection(
            connection_id=connection_id,
            kind=stored.kind,
            params=dict(stored.document.get("params") or {}),
            secrets=values,
        )


class AdapterPool:
    """Opened adapters per connection; implements ``jane_storage.handler.AdapterProvider``.

    One adapter per (connection, definition ETag, options). A changed definition (``PUT``) or a deleted connection
    *retires* the connection's adapters: new work opens a new adapter, while work that already holds one through
    :meth:`lease` finishes on it; a retired adapter is closed when its last lease ends. An unchanged ``PUT`` keeps
    the open adapter.
    """

    def __init__(
        self,
        registry: ConnectionRegistry,
        default_options: Mapping[str, Any] | None = None,
        *,
        connection_first: Iterable[str] = (),
    ) -> None:
        self.registry = registry
        self.default_options = dict(default_options or {})
        self.connection_first = frozenset(connection_first)
        """Default options that are only defaults: a connection whose ``params`` set the same name keeps its value."""
        self._open: MutableMapping[tuple[str, str, str], StorageAdapter] = {}
        self._schema_ready: set[tuple[str, str, str]] = set()
        self._users: dict[int, int] = {}
        """Leases in progress per adapter (``id(adapter)``)."""
        self._retired: dict[int, StorageAdapter] = {}
        """Adapters no longer handed out, closed when their last lease ends."""
        self._lock = asyncio.Lock()

    def check(self, connection_id: str, adapter_kind: str) -> None:
        stored = self.registry.get(connection_id)
        if stored.kind != adapter_kind:
            raise ValidationFailed(
                f"connection {connection_id!r} is {stored.kind!r}, the package needs {adapter_kind!r}",
                errors=[FieldError(pointer="/connections/target", message="connection kind mismatch")],
            )
        self.registry.ensure_allowed(connection_id, pointer="/connections/target")

    async def _acquire(
        self, connection_id: str, adapter_kind: str, options: Mapping[str, Any], *, hold: bool
    ) -> StorageAdapter:
        self.check(connection_id, adapter_kind)
        stored = self.registry.get(connection_id)
        params = stored.document.get("params") or {}
        defaults = {
            k: v for k, v in self.default_options.items() if k not in self.connection_first or k not in params
        }
        merged = {**defaults, **options}
        key = (connection_id, stored.etag, json.dumps(merged, sort_keys=True))
        async with self._lock:
            adapter = self._open.get(key)
            if adapter is None:
                await self._retire(connection_id, keep=stored.etag)
                conn = self.registry.resolve(connection_id)
                try:
                    adapter = create_adapter(adapter_kind)
                except UnknownAdapter as exc:
                    raise ValidationFailed(
                        str(exc), errors=[FieldError(pointer="/handler", message=str(exc))]
                    ) from exc
                try:
                    await adapter.open(conn, merged)
                except AdapterError as exc:
                    raise self._redacted(exc, conn.secrets.values()) from None
                self._open[key] = adapter
            if key not in self._schema_ready:
                try:
                    await adapter.ensure_schema([])
                except AdapterError as exc:
                    raise self._redacted(exc, self.registry.secret_values(connection_id)) from None
                self._schema_ready.add(key)
            if hold:
                self._users[id(adapter)] = self._users.get(id(adapter), 0) + 1
            return adapter

    async def adapter_for(
        self, connection_id: str, adapter_kind: str, options: Mapping[str, Any]
    ) -> StorageAdapter:
        """The opened adapter without a lease: a retirement may close it under the caller (prefer :meth:`lease`)."""
        return await self._acquire(connection_id, adapter_kind, options, hold=False)

    @asynccontextmanager
    async def lease(
        self, connection_id: str, adapter_kind: str, options: Mapping[str, Any]
    ) -> AsyncIterator[StorageAdapter]:
        """The opened adapter for the duration of the block: retiring it waits for the block to end."""
        adapter = await self._acquire(connection_id, adapter_kind, options, hold=True)
        try:
            yield adapter
        finally:
            await self._release(adapter)

    async def _release(self, adapter: StorageAdapter) -> None:
        async with self._lock:
            left = self._users.get(id(adapter), 1) - 1
            if left > 0:
                self._users[id(adapter)] = left
                return
            self._users.pop(id(adapter), None)
            retired = self._retired.pop(id(adapter), None)
        if retired is not None:
            await self._close_quietly(retired)

    @staticmethod
    def _redacted(exc: AdapterError, secrets: Iterable[str]) -> AdapterError:
        """Driver messages may echo a login or a connection string: never pass secret values on."""
        return AdapterError(redact(str(exc), secrets), retryable=exc.retryable)

    @staticmethod
    async def _close_quietly(adapter: StorageAdapter) -> None:
        try:
            await adapter.close()
        except Exception:  # a retired adapter: nothing waits for it
            log.warning("closing a retired adapter failed", exc_info=True)

    async def _retire(self, connection_id: str, keep: str | None) -> None:
        """Stop handing out the connection's adapters of another definition (``keep``: the current ETag); close
        the ones nobody holds now, the others when their last lease ends. Caller holds the lock."""
        for key in [k for k in self._open if k[0] == connection_id and k[1] != keep]:
            adapter = self._open.pop(key)
            self._schema_ready.discard(key)
            if self._users.get(id(adapter), 0) > 0:
                self._retired[id(adapter)] = adapter
            else:
                await self._close_quietly(adapter)

    async def forget(self, connection_id: str) -> None:
        """The connection changed or was deleted: retire all its adapters (in-flight work finishes first)."""
        async with self._lock:
            await self._retire(connection_id, None)

    async def close(self) -> None:
        async with self._lock:
            for adapter in [*self._open.values(), *self._retired.values()]:
                await self._close_quietly(adapter)
            self._open.clear()
            self._retired.clear()
            self._users.clear()
            self._schema_ready.clear()
