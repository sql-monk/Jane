"""Check active Markdown links, GFM heading IDs, fences, languages and raw HTML."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

from common import LANGUAGES, ROOT, read, slug

HTML = re.compile(r"<!--|</?[A-Za-z][A-Za-z0-9-]*(?:\s+[^<>]*?|\s*/?)>")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})([^\n]*)$")
HEAD = re.compile(r"^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
LINK = re.compile(r"!?\[([^\]\n]*)\]\((<[^>]+>|[^\s)]+)(?:\s+[\"'][^\n]*?[\"'])?\)")
REFERENCE = re.compile(r"^ {0,3}\[([^\]]+)\]:\s*(<[^>]+>|\S+)", re.M)
SCHEMES = {"http", "https", "mailto", "tel", "app", "codex", "plugin", "data"}


@dataclass
class Parsed:
    anchors: set[str] = field(default_factory=set)
    links: list[tuple[int, str]] = field(default_factory=list)
    diagrams: list[tuple[int, str]] = field(default_factory=list)
    errors: list[tuple[int, str]] = field(default_factory=list)
    code_blocks: int = 0


def parse(text: str, template: bool = False) -> Parsed:
    result = Parsed()
    fence = None
    language = ""
    start = 0
    content: list[str] = []
    counts: dict[str, int] = {}
    headings: list[int] = []
    outside = []
    definitions = {}
    reference_uses = []
    for line_number, line in enumerate(text.splitlines(), 1):
        marker = FENCE.match(line)
        if fence is not None:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                if language == "mermaid":
                    result.errors.append((start, "Draw.io source and themed PNG exports are required"))
                    value = "\n".join(content)
                    result.diagrams.append((start + 1, value))
                    if HTML.search(value):
                        result.errors.append((start, "raw HTML inside Mermaid"))
                    if not re.match(
                        r"\s*(?:%%[^\n]*\n\s*)*(?:flowchart|graph|sequenceDiagram|stateDiagram(?:-v2)?|classDiagram|erDiagram|journey|gantt|pie|mindmap|timeline|gitGraph|quadrantChart|block-beta|architecture-beta|sankey-beta|xychart-beta|requirementDiagram|C4Context|C4Container)\b",
                        value,
                    ):
                        result.errors.append((start, "unknown Mermaid diagram type"))
                if language == "text" and not template:
                    first = next((x.strip() for x in content if x.strip()), "")
                    if re.match(
                        r"(?:def\s|class\s|import\s|from\s+\S+\s+import\s|export\s|const\s+\w+\s*=|(?:uv|just|docker|python|node|npm|pnpm)\s)",
                        first,
                    ):
                        result.errors.append((start, "executable code marked as text"))
                fence = None
                content = []
            else:
                content.append(line)
            continue
        if marker:
            fence = marker[1]
            info = marker[2].strip()
            language = info.split()[0].lower() if info else ""
            start = line_number
            result.code_blocks += 1
            if not language:
                result.errors.append((line_number, "code fence has no language"))
            elif language not in LANGUAGES:
                result.errors.append((line_number, f"unsupported highlighting language: {language}"))
            continue
        # Inline code is literal; preserve its contents for heading slugs, strip for HTML/links.
        clean = re.sub(r"(`+)(.*?)\1", lambda m: " " * len(m[0]), line)
        outside.append((line_number, clean))
        if HTML.search(clean):
            result.errors.append((line_number, "raw HTML"))
        heading = HEAD.match(line)
        if heading:
            level = len(heading[1])
            if headings and level > headings[-1] + 1:
                result.errors.append((line_number, "heading level is skipped"))
            headings.append(level)
            base = slug(heading[2])
            count = counts.get(base, 0)
            counts[base] = count + 1
            result.anchors.add(base if not count else f"{base}-{count}")
        # Inline-code names are common labels in links. Link extraction uses the original
        # line, but ignores links actually inside literal code spans.
        spans = [m.span() for m in re.finditer(r"(`+)(.*?)\1", line)]
        for link in LINK.finditer(line):
            if not any(a <= link.start() and link.end() <= b for a, b in spans):
                result.links.append((line_number, link[2].strip("<>")))
        for definition in REFERENCE.finditer(clean):
            definitions[definition[1].strip().casefold()] = (line_number, definition[2].strip("<>"))
        for use in re.finditer(r"!?\[([^\]\n]+)\](?:\[([^\]\n]*)\])?", clean):
            if use.end() < len(clean) and clean[use.end()] in "(:":
                continue
            reference_uses.append((line_number, (use[2] or use[1]).strip().casefold()))
    result.links += list(definitions.values())
    # Bracketed prose is legal Markdown. Validate declared reference links; fail
    # explicit [label][missing] references rather than treating tables as links.
    for line_number, clean in outside:
        for use in re.finditer(r"\[[^\]]+\]\[([^\]]*)\]", clean):
            key = use[1].strip().casefold()
            if key and key not in definitions:
                result.errors.append((line_number, f"undefined reference link: {key}"))
    if fence:
        result.errors.append((start, "unclosed code fence"))
    if headings and headings.count(1) != 1:
        result.errors.append((1, "page must have exactly one H1"))
    if not headings and not template:
        result.errors.append((1, "page has no H1"))
    return result


def active_files(root: Path) -> list[Path]:
    files = [root / x for x in ("README.md", "DOCUMENTATION_REQUIREMENTS.md", "DOCUMENTATION_PLAN.md")]
    files += sorted((root / "docs").rglob("*.md"))
    return sorted({x for x in files if x.is_file()})


def expand(root: Path, paths: list[str] | None) -> list[Path]:
    if not paths:
        return active_files(root)
    result: set[Path] = set()
    for value in paths:
        candidate = (root / value).resolve()
        if not candidate.is_relative_to(root):
            raise ValueError(f"Path outside checkout: {value}")
        if "docs-archive" in candidate.relative_to(root).parts:
            continue
        if candidate.is_dir():
            result.update(candidate.rglob("*.md"))
        elif candidate.is_file():
            result.add(candidate)
        else:
            raise ValueError(f"Document does not exist: {value}")
    return sorted(result)


def pointer_exists(path: Path, fragment: str, cache: dict[Path, Any] | None = None) -> bool:
    if not fragment.startswith("/"):
        return True  # Viewer-specific fragments are handled by its renderer.
    cache = {} if cache is None else cache
    if path in cache:
        value = cache[path]
    elif path.suffix.lower() == ".json":
        value = json.loads(read(path))
    elif path.suffix.lower() in {".yaml", ".yml"}:
        import yaml

        value = yaml.safe_load(read(path))
    else:
        return True
    cache[path] = value
    try:
        for part in fragment.split("/")[1:]:
            key = part.replace("~1", "/").replace("~0", "~")
            value = value[int(key)] if isinstance(value, list) else value[key]
        return True
    except (KeyError, IndexError, TypeError, ValueError):
        return False


def check_files(root: Path, files: list[Path]) -> tuple[list[str], dict[str, Any]]:
    cache = {}
    pointer_cache: dict[Path, Any] = {}
    source_lines = {}
    targets = {}
    exists = {}
    failures = []
    stats = {"files": len(files), "links": 0, "diagrams": 0, "code_blocks": 0}

    def parsed(path: Path) -> Parsed:
        if path not in cache:
            cache[path] = parse(read(path), "documentation-templates" in path.parts)
        return cache[path]

    for path in files:
        data = parsed(path)
        label = path.relative_to(root).as_posix()
        failures += [f"{label}:{line}: {error}" for line, error in data.errors]
        stats["diagrams"] += len(data.diagrams)
        stats["diagrams"] += sum(urlsplit(link).path.endswith(".light.png") for _, link in data.links)
        stats["code_blocks"] += data.code_blocks
        for line, link in data.links:
            stats["links"] += 1
            url = urlsplit(link)
            if url.scheme in SCHEMES or url.netloc:
                continue
            if url.scheme:
                failures.append(f"{label}:{line}: unsupported URL scheme: {url.scheme}")
                continue
            if "\\" in url.path:
                failures.append(f"{label}:{line}: path uses backslash: {link}")
                continue
            candidate = Path(os.path.abspath(path.parent / unquote(url.path))) if url.path else path
            if candidate not in targets:
                targets[candidate] = candidate.resolve()
            target = targets[candidate]
            if not target.is_relative_to(root):
                failures.append(f"{label}:{line}: link leaves checkout: {link}")
                continue
            if target not in exists:
                exists[target] = target.exists()
            if not exists[target]:
                failures.append(f"{label}:{line}: missing link target: {link}")
                continue
            fragment = unquote(url.fragment)
            if fragment and target.suffix.lower() == ".md" and fragment not in parsed(target).anchors:
                failures.append(f"{label}:{line}: missing heading anchor: {link}")
            elif fragment and re.fullmatch(r"L\d+(?:-L\d+)?", fragment):
                end = int(fragment.split("-L")[-1].removeprefix("L"))
                if target not in source_lines:
                    source_lines[target] = len(read(target).splitlines())
                if end > source_lines[target]:
                    failures.append(f"{label}:{line}: source line does not exist: {link}")
            elif fragment and not pointer_exists(target, fragment, pointer_cache):
                failures.append(f"{label}:{line}: missing JSON pointer: {link}")
    return failures, stats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--paths", nargs="+", help="Explicit Markdown files or directories; default is active docs"
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    failures, stats = check_files(root, expand(root, args.paths))
    if args.json:
        print(json.dumps({**stats, "errors": failures}, ensure_ascii=False, indent=2))
    else:
        print(
            f"Markdown check: {stats['files']} files, {stats['links']} links, {stats['diagrams']} diagrams, {stats['code_blocks']} code blocks, {len(failures)} errors"
        )
        for failure in failures[:60]:
            print(failure)
        if stats["diagrams"]:
            print("Draw.io XML/PNG validation: diagrams.py; actual page rendering: render.mjs.")
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
