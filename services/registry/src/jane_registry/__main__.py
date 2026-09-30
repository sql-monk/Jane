"""Entry point.

    jane-registry [serve]                                        # the HTTP service (python -m jane_registry)
    jane-registry export <package_id>@<version> --registry URL --out DIR [--no-dependencies] [--token-env VAR]
    jane-registry verify <archive.zip> [--digest sha256:...]     # offline, no registry needed
    jane-registry archive <package dir> --out FILE.zip           # canonical archive + digest of a local package

Exit codes: 0 - ok; 1 - verification failed; 2 - the command could not run.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Sequence
from pathlib import Path

import httpx

from jane_kit.service import run

from .app import build_app
from .archive import ArchiveError, canonical_archive, digest_of, files_from_dir
from .export import ExportError, export_package, verify_archive
from .settings import Settings, resolve_service_limits


def _serve() -> int:
    settings = Settings()
    run(build_app(settings), settings)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] == "serve":
        return _serve()
    parser = argparse.ArgumentParser(prog="jane-registry", description="Jane handler registry")
    sub = parser.add_subparsers(dest="cmd", required=True)
    exp = sub.add_parser(
        "export", help="download a version (and its package dependencies) for autonomous use"
    )
    exp.add_argument("ref", help="<package_id>@<version>")
    exp.add_argument("--registry", required=True, help="registry base URL, e.g. http://localhost:8105")
    exp.add_argument("--out", required=True, type=Path)
    exp.add_argument("--no-dependencies", action="store_true")
    exp.add_argument("--token-env", default=None, help="environment variable holding a bearer token")
    exp.add_argument("--timeout-ms", type=int, default=30_000, help="HTTP timeout (default 30000)")
    exp.add_argument(
        "--max-packages",
        type=int,
        default=100,
        help="upper bound of the dependency closure to download (default 100)",
    )
    ver = sub.add_parser("verify", help="verify an exported archive offline")
    ver.add_argument("archive", type=Path)
    ver.add_argument("--digest", default=None)
    ver.add_argument(
        "--contracts", type=Path, default=None, help="contracts/ directory for schema validation"
    )
    arc = sub.add_parser("archive", help="build the canonical archive of a local package directory")
    arc.add_argument("package_dir", type=Path)
    arc.add_argument("--out", required=True, type=Path)
    ns = parser.parse_args(args)

    if ns.cmd == "export":
        pid, sep, version = ns.ref.partition("@")
        if not sep:
            parser.error("ref must be <package_id>@<version>")
        headers = {}
        if ns.token_env:
            headers["Authorization"] = f"Bearer {os.environ[ns.token_env]}"
        try:
            with httpx.Client(base_url=ns.registry, headers=headers, timeout=ns.timeout_ms / 1000) as client:
                entries = export_package(
                    client,
                    pid,
                    version,
                    ns.out,
                    with_dependencies=not ns.no_dependencies,
                    max_packages=ns.max_packages,
                )
        except (ExportError, httpx.HTTPError) as exc:
            print(f"export failed: {exc}", file=sys.stderr)
            return 2
        for e in entries:
            print(f"{e['package_id']}@{e['version']}  {e['digest']}  {ns.out / e['file']}")
        return 0
    if ns.cmd == "verify":
        # limits of `verify` are the registry's configured limits (JANE_REGISTRY_LIMITS__PACKAGES__*, __SECRETS__*)
        limits = resolve_service_limits(Settings()).limits
        report = verify_archive(
            ns.archive,
            expected_digest=ns.digest,
            contracts=ns.contracts,
            package_limits=limits.packages,
            secret_limits=limits.secrets,
        )
        print(json.dumps(report.wire(), indent=2, ensure_ascii=False))
        return 0 if report.ok else 1
    try:
        data = canonical_archive(files_from_dir(ns.package_dir))
    except ArchiveError as exc:
        print(f"archive failed: {exc}", file=sys.stderr)
        return 2
    ns.out.write_bytes(data)
    print(f"{ns.out}  {digest_of(data)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
