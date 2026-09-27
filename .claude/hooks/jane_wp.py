"""Спільна логіка власності шляхів WP (plan.md §3.1).

Checkout виконавця містить файл `.jane-wp` з номером пакета (наприклад `WP-02`).
Дозволені шляхи беруться з `.claude/wp-paths.json`, який змінює лише координатор.
Checkout без `.jane-wp` вважається checkout координатора й не обмежується.

CLI для рев'юера й координатора:
    python .claude/hooks/jane_wp.py check-diff <base-ref> [--wp NN]
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

MARKER = ".jane-wp"
MAP_FILE = Path(".claude") / "wp-paths.json"


def find_root(start: Path) -> Path | None:
    """Корінь checkout: найближчий предок із `.git` (каталог або файл worktree)."""
    p = start if start.is_dir() else start.parent
    for candidate in (p, *p.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def read_wp(root: Path) -> str | None:
    marker = root / MARKER
    if not marker.is_file():
        return None
    m = re.search(r"(\d{2})", marker.read_text(encoding="utf-8"))
    return m.group(1) if m else "??"


@lru_cache(maxsize=None)
def _glob_to_regex(pattern: str) -> re.Pattern[str]:
    out = []
    i = 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("".join(out) + r"\Z")


def load_rules(root: Path, wp: str) -> tuple[list[str], list[str]] | None:
    map_path = root / MAP_FILE
    if not map_path.is_file():
        return None
    data = json.loads(map_path.read_text(encoding="utf-8"))
    pkg = data.get("packages", {}).get(wp)
    if pkg is None:
        return None
    allow = [p.replace("{wp}", wp) for p in data.get("common_allow", []) + pkg.get("allow", [])]
    deny = [p.replace("{wp}", wp) for p in pkg.get("deny", [])]
    return allow, deny


def check(root: Path, wp: str, rel: str) -> str | None:
    """None, якщо шлях дозволено; інакше текст причини."""
    rel = rel.replace("\\", "/").lstrip("/")
    if rel == MARKER:
        return f"`{MARKER}` уже створено; змінювати його може лише координатор."
    rules = load_rules(root, wp)
    if rules is None:
        return f"WP-{wp} не знайдено в {MAP_FILE.as_posix()}; зверніться до координатора."
    allow, deny = rules
    if any(_glob_to_regex(p).match(rel) for p in deny):
        return f"`{rel}` явно виключено з області WP-{wp}."
    if any(_glob_to_regex(p).match(rel) for p in allow):
        return None
    return (
        f"`{rel}` поза областю WP-{wp} (plan.md §5). Дозволено: {', '.join(allow)}. "
        "Опишіть потрібну зміну в розділі «Запити до інших власників» свого звіту."
    )


def relative_to_root(root: Path, target: Path) -> str | None:
    try:
        return target.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return None


def _check_diff(argv: list[str]) -> int:
    if not argv:
        print("usage: jane_wp.py check-diff <base-ref> [--wp NN]", file=sys.stderr)
        return 2
    base = argv[0]
    root = find_root(Path.cwd())
    if root is None:
        print("not inside a git checkout", file=sys.stderr)
        return 2
    wp = argv[argv.index("--wp") + 1].zfill(2) if "--wp" in argv else read_wp(root)
    if wp is None:
        print("WP unknown: pass --wp NN or create .jane-wp", file=sys.stderr)
        return 2
    out = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        cwd=root, capture_output=True, text=True, check=True,
    ).stdout
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=root, capture_output=True, text=True, check=True,
    ).stdout
    files = sorted({f for f in (out + untracked).splitlines() if f and f != MARKER})
    bad = [(f, r) for f in files if (r := check(root, wp, f))]
    for f, reason in bad:
        print(f"OUTSIDE  {f}")
    print(f"WP-{wp}: {len(files)} changed file(s), {len(bad)} outside ownership")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "check-diff":
        sys.exit(_check_diff(sys.argv[2:]))
    print(__doc__)
    sys.exit(2)
