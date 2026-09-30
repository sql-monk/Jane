"""Make deploy/profiles (stack.py, check.py) and its harness importable for these tests (not a workspace member)."""

from __future__ import annotations

import sys
from pathlib import Path

PROFILES = Path(__file__).resolve().parents[1]
for path in (PROFILES, PROFILES / "harness", PROFILES.parents[1] / "examples"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
