"""Meaningful negative/coverage fixtures for source extraction and documentation gates."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check import check_files, parse
from common import ROOT, digest, matches, slug
from generate import operations, synchronize
from ownership import check, owners
from python_symbols import configuration, extract


def temporary() -> tempfile.TemporaryDirectory[str]:
    base = ROOT / ".jane/doc-tests"
    base.mkdir(parents=True, exist_ok=True)
    directory = tempfile.TemporaryDirectory(dir=base)
    if not Path(directory.name).resolve().is_relative_to(base.resolve()):
        raise ValueError("Temporary fixture outside workspace")
    return directory


class CoverageTests(unittest.TestCase):
    def test_ast_public_members_reexports_and_inherited_configuration(self) -> None:
        with temporary() as directory:
            root = Path(directory)
            source_root = root / "libs/library/src"
            pkg = source_root / "library"
            pkg.mkdir(parents=True)
            source = pkg / "types.py"
            source.write_text(
                """from dataclasses import dataclass, field
from enum import Enum
__all__ = ["Base", "Thing", "Mode", "Settings"]
class Base:
    inherited: str = "yes"
    def run(self, item: str, /, *, repeat: int = 2) -> str:
        raise ValueError("bad")
@dataclass
class Thing(Base):
    number: int = 2
    values: list[str] = field(default_factory=list)
    @property
    def value(self) -> int:
        return self.number
    @value.setter
    def value(self, new: int) -> None:
        self.number = new
class Mode(Enum):
    FIRST = "first"
class Settings(Base):
    model_config = SettingsConfigDict(env_prefix="DEMO_")
    port: int = Field(default=8200, ge=1)
def hidden_by_all():
    pass
""",
                encoding="utf-8",
            )
            init = pkg / "__init__.py"
            init.write_text('from .types import Thing\n__all__ = ["Thing"]\n', encoding="utf-8")
            symbols, modules, inputs = extract(
                root, [("library", source, source_root), ("library", init, source_root)]
            )
            by_id = {x["id"]: x for x in symbols}
            assert "library.types.hidden_by_all" not in by_id
            assert by_id["library.Thing"]["target"] == "library.types.Thing"
            assert by_id["library.types.Thing.value"]["writable"]
            assert by_id["library.types.Base.run"]["raises"] == ["ValueError"]
            assert "/" in by_id["library.types.Base.run"]["signature"]
            assert "*" in by_id["library.types.Base.run"]["signature"]
            assert "library.types.Thing.__init__" in by_id
            assert "FIRST" in [x["name"] for x in symbols]
            assert "run" in [x["name"] for x in by_id["library.types.Thing"]["members"] if x["inherited"]]
            config = configuration(symbols, modules)
            assert any(x["environment"] == "DEMO_INHERITED" for x in config)
            assert next(x for x in config if x.get("environment") == "DEMO_PORT")["constraints"]["ge"] == "1"
            assert inputs[0]["sha256"] == digest(source)

    def test_typescript_compiler_includes_exports_public_members_and_overloads(self) -> None:
        with temporary() as directory:
            root = Path(directory)
            src = root / "web/admin/src"
            src.mkdir(parents=True)
            (src / "demo.ts").write_text(
                """export interface Input { value: string; optional?: number; }
export class Base { inherited(): string { return "ok"; } }
export class Service extends Base {
  private secret = 1;
  protected hidden = 2;
  readonly name: string = "test";
  static make(): Service { return new Service("x"); }
  constructor(public value: string) { super(); }
  get count(): number { return 2; }
  set count(value: number) {}
  run(value: string): string;
  run(value: number): number;
  run(value: string | number): string | number { return value; }
}
const internal = 1;
export { Service as Worker };
""",
                encoding="utf-8",
            )
            result = subprocess.run(
                ["node", str(ROOT / "scripts/docs/typescript-symbols.mjs"), str(root)],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            parsed = json.loads(result.stdout)
            by_id = {x["id"]: x for x in parsed["symbols"]}
            assert parsed["parser"] == "typescript-compiler-api"
            assert "admin.demo.Service.constructor" in by_id
            assert "admin.demo.Service.value" in by_id
            assert "admin.demo.Service.make" in by_id
            assert "admin.demo.Service.inherited" in by_id
            assert by_id["admin.demo.Service.count"]["writable"]
            assert not by_id["admin.demo.Service.name"]["writable"]
            assert by_id["admin.demo.Service.run"]["overloads"]
            assert "admin.demo.Service.secret" not in by_id
            assert "admin.demo.internal" not in by_id
            assert by_id["admin.demo.Worker"]["reexport"]

    def test_openapi_common_path_refs_and_schema_links(self) -> None:
        with temporary() as directory:
            root = Path(directory)
            folder = root / "contracts/openapi"
            folder.mkdir(parents=True)
            (folder / "common.yaml").write_text(
                """components:
  pathItems:
    Health:
      get:
        operationId: health
        parameters:
          - {name: trace, in: query, schema: {type: string}}
        responses:
          '200': {description: OK, content: {application/json: {schema: {$ref: '#/components/schemas/State'}}}}
          '503': {description: Unavailable}
  schemas:
    State: {type: object}
