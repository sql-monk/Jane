"""Command line: run a package on a local file or run its tests without any other Jane service.

    jane-handler-runtime run  <package dir|zip> <file> [--media-type text/html] [--url URL] [--params JSON|@file]
    jane-handler-runtime test <package dir|zip> [--case NAME ...] [--json]
    jane-handler-runtime profile [--json]
    jane-handler-runtime build-image [--profile python-extractor@1] [--tag jane/python-extractor:1]
    jane-handler-runtime serve                    # the HTTP service (same as python -m jane_handler_runtime)

Execution always happens in the sandbox backend from the settings (``docker`` by default). ``--backend
subprocess --unsafe-no-sandbox`` runs trusted code without isolation (local development only).
Exit codes: ``run`` 0 = success/empty, 1 = unrecognized/failed; ``test`` 0 = all passed, 1 = failures;
2 = the call could not be made (invalid package, params, no sandbox...).
"""

from __future__ import annotations

import argparse
import asyncio
import io
import json
import sys
import tarfile
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from jane_extractor_sdk.package import material_from_file
from jane_kit.errors import JaneError

from .profiles import load_profiles
from .runtime import Runtime, build_runtime
from .settings import DEFAULT_PROFILE, Settings
from .testrun import run_tests, select_cases

__all__ = ["main"]


def _settings(ns: argparse.Namespace) -> Settings:
    overrides: dict[str, Any] = {}
    if getattr(ns, "backend", None):
        overrides["sandbox_backend"] = ns.backend
    if getattr(ns, "unsafe_no_sandbox", False):
        overrides["allow_unsafe_subprocess"] = True
    if getattr(ns, "image", None):
        overrides["profile_images"] = dict.fromkeys(load_profiles(), ns.image)
    return Settings().model_copy(update=overrides)


