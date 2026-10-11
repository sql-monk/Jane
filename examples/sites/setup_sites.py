"""Real sites on a running Jane stack: product catalogs with prices, car and classified ads, news and Telegram.

Every site is one declarative file ``sites/<site>.json``::

    {
      "site": "makeup", "group": "catalog", "title": "...", "url": "https://...",
      "sources": [<source.schema.json documents>],
      "tasks": [<task-config.schema.json documents>],
      "verify": {"<source_id>": {"<entity_type>": {"min": 50, "required": ["title", "price"]}}}
    }

A package reference is written as the string ``"@pkg:<package_id>"`` and resolves to ``{package_id, version,
digest}`` of the package directory (``packages/``, ``../shops/packages`` or the storage packages); the digest is
that of the registry's canonical archive. Connection ids are those of ``../documents/connections.json``.

    uv run --all-packages python examples/sites/setup_sites.py check [site ...]
    uv run --all-packages python examples/sites/setup_sites.py apply --project <p> [site ...] [--run]
    uv run --all-packages python examples/sites/setup_sites.py run --project <p> <site> [--task <id> ...]
    uv run --all-packages python examples/sites/setup_sites.py verify --project <p> [site ...]

``check`` needs no services: documents against the contracts, package manifests, package tests in process.
``apply`` publishes and approves the referenced packages, puts the connections and creates or replaces the
sources and tasks (their schedules then run them); ``--run`` also starts every task of the site once.
``verify`` reads the entities of each source from storage and checks counts, required fields and the
package's entity schema; the summary goes to ``.jane/sites-<project>.json``.
"""

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import jane_examples as ex  # noqa: E402 - examples/jane_examples.py: contract-validated API clients

SITES = HERE / "sites"
PACKAGE_ROOTS = (HERE / "packages", HERE.parent / "shops" / "packages")
STORAGE = ("jane.storage-files", "jane.storage-postgresql")
REF = "@pkg:"
DUMMY_DIGEST = "sha256:" + "0" * 64


def site_files(names: Sequence[str] = ()) -> list[Path]:
    files = sorted(SITES.glob("*.json"))
    if names:
        wanted = set(names)
        files = [f for f in files if f.stem in wanted]
        missing = wanted - {f.stem for f in files}
        if missing:
            raise SystemExit(f"no site file for: {', '.join(sorted(missing))}")
    return files


def package_dirs() -> dict[str, Path]:
    from jane_storage.adapters import package_dirs as storage_dirs

    dirs: dict[str, Path] = {}
    for root in PACKAGE_ROOTS:
        for d in sorted(p for p in root.iterdir() if (p / "jane-package.json").is_file()):
            dirs[ex.read_json(d / "jane-package.json")["package_id"]] = d
    for root in storage_dirs().values():
        pid = ex.read_json(Path(root) / "jane-package.json")["package_id"]
        if pid in STORAGE:
            dirs[pid] = Path(root)
    return dirs


def refs_in(doc: Any) -> Iterator[str]:
    if isinstance(doc, str) and doc.startswith(REF):
        yield doc[len(REF) :]
    elif isinstance(doc, Mapping):
        for v in doc.values():
            yield from refs_in(v)
    elif isinstance(doc, list):
        for v in doc:
            yield from refs_in(v)


def resolve(doc: Any, refs: Mapping[str, Mapping[str, str]]) -> Any:
    if isinstance(doc, str) and doc.startswith(REF):
        return dict(refs[doc[len(REF) :]])
    if isinstance(doc, Mapping):
        return {k: resolve(v, refs) for k, v in doc.items()}
    if isinstance(doc, list):
        return [resolve(v, refs) for v in doc]
    return doc


def local_ref(directory: Path) -> dict[str, str]:
    from jane_registry.archive import canonical_archive, digest_of, files_from_dir

    manifest = ex.read_json(directory / "jane-package.json")
    archive = bytes(canonical_archive(files_from_dir(directory)))
    return {
        "package_id": manifest["package_id"],
        "version": manifest["version"],
        "digest": str(digest_of(archive)),
    }


