"""Collector rules: validation against ``collector-rules.schema.json`` and loading by ``rules_ref``.

Sources of ``rules_ref`` (``PackageRef``), in order:

1. a local package directory ``<rules_dir>/<package_id>/<version>/`` or an exported archive
   ``<rules_dir>/<package_id>-<version>.zip`` / ``<rules_dir>/<package_id>/<version>.zip``
   (``jane-package.json`` + the file named by ``entry.rules``);
2. the package registry (``registry.v1``): ``GET /v1/packages/{id}/versions/{v}`` (manifest, digest),
   then ``GET .../file?path=<entry.rules>``.

If the reference has a ``digest``, it must equal the registry's version digest (``digest_mismatch``);
for a local archive it is compared with ``sha256`` of the archive file.
"""

from __future__ import annotations

import hashlib
import io
import json
import logging
import os
import zipfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from jane_kit.contracts import OpenAPISpec, contracts_dir
from jane_kit.errors import FieldError, JaneError, ServiceUnavailable, ValidationFailed

from .discovery.registry import RESERVED_TYPES, Registry

__all__ = ["ContractSchemas", "RulesLoader", "RulesReport", "validate_rules"]

log = logging.getLogger(__name__)

MANIFEST = "jane-package.json"
STRATEGY_DEFS = {
    "seed_list": "SeedListStrategy",
    "recursive": "RecursiveStrategy",
    "sitemap": "SitemapStrategy",
    "feed": "FeedStrategy",
    "listing": "ListingStrategy",
    "url_template": "UrlTemplateStrategy",
    "api_feed": "ApiFeedStrategy",
    "llm_explore": "LlmExploreStrategy",
}


def _pointer(path: Sequence[Any]) -> str:
    return "/" + "/".join(str(p).replace("~", "~0").replace("/", "~1") for p in path) if path else ""


