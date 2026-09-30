"""PreToolUse (Bash|PowerShell): заборони для паралельної роботи агентів.

Завжди:  `git push --force`/`-f`/`--force-with-lease`, `docker compose down -v` без `-p`.
У checkout виконавця (є `.jane-wp`): push у main, `git merge`, перемикання на main,
видалення або перезапис `.jane-wp` і `.claude/wp-paths.json`.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jane_wp import find_root, read_wp  # noqa: E402

ALWAYS = [
    (r"\bgit\b[^;&|\n]*\bpush\b[^;&|\n]*(\s--force\b|\s--force-with-lease\b|\s-[a-zA-Z]*f\b|\s\+\S)",
     "force push заборонено (plan.md §7: зливає лише координатор)."),
]

WP_ONLY = [
    (r"\bgit\b[^;&|\n]*\bpush\b[^;&|\n]*\b(main|master)\b",
     "push у main заборонено: зливає лише координатор."),
    (r"\bgit\b[^;&|\n]*\bmerge\b(?!-)",
     "git merge у checkout виконавця заборонено: зливає лише координатор."),
    (r"\bgit\b[^;&|\n]*\b(checkout|switch)\b\s+(-\S+\s+)*(main|master)\b",
     "перемикання на main заборонено: працюйте у своїй гілці wp/NN-*."),
    # Worktree мають спільні refs: ці команди змінюють main або чужі гілки в обхід злиття.
    (r"\bgit\b[^;&|\n]*\bbranch\b[^;&|\n]*\s(-f|--force|-D|-d|--delete|-M|-m|--move|-C|-c|--copy)\b",
     "примусове переміщення, видалення чи перейменування гілок заборонено: спільні refs між worktree."),
    (r"\bgit\b[^;&|\n]*\bbranch\b[^;&|\n]*\b(main|master)\b",
     "операції з гілкою main у checkout виконавця заборонено."),
    (r"\bgit\b[^;&|\n]*\b(fetch|push)\b[^;&|\n]*\S:\S",
     "refspec із `:` заборонено: так можна переписати main або чужу гілку."),
    (r"\bgit\b[^;&|\n]*\b(update-ref|symbolic-ref)\b",
     "пряма зміна refs заборонена."),
    (r"\bgit\b[^;&|\n]*\bworktree\b[^;&|\n]*\b(remove|prune|move)\b",
     "керування worktree — лише координатор."),
    (r"(\.jane-wp|wp-paths\.json)",
     "`.jane-wp` і `.claude/wp-paths.json` змінює лише координатор."),
]


def compose_down_v_without_p(cmd: str) -> bool:
    for seg in re.split(r"[;&|\n]+", cmd):
        if re.search(r"\bdocker[\s-]+compose\b.*\bdown\b", seg) and re.search(r"\s(-v|--volumes)\b", seg):
            if not re.search(r"\s(-p|--project-name)[\s=]\S+", seg):
                return True
    return False


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    cmd = (data.get("tool_input") or {}).get("command") or ""
    if not cmd:
        return 0
    problems = [msg for pat, msg in ALWAYS if re.search(pat, cmd)]
    if compose_down_v_without_p(cmd):
        problems.append("`docker compose down -v` лише з `-p <унікальне-ім'я>`, щоб не знести томи іншого агента.")
    root = find_root(Path(data.get("cwd") or "."))
    if root is not None and read_wp(root) is not None:
        # Читання маркера дозволене; блокуємо лише очевидні зміни.
        for pat, msg in WP_ONLY:
            if pat.startswith(r"(\.jane-wp"):
                if re.search(pat, cmd) and re.search(r"\b(rm|del|Remove-Item|mv|move|Move-Item|Set-Content|Out-File|tee)\b|>", cmd):
                    problems.append(msg)
            elif re.search(pat, cmd):
                problems.append(msg)
    if not problems:
        return 0
    print("Jane guard: " + " ".join(problems), file=sys.stderr)
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"guard_bash hook error (ignored): {exc}", file=sys.stderr)
        sys.exit(0)
