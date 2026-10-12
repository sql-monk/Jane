"""Real sites on a running Jane stack: product catalogs with prices, car and classified ads, news and Telegram.

Every site is one declarative file ``sites/<site>.json``::

    {
      "site": "makeup", "group": "catalog", "title": "...", "url": "https://...",
      "sources": [<source.schema.json documents>],
      "tasks": [<task-config.schema.json documents>],
      "verify": {"<source_id>": {"<entity_type or glob>": {"min": 50, "required": ["title", "price"]}}}
    }

A package reference is written as the string ``"@pkg:<package_id>"`` and resolves to ``{package_id, version,
digest}`` of the package directory (``packages/``, ``../shops/packages`` or the storage packages); the digest is
that of the registry's canonical archive. Connection ids are those of ``../documents/connections.json``.
RAW goes to ``jane.storage-files`` / ``raw-files``, entities to ``jane.storage-mongodb`` / ``results-mongo``
(a MongoDB collection per entity type). A ``verify`` key with ``*`` (``product_*``) stands for every entity
type the site's extractors declare that matches it: a catalog writes ``product_<group>`` types chosen by the
extractor from the shop's category table (``CATEGORY_TYPES`` in each extractor of the site, the same table in
the card and the price extractor).

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
import ast
import json
import sys
import time
from collections.abc import Iterable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import jane_examples as ex  # noqa: E402 - examples/jane_examples.py: contract-validated API clients

SITES = HERE / "sites"
PACKAGE_ROOTS = (HERE / "packages", HERE.parent / "shops" / "packages")
CONNECTIONS = HERE.parent / "documents" / "connections.json"
RESULTS_PACKAGE = "jane.storage-mongodb"  # entities: a MongoDB collection per entity type
RESULTS_CONNECTION = "results-mongo"
STORAGE = ("jane.storage-files", RESULTS_PACKAGE)
REF = "@pkg:"
DUMMY_DIGEST = "sha256:" + "0" * 64
# A catalog extractor chooses product_<group> by the shop's category table; every extractor of one catalog
# site carries the same table and the same lookup (the price task must write the type the card task wrote).
CATEGORY_TABLE = "CATEGORY_TYPES"
CATEGORY_OTHER = "OTHER_TYPE"
CATEGORY_LOOKUP = ("APOSTROPHES", "_section", "TYPES_BY_PREFIX", "_mapped_type")
# Product types of the taxonomy (docs/delivery/mongo-entities.md, docs/reference/entity-types.md).
PRODUCT_TYPES = frozenset(
    {
        "product_food",
        "product_beauty",
        "product_household",
        "product_book",
        "product_kids",
        "product_electronics",
        "product_appliance",
        "product_tools",
        "product_garden",
        "product_home",
        "product_clothing",
        "product_auto",
        "product_pet",
        "product_sport",
        "product_office",
        "product_health",
        "product_other",
    }
)


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


def stage_package(stage: Mapping[str, Any]) -> str | None:
    handler = stage.get("handler")
    return handler[len(REF) :] if isinstance(handler, str) and handler.startswith(REF) else None


def manifest_of(dirs: Mapping[str, Path], package_id: str) -> dict[str, Any]:
    return cast(dict[str, Any], ex.read_json(dirs[package_id] / "jane-package.json"))


def declared_types(dirs: Mapping[str, Path], package_ids: Iterable[str]) -> set[str]:
    """Entity types the packages declare in ``output.entities`` (the runtime rejects any other)."""
    return {
        str(e["entity_type"])
        for pid in package_ids
        if pid in dirs
        for e in (manifest_of(dirs, pid).get("output") or {}).get("entities", [])
    }


def source_extractors(site: Mapping[str, Any], dirs: Mapping[str, Path], source_id: str) -> list[str]:
    """Extractor packages of the site's tasks that read ``source_id``, in the order of the tasks."""
    found: dict[str, None] = {}
    for task in site.get("tasks", []):
        if task.get("input", {}).get("source_id") != source_id:
            continue
        for stage in task.get("stages", []):
            pid = stage_package(stage)
            if pid is not None and pid in dirs and manifest_of(dirs, pid)["kind"] == "extractor":
                found[pid] = None
    return list(found)


def verify_types(key: str, declared: Iterable[str]) -> list[str]:
    """A ``verify`` key: one entity type, or a glob (``product_*``) over the types the extractors declare."""
    if any(ch in key for ch in "*?["):
        return sorted(t for t in declared if fnmatchcase(t, key))
    return [key]