def check_site(path: Path, dirs: Mapping[str, Path], tested: set[str]) -> list[str]:
    from jane_extractor_sdk.testing import assert_package_tests_pass

    problems: list[str] = []
    site = ex.read_json(path)
    name = path.stem
    if site.get("site") != name:
        problems.append(f"{name}: 'site' must equal the file name")
    for key in ("group", "title", "url", "sources", "tasks"):
        if key not in site:
            problems.append(f"{name}: missing '{key}'")
    used = sorted(set(refs_in(site)))
    for pid in used:
        if pid not in dirs:
            problems.append(f"{name}: unknown package {pid}")
    fake = {pid: {"package_id": pid, "version": "1.0.0", "digest": DUMMY_DIGEST} for pid in used}
    source_ids = set()
    for source in site.get("sources", []):
        source_ids.add(source.get("source_id"))
        problems += [
            f"{name}: source {source.get('source_id')}: {e}"
            for e in ex.validate("source.schema.json", resolve(source, fake))
        ]
    for task in site.get("tasks", []):
        problems += [
            f"{name}: task {task.get('task_id')}: {e}"
            for e in ex.validate("task-config.schema.json", resolve(task, fake))
        ]
        if task.get("input", {}).get("source_id") not in source_ids:
            problems.append(f"{name}: task {task.get('task_id')} reads a source not defined in this site")
    for sid in site.get("verify", {}):
        if sid not in source_ids:
            problems.append(f"{name}: verify names unknown source {sid}")
    for pid in used:
        if pid in STORAGE or pid not in dirs or pid in tested:
            continue
        tested.add(pid)
        d = dirs[pid]
        manifest = ex.read_json(d / "jane-package.json")
        problems += [f"{pid}: {e}" for e in ex.validate("package-manifest.schema.json", manifest)]
        problems += [f"{pid}: {e}" for e in ex.package_json_problems(d, manifest)]
        if manifest["kind"] == "collector-rules":
            rules = ex.read_json(d / manifest["entry"]["rules"])
            problems += [f"{pid}: rules: {e}" for e in ex.validate("collector-rules.schema.json", rules)]
            if (rules.get("robots") or {}).get("mode", "respect") != "respect":
                problems.append(f"{pid}: robots.txt must be respected")
        elif manifest["kind"] == "extractor" and manifest.get("tests"):
            try:
                assert_package_tests_pass(d)
            except AssertionError as exc:
                problems.append(f"{pid}: package tests fail: {str(exc)[:1500]}")
    return problems


def cmd_check(ns: argparse.Namespace) -> int:
    dirs, tested = package_dirs(), set[str]()
    problems: list[str] = []
    for path in site_files(ns.sites):
        found = check_site(path, dirs, tested)
        ex.log(f"check {path.stem}: {'ok' if not found else f'{len(found)} problem(s)'}")
        problems += found
    for p in problems:
        print(f"  - {p}")
    return 1 if problems else 0


def publish(svc: ex.Services, directories: Mapping[str, Path]) -> dict[str, dict[str, str]]:
    """Create, publish and approve each package; a changed package needs a new version."""
    from jane_registry.archive import canonical_archive, files_from_dir

    refs: dict[str, dict[str, str]] = {}
    for pid, directory in directories.items():
        manifest = ex.read_json(directory / "jane-package.json")
        ref = local_ref(directory)
        svc.registry.call(
            "POST",
            "/v1/packages",
            ok=(201, 409),
            json={
                "package_id": pid,
                "kind": manifest["kind"],
                "title": manifest["title"],
                "description": manifest.get("description", ""),
                "auto_changes_allowed": False,
            },
            headers={"Idempotency-Key": ex.key()},
        )
        path = f"/v1/packages/{pid}/versions/{manifest['version']}"
        r = svc.registry.call(
            "POST",
            f"/v1/packages/{pid}/versions",
            ok=(201, 409),
            content=bytes(canonical_archive(files_from_dir(directory))),
            headers={"Content-Type": "application/zip", "Idempotency-Key": ex.key()},
        )
        version = r.json() if r.status_code == 201 else svc.registry.call("GET", path).json()
        if version["digest"] != ref["digest"]:
            raise RuntimeError(f"{pid}@{manifest['version']}: registry has another digest; bump the version")
        if version["status"] == "draft":
            version = svc.registry.call(
                "POST",
                f"{path}/status",
                json={
                    "status": "approved",
                    "reason": "examples/sites: package tests pass (setup_sites.py check)",
                },
                headers={"Idempotency-Key": ex.key()},
            ).json()
        refs[pid] = ref
        ex.log(f"registry: {pid}@{manifest['version']} {version['status']}")
    return refs


def upsert(orch: ex.Api, collection: str, id_field: str, doc: dict[str, Any]) -> int:
    if collection == "tasks":
        check = orch.call("POST", "/v1/task-validations", json=doc).json()
        if not check["valid"]:
            raise RuntimeError(f"task {doc['task_id']} is invalid: {check['errors']}")
    r = orch.call("POST", f"/v1/{collection}", ok=(201, 409), json=doc, headers={"Idempotency-Key": ex.key()})
    if r.status_code == 409:  # exists: replace it (new package versions, changed limits or schedule)
        current = orch.call("GET", f"/v1/{collection}/{doc[id_field]}")
        r = orch.call(
            "PUT",
            f"/v1/{collection}/{doc[id_field]}",
            json=doc,
            headers={"If-Match": current.headers["ETag"]},
        )
    ex.log(f"orchestrator: {collection[:-1]} {doc[id_field]} -> {r.status_code}")
    return r.status_code


def run_tasks(svc: ex.Services, task_ids: Sequence[str], timeout_s: float) -> int:
    runs = {t: ex.start_run(svc.orchestrator, t, "examples/sites: manual run") for t in task_ids}
    failed = 0
    for task_id, run_id in runs.items():
        run = ex.wait_run(svc.orchestrator, run_id, timeout_s)
        ex.log(
            f"run {task_id} ({run_id}): {run['status']} counters={run.get('counters')} error={run.get('error')}"
        )
        failed += run["status"] != "succeeded"
    return failed


