"""Validate the WP-14 PlatformLimits candidates against the owned contract schema."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "contracts/schemas/common/limits.schema.json"
SCHEMA_URI = "https://jane.local/contracts/schemas/common/limits.schema.json"
PROFILES = ("dev-laptop", "ci", "single-node")


def main() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    schema["$id"] = SCHEMA_URI
    registry = Registry().with_resource(SCHEMA_URI, Resource.from_contents(schema))
    validator = Draft202012Validator({"$ref": f"{SCHEMA_URI}#/$defs/PlatformLimits"}, registry=registry)
    for name in PROFILES:
        path = Path(__file__).with_name(f"{name}.json")
        profile = json.loads(path.read_text(encoding="utf-8"))
        validator.validate(profile)
        if profile["profile"] != name:
            raise ValueError(f"{path}: profile name does not match file name")
        print(f"{path.relative_to(ROOT)}: schema valid")


if __name__ == "__main__":
    main()
