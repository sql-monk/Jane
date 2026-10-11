"""Validate editable Draw.io models, paired transparent PNGs and export drift."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def model(path: Path) -> tuple[int, int]:
    text = path.read_text(encoding="utf-8-sig")
    if re.search(r"<!\s*(DOCTYPE|ENTITY)", text, re.I):
        raise ValueError("XML declarations are forbidden")
    tree = ET.ElementTree(ET.fromstring(text))  # noqa: S314 -- DTD and entity declarations rejected above
    root = tree.getroot()
    if root is None or root.tag != "mxfile":
        raise ValueError("expected mxfile")
    models = root.findall(".//mxGraphModel")
    if len(models) != 1:
        raise ValueError("one uncompressed editable model required")
    cells = models[0].findall("./root/mxCell")
    ids = [c.get("id") for c in cells]
    if len(ids) != len(set(ids)) or not {"0", "1"} <= set(ids):
        raise ValueError("invalid or duplicate cell IDs")
    vertices = [c for c in cells if c.get("vertex") == "1"]
    edges = [c for c in cells if c.get("edge") == "1"]
    if not vertices or all("shape=image" in c.get("style", "") for c in vertices):
        raise ValueError("diagram must contain editable shapes")
    for c in vertices:
        g = c.find("mxGeometry")
        if g is None or float(g.get("width", "0")) <= 0 or float(g.get("height", "0")) <= 0:
            raise ValueError("invalid shape geometry")
    for c in edges:
        for key in ("source", "target"):
            if c.get(key) and c.get(key) not in ids:
                raise ValueError("edge references missing cell")
        if not c.get("source") and c.find('mxGeometry/mxPoint[@as="sourcePoint"]') is None:
            raise ValueError("edge missing source")
        if not c.get("target") and c.find('mxGeometry/mxPoint[@as="targetPoint"]') is None:
            raise ValueError("edge missing target")
    return len(vertices), len(edges)


def png_pixels(path: Path) -> tuple[int, int, int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("invalid PNG")
    offset = 8
    idat = []
    header = None
    while offset < len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        kind = data[offset + 4 : offset + 8]
        chunk = data[offset + 8 : offset + 8 + length]
        crc = struct.unpack(">I", data[offset + 8 + length : offset + 12 + length])[0]
        if zlib.crc32(kind + chunk) & 0xFFFFFFFF != crc:
            raise ValueError("PNG checksum mismatch")
        if kind == b"IHDR":
            header = struct.unpack(">IIBBBBB", chunk)
        if kind == b"IDAT":
            idat.append(chunk)
        offset += 12 + length
    if header is None or header[2:] != (8, 6, 0, 0, 0):
        raise ValueError("RGBA PNG required")
    width, height = header[:2]
    if not 0 < width <= 24000 or not 0 < height <= 24000:
        raise ValueError("invalid PNG dimensions")
    raw = zlib.decompress(b"".join(idat))
    stride = width * 4 + 1
    if len(raw) != stride * height:
        raise ValueError("invalid PNG scanline length")
    previous = bytes(width)
    transparent = visible = 0
    for row in range(height):
        start = row * stride
        filtering = raw[start]
        alpha = bytearray(raw[start + 4 : start + stride : 4])
        if filtering not in range(5):
            raise ValueError("invalid PNG filter")
        if filtering:
            for i, encoded in enumerate(alpha):
                left = alpha[i - 1] if i else 0
                above = previous[i]
                upper_left = previous[i - 1] if i else 0
                if filtering == 1:
                    predictor = left
                elif filtering == 2:
                    predictor = above
                elif filtering == 3:
                    predictor = (left + above) // 2
                else:
                    estimate = left + above - upper_left
                    distances = [abs(estimate - left), abs(estimate - above), abs(estimate - upper_left)]
                    predictor = (left, above, upper_left)[distances.index(min(distances))]
                alpha[i] = (encoded + predictor) & 255
        if row == 0 and alpha[0] != 0:
            raise ValueError("transparent outer background required")
        zeros = alpha.count(0)
        transparent += zeros
        visible += width - zeros
        previous = bytes(alpha)
    if not transparent or not visible:
        raise ValueError("PNG requires visible content and transparent background")
    return width, height, transparent, visible


def png(path: Path) -> tuple[int, int]:
    width, height, _, _ = png_pixels(path)
    return width, height


def check(root: Path = ROOT) -> tuple[list[str], dict[str, int]]:
    failures = []
    folder = root / "docs/diagrams"
    sources = sorted(folder.rglob("*.drawio"))
    manifest = folder / "manifest.json"
    if not manifest.is_file():
        return ["Draw.io export manifest missing"], {"sources": len(sources), "pngs": 0}
    entries = json.loads(manifest.read_text(encoding="utf-8")).get("diagrams", [])
    records = {(e["source"], e["theme"]): e for e in entries}
    expected = set()
    pngs = 0
    for source in sources:
        rel = source.relative_to(root).as_posix()
        try:
            vertices, edges = model(source)
        except (ValueError, ET.ParseError) as e:
            failures.append(f"{rel}: {e}")
            continue
        for theme in ("light", "dark"):
            expected.add((rel, theme))
            image = source.with_suffix(f".{theme}.png")
            record = records.get((rel, theme))
            try:
                if not image.is_file():
                    raise ValueError("themed PNG missing")
                width, height, transparent, visible = png_pixels(image)
                dimensions = (width, height)
                pngs += 1
                if not record:
                    raise ValueError("export evidence missing")
                if record["source_sha256"] != sha(source) or record["png_sha256"] != sha(image):
                    raise ValueError("source/PNG drift; export both themes")
                if record["vertices"] != vertices or record["edges"] != edges:
                    raise ValueError("model/export structural mismatch")
                if min(record.get("transparentPixels", 0), record.get("visiblePixels", 0)) <= 0:
                    raise ValueError("pixel evidence absent or empty")
                if (transparent, visible) != (record["transparentPixels"], record["visiblePixels"]):
                    raise ValueError("pixel evidence mismatch")
                if dimensions != (record["width"] * 2, record["height"] * 2):
                    raise ValueError("PNG geometry mismatch")
            except (ValueError, KeyError, OSError, struct.error, zlib.error) as e:
                failures.append(f"{rel} {theme}: {e}")
    if set(records) != expected:
        failures.append("Draw.io export manifest includes stale or missing sources")
    return failures, {"sources": len(sources), "pngs": pngs}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=ROOT)
    ns = ap.parse_args()
    failures, counts = check(ns.root.resolve())
    print(f"Draw.io check: {counts['sources']} sources, {counts['pngs']} PNGs, {len(failures)} errors")
    print("\n".join(failures[:40]))
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