class ContractSchemas:
    """JSON Schemas of ``collector.v1`` (with cross-file ``$ref``) for request and rules validation."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.spec = OpenAPISpec.load(root / "openapi" / "collector.v1.yaml")
        self.rules_uri = (root / "schemas" / "collector-rules.schema.json").resolve().as_uri()
        self._validators: dict[str, Draft202012Validator] = {}

    @classmethod
    def locate(cls, configured: Path | None) -> ContractSchemas:
        root = configured or contracts_dir(Path(__file__).parent)
        if root is None or not (root / "openapi" / "collector.v1.yaml").is_file():
            raise RuntimeError(
                "contracts/ not found: set JANE_WEB_COLLECTOR_CONTRACTS_DIR or JANE_CONTRACTS_DIR"
            )
        return cls(root)

    def validator(self, uri: str) -> Draft202012Validator:
        if uri not in self._validators:
            self._validators[uri] = Draft202012Validator({"$ref": uri}, registry=self.spec.registry)
        return self._validators[uri]

    def component(self, name: str) -> str:
        return f"{self.spec.base_uri}#/components/schemas/{name}"

    def errors(self, uri: str, instance: Any, prefix: Sequence[Any] = ()) -> list[FieldError]:
        out: list[FieldError] = []
        for err in sorted(self.validator(uri).iter_errors(instance), key=lambda e: list(e.absolute_path)):
            out.extend(self._explain(err, instance, list(prefix)))
        return out

    def _explain(self, err: ValidationError, instance: Any, prefix: list[Any]) -> list[FieldError]:
        path = list(err.absolute_path)
        # oneOf over strategies / rules: re-validate against the branch named by the discriminator.
        if err.validator == "oneOf" and isinstance(err.instance, Mapping):
            branch = None
            if err.instance.get("type") in STRATEGY_DEFS:
                branch = STRATEGY_DEFS[str(err.instance["type"])]
            elif err.instance.get("collector") == "web":
                branch = "WebRules"
            elif err.instance.get("collector") == "telegram":
                branch = "TelegramRules"
            if branch:
                return self.errors(f"{self.rules_uri}#/$defs/{branch}", err.instance, prefix + path)
        return [FieldError(pointer=_pointer(prefix + path), code=str(err.validator), message=err.message)]

    def rules_errors(self, rules: Any, prefix: Sequence[Any] = ()) -> list[FieldError]:
        return self.errors(self.rules_uri, rules, prefix)


@dataclass
class RulesReport:
    valid: bool
    supported: bool
    errors: list[FieldError]
    warnings: list[FieldError]

    def wire(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "supported": self.supported,
            "errors": [e.model_dump(exclude_none=True) for e in self.errors],
            "warnings": [w.model_dump(exclude_none=True) for w in self.warnings],
        }


def validate_rules(schemas: ContractSchemas, registry: Registry, rules: Any) -> RulesReport:
    """Schema validation + what this implementation supports (unsupported strategies, telegram rules)."""
    errors = schemas.rules_errors(rules)
    warnings: list[FieldError] = []
    supported = True
    if errors or not isinstance(rules, Mapping):
        return RulesReport(False, False, errors, warnings)
    if rules.get("collector") != "web":
        warnings.append(
            FieldError(pointer="/collector", message="web-collector executes only collector=web rules")
        )
        return RulesReport(True, False, errors, warnings)
    has_depth = "max_depth" in ((rules.get("limits") or {}).get("crawl") or {})
    for i, strategy in enumerate(rules.get("strategies") or []):
        kind = strategy.get("type")
        if kind in RESERVED_TYPES:
            supported = False
            warnings.append(
                FieldError(
                    pointer=f"/strategies/{i}",
                    code="unsupported_strategy",
                    message=f"strategy {kind} is not executed by the collector (ADR-0010: LLM exploration is done by the assistant)",
                )
            )
        elif not registry.supported(kind):
            supported = False
            warnings.append(
                FieldError(
                    pointer=f"/strategies/{i}",
                    code="unsupported_strategy",
                    message=f"strategy {kind} is not available in this collector build",
                )
            )
        elif (
            kind == "recursive"
            and not has_depth
            and "max_depth" not in ((strategy.get("limits") or {}).get("crawl") or {})
        ):
            warnings.append(
                FieldError(
                    pointer=f"/strategies/{i}",
                    message="recursive strategy without max_depth inherits limits.crawl.max_depth",
                )
            )
    return RulesReport(True, supported, errors, warnings)


def _package_errors(ref: Mapping[str, Any], message: str) -> list[FieldError]:
    return [
        FieldError(pointer="/rules_ref", message=f"{ref.get('package_id')}@{ref.get('version')}: {message}")
    ]


class RulesLoader:
    def __init__(
        self,
        *,
        rules_dir: Path | None,
        registry_url: str | None,
        registry_token_env: str | None,
        timeout_s: float,
    ) -> None:
        self.rules_dir = rules_dir
        self.registry_url = registry_url.rstrip("/") if registry_url else None
        self.registry_token_env = registry_token_env
        self.timeout_s = timeout_s

    def sources(self) -> list[str]:
        out = ["inline"]
        if self.rules_dir:
            out.append("local_dir")
        if self.registry_url:
            out.append("registry")
        return out

    async def load(self, ref: Mapping[str, Any]) -> dict[str, Any]:
        local = self._load_local(ref)
        if local is not None:
            return local
        if self.registry_url:
            return await self._load_registry(ref)
        raise ValidationFailed(
            "rules_ref cannot be resolved: no local package and no registry configured",
            errors=_package_errors(
                ref, "not found (JANE_WEB_COLLECTOR_RULES_DIR / JANE_WEB_COLLECTOR_REGISTRY_URL)"
            ),
        )

    # ------------------------------------------------------------------ local packages
    @staticmethod
    def _rules_from_manifest(
        manifest: Mapping[str, Any], read: Any, ref: Mapping[str, Any]
    ) -> dict[str, Any]:
        if manifest.get("kind") != "collector-rules":
            raise ValidationFailed(
                "package is not collector-rules", errors=_package_errors(ref, "wrong kind")
            )
        if manifest.get("package_id") != ref["package_id"] or manifest.get("version") != ref["version"]:
            raise ValidationFailed(
                "package manifest does not match rules_ref",
                errors=_package_errors(ref, "id/version mismatch"),
            )
        entry = manifest.get("entry") or {}
        name = entry.get("rules")
        if not isinstance(name, str):
            raise ValidationFailed(
                "manifest has no entry.rules", errors=_package_errors(ref, "no entry.rules")
            )
        try:
            data = json.loads(read(name))
        except (KeyError, FileNotFoundError, ValueError) as exc:
            raise ValidationFailed(
                f"rules file {name} unreadable: {exc}", errors=_package_errors(ref, "rules file unreadable")
            ) from exc
        if not isinstance(data, dict):
            raise ValidationFailed(
                "rules file must contain an object", errors=_package_errors(ref, "rules not an object")
            )
        return data

    def _load_local(self, ref: Mapping[str, Any]) -> dict[str, Any] | None:
        if self.rules_dir is None:
            return None
        pid, ver = str(ref["package_id"]), str(ref["version"])
        directory = self.rules_dir / pid / ver
        if (directory / MANIFEST).is_file():
            if ref.get("digest"):
                raise ValidationFailed(
                    "a digest can be verified only for an archive or a registry version",
                    errors=_package_errors(ref, "digest given for an unpacked local package"),
                )
            manifest = json.loads((directory / MANIFEST).read_text(encoding="utf-8"))

            def read_dir(name: str) -> str:
                target = (directory / name).resolve()
                if directory.resolve() not in target.parents:
                    raise FileNotFoundError(name)
                return target.read_text(encoding="utf-8")

            return self._rules_from_manifest(manifest, read_dir, ref)
        for archive in (self.rules_dir / f"{pid}-{ver}.zip", self.rules_dir / pid / f"{ver}.zip"):
            if archive.is_file():
                raw = archive.read_bytes()
                digest = "sha256:" + hashlib.sha256(raw).hexdigest()
                if ref.get("digest") and ref["digest"] != digest:
                    raise JaneError(f"archive digest {digest} != rules_ref.digest", code="digest_mismatch")
                with zipfile.ZipFile(io.BytesIO(raw)) as zf:
                    manifest = json.loads(zf.read(MANIFEST))
                    return self._rules_from_manifest(manifest, lambda n: zf.read(n).decode("utf-8"), ref)
        return None

    # ------------------------------------------------------------------ registry.v1
    async def _load_registry(self, ref: Mapping[str, Any]) -> dict[str, Any]:
        headers = {}
        if self.registry_token_env and (token := os.environ.get(self.registry_token_env)):
            headers["Authorization"] = f"Bearer {token}"
        base = f"{self.registry_url}/v1/packages/{ref['package_id']}/versions/{ref['version']}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout_s, headers=headers, trust_env=False) as client:
                resp = await client.get(base)
                if resp.status_code == 404:
                    raise ValidationFailed(
                        "rules package version not found",
                        errors=_package_errors(ref, "not found in registry"),
                    )
                resp.raise_for_status()
                version = resp.json()
                if ref.get("digest") and version.get("digest") != ref["digest"]:
                    raise JaneError(
                        f"registry digest {version.get('digest')} != rules_ref.digest", code="digest_mismatch"
                    )
                manifest = version.get("manifest") or {}
                name = (manifest.get("entry") or {}).get("rules")
                if not isinstance(name, str):
                    raise ValidationFailed(
                        "manifest has no entry.rules", errors=_package_errors(ref, "no entry.rules")
                    )
                file_resp = await client.get(f"{base}/file", params={"path": name})
                if file_resp.status_code == 404:
                    raise ValidationFailed(
                        "rules file not found", errors=_package_errors(ref, f"{name} not in package")
                    )
                file_resp.raise_for_status()
                text = file_resp.text
        except httpx.HTTPError as exc:
            raise ServiceUnavailable(
                f"registry unavailable: {exc}", code="upstream_unavailable", retryable=True
            ) from exc
        return self._rules_from_manifest(manifest, lambda _n: text, ref)
