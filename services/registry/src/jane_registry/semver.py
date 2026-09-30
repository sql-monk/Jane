"""Semantic Versioning 2.0.0 ordering (``SemVer`` of the contracts: exact versions, no ranges)."""

from __future__ import annotations

import re
from functools import total_ordering

__all__ = ["SEMVER_RE", "SemVer", "is_semver", "max_version", "sort_versions"]

SEMVER_RE = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-([0-9A-Za-z.-]+))?(?:\+([0-9A-Za-z.-]+))?$"
)


@total_ordering
class _Ident:
    """One dot-separated pre-release identifier: numeric identifiers sort before alphanumeric ones."""

    __slots__ = ("num", "text")

    def __init__(self, raw: str) -> None:
        self.num = int(raw) if raw.isdigit() else None
        self.text = raw

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _Ident) and (self.num, self.text) == (other.num, other.text)

    def __hash__(self) -> int:
        return hash((self.num, self.text))

    def __lt__(self, other: _Ident) -> bool:
        if self.num is not None and other.num is not None:
            return self.num < other.num
        if self.num is not None:
            return True
        if other.num is not None:
            return False
        return self.text < other.text


@total_ordering
class SemVer:
    """Parsed version; build metadata is ignored for ordering (SemVer §10)."""

    __slots__ = ("build", "core", "pre", "raw")

    def __init__(self, raw: str) -> None:
        m = SEMVER_RE.match(raw)
        if m is None:
            raise ValueError(f"not a semantic version: {raw!r}")
        self.raw = raw
        self.core = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        self.pre = tuple(_Ident(p) for p in m.group(4).split(".")) if m.group(4) else ()
        self.build = m.group(5)

    def _key(self) -> tuple[tuple[int, int, int], int, tuple[_Ident, ...]]:
        # A version without pre-release is greater than any of its pre-releases.
        return (self.core, 0 if self.pre else 1, self.pre)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, SemVer) and self._key() == other._key()

    def __hash__(self) -> int:
        return hash((self.core, self.pre))

    def __lt__(self, other: SemVer) -> bool:
        return self._key() < other._key()

    def __str__(self) -> str:
        return self.raw


def is_semver(raw: str) -> bool:
    return SEMVER_RE.match(raw) is not None


def sort_versions(versions: list[str], *, reverse: bool = False) -> list[str]:
    return sorted(versions, key=SemVer, reverse=reverse)


def max_version(versions: list[str]) -> str | None:
    return max(versions, key=SemVer) if versions else None
