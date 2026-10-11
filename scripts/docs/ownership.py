"""Check DOC ownership using its registry, without replacing numeric WP hooks."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from common import ROOT, digest, matches, read


def git(root: Path, *args: str) -> list[str]:
    result = subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)
    return result.stdout.decode("utf-8").split("\0")[:-1]


def changes(root: Path, base: str) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for args, state in (
        (["diff", "--name-status", "--no-renames", "-z", base, "HEAD"], "committed"),
        (["diff", "--name-status", "--no-renames", "-z", "--cached"], "staged"),
        (["diff", "--name-status", "--no-renames", "-z"], "unstaged"),
    ):
        fields = git(root, *args)
        for status, path in zip(fields[::2], fields[1::2], strict=True):
            result.setdefault(path, set()).add(f"{state}:{status}")
    for path in git(root, "ls-files", "--others", "--exclude-standard", "-z"):
        result.setdefault(path, set()).add("untracked:A")
    return result


def owners(registry: dict[str, Any], path: str) -> list[str]:
    found = []
    for doc, package in registry["packages"].items():
        allow = package["allow"] + [x.format(doc=doc) for x in registry.get("common_allow", [])]
        if any(matches(path, pattern) for pattern in allow) and not any(
            matches(path, pattern) for pattern in package.get("deny", [])
        ):
            found.append(doc)
    if any(matches(path, pattern) for pattern in registry.get("coordinator_allow", [])):
        found.append("coordinator")
    return found


def check(root: Path, registry: dict[str, Any], changed: dict[str, set[str]], doc: str | None) -> list[str]:
    failures = []
    inventory_path = root / "docs-archive/inventory.json"
    inventory = json.loads(read(inventory_path)) if inventory_path.exists() else {"entries": []}
    archived = {x["source"]: x for x in inventory["entries"] if x.get("action") == "archive"}
    for path, states in sorted(changed.items()):
        responsible = owners(registry, path)
        if not responsible or (doc and doc not in responsible):
            failures.append(
                f"{path}: outside {'all DOC packages' if doc is None else doc}; states={','.join(sorted(states))}; owners={','.join(responsible) or 'none'}"
            )
            continue
        if path in archived and not (root / path).exists():
            entry = archived[path]
            copy = root / entry["archive"]
            if not copy.is_file() or digest(copy) != entry["sha256"]:
                failures.append(f"{path}: deleted DOC-01 source lacks a checksum-verified archive")
        # Source-file deletion is accepted only when DOC-00 explicitly listed it.
        if (
            "DOC-01" in responsible
            and path not in archived
            and not path.startswith(("docs-archive/legacy/", "docs/delivery/documentation/"))
            and not (root / path).exists()
        ):
            failures.append(f"{path}: DOC-01 source deletion is absent from inventory")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--doc", help="Check changes against one DOC package")
    selection.add_argument("--all", action="store_true", help="Coordinator: union of all DOC ownership")
    parser.add_argument("--base", help="Default is documentation_packages.base_revision")
    parser.add_argument(
        "--paths",
        nargs="+",
        help="Scope an author's check to explicit paths/globs; not a whole-checkout acceptance",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    registry = json.loads(read(root / ".claude/wp-paths.json"))["documentation_packages"]
    if args.doc and args.doc not in registry["packages"]:
        parser.error(f"Unknown DOC package: {args.doc}")
    changed = changes(root, args.base or registry["base_revision"])
    if args.paths:
        changed = {
            path: states
            for path, states in changed.items()
            if any(matches(path, x) or path == x or path.startswith(x.rstrip("/") + "/") for x in args.paths)
        }
    failures = check(root, registry, changed, args.doc)
    print(
        f"DOC ownership: {len(changed)} paths (committed/staged/unstaged/untracked), {len(failures)} violations; {'scoped' if args.paths else 'whole checkout'}"
    )
    for failure in failures:
        print(failure)
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
