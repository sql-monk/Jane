"""Executing a ``HandlerInvocation``: prepare (package, dependencies, params, inputs, limits), run in the
sandbox, turn the runner output into a ``HandlerResult`` with the four states of TZ §9.

``prepare`` raises :class:`JaneError` (HTTP errors: the call did not happen); once the sandbox ran, every
problem is a ``HandlerResult`` with ``status: failed`` and ``failure.kind``.
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from fnmatch import fnmatch
from typing import Any

from jane_extractor_sdk.entities import to_entity_record
from jane_extractor_sdk.package import PackageError, iter_package_files, read_package_file
from jane_extractor_sdk.runner import PROTOCOL_VERSION
from jane_extractor_sdk.testing import apply_param_defaults
from jane_kit.errors import FieldError, JaneError, ServiceUnavailable, ValidationFailed

from .packages import ContentFetcher, LoadedPackage, PackageStore
from .profiles import check_dependencies, load_profiles
from .sandbox import Bundle, SandboxBackend, SandboxOutcome, SandboxUnavailable
from .schemas import ContractSchemas, validate_instance
from .settings import DEFAULT_PROFILE, ServiceLimits, Settings, request_layer, resolve_service_limits

__all__ = ["Executor", "PreparedInvocation", "new_invocation_id", "now_rfc3339"]

log = logging.getLogger(__name__)

SUPPORTED_KINDS = ("extractor", "transform")
MAX_STDERR_IN_RESULT = 16_000


def now_rfc3339() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def new_invocation_id() -> str:
    return f"inv_{uuid.uuid4().hex}"


@dataclass
class PreparedInvocation:
    invocation_id: str
    package: LoadedPackage
    params: dict[str, Any]
    inputs: list[dict[str, Any]]
    contents: list[bytes | None]
    limits: ServiceLimits
    image: str
    test_mode: bool = False
    delivery_key: str | None = None
    context: dict[str, Any] = field(default_factory=dict)


class _Invalid(ValueError):
    def __init__(self, pointer: str, message: str) -> None:
        super().__init__(message)
        self.pointer = pointer
        self.message = message


class Executor:
    def __init__(
        self,
        settings: Settings,
        store: PackageStore,
        fetcher: ContentFetcher,
        backend: SandboxBackend,
        schemas: ContractSchemas,
    ) -> None:
        self.settings = settings
        self.store = store
        self.fetcher = fetcher
        self.backend = backend
        self.schemas = schemas
        base = resolve_service_limits(settings)
        self._slots = asyncio.Semaphore(base.limits.concurrency.max_parallel_invocations)

    # ------------------------------------------------------------------ prepare

    def check_package(self, package: LoadedPackage) -> str:
        """Kind, entry, access and dependencies; returns the sandbox image of the runtime profile."""
        manifest = package.manifest
        errors = self.schemas.errors("package-manifest.schema.json", manifest)
        if errors:
            raise ValidationFailed(
                "package manifest is invalid",
                errors=[FieldError(pointer=e["pointer"] or "/", message=e["message"]) for e in errors[:20]],
            )
        kind = manifest.get("kind")
        entry = manifest.get("entry") or {}
        if kind not in SUPPORTED_KINDS or entry.get("runtime") != "python":
            raise ValidationFailed(
                f"handler-runtime executes Python packages of kinds {SUPPORTED_KINDS}; got kind={kind!r}",
                details={"kind": kind},
            )
        access = manifest.get("access") or {}
        if access.get("network", "none") != "none":
            raise ValidationFailed(
                "network access (access.network=allowlist) is not permitted by the platform policy of this runtime",
                details={"access": access},
            )
        deps = manifest.get("dependencies") or {}
        profile_name = str(deps.get("runtime_profile") or DEFAULT_PROFILE)
        profile = load_profiles().get(profile_name)
        image = self.settings.profile_images.get(profile_name)
        if profile is None or image is None:
            raise JaneError(
                f"runtime profile {profile_name} is not available in this runtime",
                code="dependency_not_allowed",
                details={"runtime_profile": profile_name, "available": sorted(load_profiles())},
            )
        problems = check_dependencies(profile, list(deps.get("python") or []))
        if problems:
            raise JaneError(
                problems[0].message,
                code="dependency_not_allowed",
                details={"runtime_profile": profile_name, "problems": [p.__dict__ for p in problems]},
            )
        return image

    def _json_file(self, package: LoadedPackage, name: str) -> Any:
        try:
            return json.loads(read_package_file(package.root, name))
        except (PackageError, ValueError) as exc:
            raise ValidationFailed(f"package file {name}: {exc}") from exc

    def check_params(self, package: LoadedPackage, params: Mapping[str, Any] | None) -> dict[str, Any]:
        name = package.manifest.get("params_schema")
        schema = self._json_file(package, str(name)) if name else None
        effective = apply_param_defaults(schema, params)
        if schema is not None:
            errors = validate_instance(schema, effective, prefix="/params")
            if errors:
                raise ValidationFailed(
                    "params do not match params_schema of the package",
                    errors=[FieldError(pointer=e["pointer"], message=e["message"]) for e in errors[:20]],
                )
        return effective

    def check_input(self, package: LoadedPackage, index: int, item: Mapping[str, Any]) -> None:
        contract = package.manifest.get("input") or {}
        accepts = contract.get("accepts") or ["material"]
        kind = item.get("kind")
        if kind not in accepts:
            raise ValidationFailed(
                f"input kind {kind!r} is not accepted by the package (accepts {accepts})",
                errors=[FieldError(pointer=f"/inputs/{index}/kind", message="not accepted")],
            )
        media_types = contract.get("media_types")
        if kind == "material" and media_types:
            media = str(((item.get("material") or {}).get("format") or {}).get("media_type", ""))
            if not any(fnmatch(media, pattern) for pattern in media_types):
                raise ValidationFailed(
                    f"media type {media!r} is not supported by the package ({media_types})",
                    errors=[
                        FieldError(
                            pointer=f"/inputs/{index}/material/format/media_type", message="unsupported"
                        )
                    ],
                )

    async def _resolve_input(
        self, item: dict[str, Any], limits: ServiceLimits
    ) -> tuple[dict[str, Any], bytes | None]:
        limit = limits.packages.max_input_bytes
        if item.get("kind") == "material":
            content = (item.get("material") or {}).get("content") or {}
            data = await self.fetcher.read(content, limit)
            return item, (data if content.get("kind") == "blob" else None)
        resolved = dict(item)
        for ref_key, value_key in (("entities_ref", "entities"), ("data_ref", "data")):
            if ref_key in resolved and value_key not in resolved:
                raw = await self.fetcher.read(resolved[ref_key], limit)
                try:
                    resolved[value_key] = json.loads(raw)
                except ValueError as exc:
                    raise ValidationFailed(f"{ref_key} is not JSON: {exc}") from exc
        return resolved, None

    async def prepare(
        self,
        invocation: Mapping[str, Any],
        *,
        package: LoadedPackage | None = None,
        test_mode: bool | None = None,
    ) -> PreparedInvocation:
        """Validate everything that must be right before the sandbox starts."""
        context = dict(invocation.get("context") or {})
        if package is None:
            package = await self.store.load(invocation["handler"], invocation.get("package_archive"))
        image = await asyncio.to_thread(self.check_package, package)
        params = self.check_params(package, invocation.get("params"))
        try:
            resolved = resolve_service_limits(self.settings, request_layer(invocation.get("limits")))
        except ValueError as exc:
            raise ValidationFailed(f"invalid limits: {exc}") from exc
        inputs: list[dict[str, Any]] = []
        contents: list[bytes | None] = []
        for index, item in enumerate(invocation.get("inputs") or []):
            self.check_input(package, index, item)
            resolved_item, content = await self._resolve_input(dict(item), resolved.limits)
            inputs.append(resolved_item)
            contents.append(content)
        if not inputs:
            raise ValidationFailed("inputs must not be empty")
        delivery = invocation.get("delivery") or {}
        return PreparedInvocation(
            invocation_id=new_invocation_id(),
            package=package,
            params=params,
            inputs=inputs,
            contents=contents,
            limits=resolved.limits,
            image=image,
            test_mode=bool(context.get("test_mode")) if test_mode is None else test_mode,
            delivery_key=delivery.get("delivery_key"),
            context=context,
        )

    # ------------------------------------------------------------------ run

    def bundle(self, prep: PreparedInvocation) -> Bundle:
        bundle = Bundle()
        for name, path in iter_package_files(prep.package.root):
            bundle.add(f"package/{name}", path.read_bytes())
        items = []
        for index, (item, content) in enumerate(zip(prep.inputs, prep.contents, strict=True)):
            content_file = None
            if content is not None:
                content_file = f"inputs/{index}"
                bundle.add(content_file, content)
            items.append({"input": item, "content_file": content_file})
        request = {
            "protocol": PROTOCOL_VERSION,
            "entry": prep.package.manifest["entry"],
            "package_dir": "package",
            "params": prep.params,
            "test_mode": prep.test_mode,
            "inputs": items,
        }
        bundle.add("request.json", json.dumps(request, ensure_ascii=False).encode("utf-8"))
        return bundle

    def labels(self, prep: PreparedInvocation) -> dict[str, str]:
        return {
            "io.jane.invocation-id": prep.invocation_id,
            "io.jane.package": f"{prep.package.manifest['package_id']}@{prep.package.manifest['version']}",
        }

    async def run(self, prep: PreparedInvocation) -> dict[str, Any]:
        started_at = now_rfc3339()
        bundle = await asyncio.to_thread(self.bundle, prep)
        timeout_s = prep.limits.timeouts.invocation_timeout_ms / 1000
        async with self._slots:
            try:
                outcome = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.backend.run, prep.image, bundle, prep.limits.sandbox, self.labels(prep)
                    ),
                    timeout=timeout_s,
                )
            except SandboxUnavailable as exc:
                raise ServiceUnavailable(str(exc), retry_after_seconds=5) from exc
            except TimeoutError:
                outcome = SandboxOutcome(
                    exit_code=None,
                    stdout=b"",
                    stderr=b"",
                    duration_ms=int(timeout_s * 1000),
                    timed_out=True,
                    backend=self.backend.name,
                    details={"reason": "invocation_timeout_ms"},
                )
        result = self.interpret(prep, outcome, started_at)
        log.info(
            "invocation finished",
            extra={
                "invocation_id": prep.invocation_id,
                "package": result["handler"],
                "status": result["status"],
                "failure": (result.get("failure") or {}).get("kind"),
                "duration_ms": outcome.duration_ms,
                "backend": outcome.backend,
            },
        )
        return result

    # ------------------------------------------------------------------ result

    def _input_refs(self, prep: PreparedInvocation) -> list[dict[str, Any]]:
        refs = []
        for item in prep.inputs:
            ref: dict[str, Any] = {"kind": item.get("kind")}
            material = item.get("material") if item.get("kind") == "material" else None
            if material:
                for key in ("material_id", "observation_id"):
                    if material.get(key):
                        ref[key] = material[key]
                sha = (material.get("revision") or {}).get("content_sha256")
                if sha:
                    ref["content_sha256"] = sha
            if item.get("from_invocation_id"):
                ref["from_invocation_id"] = item["from_invocation_id"]
            refs.append(ref)
        return refs

    def interpret(self, prep: PreparedInvocation, outcome: SandboxOutcome, started_at: str) -> dict[str, Any]:
        sandbox = prep.limits.sandbox
        result: dict[str, Any] = {
            "invocation_id": prep.invocation_id,
            "handler": prep.package.ref,
            "handler_kind": prep.package.manifest["kind"],
            "status": "failed",
            "inputs": self._input_refs(prep),
            "output": {},
            "test_mode": prep.test_mode,
            "duplicate": False,
            "started_at": started_at,
        }
        if prep.delivery_key:
            result["delivery_key"] = prep.delivery_key
        metrics: dict[str, Any] = {"duration_ms": outcome.duration_ms, "output_bytes": len(outcome.stdout)}
        diagnostics: dict[str, Any] = {"messages": [], "metrics": metrics}
        if outcome.stderr:
            text = outcome.stderr.decode("utf-8", errors="replace")[-MAX_STDERR_IN_RESULT:]
            diagnostics["logs_ref"] = {
                "kind": "inline",
                "media_type": "text/plain",
                "encoding": "utf-8",
                "data": text,
            }
        result["diagnostics"] = diagnostics

        def fail(kind: str, message: str, retryable: bool = False, **details: Any) -> dict[str, Any]:
            result["status"] = "failed"
            result["failure"] = {"kind": kind, "message": message, "retryable": retryable}
            if details:
                result["failure"]["details"] = details
            result["finished_at"] = now_rfc3339()
            return result

        if outcome.timed_out:
            return fail(
                "timeout",
                f"wall time limit {sandbox.wall_time_ms} ms exceeded; sandbox killed",
                wall_time_ms=sandbox.wall_time_ms,
                **outcome.details,
            )
        if outcome.oom_killed:
            return fail(
                "resource_exceeded",
                f"memory limit {sandbox.memory_mb} MB exceeded; sandbox killed",
                memory_mb=sandbox.memory_mb,
            )
        if outcome.stdout_truncated:
            return fail(
                "resource_exceeded",
                f"output exceeds max_output_bytes={sandbox.max_output_bytes}",
                max_output_bytes=sandbox.max_output_bytes,
            )
        try:
            response = json.loads(outcome.stdout.decode("utf-8"))
            results = list(response["results"])
            if len(results) != len(prep.inputs):
                raise ValueError("result count does not match inputs")
        except (ValueError, KeyError, TypeError) as exc:
            return fail(
                "execution_error",
                f"sandbox runner produced no valid result (exit code {outcome.exit_code})",
                exit_code=outcome.exit_code,
                error=str(exc)[:500],
                max_processes=sandbox.max_processes,
            )
        for key in ("cpu_ms", "peak_memory_mb"):
            if isinstance((response.get("metrics") or {}).get(key), int | float):
                metrics[key] = response["metrics"][key]

        violations = list(response.get("violations") or [])
        if violations:
            first_error = next((r["error"] for r in results if "error" in r), None)
            for v in violations[:20]:
                diagnostics["messages"].append(
                    {
                        "level": "error",
                        "code": f"sandbox.{v.get('kind', 'violation')}_blocked",
                        "message": f"{v.get('event')}: {v.get('detail')}"[:4000],
                    }
                )
            kinds = sorted({str(v.get("kind")) for v in violations})
            return fail(
                "sandbox_violation",
                f"the package attempted forbidden operations ({', '.join(kinds)}); the sandbox blocks them",
                violations=violations[:20],
                error=first_error,
            )
        errors = [(i, r["error"]) for i, r in enumerate(results) if "error" in r]
        if errors:
            index, error = errors[0]
            return fail(
                "execution_error",
                f"{error.get('type')}: {error.get('message')}"[:4000],
                input=index,
                stage=error.get("stage"),
                traceback=error.get("traceback"),
            )
        return self._success_like(prep, results, result, diagnostics, fail)

    def _success_like(
        self,
        prep: PreparedInvocation,
        results: Sequence[Mapping[str, Any]],
        result: dict[str, Any],
        diagnostics: dict[str, Any],
        fail: Any,
    ) -> dict[str, Any]:
        manifest = prep.package.manifest
        declared = {str(e["entity_type"]): e for e in (manifest.get("output") or {}).get("entities") or []}
        schemas: dict[str, Any] = {}
        validation_errors: list[dict[str, str]] = []
        entities: list[dict[str, Any]] = []
        data_values: list[Any] = []
        provenance: dict[str, Any] = {"package": prep.package.ref, "invocation_id": prep.invocation_id}
        trace = prep.context.get("trace") or {}
        for key in ("run_id", "stage_id"):
            if trace.get(key):
                provenance[key] = trace[key]
        for index, raw in enumerate(results):
            diagnostics["messages"].extend(
                self._diagnostics(raw.get("diagnostics"), index, validation_errors)
            )
            item = prep.inputs[index]
            material = item.get("material") if item.get("kind") == "material" else None
            raw_entities = raw.get("entities") or []
            if not isinstance(raw_entities, list):
                validation_errors.append({"pointer": "/entities", "message": "entities must be an array"})
                continue
            for entity in raw_entities:
                pointer = f"/entities/{len(entities)}"
                try:
                    entities.append(
                        self._entity(entity, pointer, declared, schemas, prep, material, provenance)
                    )
                except _Invalid as exc:
                    validation_errors.append({"pointer": exc.pointer, "message": exc.message})
                    entities.append(dict(entity) if isinstance(entity, Mapping) else {"invalid": True})
                    continue
                validation_errors.extend(
                    self._validate_fields(entities[-1], pointer, declared, schemas, prep)
                )
            if "data" in raw:
                data_values.append(raw["data"])
        data_schema_name = (manifest.get("output") or {}).get("data_schema")
        if data_values and data_schema_name:
            schema = self._schema(prep, str(data_schema_name), schemas)
            for i, value in enumerate(data_values):
                validation_errors.extend(
                    validate_instance(
                        schema, value, prefix="/data" + (f"/{i}" if len(data_values) > 1 else "")
                    )
                )
        diagnostics["messages"] = diagnostics["messages"][:200]
        if validation_errors:
            diagnostics["validation_errors"] = validation_errors[:100]
            result["output"] = {"entities": []} if manifest["kind"] == "extractor" else {}
            return fail(
                "schema_mismatch",
                f"{len(validation_errors)} validation error(s) in the output of {manifest['package_id']}",
            )
        statuses = [str(r.get("status")) for r in results]
        output: dict[str, Any] = {}
        if manifest["kind"] == "extractor" or entities:
            output["entities"] = entities
        if data_values:
            output["data"] = data_values[0] if len(data_values) == 1 else data_values
        result["output"] = output
        if "unrecognized" in statuses:
            info = next(
                (dict(r["unrecognized"]) for r in results if isinstance(r.get("unrecognized"), Mapping)), {}
            )
            info["partial"] = bool(info.get("partial")) or bool(entities)
            result["status"] = "unrecognized"
            result["unrecognized"] = info
        elif "success" in statuses:
            result["status"] = "success"
        else:
            result["status"] = "empty"
        if not diagnostics["messages"]:
            del diagnostics["messages"]
        result["finished_at"] = now_rfc3339()
        return result

    @staticmethod
    def _diagnostics(raw: Any, index: int, validation_errors: list[dict[str, str]]) -> list[dict[str, Any]]:
        out = []
        for diag in raw or []:
            if not isinstance(diag, Mapping) or diag.get("level") not in {
                "debug",
                "info",
                "warning",
                "error",
            }:
                validation_errors.append(
                    {
                        "pointer": "/diagnostics",
                        "message": f"invalid diagnostic in input {index}: {diag!r}"[:500],
                    }
                )
                continue
            clean = {
                k: diag[k]
                for k in ("level", "code", "message", "pointer", "material_id", "selector")
                if k in diag
            }
            clean["message"] = str(clean.get("message", ""))[:4000]
            out.append(clean)
        return out

    def _schema(self, prep: PreparedInvocation, name: str, cache: dict[str, Any]) -> Any:
        if name not in cache:
            cache[name] = self._json_file(prep.package, name)
        return cache[name]

    def _entity(
        self,
        raw: Any,
        pointer: str,
        declared: Mapping[str, Mapping[str, Any]],
        schemas: dict[str, Any],
        prep: PreparedInvocation,
        material: Mapping[str, Any] | None,
        provenance: Mapping[str, Any],
    ) -> dict[str, Any]:
        if not isinstance(raw, Mapping):
            raise _Invalid(pointer, "entity must be an object")
        entity_type = raw.get("entity_type")
        if entity_type not in declared:
            raise _Invalid(
                f"{pointer}/entity_type", f"entity_type {entity_type!r} is not declared in output.entities"
            )
        fields = raw.get("fields")
        if not isinstance(fields, Mapping):
            raise _Invalid(f"{pointer}/fields", "fields must be an object")
        for name, value in fields.items():
            if value is None:
                raise _Invalid(
                    f"{pointer}/fields/{name}", "null is not allowed; omit the field or list it in 'cleared'"
                )
        spec = declared[str(entity_type)]
        manifest = prep.package.manifest
        return to_entity_record(
            raw,
            key_fields=list(spec.get("key_fields") or []),
            material=material,
            schema_ref=f"{manifest['package_id']}@{manifest['version']}#{entity_type}",
            provenance=provenance,
        )

    def _validate_fields(
        self,
        record: Mapping[str, Any],
        pointer: str,
        declared: Mapping[str, Mapping[str, Any]],
        schemas: dict[str, Any],
        prep: PreparedInvocation,
    ) -> list[dict[str, str]]:
        spec = declared[str(record["entity_type"])]
        errors = validate_instance(
            self._schema(prep, str(spec["schema"]), schemas), record["fields"], prefix=f"{pointer}/fields"
        )
        if "key" not in record:
            errors.append(
                {"pointer": f"{pointer}/key", "message": f"key fields {spec.get('key_fields')} are missing"}
            )
        for e in self.schemas.errors("entity.schema.json", record):
            errors.append({"pointer": pointer + e["pointer"], "message": e["message"]})
        return errors
