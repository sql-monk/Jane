"""Package drafts built by the assistant (``jane-handler-package`` skill, ``package-manifest.schema.json``).

The manifest is always assembled by the assistant, never taken from the model: the model only
supplies code, the entity schema and expected outputs. Tests are package files
(``tests/<case>/material.json`` + ``expected.json``) so the package stays usable without the
registry; problem samples become tests with ``origin: problem_sample``.
"""

from __future__ import annotations

import base64
import copy
import hashlib
import io
import json
import re
import zipfile
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

__all__ = [
    "PackageDraft",
    "bump",
    "case_name",
    "collector_rules_draft",
    "extractor_draft",
    "slug",
]

_SLUG_BAD = re.compile(r"[^a-z0-9._-]+")
_CASE_BAD = re.compile(r"[^A-Za-z0-9._-]+")
_SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)")
MANIFEST = "jane-package.json"
RUNTIME_PROFILE = "python-extractor@1"
"""Runtime profile of handler-runtime (ADR-0003, WP-06). Generated code uses only the stdlib."""


def slug(text: str, max_len: int = 100) -> str:
    s = _SLUG_BAD.sub("-", text.lower()).strip("-._")
    return (s[:max_len].rstrip("-._") or "source") if s else "source"


def case_name(text: str) -> str:
    return (_CASE_BAD.sub("-", text).strip("-") or "case")[:100]


def bump(version: str, part: str) -> str:
    m = _SEMVER.match(version)
    if not m:
        return "1.0.0"
    major, minor, patch = (int(x) for x in m.groups())
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def strip_material(material: dict[str, Any]) -> dict[str, Any]:
    """Material fixture for a test: only fields the runtime needs, content inline."""
    keep = (
        "material_id",
        "observation_id",
        "source",
        "locator",
        "fetched_at",
        "format",
        "revision",
        "content",
        "collector",
    )
    return {k: copy.deepcopy(material[k]) for k in keep if k in material}


def expected_output(entities: list[dict[str, Any]]) -> dict[str, Any]:
    """``expected.json`` of a test: entities without observation/provenance."""
    return {
        "entities": [{k: v for k, v in e.items() if k not in {"observation", "provenance"}} for e in entities]
    }


