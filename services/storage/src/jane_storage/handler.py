"""Storage handler: ``HandlerInvocation`` → ``HandlerResult`` (handler.v1, ``handler_kind: storage``).

The package (:meth:`StorageHandler.resolve_package`) comes from, in this order: ``package_archive`` of the
request; the built-in catalog (installed adapter distributions; its ``package_id@version`` is authoritative, a
different ``digest`` is ``digest_mismatch`` without asking the registry); the registry, when configured
(:mod:`jane_storage.registry_packages`). Not found anywhere → 404; registry unreachable → 502
``upstream_unavailable`` (retryable).

Two phases:

* :meth:`StorageHandler.prepare` validates the request and raises :class:`jane_kit.errors.JaneError`
  (HTTP 404/422/502: unknown package or connection, digest mismatch, invalid params, input kind not
  accepted by the package, registry unavailable) — the call did not happen;
* :meth:`StorageHandler.execute` runs it; storage failures are ``status: failed`` results
  (``AdapterError(retryable=True)`` → ``failure.kind = connection_error``), never exceptions.

Delivery keys of the parts of one invocation — :mod:`jane_storage.keys`; ``test_mode`` validates and
returns ``simulated`` acks without touching the adapter.
"""

from __future__ import annotations

import json
import logging
import secrets
import time
from collections.abc import Callable, Collection, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol

from jsonschema import Draft202012Validator

from jane_contracts.storage_adapter import AdapterError, StorageAdapter
from jane_kit.clients import RetryPolicy
from jane_kit.errors import FieldError, JaneError, NotFound, ValidationFailed

from .codec import format_ts, utcnow
from .content import ContentError, ContentReader
from .engine import StorageEngine
from .formats import (
    RAW_FORMATS,
    InvalidFormat,
    build_data_object,
    build_raw_object,
    entities_format,
    raw_format,
)
from .keys import canonical_key, entity_delivery_key, key_digest, object_delivery_key
from .merge import InvalidRecord, validate_record
from .packages import (
    ArchiveLimits,
    DependencyNotAllowed,
    PackageCatalog,
    StoragePackage,
    package_from_archive,
)

__all__ = ["AdapterProvider", "PackageSource", "Prepared", "StorageHandler", "new_id"]

log = logging.getLogger(__name__)

WRITES_ACCEPT = {
    "raw": {"material"},
    "entities": {"entities"},
    "raw_and_entities": {"material", "entities"},
    "data": {"data"},
}
ADAPTER_PARAM_KEYS = ("prefix", "table_prefix", "schema")
"""Stage params that select the namespace inside the connection; passed to ``adapter.open`` options."""


def new_id(prefix: str) -> str:
    """Sortable opaque id: ``<prefix>_<ms timestamp hex><random>`` (``Id`` pattern)."""
    return f"{prefix}_{int(time.time() * 1000):012x}{secrets.token_hex(8)}"


class AdapterProvider(Protocol):
    def check(self, connection_id: str, adapter_kind: str) -> None:
        """Raise NotFound (unknown connection) or ValidationFailed (kind mismatch) before execution."""
        ...

    async def adapter_for(
        self, connection_id: str, adapter_kind: str, options: Mapping[str, Any]
    ) -> StorageAdapter:
        """Opened adapter for the connection (raises NotFound / ValidationFailed / AdapterError)."""
        ...


class PackageSource(Protocol):
    async def get(self, ref: Mapping[str, Any]) -> StoragePackage:
        """Verified package of ``ref`` (``package_id``, ``version``, digest when given) or a JaneError."""
        ...


@dataclass
class Prepared:
    invocation: dict[str, Any]
    package: StoragePackage
    params: dict[str, Any]
    connection_id: str | None
    options: dict[str, Any]
    raw_format: str
    test_mode: bool
    started_at: datetime
    invocation_id: str = field(default_factory=lambda: new_id("inv"))


class _Failure(Exception):
    def __init__(
        self, kind: str, message: str, retryable: bool, details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message)
        self.kind = kind
        self.retryable = retryable
        self.details = details


def _schema_errors(validator: Draft202012Validator, instance: Any, prefix: str = "") -> list[FieldError]:
    errors = []
    for err in sorted(validator.iter_errors(instance), key=lambda e: list(e.path)):
        pointer = prefix + "".join(f"/{p}" for p in err.path)
        errors.append(FieldError(pointer=pointer or "/", message=err.message[:500]))
    return errors