def results_connection(site: Mapping[str, Any], source_id: str) -> str:
    """``connections.target`` of the entity storage stage of the source's tasks."""
    for task in site.get("tasks", []):
        if task.get("input", {}).get("source_id") != source_id:
            continue
        for stage in task.get("stages", []):
            target = (stage.get("connections") or {}).get("target")
            if stage_package(stage) == RESULTS_PACKAGE and target:
                return str(target)
    return RESULTS_CONNECTION


def category_code(directory: Path) -> dict[str, Any] | None:
    """Category table, default type and lookup functions of an extractor's module, read from its syntax tree
    (nothing is imported); ``None`` when the module has no table."""
    entry = ex.read_json(directory / "jane-package.json").get("entry") or {}
    relative = Path(*str(entry.get("module", "")).split(".")).with_suffix(".py")
    source = next(
        (root / relative for root in (directory / "src", directory) if (root / relative).is_file()), None
    )
    if source is None:
        return None
    found: dict[str, Any] = {}
    for node in ast.parse(source.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign | ast.AnnAssign) and node.value is not None:
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name) and target.id in (CATEGORY_TABLE, CATEGORY_OTHER):
                    found[target.id] = ast.literal_eval(node.value)
                elif isinstance(target, ast.Name) and target.id in CATEGORY_LOOKUP:
                    found[target.id] = ast.dump(node.value)
        elif isinstance(node, ast.FunctionDef) and node.name in CATEGORY_LOOKUP:
            found[node.name] = ast.dump(node)
    return found if CATEGORY_TABLE in found else None


def category_problems(name: str, site: Mapping[str, Any], dirs: Mapping[str, Path]) -> list[str]:
    """A catalog site: its extractors carry one and the same category table and lookup, yield only taxonomy
    types and declare exactly what they can yield; every source expects exactly the declared types."""
    if site.get("group") != "catalog":
        return []
    problems: list[str] = []
    reference: tuple[str, dict[str, Any]] | None = None
    for source in site.get("sources", []):
        source_id = str(source.get("source_id"))
        extractors = source_extractors(site, dirs, source_id)
        for pid in extractors:
            code = category_code(dirs[pid])
            if code is None:
                problems.append(f"{name}: {pid}: no {CATEGORY_TABLE} table in the entry module")
                continue
            missing = [n for n in (CATEGORY_OTHER, *CATEGORY_LOOKUP) if n not in code]
            if missing:
                problems.append(f"{name}: {pid}: the category lookup lacks {missing}")
            table: dict[tuple[str, ...], str] = code[CATEGORY_TABLE]
            other = code.get(CATEGORY_OTHER)
            yielded = set(table.values())
            unknown = sorted((yielded | {str(other)}) - PRODUCT_TYPES)
            if unknown:
                problems.append(f"{name}: {pid}: types outside the taxonomy: {unknown}")
            declared = declared_types(dirs, [pid])
            if not yielded <= declared or not declared <= yielded | {other}:
                problems.append(
                    f"{name}: {pid}: output.entities {sorted(declared)} must cover the table types "
                    f"{sorted(yielded)} (and may add {other})"
                )
            if reference is None:
                reference = (pid, code)
            elif code != reference[1]:
                problems.append(f"{name}: {pid}: category table or lookup differs from {reference[0]}")
        expected = set(source.get("expected_entity_types") or [])
        declared = declared_types(dirs, extractors)
        if expected != declared:
            problems.append(
                f"{name}: source {source_id}: expected_entity_types {sorted(expected)} differ from the types "
                f"its extractors declare {sorted(declared)}"
            )
    return problems


