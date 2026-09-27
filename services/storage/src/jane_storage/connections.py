"""Managed connections of the storage executor (ADR-0006) and the pool of opened adapters.

* Definitions (``connection.schema.json``: ``params`` + ``secret_refs``) come from a config file
  (``JANE_STORAGE_CONNECTIONS_FILE``, JSON/YAML: ``{"connections": [...]}``) and from
  ``PUT /v1/connections/{id}`` (the orchestrator syncs its registry; values are never secrets).
* ``secret_refs`` are resolved only here, in the executor's environment: ``env:VAR``,
  ``file:<path>``; ``vault:`` is not supported in v1 (reported as unresolved).
* :class:`AdapterPool` keeps one opened adapter per (connection, definition ETag, options) and closes
  adapters whose connection changed or was deleted.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from jane_contracts.storage_adapter import ResolvedConnection, StorageAdapter
from jane_kit.errors import FieldError, JaneError, NotFound, ValidationFailed

from .adapters import UnknownAdapter, create_adapter

__all__ = ["AdapterPool", "ConnectionRegistry", "SecretUnresolved", "StoredConnection"]

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
    ) -> None:
        self._items: dict[str, StoredConnection] = {}
        self._resolved: dict[str, ResolvedConnection] = {}
        self._validator = validator
        self._environ = environ

    # -------------------------------------------------------------------------------- definitions
    def load_file(self, path: Path) -> int:
        text = path.read_text(encoding="utf-8")
        data = yaml.safe_load(text) if path.suffix.lower() in {".yaml", ".yml"} else json.loads(text)
        items = data.get("connections", []) if isinstance(data, Mapping) else data
        for doc in items:
            self.put(dict(doc))
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

    def put(self, doc: dict[str, Any]) -> tuple[StoredConnection, bool]:
        self.validate(doc)
        cid = str(doc["connection_id"])
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

    # -------------------------------------------------------------------------------- secrets
    def _resolve_ref(self, ref: str) -> str | None:
        env: Mapping[str, str] = os.environ if self._environ is None else self._environ
        scheme, _, rest = ref.partition(":")
        if scheme == "env":
            return env.get(rest)
        if scheme == "file":
            try:
                return Path(rest).read_text(encoding="utf-8").strip()
            except OSError:
                return None
        return None  # vault: not supported in v1 (ADR-0006: optional provider)

    def secrets_resolved(self, connection_id: str) -> dict[str, bool]:
        stored = self.get(connection_id)
        if connection_id in self._resolved:
            return dict.fromkeys(self._resolved[connection_id].secrets, True)
        refs = stored.document.get("secret_refs") or {}
        return {name: self._resolve_ref(ref) is not None for name, ref in refs.items()}

    def resolve(self, connection_id: str) -> ResolvedConnection:
        stored = self.get(connection_id)
        if connection_id in self._resolved:
            return self._resolved[connection_id]
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
    """Opened adapters per connection; implements ``jane_storage.handler.AdapterProvider``."""

    def __init__(
        self, registry: ConnectionRegistry, default_options: Mapping[str, Any] | None = None
    ) -> None:
        self.registry = registry
        self.default_options = dict(default_options or {})
        self._open: MutableMapping[tuple[str, str, str], StorageAdapter] = {}
        self._schema_ready: set[tuple[str, str, str]] = set()
        self._lock = asyncio.Lock()

    def check(self, connection_id: str, adapter_kind: str) -> None:
        stored = self.registry.get(connection_id)
        if stored.kind != adapter_kind:
            raise ValidationFailed(
                f"connection {connection_id!r} is {stored.kind!r}, the package needs {adapter_kind!r}",
                errors=[FieldError(pointer="/connections/target", message="connection kind mismatch")],
            )

    async def adapter_for(
        self, connection_id: str, adapter_kind: str, options: Mapping[str, Any]
    ) -> StorageAdapter:
        self.check(connection_id, adapter_kind)
        stored = self.registry.get(connection_id)
        merged = {**self.default_options, **options}
        key = (connection_id, stored.etag, json.dumps(merged, sort_keys=True))
        async with self._lock:
            adapter = self._open.get(key)
            if adapter is None:
                await self._close_stale(connection_id, stored.etag)
                conn = self.registry.resolve(connection_id)
                try:
                    adapter = create_adapter(adapter_kind)
                except UnknownAdapter as exc:
                    raise ValidationFailed(
                        str(exc), errors=[FieldError(pointer="/handler", message=str(exc))]
                    ) from exc
                await adapter.open(conn, merged)
                self._open[key] = adapter
            if key not in self._schema_ready:
                await adapter.ensure_schema([])
                self._schema_ready.add(key)
            return adapter

    async def _close_stale(self, connection_id: str, etag: str | None) -> None:
        for key in [k for k in self._open if k[0] == connection_id and k[1] != etag]:
            adapter = self._open.pop(key)
            self._schema_ready.discard(key)
            await adapter.close()

    async def forget(self, connection_id: str) -> None:
        async with self._lock:
            await self._close_stale(connection_id, None)

    async def close(self) -> None:
        async with self._lock:
            for adapter in self._open.values():
                await adapter.close()
            self._open.clear()
            self._schema_ready.clear()
