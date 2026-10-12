"""Publish verified auto packages and configure a bounded six-hour catalog in a running Jane stack."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import httpx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from jsonschema import Draft202012Validator  # noqa: E402

import jane_examples as ex  # noqa: E402
from jane_extractor_sdk.testing import run_local, run_package_tests  # noqa: E402
from jane_kit.contracts import ContractClient  # noqa: E402
from jane_registry.archive import canonical_archive, digest_of, files_from_dir  # noqa: E402

# One source with examples/sites: the same package_id and version must never have two different archives.
PACKAGES = HERE.parent / "sites" / "packages"
PACKAGE_IDS = (
    "autos.autoria-ad-page",
    "autos.autoria-rules",
    "autos.autoria-search-page",
    "autos.rst-car-ads",
    "autos.rst-rules",
)
ENTITY_TYPE = "ad_car"
SITES = {
    "autoria": (
        "autoria-cars",
        "ads-autoria",
        "AUTO.RIA",
        "https://auto.ria.com/uk/",
        "autos.autoria-ad-page",
    ),
    "rst": ("autos-rst", "ads-rst", "RST.ua", "https://rst.ua/ukr/oldcars/", "autos.rst-car-ads"),
}
STORAGE = ("jane.storage-files", "jane.storage-mongodb")
RAW_CONNECTION, ENTITY_CONNECTION = "raw-files", "results-mongo"


class StackApi(ex.Api):
    """Contract client with bounded retry of a stale connection, preserving the same idempotency key."""

    def __init__(
        self,
        base_url: str,
        api: str,
        *,
        token: str | None,
        retries: int,
        keepalive: float,
        http_timeout: float = 120,
        container_name: str | None = None,
        retry_delay: float = 2,
    ) -> None:
        super().__init__(base_url, api, token=token)
        self.http.close()
        self.http = httpx.Client(
            base_url=base_url,
            timeout=http_timeout,
            headers={"Authorization": f"Bearer {token}"} if token else None,
            limits=httpx.Limits(keepalive_expiry=keepalive),
        )
        self.client = ContractClient(ex.spec(api), self.http)
        self.transport_retries = retries
        self.container_name = container_name
        self.retry_delay = retry_delay

    def call(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        safe = method in {"GET", "HEAD", "OPTIONS", "PUT", "DELETE"} or "Idempotency-Key" in kwargs.get(
            "headers", {}
        )
        for attempt in range(self.transport_retries + 1):
            try:
                return super().call(method, path, **kwargs)
            except httpx.TransportError:
                if not safe or attempt == self.transport_retries:
                    raise
                if self.container_name:
                    self.http.base_url = runtime_url(self.container_name, str(self.http.base_url))
                time.sleep(self.retry_delay)
        raise RuntimeError("unreachable transport retry state")


def package_dirs() -> dict[str, Path]:
    directories = {pid: PACKAGES / pid for pid in PACKAGE_IDS}
    for pid, directory in directories.items():
        if ex.read_json(directory / "jane-package.json")["package_id"] != pid:
            raise RuntimeError(f"{directory}: manifest package_id differs from {pid}")
    return directories


def package_ref(directory: Path) -> dict[str, str]:
    manifest = ex.read_json(directory / "jane-package.json")
    return {
        "package_id": manifest["package_id"],
        "version": manifest["version"],
        "digest": str(digest_of(bytes(canonical_archive(files_from_dir(directory))))),
    }


def local_refs() -> dict[str, dict[str, str]]:
    from jane_storage.adapters import package_dirs as storage_dirs

    directories = package_dirs()
    for root in storage_dirs().values():
        directory = Path(root)
        if ex.read_json(directory / "jane-package.json")["package_id"] in STORAGE:
            directories[ex.read_json(directory / "jane-package.json")["package_id"]] = directory
    return {pid: package_ref(directory) for pid, directory in directories.items()}


def source_doc(site: str, refs: Mapping[str, Any]) -> dict[str, Any]:
    source_id, _, title, url, _ = SITES[site]
    return {
        "source_id": source_id,
        "kind": "web",
        "title": f"{title} — каталог авторинку",
        "description": "Публічні сторінки каталогу й повні картки авто; правила robots.txt дотримуються.",
        "locator": {"url": url},
        "collector_rules": refs[f"autos.{site}-rules"],
        "limits": {
            "rate": {
                "requests_per_second_per_host": 1,
                "min_delay_ms_per_host": 1000,
                "respect_crawl_delay": True,
            },
            "concurrency": {"max_parallel_fetches_per_host": 1},
        },
        "expected_entity_types": [ENTITY_TYPE],
        "forward_unknown_to_llm": False,
        "labels": {"group": "autos", "site": site, "catalog": "automarket"},
    }


def task_doc(
    site: str, refs: Mapping[str, Any], *, interval: int = 21600, pages: int = 120
) -> dict[str, Any]:
    source_id, task_id, title, _, extractor = SITES[site]
    return {
        "task_id": task_id,
        "enabled": True,
        "title": f"{title}: детальні оголошення кожні {interval // 3600} год",
        "description": f"Обмежений інкрементальний обхід: RAW → files, лише повні картки оголошень → {ENTITY_TYPE} у MongoDB.",
        "input": {"source_id": source_id},
        "stages": [
            {
                "stage_id": "collect",
                "kind": "collect",
                "collector": {"collector": "web", "mode": "incremental"},
            },
            {
                "stage_id": "store-raw",
                "kind": "handler",
                "handler": refs["jane.storage-files"],
                "connections": {"target": RAW_CONNECTION},
                "inputs": [{"from": "collect"}],
                "on_failure": "fail_run",
            },
            {
                "stage_id": "extract-ad",
                "kind": "handler",
                "handler": refs[extractor],
                "inputs": [
                    {
                        "from": "collect",
                        "when": {"field": "material.format.media_type", "op": "eq", "value": "text/html"},
                    }
                ],
                "bindings": [{"sections": ["ad"]}],
                "on_failure": "fail_run",
            },
            {
                "stage_id": "store-ads",
                "kind": "handler",
                "handler": refs["jane.storage-mongodb"],
                "connections": {"target": ENTITY_CONNECTION},
                "inputs": [
                    {
                        "from": "extract-ad",
                        "select": "output",
                        "when": {"field": "result.status", "op": "eq", "value": "success"},
                    }
                ],
                "on_failure": "fail_run",
            },
        ],
        "schedule": {"type": "interval", "interval_seconds": interval, "overlap": "skip", "enabled": True},
        "limits": {
            "crawl": {"max_depth": 5, "max_pages_per_run": pages, "revisit_interval_seconds": interval}
        },
        "forward_unknown_to_llm": False,
        "labels": {"group": "autos", "site": site, "catalog": "automarket"},
    }


def check_offline() -> list[str]:
    problems: list[str] = []
    refs = local_refs()
    for pid, directory in package_dirs().items():
        manifest = ex.read_json(directory / "jane-package.json")
        problems.extend(f"{pid}: {p}" for p in ex.validate("package-manifest.schema.json", manifest))
        problems.extend(f"{pid}: {p}" for p in ex.package_json_problems(directory, manifest))
        if manifest["kind"] == "collector-rules":
            problems.extend(
                f"{pid}: {p}"
                for p in ex.validate(
                    "collector-rules.schema.json", ex.read_json(directory / manifest["entry"]["rules"])
                )
            )
            continue
        schemas = {
            s["entity_type"]: Draft202012Validator(ex.read_json(directory / s["schema"]))
            for s in manifest["output"]["entities"]
        }
        cases = run_package_tests(directory)
        if (
            not cases
            or not any(c.expected_status == "success" for c in cases)
            or not any(c.expected_status in {"empty", "unrecognized"} for c in cases)
        ):
            problems.append(f"{pid}: success and empty/unrecognized cases required")
        for case in cases:
            if not case.passed:
                problems.append(
                    f"{pid}/{case.name}: {case.actual_status} {case.differences} {case.result.get('error')}"
                )
            for entity in case.result.get("output", {}).get("entities", []):
                problems.extend(
                    f"{pid}/{case.name}: {e.message}"
                    for e in schemas[entity["entity_type"]].iter_errors(entity["fields"])
                )
    for site in SITES:
        problems.extend(ex.validate("source.schema.json", source_doc(site, refs)))
        problems.extend(ex.validate("task-config.schema.json", task_doc(site, refs)))
    return problems


def connect(
    stack_file: Path,
    *,
    retries: int = 2,
    keepalive: float = 2,
    http_timeout: float = 120,
    retry_delay: float = 2,
) -> tuple[ex.Services, ex.Api]:
    stack = ex.read_json(stack_file)
    token = stack.get("env", {}).get("JANE_API_KEY_ADMIN")
    urls = {name: service["url"] for name, service in stack["services"].items() if "url" in service}
    project = stack.get("project") or stack_file.stem.removeprefix("stack-")
    containers = {name: f"{project}-{name}-1" for name in urls}
    for name in ("registry", "orchestrator", "storage", "handler-runtime"):
        urls[name] = runtime_url(containers[name], urls[name])
    return ex.Services(
        StackApi(
            urls["registry"],
            "registry",
            token=token,
            retries=retries,
            keepalive=keepalive,
            http_timeout=http_timeout,
            container_name=containers["registry"],
            retry_delay=retry_delay,
        ),
        StackApi(
            urls["orchestrator"],
            "orchestrator",
            token=token,
            retries=retries,
            keepalive=keepalive,
            http_timeout=http_timeout,
            container_name=containers["orchestrator"],
            retry_delay=retry_delay,
        ),
        StackApi(
            urls["storage"],
            "storage",
            token=token,
            retries=retries,
            keepalive=keepalive,
            http_timeout=http_timeout,
            container_name=containers["storage"],
            retry_delay=retry_delay,
        ),
    ), StackApi(
        urls["handler-runtime"],
        "handler",
        token=token,
        retries=retries,
        keepalive=keepalive,
        http_timeout=http_timeout,
        container_name=containers["handler-runtime"],
        retry_delay=retry_delay,
    )


def runtime_url(container_name: str, fallback: str) -> str:
    """Resolve a local container's current published port without changing shared metadata."""
    docker = shutil.which("docker")
    if docker is None or urlsplit(fallback).hostname not in {"127.0.0.1", "localhost"}:
        return fallback
    published = subprocess.run(  # noqa: S603 - trusted local project name, argv only; read-only
        [docker, "port", container_name, "8000/tcp"],
        capture_output=True,
        text=True,
        check=False,
    )
    if published.returncode == 0:
        address = next(
            (line.strip() for line in published.stdout.splitlines() if line.startswith("127.0.0.1:")), None
        )
        if address:
            return f"http://{address}"
    return fallback


