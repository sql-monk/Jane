# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11"]
# ///
"""Export and check the Draw.io diagrams of docs/diagrams (DOCUMENTATION_REQUIREMENTS.md, "Формат діаграм").

    uv run --script scripts/docs_diagrams.py export [docs/diagrams/<section>/<name>.drawio ...]
    uv run --script scripts/docs_diagrams.py check
    uv run --script scripts/docs_diagrams.py lint [sources ...]

``export`` renders every source (or the given ones) twice with the draw.io desktop CLI - ``--theme light`` and
``--theme dark``, transparent background - into ``<name>.light.png`` and ``<name>.dark.png`` next to the source,
checks the images and records SHA-256 of the source and both PNGs in ``docs/diagrams/checksums.json``.
Colors that differ between themes are written in the source as ``light-dark(#light,#dark)``.

``lint`` only parses the sources (for authors before an export). ``check`` needs no draw.io: it parses each source (edges point to existing cells, no HTML labels), checks both
PNGs (RGBA, transparent background, visible content, same size) and compares the checksums, so a source edited
without a new export fails.

draw.io executable: ``JANE_DRAWIO``, else ``C:\\Program Files\\draw.io\\draw.io.exe`` on Windows or ``drawio``
in PATH (Linux without a display: run under ``xvfb-run``). The desktop CLI may keep running after it wrote the
file, so the script waits for a stable output file and then stops the process tree.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image  # type: ignore[import-not-found]  # uv script dependency, not a workspace one

ROOT = Path(__file__).resolve().parents[1]
DIAGRAMS = ROOT / "docs" / "diagrams"
CHECKSUMS = DIAGRAMS / "checksums.json"
THEMES = ("light", "dark")
EXPORT_TIMEOUT_S = float(os.environ.get("JANE_DRAWIO_TIMEOUT_S", "90"))


def drawio_executable() -> str:
    if exe := os.environ.get("JANE_DRAWIO"):
        return exe
    if os.name == "nt":
        return r"C:\Program Files\draw.io\draw.io.exe"
    found = shutil.which("drawio") or shutil.which("draw.io")
    if not found:
        sys.exit("draw.io CLI not found: install draw.io desktop or set JANE_DRAWIO")
    return found


def sha256(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix == ".drawio":  # text: the same digest for CRLF and LF checkouts
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def key_of(source: Path) -> str:
    return source.relative_to(DIAGRAMS).with_suffix("").as_posix()


def png_path(source: Path, theme: str) -> Path:
    return source.with_name(f"{source.stem}.{theme}.png")


def stop_tree(proc: subprocess.Popen[bytes]) -> None:
    if proc.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True, check=False)
    else:
        getattr(os, "killpg")(proc.pid, signal.SIGTERM)  # noqa: B009 - POSIX only; mypy checks on Windows too
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        # On Windows the Electron process may linger in termination after taskkill; the file is complete.
        print(f"     draw.io (pid {proc.pid}) is still terminating", file=sys.stderr)


def export_one(source: Path, theme: str) -> Path:
    out = png_path(source, theme)
    out.unlink(missing_ok=True)
    cmd = [drawio_executable(), "--disable-update", "-x", "-f", "png", "-t", "--theme", theme]
    cmd += ["-b", "16", "-s", "2", "-o", str(out), str(source)]
    kwargs: dict[str, object] = {} if os.name == "nt" else {"start_new_session": True}
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kwargs)  # type: ignore[call-overload]
    deadline, last_size, stable_since = time.monotonic() + EXPORT_TIMEOUT_S, -1, 0.0
    try:
        while time.monotonic() < deadline:
            size = out.stat().st_size if out.exists() else -1
            if size > 0 and size == last_size:
                if time.monotonic() - stable_since >= 1.0:
                    return out
            else:
                last_size, stable_since = size, time.monotonic()
            if proc.poll() is not None and size <= 0:
                break
            time.sleep(0.2)
    finally:
        stop_tree(proc)
    sys.exit(f"draw.io did not export {out.relative_to(ROOT).as_posix()}")


def check_source(source: Path) -> list[str]:
    errors = []
    tree = ET.parse(source)  # noqa: S314 - repository files, not untrusted input
    cells = {c.get("id"): c for c in tree.iter("mxCell")}
    for cell in cells.values():
        style, value = cell.get("style") or "", cell.get("value") or ""
        if "html=1" in style or "<br" in value.lower():
            errors.append(f"{cell.get('id')}: HTML label")
        if cell.get("edge") == "1":
            for end in ("source", "target"):
                ref = cell.get(end)
                if ref is not None and ref not in cells:
                    errors.append(f"{cell.get('id')}: {end} {ref!r} does not exist")
    if not any(c.get("vertex") == "1" for c in cells.values()):
        errors.append("no vertices")
    return errors


def check_png(path: Path) -> list[str]:
    if not path.is_file():
        return [f"{path.name}: missing"]
    with Image.open(path) as img:
        if img.mode != "RGBA":
            return [f"{path.name}: mode {img.mode}, expected RGBA"]
        alpha = img.getchannel("A")
        lo, hi = alpha.getextrema()
        corners = [alpha.getpixel(p) for p in ((0, 0), (img.width - 1, 0), (0, img.height - 1))]
        errors = []
        if lo != 0 or any(corners):
            errors.append(f"{path.name}: background is not transparent")
        if hi == 0:
            errors.append(f"{path.name}: no visible pixels")
        return errors


def sources(args: list[str]) -> list[Path]:
    if args:
        return [Path(a).resolve() for a in args]
    return sorted(DIAGRAMS.rglob("*.drawio"))


def check(paths: list[Path]) -> int:
    recorded = json.loads(CHECKSUMS.read_text(encoding="utf-8")) if CHECKSUMS.is_file() else {}
    failed = 0
    for source in paths:
        key = key_of(source)
        errors = check_source(source)
        for theme in THEMES:
            errors += check_png(png_path(source, theme))
        sizes = {Image.open(png_path(source, t)).size for t in THEMES if png_path(source, t).is_file()}
        if len(sizes) > 1:
            errors.append(f"light and dark sizes differ: {sorted(sizes)}")
        entry = recorded.get(key)
        actual = {"drawio": sha256(source)} | {
            t: sha256(png_path(source, t)) for t in THEMES if png_path(source, t).is_file()
        }
        if entry != actual:
            errors.append("checksums differ from checksums.json: run `export`")
        status = "ok" if not errors else "FAIL"
        print(f"{status:4} {key}  {' x '.join(f'{w}x{h}' for w, h in sorted(sizes))}")
        for error in errors:
            print(f"     - {error}")
        failed += bool(errors)
    return 1 if failed else 0


def export(paths: list[Path]) -> int:
    recorded = json.loads(CHECKSUMS.read_text(encoding="utf-8")) if CHECKSUMS.is_file() else {}
    for source in paths:
        if errors := check_source(source):
            sys.exit(f"{key_of(source)}: " + "; ".join(errors))
        for theme in THEMES:
            print(f"export {png_path(source, theme).relative_to(ROOT).as_posix()}")
            export_one(source, theme)
        recorded[key_of(source)] = {"drawio": sha256(source)} | {
            t: sha256(png_path(source, t)) for t in THEMES
        }
    CHECKSUMS.write_text(json.dumps(dict(sorted(recorded.items())), indent=2) + "\n", encoding="utf-8")
    return check(paths)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=("export", "check", "lint"))
    parser.add_argument("paths", nargs="*", help="sources to export (default: all of docs/diagrams)")
    ns = parser.parse_args()
    paths = sources(ns.paths)
    if ns.command == "lint":
        failed = 0
        for source in paths:
            errors = check_source(source)
            print(f"{'ok' if not errors else 'FAIL':4} {key_of(source)}")
            for error in errors:
                print(f"     - {error}")
            failed += bool(errors)
        return 1 if failed else 0
    return export(paths) if ns.command == "export" else check(paths)


if __name__ == "__main__":
    raise SystemExit(main())
