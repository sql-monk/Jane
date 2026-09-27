"""Differences between two package versions (``GET /v1/packages/{id}/diff``, ``PackageDiff``).

* ``manifest_changes`` - JSON Pointer (RFC 6901) changes of ``jane-package.json`` (objects are compared
  key by key, arrays and scalars as whole values);
* ``files`` - every other file: ``added | removed | modified | unchanged``; text files get a unified
  diff (``modified`` only), non-UTF-8 files are ``binary: true``; files above
  ``diff.max_diff_file_bytes`` get the status only.
"""

from __future__ import annotations

import difflib
from collections.abc import Mapping
from typing import Any

from .archive import MANIFEST_NAME

__all__ = ["diff_files", "diff_manifest", "escape_pointer", "is_text"]

_MISSING = object()


def escape_pointer(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


def diff_manifest(old: Any, new: Any, pointer: str = "") -> list[dict[str, Any]]:
    if isinstance(old, Mapping) and isinstance(new, Mapping):
        changes: list[dict[str, Any]] = []
        for key in sorted(set(old) | set(new), key=str):
            p = f"{pointer}/{escape_pointer(str(key))}"
            a, b = old.get(key, _MISSING), new.get(key, _MISSING)
            if a is _MISSING:
                changes.append({"pointer": p, "op": "add", "new": b})
            elif b is _MISSING:
                changes.append({"pointer": p, "op": "remove", "old": a})
            else:
                changes.extend(diff_manifest(a, b, p))
        return changes
    if old == new and type(old) is type(new):
        return []
    return [{"pointer": pointer or "/", "op": "replace", "old": old, "new": new}]


def is_text(data: bytes) -> bool:
    if b"\0" in data:
        return False
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def diff_files(
    old: Mapping[str, bytes],
    new: Mapping[str, bytes],
    *,
    context_lines: int,
    max_file_bytes: int,
    old_label: str,
    new_label: str,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for path in sorted((set(old) | set(new)) - {MANIFEST_NAME}):
        a, b = old.get(path), new.get(path)
        entry: dict[str, Any] = {"path": path}
        if a is None:
            entry["status"] = "added"
        elif b is None:
            entry["status"] = "removed"
        elif a == b:
            entry["status"] = "unchanged"
        else:
            entry["status"] = "modified"
            if not (is_text(a) and is_text(b)):
                entry["binary"] = True
            elif max(len(a), len(b)) <= max_file_bytes:
                entry["unified_diff"] = "".join(
                    difflib.unified_diff(
                        a.decode("utf-8").splitlines(keepends=True),
                        b.decode("utf-8").splitlines(keepends=True),
                        fromfile=f"{old_label}/{path}",
                        tofile=f"{new_label}/{path}",
                        n=context_lines,
                    )
                )
        present = b if b is not None else a
        if present is not None and entry["status"] != "modified" and not is_text(present):
            entry["binary"] = True
        out.append(entry)
    return out