def wait_job(api: ex.Api, job: dict[str, Any], timeout: float, poll: float) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    while job["status"] not in ex.TERMINAL:
        if time.monotonic() > deadline:
            raise TimeoutError(f"job {job['job_id']} still {job['status']}")
        time.sleep(poll)
        job = api.call("GET", f"/v1/jobs/{job['job_id']}").json()
    return job


def test_package(
    handler: ex.Api, ref: dict[str, str], timeout: float, poll: float, retries: int
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    identity = f"automarket-test:{ref['digest']}"
    for attempt in range(retries + 1):
        if time.monotonic() >= deadline:
            raise TimeoutError(f"{ref['package_id']}: test retry deadline exceeded")
        job = handler.call(
            "POST",
            "/v1/test-runs",
            ok=(200, 202),
            json={"handler": ref, "tests": "all"},
            headers={"Idempotency-Key": hashlib.sha256(identity.encode()).hexdigest()},
        ).json()
        job = wait_job(handler, job, max(0, deadline - time.monotonic()), poll)
        if job["status"] == "succeeded":
            return dict(job["result"])
        error = job.get("error") or {}
        if job["status"] != "failed" or not error.get("retryable") or attempt == retries:
            raise RuntimeError(f"job {job['job_id']}: {job['status']} {error}")
        identity = f"automarket-test:{ref['digest']}:retry:{job['job_id']}"
        ex.log(f"{ref['package_id']}: retrying failed test job {job['job_id']} after {error.get('code')}")
    raise RuntimeError("unreachable test retry state")


def upload_version(
    registry: ex.Api, pid: str, directory: Path, *, allow_generated: bool = False
) -> httpx.Response:
    """Temporarily permit an explicitly authorized LLM upload, restoring the package policy."""
    path = f"/v1/packages/{pid}"
    manifest = ex.read_json(directory / "jane-package.json")

    def policy_patch(allowed: bool, etag: str) -> None:
        body = {"auto_changes_allowed": allowed}
        registry.client.spec.validate_request("PATCH", path, body, "application/merge-patch+json")
        registry.call(
            "PATCH",
            path,
            content=json.dumps(body).encode(),
            headers={"If-Match": etag, "Content-Type": "application/merge-patch+json"},
        )

    current = registry.call("GET", path)
    changed = manifest["provenance"]["created_by"] == "llm" and not current.json()["auto_changes_allowed"]
    if changed and not allow_generated:
        raise RuntimeError(f"{pid}: publication requires explicit --allow-generated-packages authorization")
    try:
        if changed:
            policy_patch(True, current.headers["ETag"])
        return registry.call(
            "POST",
            f"{path}/versions",
            ok=(201, 409),
            content=bytes(canonical_archive(files_from_dir(directory))),
            headers={"Content-Type": "application/zip", "Idempotency-Key": ex.key()},
        )
    finally:
        if changed:
            latest = registry.call("GET", path)
            policy_patch(False, latest.headers["ETag"])


def publish(
    svc: ex.Services,
    handler: ex.Api,
    timeout: float,
    poll: float,
    *,
    allow_generated: bool = False,
    test_retries: int = 2,
) -> dict[str, dict[str, str]]:
    refs = local_refs()
    for pid, directory in package_dirs().items():
        manifest, ref = ex.read_json(directory / "jane-package.json"), refs[pid]
        svc.registry.call(
            "POST",
            "/v1/packages",
            ok=(201, 409),
            json={
                "package_id": pid,
                "kind": manifest["kind"],
                "title": manifest["title"],
                "description": manifest.get("description", ""),
                "auto_changes_allowed": False,
            },
            headers={"Idempotency-Key": ex.key()},
        )
        path = f"/v1/packages/{pid}/versions/{ref['version']}"
        response = svc.registry.call("GET", path, ok=(200, 404))
        if response.status_code == 404:
            response = upload_version(svc.registry, pid, directory, allow_generated=allow_generated)
        version = (
            response.json() if response.status_code in (200, 201) else svc.registry.call("GET", path).json()
        )
        if version["digest"] != ref["digest"]:
            raise RuntimeError(f"{pid}: immutable registry version differs; bump version")
        if manifest["kind"] == "extractor":
            report = test_package(handler, ref, timeout, poll, test_retries)
            if report["failed"] or not report["passed"]:
                raise RuntimeError(f"{pid}: runtime package tests failed: {report}")
            svc.registry.call(
                "POST",
                f"{path}/test-results",
                ok=(200, 201),
                json={"runner": "handler-runtime", "context": "automarket-package-tests", "report": report},
                headers={"Idempotency-Key": ex.key()},
            )
            ex.log(f"{pid}@{ref['version']}: runtime {report['passed']} passed, {report['failed']} failed")
        if version["status"] == "draft":
            svc.registry.call(
                "POST",
                f"{path}/status",
                json={
                    "status": "approved",
                    "reason": "automarket: schema, fixtures and runtime tests verified",
                },
                headers={"Idempotency-Key": ex.key()},
            )
        elif version["status"] != "approved":
            raise RuntimeError(f"{pid}: unexpected package status {version['status']}")
    for pid in STORAGE:
        ref = refs[pid]
        version = svc.registry.call("GET", f"/v1/packages/{pid}/versions/{ref['version']}").json()
        if version["status"] != "approved" or version["digest"] != ref["digest"]:
            raise RuntimeError(f"{pid}: approved storage package does not match this checkout")
    return refs


def put_config(api: ex.Api, collection: str, identifier: str, doc: dict[str, Any]) -> None:
    current = api.call("GET", f"/v1/{collection}/{identifier}", ok=(200, 404))
    if current.status_code == 404:
        api.call("POST", f"/v1/{collection}", ok=(201,), json=doc, headers={"Idempotency-Key": ex.key()})
    elif {k: v for k, v in current.json().items() if k not in ("created_at", "updated_at")} != doc:
        if collection == "tasks":
            validation = api.call("POST", "/v1/task-validations", json=doc).json()
            if not validation["valid"]:
                raise RuntimeError(f"invalid task {identifier}: {validation['errors']}")
        api.call(
            "PUT", f"/v1/{collection}/{identifier}", json=doc, headers={"If-Match": current.headers["ETag"]}
        )


def cancel_active(orch: ex.Api, task_id: str, timeout: float) -> None:
    for run in orch.pages("/v1/runs", {"task_id": task_id}):
        if run["status"] not in ex.TERMINAL:
            orch.call(
                "POST",
                f"/v1/runs/{run['run_id']}/cancel",
                ok=(200, 202),
                headers={"Idempotency-Key": ex.key()},
            )
            ex.wait_run(orch, run["run_id"], timeout)
            ex.log(f"cancelled obsolete auto run {run['run_id']}")


def disable_unavailable(orch: ex.Api) -> None:
    put_config(
        orch,
        "sources",
        "autos-avtobazar",
        {
            "source_id": "autos-avtobazar",
            "kind": "web",
            "title": "Avtobazar.ua — недоступний",
            "locator": {"url": "https://avtobazar.ua/"},
            "description": "Перенаправляє на новинний Autocentre.ua; оголошення відсутні. InfoCar користувач не обрав.",
            "forward_unknown_to_llm": False,
            "labels": {
                "group": "autos",
                "site": "avtobazar",
                "availability": "unavailable",
                "catalog": "automarket",
            },
        },
    )
    current = orch.call("GET", "/v1/tasks/ads-avtobazar", ok=(200, 404))
    if current.status_code == 200:
        task = current.json()
        task["title"] = "Avtobazar.ua — недоступний (перенаправлення на новини)"
        task["description"] = (
            "Avtobazar.ua перенаправляє на Autocentre.ua. Користувач відхилив заміну на InfoCar; сканування вимкнено."
        )
        task["schedule"] = {"type": "manual", "enabled": False}
        task["labels"] = {**task.get("labels", {}), "availability": "unavailable", "catalog": "automarket"}
        orch.call("PUT", "/v1/tasks/ads-avtobazar", json=task, headers={"If-Match": current.headers["ETag"]})


def verify_catalog(svc: ex.Services, runs: Mapping[str, str]) -> dict[str, Any]:
    source = svc.orchestrator.call("GET", "/v1/sources/autos-avtobazar").json()
    disabled_task = svc.orchestrator.call("GET", "/v1/tasks/ads-avtobazar", ok=(200, 404))
    unavailable_schedule = (
        disabled_task.json().get("schedule", {})
        if disabled_task.status_code == 200
        else {"type": "manual", "enabled": False}
    )
    if (
        source.get("labels", {}).get("availability") != "unavailable"
        or source["locator"].get("url") != "https://avtobazar.ua/"
        or unavailable_schedule.get("enabled", True)
    ):
        raise RuntimeError("avtobazar.ua: unavailable source must have no active scan")
    receipt: dict[str, Any] = {
        "sites": {},
        "unavailable": {
            "avtobazar.ua": {
                "source_id": source["source_id"],
                "locator": source["locator"],
                "availability": source["labels"]["availability"],
                "schedule": unavailable_schedule,
                "reason": "redirects_to_news; user declined InfoCar",
            }
        },
    }
    directories = package_dirs()
    for site, (source_id, task_id, _, _, extractor) in SITES.items():
        run = svc.orchestrator.call("GET", f"/v1/runs/{runs[site]}").json()
        if run["status"] != "succeeded" or run["task_id"] != task_id:
            raise RuntimeError(f"{site}: run {runs[site]} has not succeeded for {task_id}")
        task = svc.orchestrator.call("GET", f"/v1/tasks/{task_id}").json()
        schedule = task.get("schedule", {})
        if (
            not task.get("enabled", True)
            or schedule.get("type") != "interval"
            or schedule.get("interval_seconds") != 21600
            or not schedule.get("enabled", True)
        ):
            raise RuntimeError(f"{site}: six-hour schedule is not active")
        entities = svc.storage.pages(
            "/v1/entities",
            {"connection_id": ENTITY_CONNECTION, "entity_type": ENTITY_TYPE, "scope": source_id},
        )
        manifest = ex.read_json(directories[extractor] / "jane-package.json")
        schema = Draft202012Validator(
            ex.read_json(directories[extractor] / manifest["output"]["entities"][0]["schema"])
        )
        verified = []
        for state in entities:
            history = svc.storage.pages(
                "/v1/entity-history",
                {
                    "connection_id": ENTITY_CONNECTION,
                    "entity_type": ENTITY_TYPE,
                    "key": state["canonical_key"],
                },
            )
            records = [
                h["record"] for h in history if h["record"].get("provenance", {}).get("run_id") == runs[site]
            ]
            for record in records:
                schema.validate(record["fields"])
                provenance = record.get("provenance", {})
                if provenance.get("package") != package_ref(directories[extractor]):
                    raise RuntimeError(f"{site}: wrong extractor provenance")
                verified.append(
                    {
                        "key": state["key"],
                        "fields": record["fields"],
                        "observation": record.get("observation"),
                        "provenance": provenance,
                    }
                )
        if not verified:
            raise RuntimeError(f"{site}: no entities written by verification run {runs[site]}")
        raw = svc.storage.pages("/v1/objects", {"connection_id": RAW_CONNECTION, "source_id": source_id})
        expected_observations = {record["observation"]["observation_id"] for record in verified}
        new_raw = [
            obj for obj in raw if obj.get("material", {}).get("observation_id") in expected_observations
        ]
        saved_observations = {obj["material"]["observation_id"] for obj in new_raw}
        if missing_raw := expected_observations - saved_observations:
            raise RuntimeError(f"{site}: verification observations lack RAW: {sorted(missing_raw)}")
        raw_checks = []
        for obj in new_raw:
            object_id = obj["object"]["object_id"]
            detail = svc.storage.call(
                "GET", f"/v1/objects/{object_id}", params={"connection_id": RAW_CONNECTION}
            ).json()
            original = svc.storage.call(
                "GET", f"/v1/objects/{object_id}/content", params={"connection_id": RAW_CONNECTION}
            ).content
            checksum = hashlib.sha256(original).hexdigest()
            material = detail.get("material", {})
            if checksum != material.get("revision", {}).get("content_sha256"):
                raise RuntimeError(
                    f"{site}/{object_id}: saved RAW content digest differs from the collected material"
                )
            observation_id = material["observation_id"]
            record = next(
                record for record in verified if record["observation"]["observation_id"] == observation_id
            )
            with tempfile.TemporaryDirectory(prefix="jane-automarket-") as temporary:
                page = Path(temporary) / "page.html"
                page.write_bytes(original)
                replay = run_local(
                    directories[extractor], file=page, media_type="text/html", url=record["fields"]["url"]
                )
            if replay["status"] != "success" or [
                e["fields"] for e in replay.get("output", {}).get("entities", [])
            ] != [record["fields"]]:
                raise RuntimeError(
                    f"{site}/{object_id}: stored entity fields differ from extraction of the saved RAW"
                )
            raw_checks.append(
                {
                    "object_id": object_id,
                    "observation_id": observation_id,
                    "sha256": checksum,
                    "size_bytes": len(original),
                    "fields_replayed": True,
                }
            )
        receipt["sites"][site] = {
            "run_id": runs[site],
            "schedule": task["schedule"],
            "verified_entity_count": len(verified),
            "total_entity_count": len(entities),
            "raw_object_count": len(raw),
            "verified_raw_object_count": len(new_raw),
            "raw_checks": raw_checks,
            "entities": verified,
        }
        ex.log(f"{site}: {len(verified)} entities of the new run verified; {len(raw)} RAW objects")
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "apply", "run", "verify"))
    parser.add_argument("--stack-file", type=Path, default=ex.ROOT / ".jane" / "stack-jane-demo.json")
    parser.add_argument(
        "--pages", type=int, default=120, help="maximum pages per scheduled run, including catalog pages"
    )
    parser.add_argument("--validation-pages", type=int, default=11)
    parser.add_argument("--timeout", type=float, default=1800)
    parser.add_argument("--poll", type=float, default=2)
    parser.add_argument("--transport-retries", type=int, default=2)
    parser.add_argument("--keepalive", type=float, default=2)
    parser.add_argument("--http-timeout", type=float, default=120)
    parser.add_argument("--retry-delay", type=float, default=2)
    parser.add_argument("--test-retries", type=int, default=2)
    parser.add_argument(
        "--allow-generated-packages",
        action="store_true",
        help="authorize LLM version upload with temporary package policy permission and immediate restoration",
    )
    parser.add_argument(
        "--cancel-active",
        action="store_true",
        help="cancel only obsolete ads-autoria/ads-rst/ads-avtobazar runs before applying",
    )
    # Local by default: evidence/runtime.json records an earlier run and stays unchanged.
    parser.add_argument("--receipt", type=Path, default=ex.STACK_DIR / "automarket-runtime.json")
    args = parser.parse_args(argv)
    if min(args.pages, args.validation_pages, args.timeout, args.poll, args.http_timeout) <= 0:
        parser.error("page counts, timeout and poll must be positive")
    if problems := check_offline():
        print("\n".join(problems), file=sys.stderr)
        return 1
    if args.command == "check":
        print(f"automarket: {len(package_dirs())} packages and both source/task documents verified")
        return 0
    if args.transport_retries < 0 or args.keepalive < 0 or args.retry_delay < 0 or args.test_retries < 0:
        parser.error("transport retry count and keepalive must not be negative")
    svc, handler = connect(
        args.stack_file,
        retries=args.transport_retries,
        keepalive=args.keepalive,
        http_timeout=args.http_timeout,
        retry_delay=args.retry_delay,
    )
    try:
        if args.command == "apply":
            disable_unavailable(svc.orchestrator)
            if args.cancel_active:
                for task_id in ("ads-autoria", "ads-rst", "ads-avtobazar"):
                    cancel_active(svc.orchestrator, task_id, args.timeout)
            refs = publish(
                svc,
                handler,
                args.timeout,
                args.poll,
                allow_generated=args.allow_generated_packages,
                test_retries=args.test_retries,
            )
            for connection in (RAW_CONNECTION, ENTITY_CONNECTION):
                svc.orchestrator.call("GET", f"/v1/connections/{connection}")
            for site, (source_id, task_id, *_rest) in SITES.items():
                put_config(svc.orchestrator, "sources", source_id, source_doc(site, refs))
                put_config(svc.orchestrator, "tasks", task_id, task_doc(site, refs, pages=args.pages))
                ex.log(f"{task_id}: interval=21600s, max_pages={args.pages}")
            return 0
        if args.command == "run":
            runs = {}
            for site, (_, task_id, *_rest) in SITES.items():
                job = svc.orchestrator.call(
                    "POST",
                    f"/v1/tasks/{task_id}/runs",
                    ok=(202,),
                    json={
                        "reason": "automarket: first real detailed catalog verification",
                        "limits": {
                            "crawl": {
                                "max_pages_per_run": args.validation_pages,
                                "max_depth": 1,
                                "revisit_interval_seconds": 0,
                            }
                        },
                    },
                    headers={"Idempotency-Key": ex.key()},
                ).json()
                runs[site] = job["job_id"]
                ex.log(f"{site}: started {runs[site]}")
            args.receipt.parent.mkdir(parents=True, exist_ok=True)
            ex.write_json(args.receipt, {"runs": runs, "status": "running"})
            for site, run_id in runs.items():
                run = ex.wait_run(svc.orchestrator, run_id, args.timeout)
                ex.log(f"{site}: {run['status']} counters={run.get('counters')}")
                if run["status"] != "succeeded":
                    raise RuntimeError(f"{site}: verification run {run['status']}")
        else:
            saved = ex.read_json(args.receipt)
            runs = saved.get("runs") or {site: detail["run_id"] for site, detail in saved["sites"].items()}
        receipt = verify_catalog(svc, runs)
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        ex.write_json(args.receipt, receipt)
        return 0
    finally:
        handler.close()
        svc.close()


if __name__ == "__main__":
    raise SystemExit(main())
