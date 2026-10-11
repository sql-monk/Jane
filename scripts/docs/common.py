"""Shared deterministic helpers for documentation tooling (no production imports)."""

from __future__ import annotations

import hashlib
import json
import os
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LANGUAGES = {
    "text",
    "powershell",
    "bash",
    "sh",
    "python",
    "typescript",
    "javascript",
    "json",
    "yaml",
    "toml",
    "ini",
    "sql",
    "mermaid",
    "dockerfile",
    "xml",
    "css",
    "diff",
    "http",
    "graphql",
    "console",
    "csharp",
    "makefile",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_text(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def relative(source: Path, target: Path) -> str:
    return Path(os.path.relpath(target, source.parent)).as_posix()


def slug(text: str) -> str:
    """GitHub-style heading ID, including Cyrillic, punctuation and inline code."""
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]*>", "", text)
    text = text.replace("`", "").replace("*", "").replace("~", "")
    return "".join(
        char
        for char in text.lower()
        if not unicodedata.category(char).startswith(("P", "S", "C")) or char in "-_"
    ).replace(" ", "-")


def code(value: str, language: str) -> str:
    fence = "`" * max(3, max((len(x) for x in re.findall(r"`+", value)), default=0) + 1)
    return f"{fence}{language}\n{value.rstrip()}\n{fence}\n"


def cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def matches(path: str, pattern: str) -> bool:
    """Registry globs: * stays in a segment; ** spans directories."""
    bits = []
    i = 0
    while i < len(pattern):
        if pattern[i : i + 3] == "**/":
            bits.append("(?:.*/)?")
            i += 3
        elif pattern[i : i + 2] == "**":
            bits.append(".*")
            i += 2
        elif pattern[i] == "*":
            bits.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            bits.append("[^/]")
            i += 1
        else:
            bits.append(re.escape(pattern[i]))
            i += 1
    return re.fullmatch("".join(bits), path) is not None