def _params(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    text = Path(raw[1:]).read_text(encoding="utf-8") if raw.startswith("@") else raw
    value = json.loads(text)
    if not isinstance(value, dict):
        raise SystemExit("--params must be a JSON object")
    return value


def _dump(doc: Any, output: str | None) -> None:
    text = json.dumps(doc, ensure_ascii=False, indent=2)
    if output:
        Path(output).write_text(text + "\n", encoding="utf-8")
    else:
        sys.stdout.write(text + "\n")


def _material(ns: argparse.Namespace) -> dict[str, Any]:
    file = Path(ns.file)
    if ns.material:
        doc: dict[str, Any] = json.loads(file.read_text(encoding="utf-8"))
        return doc
    return material_from_file(file, media_type=ns.media_type, url=ns.url, source_id=ns.source_id)


async def _run(runtime: Runtime, ns: argparse.Namespace) -> int:
    package = await asyncio.to_thread(runtime.store.load_local, Path(ns.package))
    material = await asyncio.to_thread(_material, ns)
    invocation = {
        "handler": {"package_id": package.manifest["package_id"], "version": package.manifest["version"]},
        "params": _params(ns.params),
        "inputs": [{"kind": "material", "material": material}],
        "context": {"test_mode": not ns.no_test_mode},
        "delivery": {"delivery_key": f"cli:{material.get('observation_id', 'local')}"},
    }
    prep = await runtime.executor.prepare(invocation, package=package)
    result = await runtime.executor.run(prep)
    _dump(result, ns.output)
    return 0 if result["status"] in {"success", "empty"} else 1


async def _test(runtime: Runtime, ns: argparse.Namespace) -> int:
    package = runtime.store.load_local(Path(ns.package))
    runtime.executor.check_package(package)
    cases = select_cases(package, ns.case or "all")
    report = await run_tests(runtime.executor, package, cases)
    if ns.json:
        _dump(report, ns.output)
    else:
        ref = report["package"]
        print(
            f"package {ref['package_id']}@{ref['version']} ({ref['digest']}), backend={runtime.backend.name}"
        )
        for case in report["cases"]:
            mark = "PASS" if case["passed"] else "FAIL"
            line = f"  {mark} {case['name']}: expected {case['expected_status']}, got {case['actual_status']}"
            failure = (case.get("result") or {}).get("failure")
            if failure:
                line += f" [{failure['kind']}: {failure['message'][:200]}]"
            print(line)
            for diff in case.get("differences", [])[:10]:
                print(
                    f"       {diff['pointer']}: expected {diff.get('expected')!r}, actual {diff.get('actual')!r}"
                )
        print(f"{report['passed']} passed, {report['failed']} failed")
        if ns.output:
            _dump(report, ns.output)
    return 0 if report["failed"] == 0 else 1


def _profile(ns: argparse.Namespace) -> int:
    profiles = load_profiles()
    if ns.json:
        _dump({name: dict(p.document) for name, p in profiles.items()}, None)
        return 0
    for name, p in profiles.items():
        print(f"{name}: Python {p.python}")
        for lib, version in sorted(p.libraries.items()):
            print(f"  {lib}=={version}")
    return 0


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for candidate in here.parents:
        if (candidate / "libs" / "extractor-sdk" / "src" / "jane_extractor_sdk").is_dir():
            return candidate
    raise SystemExit("build-image needs a repository checkout (libs/extractor-sdk not found)")


def build_context(profile: str) -> tuple[bytes, str]:
    """Minimal build context (only the files the Dockerfile copies) and the Dockerfile path inside it."""
    doc = load_profiles()[profile].document
    root = repo_root()
    files = dict(doc["image_files"])
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        for rel in (files["dockerfile"], files["requirements"]):
            tar.add(root / rel, arcname=rel)
        sdk = root / "libs" / "extractor-sdk" / "src" / "jane_extractor_sdk"
        for path in sorted(sdk.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                tar.add(path, arcname=path.relative_to(root).as_posix())
    return buf.getvalue(), str(files["dockerfile"])


def _build_image(settings: Settings, ns: argparse.Namespace) -> int:
    import docker  # type: ignore[import-untyped]

    tag = ns.tag or settings.profile_images.get(ns.profile)
    if not tag:
        raise SystemExit(f"no image tag for profile {ns.profile}")
    context, dockerfile = build_context(ns.profile)
    client = (
        docker.DockerClient(base_url=settings.docker_host, version="auto")
        if settings.docker_host
        else docker.from_env(version="auto")
    )
    for chunk in client.api.build(
        fileobj=io.BytesIO(context), custom_context=True, dockerfile=dockerfile, tag=tag, rm=True, decode=True
    ):
        if "stream" in chunk:
            sys.stderr.write(chunk["stream"])
        if "error" in chunk:
            sys.stderr.write(chunk["error"] + "\n")
            return 2
    print(tag)
    return 0


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="jane-handler-runtime", description=__doc__.split("\n\n")[0] if __doc__ else ""
    )
    sub = p.add_subparsers(dest="command")

    def sandbox_args(sp: argparse.ArgumentParser) -> None:
        sp.add_argument(
            "--backend", choices=["docker", "subprocess"], help="sandbox backend (default: settings)"
        )
        sp.add_argument("--unsafe-no-sandbox", action="store_true", help="allow the subprocess backend")
        sp.add_argument("--image", help="sandbox image for the runtime profile (default: settings)")
        sp.add_argument("--output", "-o", help="write the JSON result to this file")

    run = sub.add_parser("run", help="run a package on a local file")
    run.add_argument("package", help="package directory or zip")
    run.add_argument("file", help="input file (raw content, or a Material JSON with --material)")
    run.add_argument("--media-type", help="media type of the file (default: guessed from the name)")
    run.add_argument("--url", help="URL of the material (locator.url)")
    run.add_argument("--source-id", help="source.source_id (key scope; default: local)")
    run.add_argument("--material", action="store_true", help="FILE is a Material JSON document")
    run.add_argument("--params", help="stage parameters: JSON object or @file.json")
    run.add_argument("--no-test-mode", action="store_true", help="mark the run as not a test (informative)")
    sandbox_args(run)

    test = sub.add_parser("test", help="run the tests of a package (manifest 'tests')")
    test.add_argument("package", help="package directory or zip")
    test.add_argument("--case", action="append", help="run only this test (repeatable)")
    test.add_argument("--json", action="store_true", help="print the TestReport JSON")
    sandbox_args(test)

    prof = sub.add_parser("profile", help="libraries of the runtime profiles")
    prof.add_argument("--json", action="store_true")

    build = sub.add_parser("build-image", help="build the sandbox image of a runtime profile")
    build.add_argument("--profile", default=DEFAULT_PROFILE)
    build.add_argument("--tag", help="image tag (default: profile_images from settings)")

    sub.add_parser("serve", help="run the HTTP service")
    return p


def main(argv: Sequence[str] | None = None) -> int:
    ns = _parser().parse_args(argv)
    command = ns.command or "serve"
    if command == "serve":
        from .__main__ import main as serve

        serve()
        return 0
    if command == "profile":
        return _profile(ns)
    settings = _settings(ns)
    if command == "build-image":
        return _build_image(settings, ns)
    runtime = build_runtime(settings)
    try:
        return asyncio.run(_run(runtime, ns) if command == "run" else _test(runtime, ns))
    except JaneError as exc:
        problem = exc.to_problem().model_dump(exclude_none=True, mode="json")
        sys.stderr.write(json.dumps(problem, ensure_ascii=False, indent=2) + "\n")
        return 2
    finally:
        runtime.close()


if __name__ == "__main__":
    raise SystemExit(main())