def connection_problems(name: str, site: Mapping[str, Any], dirs: Mapping[str, Path]) -> list[str]:
    """Every connection a stage names is in ``documents/connections.json`` with the kind the package requires."""
    kinds = {c["connection_id"]: c["kind"] for c in ex.read_json(CONNECTIONS)["connections"]}
    problems: list[str] = []
    for task in site.get("tasks", []):
        for stage in task.get("stages", []):
            pid = stage_package(stage)
            required = (
                {r["name"]: r["kind"] for r in manifest_of(dirs, pid).get("required_connections", [])}
                if pid is not None and pid in dirs
                else {}
            )
            for slot, connection_id in (stage.get("connections") or {}).items():
                where = f"{name}: task {task.get('task_id')} stage {stage.get('stage_id')}"
                if connection_id not in kinds:
                    problems.append(f"{where}: connection {connection_id} is not in {CONNECTIONS.name}")
                elif slot in required and required[slot] != kinds[connection_id]:
                    problems.append(
                        f"{where}: {pid} needs a {required[slot]} connection, {connection_id} is {kinds[connection_id]}"
                    )
    return problems


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
    for sid, rules in site.get("verify", {}).items():
        if sid not in source_ids:
            problems.append(f"{name}: verify names unknown source {sid}")
            continue
        declared = declared_types(dirs, source_extractors(site, dirs, sid))
        for key in rules:
            types = verify_types(key, declared)
            if not types or not set(types) <= declared:
                problems.append(f"{name}: verify {sid}/{key}: not a type the source's extractors declare")
    if not any(pid not in dirs for pid in used):
        problems += connection_problems(name, site, dirs)
        problems += category_problems(name, site, dirs)
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
            declared = declared_types(dirs, [pid])
            for case in manifest["tests"]:
                expected = ex.read_json(d / case["expected"]) if case.get("expected") else {}
                stray = {str(e.get("entity_type")) for e in expected.get("entities", [])} - declared
                if stray:
                    problems.append(f"{pid}: test {case['name']} expects undeclared types {sorted(stray)}")
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


@contextmanager
def reviewed_publication(
    registry: ex.Api, package_id: str, manifest: dict[str, Any], authorized: bool
) -> Iterator[None]:
    """Allow one operator-reviewed LLM upload, restoring the original policy even on failure."""
    path = f"/v1/packages/{package_id}"
    current = registry.call("GET", path)
    locked = (
        manifest.get("provenance", {}).get("created_by") == "llm"
        and not current.json()["auto_changes_allowed"]
    )
    if locked and not authorized:
        raise RuntimeError(
            f"{package_id}: use --reviewed-package-updates for this checked operator-approved version"
        )
    if locked:
        registry.call(
            "PATCH",
            path,
            content=json.dumps({"auto_changes_allowed": True}).encode(),
            headers={"If-Match": current.headers["ETag"], "Content-Type": "application/merge-patch+json"},
        )
    try:
        yield
    finally:
        if locked:
            current = registry.call("GET", path)
            registry.call(
                "PATCH",
                path,
                content=json.dumps({"auto_changes_allowed": False}).encode(),
                headers={"If-Match": current.headers["ETag"], "Content-Type": "application/merge-patch+json"},
            )
            ex.log(f"registry: {package_id} automatic-change prohibition restored")


def publish(
    svc: ex.Services, directories: Mapping[str, Path], *, reviewed_updates: bool = False
) -> dict[str, dict[str, str]]:
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
        existing = svc.registry.call("GET", path, ok=(200, 404))
        if existing.status_code == 200:
            version = existing.json()
        else:
            with reviewed_publication(svc.registry, pid, manifest, reviewed_updates):
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


def run_tasks(
    svc: ex.Services, task_ids: Sequence[str], timeout_s: float, sources: Mapping[str, str] | None = None
) -> int:
    """Tasks of different sources run together; tasks of one source (``sources``: task_id -> source_id) one
    after another - the collector keeps one collection per source state (state_key = source_id) and refuses
    a second one with 409 conflict (a full catalog and a price check of the same shop)."""
    waves: list[list[str]] = []
    per_source: dict[str, int] = {}
    for task_id in task_ids:
        source = (sources or {}).get(task_id, task_id)
        n = per_source[source] = per_source.get(source, -1) + 1
        if n == len(waves):
            waves.append([])
        waves[n].append(task_id)
    failed = 0
    for wave in waves:
        runs = {t: ex.start_run(svc.orchestrator, t, "examples/sites: manual run") for t in wave}
        for task_id, run_id in runs.items():
            run = ex.wait_run(svc.orchestrator, run_id, timeout_s)
            ex.log(
                f"run {task_id} ({run_id}): {run['status']} counters={run.get('counters')} "
                f"error={run.get('error')}"
            )
            failed += run["status"] != "succeeded"
    return failed


def task_sources(sites: Sequence[Mapping[str, Any]]) -> dict[str, str]:
    return {t["task_id"]: t["input"]["source_id"] for s in sites for t in s["tasks"]}