@dataclass
class PackageDraft:
    manifest: dict[str, Any]
    files: dict[str, bytes] = field(default_factory=dict)

    @property
    def ref(self) -> dict[str, str]:
        return {"package_id": self.manifest["package_id"], "version": self.manifest["version"]}

    def copy(self) -> PackageDraft:
        return PackageDraft(copy.deepcopy(self.manifest), dict(self.files))

    def add_test(
        self,
        name: str,
        material: dict[str, Any],
        expected_status: str,
        entities: list[dict[str, Any]] | None,
        origin: str,
    ) -> str:
        name = case_name(name)
        existing = {t["name"] for t in self.manifest.get("tests", [])}
        base, n = name, 2
        while name in existing:
            name, n = f"{base}-{n}", n + 1
        self.files[f"tests/{name}/material.json"] = json.dumps(
            strip_material(material), ensure_ascii=False, indent=1
        ).encode()
        test: dict[str, Any] = {
            "name": name,
            "input": {"material": f"tests/{name}/material.json"},
            "expected_status": expected_status,
            "origin": origin,
        }
        if entities is not None and expected_status in {"success", "unrecognized"}:
            self.files[f"tests/{name}/expected.json"] = json.dumps(
                expected_output(entities), ensure_ascii=False, indent=1
            ).encode()
            test["expected"] = f"tests/{name}/expected.json"
            test["compare"] = "subset"
        self.manifest.setdefault("tests", []).append(test)
        return name

    def publish_body(self) -> dict[str, Any]:
        """``registry.v1`` ``PublishRequest``: manifest + files (jane-package.json comes from manifest)."""
        files = {}
        for path, data in sorted(self.files.items()):
            if path == MANIFEST:
                continue
            try:
                files[path] = {"encoding": "utf-8", "data": data.decode("utf-8")}
            except UnicodeDecodeError:
                files[path] = {"encoding": "base64", "data": base64.b64encode(data).decode()}
        return {"manifest": self.manifest, "files": files}

    def archive(self) -> bytes:
        """Deterministic zip (sorted paths, fixed timestamps) with ``jane-package.json``."""
        buf = io.BytesIO()
        entries = dict(self.files)
        entries[MANIFEST] = json.dumps(self.manifest, ensure_ascii=False, indent=1, sort_keys=True).encode()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(entries):
                info = zipfile.ZipInfo(path, date_time=(1980, 1, 1, 0, 0, 0))
                info.external_attr = 0o644 << 16
                zf.writestr(info, entries[path])
        return buf.getvalue()

    def content_ref(self) -> dict[str, Any]:
        data = self.archive()
        return {
            "kind": "inline",
            "media_type": "application/zip",
            "encoding": "base64",
            "data": base64.b64encode(data).decode(),
            "size_bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }

    @classmethod
    def from_files(cls, files: dict[str, bytes]) -> PackageDraft:
        manifest = json.loads(files[MANIFEST].decode("utf-8"))
        return cls(manifest, {p: d for p, d in files.items() if p != MANIFEST})

    def text(self, path: str) -> str:
        return self.files.get(path, b"").decode("utf-8", errors="replace")


def extractor_draft(
    *,
    package_id: str,
    version: str,
    title: str,
    entity_type: str,
    key_fields: list[str],
    entity_schema: dict[str, Any],
    module_code: str,
    domains: list[str],
    source_kind: str,
    media_types: list[str],
    job_id: str,
    model: dict[str, str],
    reason: str,
    based_on: dict[str, str] | None = None,
    change_summary: str | None = None,
) -> PackageDraft:
    module = entity_type.replace("-", "_") + "_extractor"
    schema = dict(entity_schema)
    schema.setdefault("$schema", "https://json-schema.org/draft/2020-12/schema")
    schema.setdefault("type", "object")
    schema["required"] = sorted(set(schema.get("required") or []) | set(key_fields))
    provenance: dict[str, Any] = {
        "created_by": "llm",
        "authors": ["assistant"],
        "created_at": _now(),
        "llm": {
            "reason": reason,
            "assistant_job_id": job_id,
            **{k: v for k, v in model.items() if k in {"provider", "model"}},
        },
    }
    if based_on:
        provenance["based_on"] = based_on
    if change_summary:
        provenance["change_summary"] = change_summary[:4000]
    manifest: dict[str, Any] = {
        "schema_version": "1",
        "package_id": package_id,
        "version": version,
        "kind": "extractor",
        "title": title[:200],
        "entry": {"runtime": "python", "module": f"{module}.main", "callable": "extract"},
        "input": {"accepts": ["material"], "media_types": media_types},
        "output": {
            "entities": [
                {
                    "entity_type": entity_type,
                    "schema": f"schemas/{entity_type}.schema.json",
                    "key_fields": key_fields,
                }
            ]
        },
        "dependencies": {"runtime_profile": RUNTIME_PROFILE, "python": []},
        "access": {"network": "none"},
        "tests": [],
        "provenance": provenance,
        "bindings_hint": {"source_kinds": [source_kind], **({"domains": domains} if domains else {})},
    }
    files = {
        f"src/{module}/__init__.py": b"",
        f"src/{module}/main.py": module_code.encode("utf-8"),
        f"schemas/{entity_type}.schema.json": json.dumps(schema, ensure_ascii=False, indent=1).encode(),
    }
    return PackageDraft(manifest, files)


def collector_rules_draft(
    *, package_id: str, version: str, title: str, rules: dict[str, Any], job_id: str, model: dict[str, str]
) -> PackageDraft:
    manifest = {
        "schema_version": "1",
        "package_id": package_id,
        "version": version,
        "kind": "collector-rules",
        "title": title[:200],
        "entry": {"collector": rules["collector"], "rules": "rules.json"},
        "tests": [],
        "provenance": {
            "created_by": "llm",
            "authors": ["assistant"],
            "created_at": _now(),
            "llm": {
                "reason": "onboarding",
                "assistant_job_id": job_id,
                **{k: v for k, v in model.items() if k in {"provider", "model"}},
            },
        },
    }
    return PackageDraft(manifest, {"rules.json": json.dumps(rules, ensure_ascii=False, indent=1).encode()})


def model_ref(result_model: dict[str, str]) -> dict[str, str]:
    """``provenance.llm`` provider/model from ``CompletionResult.model``."""
    out = {}
    if result_model.get("provider_id"):
        out["provider"] = result_model["provider_id"]
    if result_model.get("model_id"):
        out["model"] = result_model["model_id"]
    return out
