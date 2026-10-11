"""Negative fixtures for editable models, transparent PNG and source/export drift."""

from __future__ import annotations

import ast
import json
import struct
import tempfile
import zlib
from pathlib import Path

from common import ROOT, digest
from diagrams import check, model, png
from python_symbols import field_data


def test_contract_field_default_is_second_argument() -> None:
    node = ast.parse('parallel: int = contract_field("concurrency.parallel", 2, ge=1)').body[0]
    assert isinstance(node, ast.AnnAssign)
    result = field_data(node)
    assert result["default"] == "2"
    assert result["constraints"] == {"ge": "1", "contract_key": "'concurrency.parallel'"}
    assert result["required"] is False


SOURCE = '<mxfile><diagram><mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/><mxCell id="a" vertex="1" parent="1"><mxGeometry width="40" height="30" as="geometry"/></mxCell><mxCell id="b" vertex="1" parent="1"><mxGeometry x="80" width="40" height="30" as="geometry"/></mxCell><mxCell id="e" edge="1" source="a" target="b" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell></root></mxGraphModel></diagram></mxfile>'


def fixture_png(opaque: bool = False, rgba: bool = True, empty: bool = False) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    color = 6 if rgba else 2
    header = struct.pack(">IIBBBBB", 2, 2, 8, color, 0, 0, 0)
    first = bytes([0, 0, 0, 255 if opaque else 0, 0, 0, 0, 0])
    second = bytes([30, 60, 90, 0 if empty else 255, 0, 0, 0, 0])
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(b"\x00" + first + b"\x00" + second))
        + chunk(b"IEND", b"")
    )


def test_models_reject_bad_references_flat_images_and_dtd() -> None:
    base = ROOT / ".jane/doc-tests"
    base.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=base) as directory:
        path = Path(directory) / "diagram.drawio"
        path.write_text(SOURCE, encoding="utf-8")
        assert model(path) == (2, 1)
        for bad in [
            SOURCE.replace('target="b"', 'target="missing"'),
            SOURCE.replace('vertex="1"', 'style="shape=image" vertex="1"'),
            '<!DOCTYPE mxfile [<!ENTITY x "bad">]>' + SOURCE,
        ]:
            path.write_text(bad, encoding="utf-8")
            try:
                model(path)
            except ValueError:
                pass
            else:
                raise AssertionError("invalid model accepted")


def test_png_rejects_opaque_rgb_and_corruption() -> None:
    base = ROOT / ".jane/doc-tests"
    base.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=base) as directory:
        path = Path(directory) / "diagram.png"
        path.write_bytes(fixture_png())
        assert png(path) == (2, 2)
        for bad in [
            fixture_png(opaque=True),
            fixture_png(rgba=False),
            fixture_png(empty=True),
            fixture_png()[:-2] + b"xx",
        ]:
            path.write_bytes(bad)
            try:
                png(path)
            except ValueError:
                pass
            else:
                raise AssertionError("invalid PNG accepted")


def test_source_change_and_missing_theme_fail_export_gate() -> None:
    base = ROOT / ".jane/doc-tests"
    base.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=base) as directory:
        root = Path(directory)
        folder = root / "docs/diagrams"
        folder.mkdir(parents=True)
        source = folder / "sample.drawio"
        source.write_text(SOURCE, encoding="utf-8")
        records = []
        for theme in ["light", "dark"]:
            image = source.with_suffix(f".{theme}.png")
            image.write_bytes(fixture_png())
            records.append(
                {
                    "source": "docs/diagrams/sample.drawio",
                    "theme": theme,
                    "source_sha256": digest(source),
                    "png_sha256": digest(image),
                    "vertices": 2,
                    "edges": 1,
                    "width": 1,
                    "height": 1,
                    "transparentPixels": 3,
                    "visiblePixels": 1,
                }
            )
        (folder / "manifest.json").write_text(json.dumps({"diagrams": records}), encoding="utf-8")
        assert check(root)[0] == []
        source.write_text(SOURCE.replace('width="40"', 'width="45"'), encoding="utf-8")
        assert any("drift" in x for x in check(root)[0])
        source.with_suffix(".dark.png").unlink()
        assert any("missing" in x for x in check(root)[0])