def cmd_apply(ns: argparse.Namespace) -> int:
    if ns.reviewed_package_updates and cmd_check(ns):
        return 1
    dirs = package_dirs()
    sites = [ex.read_json(p) for p in site_files(ns.sites)]
    used = sorted({pid for site in sites for pid in refs_in(site)})
    svc = ex.Services.of_project(ns.project)
    try:
        refs = publish(svc, {pid: dirs[pid] for pid in used}, reviewed_updates=ns.reviewed_package_updates)
        for conn in ex.read_json(HERE.parent / "documents" / "connections.json")["connections"]:
            svc.orchestrator.call("PUT", f"/v1/connections/{conn['connection_id']}", ok=(200, 201), json=conn)
        for site in sites:
            for source in site["sources"]:
                upsert(svc.orchestrator, "sources", "source_id", resolve(source, refs))
            for task in site["tasks"]:
                upsert(svc.orchestrator, "tasks", "task_id", resolve(task, refs))
        if not ns.run:
            return 0
        task_ids = [t["task_id"] for s in sites for t in s["tasks"]]
        return 1 if run_tasks(svc, task_ids, ns.timeout, task_sources(sites)) else 0
    finally:
        svc.close()


def cmd_run(ns: argparse.Namespace) -> int:
    site = ex.read_json(site_files([ns.site])[0])
    task_ids = ns.task or [t["task_id"] for t in site["tasks"]]
    svc = ex.Services.of_project(ns.project)
    try:
        return 1 if run_tasks(svc, task_ids, ns.timeout, task_sources([site])) else 0
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


def stored_entities(
    svc: ex.Services, connection: str, entity_types: Iterable[str], source_id: str
) -> list[dict[str, Any]]:
    """Current state of every entity of ``source_id`` of these types (one collection per type in MongoDB)."""
    items: list[dict[str, Any]] = []
    for entity_type in entity_types:
        items += svc.storage.pages(
            "/v1/entities", {"connection_id": connection, "entity_type": entity_type, "scope": source_id}
        )
    return items


def verify_site(svc: ex.Services, site: Mapping[str, Any], dirs: Mapping[str, Path]) -> dict[str, Any]:
    report: dict[str, Any] = {}
    for source_id, expected in site.get("verify", {}).items():
        extractors = source_extractors(site, dirs, source_id)
        schemas = entity_schemas({pid: dirs[pid] for pid in extractors})
        connection = results_connection(site, source_id)
        for key, rule in expected.items():
            types = verify_types(key, schemas)
            items = stored_entities(svc, connection, types, source_id)
            required = rule.get("required", [])
            missing = {f: sum(1 for i in items if i["fields"].get(f) in (None, "", [])) for f in required}
            invalid = 0
            for item in items:
                if not any(
                    Draft202012Validator(s).is_valid(item["fields"])
                    for s in schemas.get(item["entity_type"], [{}])
                ):
                    invalid += 1
            ok = len(items) >= rule.get("min", 1) and invalid == 0 and not any(missing.values())
            by_type: dict[str, int] = {}
            for item in items:
                by_type[item["entity_type"]] = by_type.get(item["entity_type"], 0) + 1
            report[f"{source_id}/{key}"] = {
                "ok": ok,
                "connection_id": connection,
                "count": len(items),
                "by_type": dict(sorted(by_type.items())),
                "min": rule.get("min", 1),
                "schema_invalid": invalid,
                "missing_required": {k: v for k, v in missing.items() if v},
                "sample": [i["fields"] for i in items[:3]],
            }
            ex.log(
                f"verify {source_id}/{key}: {'ok' if ok else 'FAIL'} count={len(items)} by_type={by_type} "
                f"invalid={invalid} missing={report[f'{source_id}/{key}']['missing_required']}"
            )
    return report


def cmd_verify(ns: argparse.Namespace) -> int:
    dirs = package_dirs()
    svc = ex.Services.of_project(ns.project)
    out_path = ex.STACK_DIR / f"sites-{ns.project}.json"
    summary: dict[str, Any] = ex.read_json(out_path) if out_path.is_file() else {}
    try:
        failed = 0
        for path in site_files(ns.sites):
            report = verify_site(svc, ex.read_json(path), dirs)
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
    p.add_argument(
        "--reviewed-package-updates",
        action="store_true",
        help="operator authorizes checked versions; restore package auto-change policy after each upload",
    )
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
