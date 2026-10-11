"""Publish and verify a documentation package on an isolated local Jane stack."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jane_examples import Api, key
from jane_registry.archive import canonical_archive, digest_of, files_from_dir


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--approve", action="store_true", help="approve after successful local tests")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z][a-z0-9-]*", args.project):
        parser.error("invalid isolated compose project")
    root = Path(__file__).resolve().parents[2]
    stack = json.loads((root / ".jane" / f"stack-{args.project}.json").read_text(encoding="utf-8"))
    if stack["project"] != args.project:
        parser.error("project does not match stack metadata")
    manifest = json.loads((args.package / "jane-package.json").read_text(encoding="utf-8"))
    archive = canonical_archive(files_from_dir(args.package))
    digest = digest_of(archive)
    api = Api(stack["services"]["registry"]["url"], "registry", token=stack["env"].get("JANE_API_KEY_ADMIN"))
    package_id, version = manifest["package_id"], manifest["version"]
    try:
        api.call(
            "POST",
            "/v1/packages",
            ok=(201, 409),
            json={
                "package_id": package_id,
                "kind": manifest["kind"],
                "title": manifest["title"],
                "auto_changes_allowed": False,
            },
            headers={"Idempotency-Key": key()},
        )
        path = f"/v1/packages/{package_id}/versions/{version}"
        response = api.call(
            "POST",
            f"/v1/packages/{package_id}/versions",
            ok=(201, 409),
            content=archive,
            headers={"Content-Type": "application/zip", "Idempotency-Key": key()},
        )
        published = response.json() if response.status_code == 201 else api.call("GET", path).json()
        if published["digest"] != digest:
            raise RuntimeError("existing version has a different digest; increment version")
        downloaded = api.call("GET", path + "/archive").content
        if digest_of(downloaded) != digest:
            raise RuntimeError("downloaded archive digest differs")
        if args.approve and published["status"] == "draft":
            published = api.call(
                "POST",
                path + "/status",
                json={"status": "approved", "reason": "Documentation example: local runtime tests passed"},
                headers={"Idempotency-Key": key()},
            ).json()
        print(
            json.dumps(
                {
                    "package_id": package_id,
                    "version": version,
                    "digest": digest,
                    "status": published["status"],
                    "download_digest_matches": True,
                },
                indent=2,
            )
        )
    finally:
        api.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
