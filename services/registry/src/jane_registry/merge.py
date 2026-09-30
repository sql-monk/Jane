"""Three-way merge for an explicit upstream port (``POST /v1/packages/{id}/upstream-ports``).

* **base** - files of the parent version last ported into the fork (``fork_of.version`` or the latest
  ``provenance.upstream_port.parent_version`` of the fork's history up to ``base_version``);
* **theirs** - files of the requested parent version;
* **ours** - files of the fork's ``base_version``.

Files: unchanged on one side -> the other side wins; the same change on both sides -> taken once;
both sides changed a text file -> line-based merge (merge3 over ``difflib`` matching blocks);
overlapping changes, binary changes on both sides, or modify/delete -> conflict.

The manifest is merged as JSON (objects key by key, other values whole). Fork-specific keys
(``package_id``, ``version``, ``fork_of``, ``provenance``) always come from the fork and are set by
the registry afterwards. Nothing is applied when any conflict exists.
"""

from __future__ import annotations

import difflib
import json
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from .archive import MANIFEST_NAME
from .diffing import escape_pointer, is_text

__all__ = ["FORK_OWNED_KEYS", "MergeConflict", "MergeResult", "merge3_lines", "merge_packages"]

FORK_OWNED_KEYS = frozenset({"package_id", "version", "fork_of", "provenance"})
_MISSING: Any = object()


@dataclass(frozen=True)
class MergeConflict:
    path: str
    reason: str
    pointer: str | None = None

    def wire(self) -> dict[str, str]:
        out = {"path": self.path, "reason": self.reason}
        if self.pointer is not None:
            out["pointer"] = self.pointer
        return out


@dataclass
class MergeResult:
    files: dict[str, bytes] = field(default_factory=dict)
    manifest: dict[str, Any] = field(default_factory=dict)
    conflicts: list[MergeConflict] = field(default_factory=list)
    changed_paths: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------------------- lines
def _intersect(ra: tuple[int, int], rb: tuple[int, int]) -> tuple[int, int] | None:
    lo, hi = max(ra[0], rb[0]), min(ra[1], rb[1])
    return (lo, hi) if lo < hi else None


def _sync_regions(
    base: Sequence[str], a: Sequence[str], b: Sequence[str]
) -> list[tuple[int, int, int, int, int, int]]:
    am = difflib.SequenceMatcher(None, base, a, autojunk=False).get_matching_blocks()
    bm = difflib.SequenceMatcher(None, base, b, autojunk=False).get_matching_blocks()
    ia = ib = 0
    regions: list[tuple[int, int, int, int, int, int]] = []
    while ia < len(am) and ib < len(bm):
        abase, amatch, alen = am[ia]
        bbase, bmatch, blen = bm[ib]
        i = _intersect((abase, abase + alen), (bbase, bbase + blen))
        if i:
            intbase, intend = i
            intlen = intend - intbase
            asub = amatch + (intbase - abase)
            bsub = bmatch + (intbase - bbase)
            regions.append((intbase, intend, asub, asub + intlen, bsub, bsub + intlen))
        if abase + alen < bbase + blen:
            ia += 1
        else:
            ib += 1
    regions.append((len(base), len(base), len(a), len(a), len(b), len(b)))
    return regions


def _merge_regions(base: Sequence[str], a: Sequence[str], b: Sequence[str]) -> Iterator[tuple[Any, ...]]:
    iz = ia = ib = 0
    for zmatch, zend, amatch, aend, bmatch, bend in _sync_regions(base, a, b):
        if amatch - ia or bmatch - ib:
            base_part, a_part, b_part = base[iz:zmatch], a[ia:amatch], b[ib:bmatch]
            if a_part == b_part:
                yield ("same", a_part)
            elif base_part == a_part:
                yield ("take", b_part)
            elif base_part == b_part:
                yield ("take", a_part)
            else:
                yield ("conflict", base_part, a_part, b_part)
        ia, ib, iz = amatch, bmatch, zmatch
        if zend - zmatch > 0:
            yield ("same", base[zmatch:zend])
            iz, ia, ib = zend, aend, bend


