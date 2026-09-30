"""Stop (м'яко): нагадує виконавцю про звіт docs/delivery/WP-NN.md із виводом команд.

Блокує зупинку лише один раз (stop_hook_active), щоб не було циклів.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jane_wp import find_root, read_wp  # noqa: E402


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    if data.get("stop_hook_active"):
        return 0
    root = find_root(Path(data.get("cwd") or "."))
    if root is None:
        return 0
    wp = read_wp(root)
    if wp is None:
        return 0
    report = root / "docs" / "delivery" / f"WP-{wp}.md"
    if not report.is_file():
        reason = f"Звіту {report.relative_to(root).as_posix()} ще немає. Якщо WP завершено, заповніть його за шаблоном скіла jane-wp."
    elif "```" not in report.read_text(encoding="utf-8"):
        reason = f"У {report.relative_to(root).as_posix()} немає блоків із виводом команд перевірки. Додайте реальний вивід або явно позначте, що не запускалося."
    else:
        return 0
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"check_report hook error (ignored): {exc}", file=sys.stderr)
        sys.exit(0)