def input_refs(inputs: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    refs = []
    for item in inputs:
        ref: dict[str, Any] = {"kind": item["kind"]}
        material = item.get("material")
        if isinstance(material, Mapping):
            ref["material_id"] = material.get("material_id")
            ref["observation_id"] = material.get("observation_id")
            if sha := (material.get("revision") or {}).get("content_sha256"):
                ref["content_sha256"] = sha
        if item.get("from_invocation_id"):
            ref["from_invocation_id"] = item["from_invocation_id"]
        refs.append({k: v for k, v in ref.items() if v is not None})
    return refs


class StorageHandler:
    def __init__(
        self,
        catalog: PackageCatalog,
        adapters: AdapterProvider,
        content: ContentReader,
        *,
        retries: RetryPolicy | None = None,
        request_validator: Callable[[dict[str, Any]], list[FieldError]] | None = None,
        clock: Callable[[], datetime] = utcnow,
        registry: PackageSource | None = None,
        archive_limits: ArchiveLimits | None = None,
        installed_adapters: Collection[str] | None = None,
    ) -> None:
        self.catalog = catalog
        self.adapters = adapters
        self.content = content
        self.retries = retries or RetryPolicy()
        self.request_validator = request_validator
        self._clock = clock
        self.registry = registry
        """Third package source after ``package_archive`` and the built-in catalog (None: no registry)."""
        self.archive_limits = archive_limits or ArchiveLimits()
        self.installed_adapters = None if installed_adapters is None else frozenset(installed_adapters)
        """Adapters a package from an archive or the registry may name (None: not checked here)."""

    # ------------------------------------------------------------------------------ prepare
    async def _archive_package(self, archive_ref: Mapping[str, Any]) -> StoragePackage:
        try:
            data = await self.content.read(archive_ref)
            if len(data) > self.archive_limits.max_archive_bytes:
                raise ValueError(
                    f"package archive is {len(data)} bytes, limit "
                    f"packages.max_archive_bytes={self.archive_limits.max_archive_bytes}"
                )
            return package_from_archive(data, self.archive_limits)
        except DependencyNotAllowed as exc:
            raise JaneError(
                f"package_archive: {exc}",
                code="dependency_not_allowed",
                errors=[FieldError(pointer="/package_archive", message=str(exc))],
            ) from exc
        except (ContentError, ValueError) as exc:
            raise ValidationFailed(
                f"package_archive: {exc}",
                errors=[FieldError(pointer="/package_archive", message=str(exc))],
            ) from exc

    async def resolve_package(
        self, ref: Mapping[str, Any], archive_ref: Mapping[str, Any] | None = None
    ) -> StoragePackage:
        """The package of ``ref``: ``archive_ref`` (``package_archive``), else built in, else the registry."""
        builtin = False
        if archive_ref is not None:
            pkg = await self._archive_package(archive_ref)
            if (pkg.package_id, pkg.version) != (ref.get("package_id"), ref.get("version")):
                raise ValidationFailed(
                    "package_archive does not contain the requested package version",
                    errors=[
                        FieldError(pointer="/handler", message=f"archive has {pkg.package_id}@{pkg.version}")
                    ],
                )
        elif (found := self.catalog.get(str(ref.get("package_id")), str(ref.get("version")))) is not None:
            pkg, builtin = found, True
        elif self.registry is not None:
            pkg = await self.registry.get(ref)
        else:
            raise NotFound(f"{ref.get('package_id')}@{ref.get('version')}")
        if ref.get("digest") and ref["digest"] != pkg.digest:
            raise JaneError(
                f"requested {ref['digest']}, package has {pkg.digest}",
                code="digest_mismatch",
                retryable=False,
            )
        if not builtin and self.installed_adapters is not None and pkg.adapter not in self.installed_adapters:
            raise ValidationFailed(
                f"{pkg.package_id}@{pkg.version} needs storage adapter {pkg.adapter!r}, which is not installed",
                errors=[
                    FieldError(
                        pointer="/handler",
                        message=f"adapter {pkg.adapter!r} not installed ({sorted(self.installed_adapters)})",
                    )
                ],
            )
        return pkg

    async def prepare(self, invocation: dict[str, Any], *, package: StoragePackage | None = None) -> Prepared:
        """Validate ``invocation``; ``package`` — already resolved (test runs), else :meth:`resolve_package`."""
        started = self._clock()
        if self.request_validator is not None:
            errors = self.request_validator(invocation)
            if errors:
                raise ValidationFailed("invalid HandlerInvocation", errors=errors)
        pkg = package or await self.resolve_package(invocation["handler"], invocation.get("package_archive"))
        params = dict(invocation.get("params") or {})
        if pkg.params_schema is not None:
            errors = _schema_errors(Draft202012Validator(pkg.params_schema), params, "/params")
            if errors:
                raise ValidationFailed("params do not match params_schema of the package", errors=errors)
        accepted = WRITES_ACCEPT.get(pkg.writes, set()) & (
            set(pkg.accepts) or WRITES_ACCEPT.get(pkg.writes, set())
        )
        bad = [
            FieldError(
                pointer=f"/inputs/{i}/kind", message=f"{pkg.package_id} does not accept {item['kind']!r}"
            )
            for i, item in enumerate(invocation["inputs"])
            if item["kind"] not in accepted
        ]
        if bad:
            raise ValidationFailed("input kind not accepted by the storage package", errors=bad)
        for i, item in enumerate(invocation["inputs"]):
            for j, record in enumerate(item.get("entities") or ()):
                try:
                    validate_record(record)
                except InvalidRecord as exc:
                    bad.append(FieldError(pointer=f"/inputs/{i}/entities/{j}", message=str(exc)))
        if bad:
            raise ValidationFailed("invalid EntityRecord", errors=bad)
        fmt = raw_format(params, pkg.entry)
        if fmt not in RAW_FORMATS:
            raise ValidationFailed(
                "unknown raw format", errors=[FieldError(pointer="/params/format/raw", message=fmt)]
            )
        test_mode = bool((invocation.get("context") or {}).get("test_mode", False))
        connection_id = (invocation.get("connections") or {}).get("target")
        if connection_id is None and not test_mode:
            raise ValidationFailed(
                "connections.target is required",
                errors=[
                    FieldError(
                        pointer="/connections/target", message="required (required_connections: target)"
                    )
                ],
            )
        if connection_id is not None and not test_mode:
            self.adapters.check(connection_id, pkg.adapter)
        options = {k: params[k] for k in ADAPTER_PARAM_KEYS if k in params}
        options["entities_format"] = entities_format(params, pkg.entry)
        return Prepared(
            invocation=invocation,
            package=pkg,
            params=params,
            connection_id=connection_id,
            options=options,
            raw_format=fmt,
            test_mode=test_mode,
            started_at=started,
        )

    # ------------------------------------------------------------------------------ execute
    def _result(self, prep: Prepared, status: str, **extra: Any) -> dict[str, Any]:
        inv = prep.invocation
        result: dict[str, Any] = {
            "invocation_id": prep.invocation_id,
            "handler": prep.package.ref,
            "handler_kind": "storage",
            "status": status,
            "inputs": input_refs(inv["inputs"]),
            "delivery_key": inv["delivery"]["delivery_key"],
            "test_mode": prep.test_mode,
            "started_at": format_ts(prep.started_at),
        }
        result.update(extra)
        result["finished_at"] = format_ts(self._clock())
        return result

    async def _entities_of(self, item: Mapping[str, Any]) -> list[dict[str, Any]]:
        if "entities" in item:
            return [dict(e) for e in item["entities"]]
        raw = await self.content.read(item["entities_ref"])
        try:
            records = json.loads(raw)
        except ValueError as exc:
            raise _Failure("schema_mismatch", f"entities_ref is not JSON: {exc}", False) from exc
        if not isinstance(records, list):
            raise _Failure("schema_mismatch", "entities_ref must be a JSON array of EntityRecord", False)
        for n, record in enumerate(records):
            try:
                validate_record(record)
            except (InvalidRecord, TypeError, AttributeError) as exc:
                raise _Failure("schema_mismatch", f"entities_ref[{n}]: {exc}", False) from exc
        return records

    async def _data_of(self, item: Mapping[str, Any]) -> Any:
        if "data" in item:
            return item["data"]
        raw = await self.content.read(item["data_ref"])
        try:
            return json.loads(raw)
        except ValueError as exc:
            raise _Failure("schema_mismatch", f"data_ref is not JSON: {exc}", False) from exc

    def _simulated(self, prep: Prepared, dk: str, **part: Any) -> dict[str, Any]:
        target: dict[str, Any] = {"adapter": prep.package.adapter}
        if prep.connection_id:
            target["connection_id"] = prep.connection_id
        return {"status": "simulated", "target": target, **part, "delivery_key": dk}

    async def execute(self, prep: Prepared) -> dict[str, Any]:
        inv = prep.invocation
        delivery_key = str(inv["delivery"]["delivery_key"])
        source_id = ((inv.get("context") or {}).get("trace") or {}).get("source_id")
        writes: list[dict[str, Any]] = []
        engine: StorageEngine | None = None
        try:
            if not prep.test_mode:
                assert prep.connection_id is not None
                adapter = await self.adapters.adapter_for(
                    prep.connection_id, prep.package.adapter, prep.options
                )
                engine = StorageEngine(
                    adapter, connection_id=prep.connection_id, retries=self.retries, clock=self._clock
                )
            n_entity = n_raw = n_data = 0
            for item in inv["inputs"]:
                kind = item["kind"]
                if kind == "material":
                    material = item["material"]
                    content = await self.content.read(material["content"])
                    obj = build_raw_object(material, content, prep.raw_format)
                    dk = object_delivery_key(delivery_key, n_raw, "raw")
                    n_raw += 1
                    if engine is None:
                        writes.append(
                            self._simulated(
                                prep,
                                dk,
                                object={
                                    "object_id": "obj_simulated",
                                    "adapter": prep.package.adapter,
                                    "media_type": obj.media_type,
                                    "size_bytes": len(obj.content),
                                    "sha256": obj.sha256,
                                    "locator": {"object_key": obj.object_key},
                                },
                            )
                        )
                    else:
                        writes.append(await engine.store_object(obj, dk))
                elif kind == "entities":
                    for record in await self._entities_of(item):
                        dk = entity_delivery_key(delivery_key, n_entity)
                        n_entity += 1
                        if engine is None:
                            fields = sorted([*record["fields"], *(record.get("cleared") or ())])
                            writes.append(
                                self._simulated(
                                    prep,
                                    dk,
                                    entity={
                                        "entity_type": record["entity_type"],
                                        "canonical_key": canonical_key(record["key"]),
                                    },
                                    applied_fields=fields,
                                    stale_fields=[],
                                )
                            )
                        else:
                            writes.append(await engine.store_entity(record, dk))
                else:  # data
                    data = await self._data_of(item)
                    obj = build_data_object(
                        data, delivery_key_digest=key_digest(delivery_key), index=n_data, source_id=source_id
                    )
                    dk = object_delivery_key(delivery_key, n_data, "data")
                    n_data += 1
                    if engine is None:
                        writes.append(
                            self._simulated(
                                prep,
                                dk,
                                object={
                                    "object_id": "obj_simulated",
                                    "adapter": prep.package.adapter,
                                    "media_type": obj.media_type,
                                    "size_bytes": len(obj.content),
                                    "sha256": obj.sha256,
                                },
                            )
                        )
                    else:
                        writes.append(await engine.store_object(obj, dk))
        except AdapterError as exc:
            kind = "connection_error" if exc.retryable else "execution_error"
            log.warning("storage adapter failed", extra={"error": str(exc), "retryable": exc.retryable})
            return self._failed(prep, kind, str(exc), exc.retryable, writes)
        except ContentError as exc:
            return self._failed(prep, exc.kind, str(exc), exc.retryable, writes)
        except InvalidFormat as exc:
            return self._failed(prep, "invalid_params", str(exc), False, writes)
        except _Failure as exc:
            return self._failed(prep, exc.kind, str(exc), exc.retryable, writes, exc.details)
        status = "success" if writes else "empty"
        duplicate = bool(writes) and all(w["status"] == "duplicate" for w in writes)
        return self._result(prep, status, output={"writes": writes}, duplicate=duplicate)

    def _failed(
        self,
        prep: Prepared,
        kind: str,
        message: str,
        retryable: bool,
        writes: list[dict[str, Any]],
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        failure: dict[str, Any] = {"kind": kind, "message": message[:4000], "retryable": retryable}
        if details:
            failure["details"] = details
        extra: dict[str, Any] = {"failure": failure, "duplicate": False}
        if writes:
            extra["output"] = {"writes": writes}
            extra["diagnostics"] = {
                "messages": [
                    {
                        "level": "warning",
                        "code": "storage.partial",
                        "message": f"{len(writes)} write(s) completed before the failure; a retry with the same "
                        "delivery_key skips them as duplicates",
                    }
                ]
            }
        return self._result(prep, "failed", **extra)

    async def invoke(self, invocation: dict[str, Any]) -> dict[str, Any]:
        """``prepare`` + ``execute`` (JaneError from ``prepare`` propagates)."""
        return await self.execute(await self.prepare(invocation))