def merge3_lines(base: Sequence[str], ours: Sequence[str], theirs: Sequence[str]) -> tuple[list[str], int]:
    """Merged lines and the number of conflicting hunks (0 = clean)."""
    out: list[str] = []
    conflicts = 0
    for region in _merge_regions(base, ours, theirs):
        if region[0] == "conflict":
            conflicts += 1
        else:
            out.extend(region[1])
    return out, conflicts


# ---------------------------------------------------------------------------------------- json
def _merge_json(
    base: Any, ours: Any, theirs: Any, pointer: str, conflicts: list[MergeConflict], skip: frozenset[str]
) -> Any:
    if all(isinstance(x, Mapping) for x in (base, ours, theirs)):
        merged: dict[str, Any] = {}
        keys = list(ours) + [k for k in theirs if k not in ours]
        for key in keys:
            if pointer == "" and key in skip:
                merged[key] = ours.get(key, _MISSING)
                if merged[key] is _MISSING:
                    del merged[key]
                continue
            value = _merge_json(
                base.get(key, _MISSING),
                ours.get(key, _MISSING),
                theirs.get(key, _MISSING),
                f"{pointer}/{escape_pointer(str(key))}",
                conflicts,
                skip,
            )
            if value is not _MISSING:
                merged[key] = value
        return merged
    if _same(ours, theirs):
        return ours
    if _same(base, ours):
        return theirs
    if _same(base, theirs):
        return ours
    conflicts.append(MergeConflict(MANIFEST_NAME, "both sides changed the value", pointer or "/"))
    return ours


def _same(x: Any, y: Any) -> bool:
    if x is _MISSING or y is _MISSING:
        return x is y
    return bool(x == y and type(x) is type(y))


# ---------------------------------------------------------------------------------------- package
def merge_packages(
    base: Mapping[str, bytes],
    ours: Mapping[str, bytes],
    theirs: Mapping[str, bytes],
    *,
    max_merge_file_bytes: int,
) -> MergeResult:
    result = MergeResult()
    try:
        manifests = [json.loads(side[MANIFEST_NAME]) for side in (base, ours, theirs)]
    except (KeyError, ValueError) as exc:
        result.conflicts.append(MergeConflict(MANIFEST_NAME, f"manifest cannot be read: {exc}"))
        return result
    base_m, ours_m, theirs_m = manifests
    result.manifest = _merge_json(base_m, ours_m, theirs_m, "", result.conflicts, FORK_OWNED_KEYS)

    for path in sorted((set(base) | set(ours) | set(theirs)) - {MANIFEST_NAME}):
        b, o, t = base.get(path), ours.get(path), theirs.get(path)
        if o == t:
            merged = o
        elif b == o:
            merged = t
        elif b == t:
            merged = o
        elif o is None or t is None:
            result.conflicts.append(MergeConflict(path, "modified on one side, deleted on the other"))
            continue
        elif not all(x is None or is_text(x) for x in (b, o, t)):
            result.conflicts.append(MergeConflict(path, "binary file changed on both sides"))
            continue
        elif max(len(x) for x in (b or b"", o, t)) > max_merge_file_bytes:
            result.conflicts.append(
                MergeConflict(path, "file changed on both sides is larger than diff.max_merge_file_bytes")
            )
            continue
        else:
            lines, n = merge3_lines(
                (b or b"").decode("utf-8").splitlines(keepends=True),
                o.decode("utf-8").splitlines(keepends=True),
                t.decode("utf-8").splitlines(keepends=True),
            )
            if n:
                result.conflicts.append(MergeConflict(path, f"{n} conflicting hunk(s)"))
                continue
            merged = "".join(lines).encode("utf-8")
        if merged is not None:
            result.files[path] = merged
        if merged != o:
            result.changed_paths.append(path)
    return result
