# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml>=6"]
# ///
"""Backward-compatibility check of contracts/ against a git ref.

    uv run contracts/tools/compat.py [--base main] [--oasdiff] [--self-test]

Compares contracts/schemas/** and contracts/openapi/*.yaml in the working tree with the same files
at --base (default: main) and reports:

  BREAKING  — removed file/operation/2xx response; new required request field or parameter;
              narrowed request type/enum/limits; removed or no-longer-required response field;
              widened response type; additionalProperties closed; const changed;
  WARNING   — changes a tolerant reader should survive (new enum value in a response, removed
              optional field, changed pattern, changed composition).

Direction matters: request bodies and parameters must not narrow; response bodies must not lose
guaranteed fields; standalone schemas (used both ways, e.g. Material) are checked in both
directions. Exit code 1 if any BREAKING finding. With --oasdiff also runs `oasdiff breaking`
(binary on PATH or the tufin/oasdiff Docker image) for every OpenAPI document; a document it does
not pass (ERR-level change, or oasdiff itself failed) also gives exit code 1. Without both oasdiff
and Docker that step is skipped with a note.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import CONTRACTS_DIR, HTTP_METHODS, deref, load_uri, pointer_get  # noqa: E402

REPO_DIR = CONTRACTS_DIR.parent
TRACKED = ("contracts/schemas", "contracts/openapi")
EXPORTED = (*TRACKED, "contracts/examples")  # examples are $ref'd by OpenAPI (needed by oasdiff)


@dataclass
class Finding:
    severity: str  # BREAKING | WARNING
    where: str
    message: str


class Comparator:
    def __init__(self) -> None:
        self.findings: list[Finding] = []
        self._seen: set[tuple[int, int, str]] = set()

    def add(self, severity: str, where: str, message: str) -> None:
        self.findings.append(Finding(severity, where, message))

    # -- JSON Schema ------------------------------------------------------------------------

    @staticmethod
    def _resolve(node: Any, uri: str) -> tuple[Any, str]:
        """Follow $ref (siblings such as description are ignored for comparison)."""
        for _ in range(32):
            if isinstance(node, dict) and isinstance(node.get("$ref"), str):
                target = urljoin(uri, node["$ref"])
                doc, _, frag = target.partition("#")
                node, uri = pointer_get(load_uri(doc), frag), target
            else:
                break
        return node, uri

    @staticmethod
    def _types(node: dict) -> set[str] | None:
        t = node.get("type")
        if t is None:
            return None
        return {t} if isinstance(t, str) else set(t)

    def schema(self, old: Any, old_uri: str, new: Any, new_uri: str, where: str, direction: str) -> None:
        old, old_uri = self._resolve(old, old_uri)
        new, new_uri = self._resolve(new, new_uri)
        key = (id(old), id(new), direction)  # node identity: load_uri caches documents, so $ref cycles terminate
        if key in self._seen or not isinstance(old, dict) or not isinstance(new, dict):
            return
        self._seen.add(key)
        req = direction in ("request", "both")
        resp = direction in ("response", "both")

        ot, nt = self._types(old), self._types(new)
        if ot is not None and nt is None:
            if resp:
                self.add("BREAKING", where, f"type constraint {sorted(ot)} removed (response may now contain anything)")
        elif ot is None and nt is not None:
            if req:
                self.add("BREAKING", where, f"type constraint {sorted(nt)} added")
        elif ot is not None and nt is not None:
            def covered(a: set[str], b: set[str]) -> bool:
                return all(x in b or (x == "integer" and "number" in b) for x in a)
            if req and not covered(ot, nt):
                self.add("BREAKING", where, f"type narrowed {sorted(ot)} -> {sorted(nt)}")
            if resp and not covered(nt, ot):
                self.add("BREAKING", where, f"type widened {sorted(ot)} -> {sorted(nt)}")

        if "const" in old or "const" in new:
            if old.get("const") != new.get("const"):
                self.add("BREAKING", where, f"const changed {old.get('const')!r} -> {new.get('const')!r}")

        if "enum" in old and "enum" in new:
            removed = [v for v in old["enum"] if v not in new["enum"]]
            added = [v for v in new["enum"] if v not in old["enum"]]
            if removed and req:
                self.add("BREAKING", where, f"enum values removed: {removed}")
            if removed and not req:
                self.add("WARNING", where, f"enum values no longer produced: {removed}")
            if added and resp:
                self.add("WARNING", where, f"enum values added (clients must tolerate): {added}")
        elif "enum" in new and "enum" not in old and req:
            self.add("BREAKING", where, "enum restriction added")

        for kw, tighter in (("minimum", 1), ("exclusiveMinimum", 1), ("minLength", 1), ("minItems", 1),
                            ("minProperties", 1), ("maximum", -1), ("exclusiveMaximum", -1),
                            ("maxLength", -1), ("maxItems", -1), ("maxProperties", -1)):
            if kw in new and (kw not in old or (new[kw] - old[kw]) * tighter > 0):
                if req:
                    self.add("BREAKING", where, f"{kw} tightened {old.get(kw)!r} -> {new[kw]!r}")
            if kw in old and (kw not in new or (new[kw] - old[kw]) * tighter < 0) and resp:
                self.add("WARNING", where, f"{kw} relaxed {old[kw]!r} -> {new.get(kw)!r} (responses may exceed old bound)")
        if old.get("pattern") != new.get("pattern") and "pattern" in new:
            self.add("BREAKING" if req and "pattern" not in old else "WARNING", where,
                     f"pattern changed {old.get('pattern')!r} -> {new['pattern']!r}")

        for kw in ("additionalProperties", "unevaluatedProperties"):
            if new.get(kw) is False and old.get(kw) is not False and req:
                self.add("BREAKING", where, f"{kw} closed (unknown fields now rejected)")

        old_req, new_req = set(old.get("required") or []), set(new.get("required") or [])
        for name in sorted(new_req - old_req):
            if req:
                self.add("BREAKING", where, f"property '{name}' became required")
        for name in sorted(old_req - new_req):
            if resp:
                self.add("BREAKING", where, f"property '{name}' is no longer guaranteed (removed from required)")

        old_props, new_props = old.get("properties") or {}, new.get("properties") or {}
        for name in sorted(set(old_props) - set(new_props)):
            if resp and name in old_req:
                self.add("BREAKING", where, f"required property '{name}' removed")
            elif req and new.get("additionalProperties") is False:
                self.add("BREAKING", where, f"property '{name}' removed and unknown fields are rejected")
            else:
                self.add("WARNING", where, f"optional property '{name}' removed")
        for name in sorted(set(old_props) & set(new_props)):
            self.schema(old_props[name], old_uri, new_props[name], new_uri, f"{where}/{name}", direction)

        for kw in ("items", "additionalProperties", "not", "if", "then", "else", "contains", "propertyNames"):
            if isinstance(old.get(kw), dict) and isinstance(new.get(kw), dict):
                self.schema(old[kw], old_uri, new[kw], new_uri, f"{where}/{kw}", direction)
        for kw in ("oneOf", "anyOf", "allOf", "prefixItems"):
            o, n = old.get(kw), new.get(kw)
            if isinstance(o, list) and isinstance(n, list):
                if len(o) != len(n):
                    self.add("WARNING", where, f"{kw} changed from {len(o)} to {len(n)} alternatives; review manually")
                for i, (a, b) in enumerate(zip(o, n)):
                    self.schema(a, old_uri, b, new_uri, f"{where}/{kw}/{i}", direction)
        defs_o, defs_n = old.get("$defs") or {}, new.get("$defs") or {}
        for name in sorted(set(defs_o) - set(defs_n)):
            self.add("BREAKING", where, f"$defs/{name} removed (may be referenced by other contracts)")

    # -- OpenAPI ---------------------------------------------------------------------------

    def openapi(self, old_path: Path, new_path: Path, name: str) -> None:
        old_doc, new_doc = load_uri(old_path.as_uri()), load_uri(new_path.as_uri())
        old_uri, new_uri = old_path.as_uri(), new_path.as_uri()
        old_paths, new_paths = old_doc.get("paths") or {}, new_doc.get("paths") or {}
        for p in sorted(old_paths):
            old_item, old_item_uri = deref(old_paths[p], old_uri)
            if p not in new_paths:
                self.add("BREAKING", f"{name} {p}", "path removed")
                continue
            new_item, new_item_uri = deref(new_paths[p], new_uri)
            for m in HTTP_METHODS:
                if m not in old_item:
                    continue
                where = f"{name} {m.upper()} {p}"
                if m not in new_item:
                    self.add("BREAKING", where, "operation removed")
                    continue
                self._operation(old_item, old_item[m], old_item_uri, new_item, new_item[m], new_item_uri, where)

    def _params(self, item: dict, op: dict, uri: str) -> dict[tuple[str, str], dict]:
        out = {}
        for p in (item.get("parameters") or []) + (op.get("parameters") or []):
            node, _ = deref(p, uri)
            out[(node.get("in"), node.get("name"))] = node
        return out

    def _operation(self, oi: dict, oo: dict, ou: str, ni: dict, no: dict, nu: str, where: str) -> None:
        op_old, op_new = self._params(oi, oo, ou), self._params(ni, no, nu)
        for key, param in op_new.items():
            if param.get("required") and not (op_old.get(key) or {}).get("required"):
                self.add("BREAKING", where, f"parameter {key[0]}:{key[1]} is now required")
        for key in op_old.keys() - op_new.keys():
            self.add("WARNING", where, f"parameter {key[0]}:{key[1]} removed")
        for key in op_old.keys() & op_new.keys():
            if "schema" in op_old[key] and "schema" in op_new[key]:
                self.schema(op_old[key]["schema"], ou, op_new[key]["schema"], nu, f"{where} param {key[1]}", "request")

        ob, obu = deref(oo["requestBody"], ou) if oo.get("requestBody") else (None, ou)
        nb, nbu = deref(no["requestBody"], nu) if no.get("requestBody") else (None, nu)
        if nb and not ob and nb.get("required"):
            self.add("BREAKING", where, "required request body added")
        if ob and nb:
            for mt, media in (ob.get("content") or {}).items():
                new_media = (nb.get("content") or {}).get(mt)
                if new_media is None:
                    self.add("BREAKING", where, f"request media type {mt} removed")
                elif "schema" in media and "schema" in new_media:
                    self.schema(media["schema"], obu, new_media["schema"], nbu, f"{where} request {mt}", "request")

        o_resp, n_resp = oo.get("responses") or {}, no.get("responses") or {}
        for code, resp in o_resp.items():
            code_s = str(code)
            if code_s not in {str(c) for c in n_resp}:
                if code_s.startswith("2"):
                    self.add("BREAKING", where, f"response {code_s} removed")
                continue
            if not code_s.startswith("2"):
                continue
            o_node, o_uri = deref(resp, ou)
            n_node, n_uri = deref(n_resp.get(code, n_resp.get(code_s, n_resp.get(int(code_s)) if code_s.isdigit() else None)), nu)
            for mt, media in (o_node.get("content") or {}).items():
                new_media = (n_node.get("content") or {}).get(mt)
                if new_media is None:
                    self.add("BREAKING", where, f"response {code_s} media type {mt} removed")
                elif "schema" in media and "schema" in new_media:
                    self.schema(media["schema"], o_uri, new_media["schema"], n_uri, f"{where} {code_s} {mt}", "response")


def export_base(base: str, dest: Path) -> list[str]:
    files = subprocess.run(["git", "ls-tree", "-r", "--name-only", base, "--", *EXPORTED], cwd=REPO_DIR,
                           capture_output=True, text=True, check=True).stdout.split()
    for rel in files:
        blob = subprocess.run(["git", "show", f"{base}:{rel}"], cwd=REPO_DIR, capture_output=True, check=True).stdout
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob)
    return files


def run_oasdiff(base_root: Path, names: list[str]) -> tuple[list[str], int]:
    """Output lines and the number of documents for which `oasdiff breaking --fail-on ERR` did not pass."""
    out = []
    failed = 0
    binary = shutil.which("oasdiff")
    docker = shutil.which("docker")
    for name in names:
        old = base_root / "contracts" / "openapi" / name
        new = CONTRACTS_DIR / "openapi" / name
        if binary:
            cmd = [binary, "breaking", str(old), str(new), "--fail-on", "ERR"]
        elif docker:
            cmd = [docker, "run", "--rm", "-v", f"{base_root / 'contracts'}:/base:ro", "-v", f"{CONTRACTS_DIR}:/rev:ro",
                   "tufin/oasdiff", "breaking", f"/base/openapi/{name}", f"/rev/openapi/{name}", "--fail-on", "ERR"]
        else:
            return ["oasdiff: skipped (neither oasdiff nor docker found)"], 0
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        status = "ok" if proc.returncode == 0 else f"exit {proc.returncode}"
        failed += proc.returncode != 0
        out.append(f"oasdiff {name}: {status}\n{(proc.stdout + proc.stderr).strip()}")
    return out, failed


def compare_trees(base_root: Path, base_files: list[str]) -> Comparator:
    comp = Comparator()
    for rel in sorted(base_files):
        old = base_root / rel
        new = REPO_DIR / rel
        if not new.exists():
            comp.add("BREAKING", rel, "file removed")
            continue
        if rel.startswith("contracts/openapi/") and rel.endswith(".v1.yaml"):
            comp.openapi(old, new, Path(rel).name)
        elif rel.startswith("contracts/schemas/") and rel.endswith(".json"):
            old_doc, new_doc = load_uri(old.as_uri()), load_uri(new.as_uri())
            comp.schema(old_doc, old.as_uri(), new_doc, new.as_uri(), rel, "both")
            old_defs, new_defs = old_doc.get("$defs") or {}, new_doc.get("$defs") or {}
            for name in sorted(set(old_defs) & set(new_defs)):
                comp.schema(old_defs[name], f"{old.as_uri()}#/$defs/{name}", new_defs[name],
                            f"{new.as_uri()}#/$defs/{name}", f"{rel}#/$defs/{name}", "both")
    return comp


def self_test() -> int:
    """Verify the comparator flags known breaking changes (runs on temporary files)."""
    import json

    cases = [
        ({"type": "object", "properties": {"a": {"type": "string"}}},
         {"type": "object", "required": ["a"], "properties": {"a": {"type": "string"}}}, "request", "became required"),
        ({"type": "object", "required": ["a"], "properties": {"a": {"type": "string"}}},
         {"type": "object", "properties": {}}, "response", "required property 'a' removed"),
        ({"type": "string", "enum": ["x", "y"]}, {"type": "string", "enum": ["x"]}, "request", "enum values removed"),
        ({"type": "integer", "maximum": 10}, {"type": "integer", "maximum": 5}, "request", "maximum tightened"),
        ({"type": "object"}, {"type": "object", "additionalProperties": False}, "request", "closed"),
        ({"type": "string"}, {"type": ["string", "null"]}, "response", "type widened"),
        # nested inline subschemas (regression: they share the parent URI)
        ({"type": "object", "properties": {"a": {"type": "object", "properties": {"b": {"type": "string"}}}}},
         {"type": "object", "properties": {"a": {"type": "object", "properties": {"b": {"type": "string", "maxLength": 3}}}}},
         "request", "maxLength tightened"),
        ({"$defs": {"X": {"type": "object", "properties": {"u": {"type": "array"}}}}, "$ref": "#/$defs/X"},
         {"$defs": {"X": {"type": "object", "required": ["u"], "properties": {"u": {"type": "array"}}}}, "$ref": "#/$defs/X"},
         "request", "became required"),
    ]
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        for i, (old, new, direction, expect) in enumerate(cases):
            o, n = Path(tmp) / f"o{i}.json", Path(tmp) / f"n{i}.json"
            o.write_text(json.dumps(old), encoding="utf-8")
            n.write_text(json.dumps(new), encoding="utf-8")
            comp = Comparator()
            comp.schema(old, o.as_uri(), new, n.as_uri(), f"case{i}", direction)
            hit = any(f.severity == "BREAKING" and expect in f.message for f in comp.findings)
            print(f"[{'ok' if hit else 'FAIL'}] case {i}: expect BREAKING '{expect}'")
            failures += 0 if hit else 1
        comp = Comparator()
        same = {"type": "object", "required": ["a"], "properties": {"a": {"type": "string"}}}
        p = Path(tmp) / "same.json"
        p.write_text(json.dumps(same), encoding="utf-8")
        comp.schema(same, p.as_uri(), same, p.as_uri(), "same", "both")
        print(f"[{'ok' if not comp.findings else 'FAIL'}] identical schema has no findings")
        failures += 1 if comp.findings else 0
    return 1 if failures else 0


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", default="main", help="git ref to compare against (default: main)")
    ap.add_argument("--oasdiff", action="store_true", help="also run oasdiff breaking (binary or Docker)")
    ap.add_argument("--self-test", action="store_true", help="verify the comparator on built-in cases")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    with tempfile.TemporaryDirectory(prefix="jane-compat-") as tmp:
        base_root = Path(tmp)
        base_files = [f for f in export_base(args.base, base_root) if f.startswith(TRACKED)]
        new_files = sorted(p.relative_to(REPO_DIR).as_posix() for d in TRACKED for p in (REPO_DIR / d).rglob("*")
                           if p.is_file() and p.suffix in (".json", ".yaml"))
        added = sorted(set(new_files) - set(base_files))
        comp = compare_trees(base_root, base_files)
        print(f"Base: {args.base} ({len(base_files)} contract files); working tree: {len(new_files)} files; added: {len(added)}")
        for f in added:
            print(f"  + {f}")
        breaking = [f for f in comp.findings if f.severity == "BREAKING"]
        warnings = [f for f in comp.findings if f.severity == "WARNING"]
        for f in breaking + warnings:
            print(f"{f.severity:8} {f.where}: {f.message}")
        oasdiff_failed = 0
        if args.oasdiff:
            names = sorted({Path(f).name for f in base_files if f.startswith("contracts/openapi/") and f.endswith(".v1.yaml")})
            lines, oasdiff_failed = run_oasdiff(base_root, names)
            for line in lines:
                print(line)
        print(f"\n{len(breaking)} breaking, {len(warnings)} warning(s).")
        if oasdiff_failed:
            print(f"oasdiff: {oasdiff_failed} document(s) did not pass `oasdiff breaking --fail-on ERR`.")
        return 1 if breaking or oasdiff_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
