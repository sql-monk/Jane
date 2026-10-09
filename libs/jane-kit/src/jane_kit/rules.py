"""Collector rules: schema validation and loading by ``rules_ref`` (shared by the collectors, R17).

* :class:`CollectorSchemas` - JSON Schemas of ``collector.v1`` (request components) and
  ``collector-rules.schema.json``; a failed ``oneOf`` over strategies or rules is re-validated against the branch
  named by its discriminator (``type`` / ``collector``), so the errors point at the real field;
* :class:`RulesReport` - ``valid`` / ``supported`` + errors and warnings (``RulesValidation`` of the contract);
* :class:`RulesLoader` - rules of a ``rules_ref`` (``PackageRef``), in order:

  1. a local package directory ``<rules_dir>/<package_id>/<version>/`` or an exported archive
     ``<rules_dir>/<package_id>-<version>.zip`` / ``<rules_dir>/<package_id>/<version>.zip``
     (``jane-package.json`` + the file named by ``entry.rules``);
  2. the package registry (``registry.v1``): ``GET /v1/packages/{id}/versions/{v}`` (manifest, digest, file list),
     then ``GET .../file?path=<entry.rules>``; the file must match ``files[].sha256`` of the immutable version.

  A ``digest`` of the reference must equal the registry's version digest (``digest_mismatch``); for a local archive
  it is compared with ``sha256`` of the archive file (an unpacked directory cannot be verified: refused). The
  registry token comes from the environment variable the operator names; a value that is not a valid HTTP header
  is refused, and error details never carry transport errors (URLs, hosts).
"""

from __future__ import annotations

import hashlib
import io
import json
import logging
import os
import re
import zipfile
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self

import httpx
from jsonschema.exceptions import ValidationError

from jane_kit.errors import FieldError, JaneError, ServiceUnavailable, ValidationFailed
from jane_kit.schemas import ContractSchemas, json_pointer

__all__ = ["STRATEGY_DEFS", "CollectorSchemas", "RulesLoader", "RulesReport", "header_value_safe"]

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
"""``strategies[].type`` -> ``$defs`` branch of ``collector-rules.schema.json``."""
COLLECTOR_DEFS = {"web": "WebRules", "telegram": "TelegramRules"}
"""``collector`` -> ``$defs`` branch of ``collector-rules.schema.json``."""


def header_value_safe(value: object) -> bool:
    """HTTP header values must be visible ASCII, with no control characters to reach error text."""
    return isinstance(value, str) and bool(value) and all(32 <= ord(char) <= 126 for char in value)


def _snake(name: str) -> str:
    """JSON Schema keyword -> Problem FieldError code (``minItems`` -> ``min_items``)."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower().lstrip("$") or "invalid"


class CollectorSchemas(ContractSchemas):
    """``collector.v1`` and ``collector-rules.schema.json`` validators (see the module docstring)."""

    def __init__(
        self, root: Path, *, openapi: str | None = "collector.v1.yaml", format_check: bool = False
    ) -> None:
        super().__init__(root, openapi=openapi or "collector.v1.yaml", format_check=format_check)
        self.rules_uri = self.uri("collector-rules.schema.json").rstrip("#")

    @classmethod
    def locate_collector(cls, configured: Path | None, *, setting: str, start: Path | None = None) -> Self:
        return cls.locate(configured, setting=setting, marker="openapi/collector.v1.yaml", start=start)

    def errors(self, uri: str, instance: Any, prefix: Sequence[Any] = ()) -> list[FieldError]:
        """Field errors with the pointer ``prefix`` + instance path (empty for the root)."""
        out: list[FieldError] = []
        for err in self.iter_errors(uri, instance):
            out.extend(self._explain(err, list(prefix)))
        return out

    def _explain(self, err: ValidationError, prefix: list[Any]) -> list[FieldError]:
        path = list(err.absolute_path)
        if err.validator == "oneOf" and isinstance(err.instance, Mapping):
            branch = None
            if err.instance.get("type") in STRATEGY_DEFS:
                branch = STRATEGY_DEFS[str(err.instance["type"])]
            elif err.instance.get("collector") in COLLECTOR_DEFS:
                branch = COLLECTOR_DEFS[str(err.instance["collector"])]
            if branch:
                return self.errors(f"{self.rules_uri}#/$defs/{branch}", err.instance, prefix + path)
        return [
            FieldError(
                pointer=json_pointer(prefix + path), code=_snake(str(err.validator)), message=err.message
            )
        ]

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


def _package_errors(ref: Mapping[str, Any], message: str) -> list[FieldError]:
    return [
        FieldError(pointer="/rules_ref", message=f"{ref.get('package_id')}@{ref.get('version')}: {message}")
    ]


class RulesLoader:
    """Rules of a ``rules_ref`` (see the module docstring); ``settings_prefix`` (``JANE_WEB_COLLECTOR_``) names
    the settings in error messages."""

    def __init__(
        self,
        *,
        rules_dir: Path | None,
        registry_url: str | None,
        registry_token_env: str | None,
        timeout_s: float,
        settings_prefix: str = "",
    ) -> None:
        self.rules_dir = rules_dir
        self.registry_url = registry_url.rstrip("/") if registry_url else None
        self.registry_token_env = registry_token_env
        self.timeout_s = timeout_s
        self.settings_prefix = settings_prefix

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
        p = self.settings_prefix
        raise ValidationFailed(
            "rules_ref cannot be resolved: no local package and no registry configured",
            errors=_package_errors(ref, f"not found ({p}RULES_DIR / {p}REGISTRY_URL)"),
        )

    # ------------------------------------------------------------------ local packages
    @staticmethod
    def _rules_from_manifest(
        manifest: Mapping[str, Any], read: Callable[[str], str], ref: Mapping[str, Any]
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
    @staticmethod
    def _check_file_digest(ref: Mapping[str, Any], version: Mapping[str, Any], name: str, raw: bytes) -> None:
        """The rules file must match ``PackageVersion.files[].sha256`` (the version is immutable)."""
        files = version.get("files")
        if files is None:
            log.warning(
                "registry version has no file list; rules file not verified", extra={"ref": dict(ref)}
            )
            return
        expected = next((f.get("sha256") for f in files if f.get("path") == name), None)
        actual = hashlib.sha256(raw).hexdigest()
        if expected != actual:
            raise JaneError(
                f"rules file {name}: sha256 {actual} does not match the registry file list ({expected})",
                code="digest_mismatch",
            )

    async def _load_registry(self, ref: Mapping[str, Any]) -> dict[str, Any]:
        headers = {}
        if self.registry_token_env and (token := os.environ.get(self.registry_token_env)):
            if not header_value_safe(token):
                raise ServiceUnavailable(
                    "registry credential is not valid for an HTTP header",
                    code="upstream_unavailable",
                    retryable=False,
                )
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
                raw = file_resp.content
                self._check_file_digest(ref, version, name, raw)
                text = raw.decode("utf-8")
        except httpx.HTTPError:
            raise ServiceUnavailable(
                "registry HTTP request failed", code="upstream_unavailable", retryable=True
            ) from None
        return self._rules_from_manifest(manifest, lambda _n: text, ref)