def cmd_apply(ns: argparse.Namespace) -> int:
    dirs = package_dirs()
    sites = [ex.read_json(p) for p in site_files(ns.sites)]
    used = sorted({pid for site in sites for pid in refs_in(site)})
    svc = ex.Services.of_project(ns.project)
    try:
        refs = publish(svc, {pid: dirs[pid] for pid in used})
        for conn in ex.read_json(HERE.parent / "documents" / "connections.json")["connections"]:
            svc.orchestrator.call("PUT", f"/v1/connections/{conn['connection_id']}", ok=(200, 201), json=conn)
        for site in sites:
            for source in site["sources"]:
                upsert(svc.orchestrator, "sources", "source_id", resolve(source, refs))
            for task in site["tasks"]:
                upsert(svc.orchestrator, "tasks", "task_id", resolve(task, refs))
        if not ns.run:
            return 0
        return 1 if run_tasks(svc, [t["task_id"] for s in sites for t in s["tasks"]], ns.timeout) else 0
    finally:
        svc.close()


def cmd_run(ns: argparse.Namespace) -> int:
    site = ex.read_json(site_files([ns.site])[0])
    task_ids = ns.task or [t["task_id"] for t in site["tasks"]]
    svc = ex.Services.of_project(ns.project)
    try:
        return 1 if run_tasks(svc, task_ids, ns.timeout) else 0
    finally:
        svc.close()


def entity_schemas(dirs: Mapping[str, Path]) -> dict[str, list[dict[str, Any]]]:
    """entity_type -> the field schemas every package of ``dirs`` declares for it."""
    out: dict[str, list[dict[str, Any]]] = {}
    for d in dirs.values():
        manifest = ex.read_json(d / "jane-package.json")
        for e in (manifest.get("output") or {}).get("entities", []):
            out.setdefault(e["entity_type"], []).append(ex.read_json(d / e["schema"]))
    return out


def verify_site(
    svc: ex.Services, site: Mapping[str, Any], schemas: Mapping[str, list[dict[str, Any]]]
) -> dict[str, Any]:
    report: dict[str, Any] = {}
    for source_id, expected in site.get("verify", {}).items():
        for entity_type, rule in expected.items():
            items = svc.storage.pages(
                "/v1/entities",
                {"connection_id": "results-pg", "entity_type": entity_type, "scope": source_id},
            )
            required = rule.get("required", [])
            missing = {f: sum(1 for i in items if i["fields"].get(f) in (None, "", [])) for f in required}
            invalid = 0
            for item in items:
                if not any(
                    Draft202012Validator(s).is_valid(item["fields"]) for s in schemas.get(entity_type, [{}])
                ):
                    invalid += 1
            ok = len(items) >= rule.get("min", 1) and invalid == 0 and not any(missing.values())
            report[f"{source_id}/{entity_type}"] = {
                "ok": ok,
                "count": len(items),
                "min": rule.get("min", 1),
                "schema_invalid": invalid,
                "missing_required": {k: v for k, v in missing.items() if v},
                "sample": [i["fields"] for i in items[:3]],
            }
            ex.log(
                f"verify {source_id}/{entity_type}: {'ok' if ok else 'FAIL'} count={len(items)} "
                f"invalid={invalid} missing={report[f'{source_id}/{entity_type}']['missing_required']}"
            )
    return report


def cmd_verify(ns: argparse.Namespace) -> int:
    schemas = entity_schemas(package_dirs())
    svc = ex.Services.of_project(ns.project)
    out_path = ex.STACK_DIR / f"sites-{ns.project}.json"
    summary: dict[str, Any] = ex.read_json(out_path) if out_path.is_file() else {}
    try:
        failed = 0
        for path in site_files(ns.sites):
            report = verify_site(svc, ex.read_json(path), schemas)
            summary[path.stem] = {
                "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "results": report,
            }
            failed += not all(r["ok"] for r in report.values())
        ex.write_json(out_path, summary)
        ex.log(f"summary: {out_path}")
        return 1 if failed else 0
    finally:
        svc.close()


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("check")
    p.add_argument("sites", nargs="*")
    p.set_defaults(fn=cmd_check)
    p = sub.add_parser("apply")
    p.add_argument("--project", required=True)
    p.add_argument("--run", action="store_true", help="start every task of the sites once")
    p.add_argument("--timeout", type=float, default=1800)
    p.add_argument("sites", nargs="*")
    p.set_defaults(fn=cmd_apply)
    p = sub.add_parser("run")
    p.add_argument("--project", required=True)
    p.add_argument("--task", action="append")
    p.add_argument("--timeout", type=float, default=1800)
    p.add_argument("site")
    p.set_defaults(fn=cmd_run)
    p = sub.add_parser("verify")
    p.add_argument("--project", required=True)
    p.add_argument("sites", nargs="*")
    p.set_defaults(fn=cmd_verify)
    ns = ap.parse_args(argv)
    return int(ns.fn(ns))


if __name__ == "__main__":
    sys.exit(main())