""",
                encoding="utf-8",
            )
            (folder / "collector.v1.yaml").write_text(
                "openapi: 3.1.0\nsecurity: [{bearer: []}]\npaths:\n  /v1/health:\n    $ref: 'common.yaml#/components/pathItems/Health'\n",
                encoding="utf-8",
            )
            records, inputs = operations(root)
            assert len(records) == 2
            assert records[0]["parameters"][0]["name"] == "trace"
            assert records[0]["errors"] == ["503"]
            assert records[0]["schema_links"][0]["file"] == "contracts/openapi/common.yaml"
            assert len(inputs) == 2

    def test_drift_and_removed_member_outputs_fail_without_touching_manual_docs(self) -> None:
        with temporary() as directory:
            root = Path(directory)
            manual = root / "docs/components/demo/reference/types/README.md"
            generated = manual.parent / "generated/demo.md"
            manual.parent.mkdir(parents=True)
            manual.write_text("# Manual\n", encoding="utf-8")
            expected = {generated: "# Generated\n\n## public.member\n"}
            assert synchronize(root, expected, False)[0] == 1
            assert synchronize(root, expected, True)[0] == 0
            generated.write_text("# Generated\n", encoding="utf-8")
            assert synchronize(root, expected, True)[0] == 1
            assert manual.read_text(encoding="utf-8") == "# Manual\n"
            stale = generated.parent / "removed.md"
            stale.write_text("# Removed\n", encoding="utf-8")
            assert any("stale:" in x for x in synchronize(root, expected, True)[1])


class MarkdownTests(unittest.TestCase):
    def test_negative_fences_html_levels_and_mermaid(self) -> None:
        fixtures = [
            ("# Title\n```\ncode\n```\n", "no language"),
            ("# Title\n```python\npass\n", "unclosed"),
            ('# Title\n<a id="x"></a>\n', "raw HTML"),
            ("# Title\n### skipped\n", "level is skipped"),
            ("# Title\n```unsupported\na\n```\n", "unsupported"),
            ("# Title\n```mermaid\nunknownDiagram\n```\n", "unknown Mermaid"),
            ('# Title\n```mermaid\nflowchart LR\nA["a<br/>b"]\n```\n', "raw HTML"),
            ("# Title\n```text\njust check\n```\n", "executable code"),
        ]
        for text, expected in fixtures:
            assert any(expected in error for _, error in parse(text).errors), expected

    def test_literals_duplicates_unicode_and_broken_links(self) -> None:
        with temporary() as directory:
            root = Path(directory)
            valid = root / "good.md"
            valid.write_text(
                '# Тема\n\n## Публічний `тип`\n\n## Публічний `тип`\n\n[другий](#публічний-тип-1)\n\n```python\nvalue = "<a id=\\"x\\"></a>"\n```\n',
                encoding="utf-8",
            )
            assert check_files(root, [valid])[0] == []
            broken = root / "bad.md"
            broken.write_text("# Bad\n\n[missing](missing.md)\n[anchor](good.md#wrong)\n", encoding="utf-8")
            errors, _ = check_files(root, [broken])
            assert len(errors) == 2
            assert slug("Публічний `тип`") == "публічний-тип"


class OwnershipTests(unittest.TestCase):
    def test_globs_are_segment_scoped_and_generated_has_one_owner(self) -> None:
        assert not matches("docs/components/a/b/c.md", "docs/components/*/*.md")
        assert matches("scripts/docs/test.py", "scripts/docs/**")
        registry = json.loads((ROOT / ".claude/wp-paths.json").read_text(encoding="utf-8-sig"))[
            "documentation_packages"
        ]
        assert owners(registry, "docs/components/storage/reference/types/generated/test.md") == ["DOC-03"]

    def test_source_deletion_requires_inventory_and_matching_archive(self) -> None:
        with temporary() as directory:
            root = Path(directory)
            archive = root / "docs-archive/legacy/old.md"
            archive.parent.mkdir(parents=True)
            archive.write_text("old", encoding="utf-8")
            (root / "docs-archive/inventory.json").write_text(
                json.dumps(
                    {
                        "entries": [
                            {
                                "source": "old.md",
                                "action": "archive",
                                "archive": "docs-archive/legacy/old.md",
                                "sha256": digest(archive),
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            registry = {"packages": {"DOC-01": {"allow": ["old.md"]}}}
            assert check(root, registry, {"old.md": {"committed:D"}}, "DOC-01") == []
            archive.write_text("changed", encoding="utf-8")
            assert check(root, registry, {"old.md": {"unstaged:D"}}, "DOC-01")
            assert check(root, registry, {"unknown.txt": {"untracked:A"}}, "DOC-01")


if __name__ == "__main__":
    unittest.main()
