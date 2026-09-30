"""PreToolUse (Edit|Write|NotebookEdit): блокує запис поза шляхами свого WP."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jane_wp import MARKER, check, find_root, read_wp, relative_to_root  # noqa: E402


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    tool_input = data.get("tool_input") or {}
    raw = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not raw:
        return 0
    target = Path(raw)
    if not target.is_absolute():
        target = Path(data.get("cwd") or ".") / target
    root = find_root(target)
    if root is None:
        return 0
    rel = relative_to_root(root, target)
    if rel is None:
        return 0
    wp = read_wp(root)
    if wp is None:
        # Checkout координатора або WP ще не позначено: дозволяємо, зокрема створення `.jane-wp`.
        return 0
    reason = check(root, wp, rel)
    if reason is None:
        return 0
    print(f"Jane path ownership: {reason}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # хук не повинен ламати роботу через власну помилку
        print(f"guard_paths hook error (ignored): {exc}", file=sys.stderr)
        sys.exit(0)
