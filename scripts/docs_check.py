"""Static checks of the Jane documentation (DOCUMENTATION_REQUIREMENTS.md, "Перевірка оформлення").

    uv run --no-project python scripts/docs_check.py [paths...]

Checks every Markdown file of the active documentation (default: README.md, DEVELOPMENT.md, docs/ and the
README files of the modules; docs-archive/ is skipped) or the given files and directories:

* local links point to existing files; ``#anchor`` links point to an existing heading (GitHub anchor rules);
  ``#L<n>`` on a code file points to an existing line;
* every fenced code block has a language and is closed; no raw HTML outside code;
* exactly one H1, no skipped heading levels, no duplicate headings;
* an image ``*.light.png#gh-light-mode-only`` is followed by its ``*.dark.png#gh-dark-mode-only`` pair.

Stdlib only. Exit code 1 when anything fails.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from functools import cache
from itertools import pairwise
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {"docs-archive", "node_modules", ".venv", ".git", ".claude", "dist", "_generated"}
FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
LINK = re.compile(r"!?\[(?:[^\]\\]|\\.)*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HTML = re.compile(r"</?[A-Za-z][A-Za-z0-9-]*(\s[^<>]*)?/?>")


def slug(text: str) -> str:
    """GitHub heading anchor: markup removed, lowercase, punctuation dropped, spaces to hyphens."""
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[`*_]{1,3}([^`*_]+)[`*_]{1,3}", r"\1", text).strip().lower()
    kept = "".join(ch for ch in text if ch in " -_" or unicodedata.category(ch)[0] in "LNM")
    return kept.replace(" ", "-")


def strip_code(lines: list[str]) -> list[tuple[int, str]]:
    """Lines outside fenced code blocks, with their numbers."""
    out, fence = [], None
    for number, line in enumerate(lines, 1):
        m = FENCE.match(line)
        if m and (fence is None or (m.group(2)[0] == fence[0] and len(m.group(2)) >= len(fence))):
            fence = m.group(2) if fence is None else None
            continue
        if fence is None:
            out.append((number, line))
    return out


@cache
def anchors(path: Path) -> frozenset[str]:
    seen: dict[str, int] = {}
    result = set()
    for _, line in strip_code(path.read_text(encoding="utf-8").splitlines()):
        m = HEADING.match(line)
        if m:
            base = slug(m.group(2))
            n = seen.get(base, 0)
            seen[base] = n + 1
            result.add(base if n == 0 else f"{base}-{n}")
    return frozenset(result)


@cache
def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8", errors="replace").splitlines())


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    fence: tuple[int, str] | None = None
    for number, line in enumerate(lines, 1):
        m = FENCE.match(line)
        if not m:
            continue
        if fence is None:
            if not m.group(3).strip():
                errors.append(f"{number}: code block without a language")
            fence = (number, m.group(2))
        elif m.group(2)[0] == fence[1][0] and len(m.group(2)) >= len(fence[1]) and not m.group(3).strip():
            fence = None
    if fence:
        errors.append(f"{fence[0]}: code block is not closed")

    text_lines = strip_code(lines)
    levels: list[int] = []
    slugs: dict[str, int] = {}
    images: list[tuple[int, str]] = []
    for number, line in text_lines:
        bare = re.sub(r"`[^`]*`", "", line)
        for m in HTML.finditer(bare):
            errors.append(f"{number}: raw HTML {m.group(0)!r}")
        h = HEADING.match(line)
        if h:
            levels.append(len(h.group(1)))
            s = slug(h.group(2))
            if s in slugs:
                errors.append(f"{number}: duplicate heading {h.group(2)!r} (also line {slugs[s]})")
            slugs[s] = number
        for m in LINK.finditer(bare):
            target = m.group(1)
            if m.group(0).startswith("!"):
                images.append((number, target))
            errors += [f"{number}: {e}" for e in check_link(path, target)]
    if levels.count(1) != 1:
        errors.append(f"expected one H1, found {levels.count(1)}")
    for a, b in pairwise(levels):
        if b > a + 1:
            errors.append(f"heading level jumps from {a} to {b}")
    for i, (number, target) in enumerate(images):
        if target.endswith(".light.png#gh-light-mode-only"):
            pair = target.replace(".light.png#gh-light-mode-only", ".dark.png#gh-dark-mode-only")
            if i + 1 >= len(images) or images[i + 1][1] != pair:
                errors.append(f"{number}: light image without the dark pair {pair}")
    return errors


def check_link(source: Path, target: str) -> list[str]:
    if re.match(r"^[a-z][a-z0-9+.-]*:", target):
        return []
    raw, _, fragment = target.partition("#")
    if "\\" in raw:
        return [f"backslash in link {target}"]
    path = source if not raw else (source.parent / raw).resolve()
    if not path.exists():
        return [f"missing target {target}"]
    if not fragment or fragment.startswith("gh-"):
        return []
    if path.is_dir():
        return [f"anchor on a directory {target}"]
    if path.suffix.lower() == ".md":
        return [] if fragment in anchors(path) else [f"missing anchor {target}"]
    m = re.fullmatch(r"L(\d+)(?:-L(\d+))?", fragment)
    if m:
        last = int(m.group(2) or m.group(1))
        return [] if last <= line_count(path) else [f"line out of range {target}"]
    return [f"unsupported anchor {target}"]


def default_files() -> list[Path]:
    files = [ROOT / "README.md", ROOT / "DEVELOPMENT.md"]
    for path in ROOT.rglob("*.md"):
        rel = path.relative_to(ROOT).parts
        if set(rel) & SKIP_DIRS or (rel[0] != "docs" and "packages" in rel):
            continue
        if rel[0] == "docs" or path.name == "README.md":
            files.append(path)
    return sorted({f for f in files if f.is_file()})


def main(argv: list[str]) -> int:
    files: list[Path] = []
    for arg in argv:
        p = Path(arg).resolve()
        files += sorted(p.rglob("*.md")) if p.is_dir() else [p]
    files = files or default_files()
    failed = 0
    for path in files:
        errors = check_file(path)
        if errors:
            failed += 1
            print(f"FAIL {path.relative_to(ROOT).as_posix()}")
            for e in errors:
                print(f"     {e}")
    print(f"{len(files)} files checked, {failed} with errors")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
