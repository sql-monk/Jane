"""Storage packages from the registry (ADR-0009 §4, WP-07c): download, verification, cache, failures.

The registry is a neighbour. Unit tests use :class:`ContractRegistry` - a stand-in built from ``registry.v1``
(``GET /v1/packages/{id}/versions/{v}/archive``: ``application/zip`` + ``ETag: "sha256:…"``; ``404`` and
``401`` bodies are the contract's examples) whose every documented response is validated against the contract.
The last test runs the REAL registry service in-process (its ``memory`` backend). Storage itself is never mocked:
requests go through its HTTP API (``build_app``) with the real filesystem adapter.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import logging
from collections.abc import AsyncIterator, Callable, Iterator
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from jane_kit.contracts import OpenAPISpec, contracts_dir
from jane_storage.app import build_app
from jane_storage.packages import PackageCatalog, StoragePackage, canonical_archive
from jane_storage.registry_packages import RegistryPackages
from jane_storage.settings import PackageLimits, Settings

CONTRACTS = contracts_dir(Path(__file__).parent)
REGISTRY_URL = "http://registry.test"
ARCHIVE_PATH = "/v1/packages/{package_id}/versions/{version}/archive"
TOKEN = "wp07c-registry-token-value"


def files_package() -> StoragePackage:
    return next(p for p in PackageCatalog.discover().all() if p.package_id == "jane.storage-files")


def variant(package_id: str, version: str = "1.0.0", **manifest: Any) -> bytes:
    """Canonical archive of a fork-like copy of ``jane.storage-files`` (registry layout, other id/version)."""
    base = files_package()
    doc = {**base.manifest, "package_id": package_id, "version": version, **manifest}
    files = [(p, d) for p, d in base.files if p != "jane-package.json"]
    data = (json.dumps(doc, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return canonical_archive([*files, ("jane-package.json", data)])


def digest(archive: bytes) -> str:
    return "sha256:" + hashlib.sha256(archive).hexdigest()


def ref(package_id: str, archive: bytes, version: str = "1.0.0") -> dict[str, str]:
    return {"package_id": package_id, "version": version, "digest": digest(archive)}


class ContractRegistry:
    """Neighbour stand-in from ``registry.v1``: serves canonical archives with ``ETag``; 404/401 from the contract
    examples. ``override`` replaces the answer (failures the contract does not describe: 5xx, redirects)."""

    def __init__(self) -> None:
        if CONTRACTS is None:
            pytest.skip("contracts not available")
        self.spec = OpenAPISpec.load(CONTRACTS / "openapi" / "registry.v1.yaml")
        common = OpenAPISpec.load(CONTRACTS / "openapi" / "common.yaml").document["components"]
        self.not_found = dict(common["examples"]["ProblemNotFound"]["value"])
        self.unauthenticated = dict(
            common["responses"]["Unauthenticated"]["content"]["application/problem+json"]["examples"][
                "unauthenticated"
            ]["value"]
        )
        self.archives: dict[tuple[str, str], bytes] = {}
        self.requests: list[httpx.Request] = []
        self.override: Callable[[httpx.Request], httpx.Response] | None = None
        self.require_token: str | None = None
        self.transport = httpx.MockTransport(self.handle)

    def publish(self, package_id: str, version: str, archive: bytes) -> dict[str, str]:
        self.archives[(package_id, version)] = archive
        return ref(package_id, archive, version)

    def downloads(self) -> int:
        return len(self.requests)

    def _problem(self, request: httpx.Request, body: dict[str, Any]) -> httpx.Response:
        self.spec.validate_response("GET", request.url.path, body["status"], body, "application/problem+json")
        return httpx.Response(body["status"], json=body, headers={"content-type": "application/problem+json"})

    def handle(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if self.override is not None:
            return self.override(request)
        if self.require_token and request.headers.get("authorization") != f"Bearer {self.require_token}":
            return self._problem(request, self.unauthenticated)
        parts = request.url.path.split("/")  # /v1/packages/<id>/versions/<v>/archive
        archive = self.archives.get((parts[3], parts[5])) if len(parts) == 7 else None
        if request.method != "GET" or archive is None:
            return self._problem(request, {**self.not_found, "detail": request.url.path})
        self.spec.validate_response("GET", request.url.path, 200, "<zip bytes>", "application/zip")
        return httpx.Response(
            200, content=archive, headers={"content-type": "application/zip", "etag": f'"{digest(archive)}"'}
        )


@pytest.fixture
def registry() -> ContractRegistry:
    return ContractRegistry()


@pytest.fixture
def with_registry(settings: Settings, registry: ContractRegistry) -> Iterator[TestClient]:
    configured = settings.with_overrides(registry_url=REGISTRY_URL)
    with TestClient(build_app(configured, registry_transport=registry.transport)) as c:
        yield c


def store(client: TestClient, h: SimpleNamespace, handler: dict[str, str], dk: str) -> httpx.Response:
    body = h.invocation([{"kind": "material", "material": h.material()}], dk)
    body["handler"] = handler
    response: httpx.Response = h.post(client, body)
    return response


def written(storage_dir: Path) -> list[Path]:
    """Stored RAW objects of the files adapter (without their ``.meta.json`` sidecars)."""
    objects = storage_dir / "objects"
    if not objects.exists():
        return []
    return sorted(p for p in objects.rglob("*") if p.is_file() and not p.name.endswith(".meta.json"))


# ---------------------------------------------------------------------------- success and cache
def test_registry_package_is_downloaded_verified_cached_and_executed(
    with_registry: TestClient, registry: ContractRegistry, h: SimpleNamespace, storage_dir: Path
) -> None:
    """A fork that exists only in the registry (RAW as a JSON Material document, unlike the built-in parent)."""
    archive = variant("jane.storage-files-fork", entry={**files_package().entry, "format": {"raw": "json"}})
    fork = registry.publish("jane.storage-files-fork", "1.0.0", archive)
    first = store(with_registry, h, fork, "dk-reg-1")
    assert first.status_code == 200, first.text
    result = first.json()
    assert result["status"] == "success" and result["handler"] == fork, result
    (ack,) = result["output"]["writes"]
    assert ack["status"] == "written" and ack["object"]["media_type"] == "application/json", ack
    path = storage_dir / ack["object"]["locator"]["path"]
    assert path.suffix == ".json" and json.loads(path.read_text(encoding="utf-8"))["material_id"]
    request = registry.requests[0]
    assert request.url.path == "/v1/packages/jane.storage-files-fork/versions/1.0.0/archive"
    assert request.headers["accept"] == "application/zip"
    # warm cache: by digest, and without a digest by package_id@version (registry versions are immutable)
    again = store(with_registry, h, fork, "dk-reg-2")
    unpinned = store(with_registry, h, {k: fork[k] for k in ("package_id", "version")}, "dk-reg-3")
    assert again.status_code == unpinned.status_code == 200, (again.text, unpinned.text)
    assert unpinned.json()["handler"] == fork
    assert registry.downloads() == 1


def test_builtin_package_is_authoritative_and_needs_no_registry(
    with_registry: TestClient, registry: ContractRegistry, h: SimpleNamespace, storage_dir: Path
) -> None:
    builtin = files_package()
    registry.publish(builtin.package_id, builtin.version, variant(builtin.package_id, description="other"))
    ok = store(with_registry, h, builtin.ref, "dk-builtin")
    assert ok.status_code == 200 and ok.json()["handler"] == builtin.ref, ok.text
    # another digest for the built-in id@version is refused without asking the registry
    other = {**builtin.ref, "digest": "sha256:" + "0" * 64}
    refused = store(with_registry, h, other, "dk-builtin-other")
    assert refused.status_code == 422 and refused.json()["code"] == "digest_mismatch", refused.text
    assert registry.downloads() == 0
    assert len(written(storage_dir)) == 1


def test_test_run_of_a_registry_package(
    with_registry: TestClient, registry: ContractRegistry, storage_dir: Path
) -> None:
    fork = registry.publish("jane.storage-files-tested", "1.0.0", variant("jane.storage-files-tested"))
    r = with_registry.post(
        "/v1/test-runs", json={"handler": fork, "tests": "all"}, headers={"Idempotency-Key": "tr-reg"}
    )
    assert r.status_code == 202, r.text
    job = r.json()
    for _ in range(500):
        job = with_registry.get(f"/v1/jobs/{job['job_id']}").json()
        if job["status"] in {"succeeded", "failed"}:
            break
    report = job["result"]
    assert report["package"] == fork and report["passed"] == 2 and report["failed"] == 0, report
    assert written(storage_dir) == []  # test_mode


# ---------------------------------------------------------------------------- digests and identity
def test_digest_mismatch_writes_nothing(
    with_registry: TestClient, registry: ContractRegistry, h: SimpleNamespace, storage_dir: Path
) -> None:
    fork = registry.publish("jane.storage-files-pinned", "1.0.0", variant("jane.storage-files-pinned"))
    wrong = {**fork, "digest": digest(variant("jane.storage-files-pinned", description="substituted"))}
    r = store(with_registry, h, wrong, "dk-mismatch")
    assert r.status_code == 422, r.text
    problem = r.json()
    assert problem["code"] == "digest_mismatch" and problem["retryable"] is False, problem
    assert fork["digest"] in problem["detail"]
    assert written(storage_dir) == []


def test_digest_of_another_version_is_refused_with_cold_and_warm_cache(
    with_registry: TestClient, registry: ContractRegistry, h: SimpleNamespace, storage_dir: Path
) -> None:
    """The LLM gateway defect of WP-13 (cache hit before the id/version check) must not exist in storage."""
    pid = "jane.storage-files-cache"
    registry.publish(pid, "1.0.0", variant(pid, "1.0.0"))
    v101 = registry.publish(pid, "1.0.1", variant(pid, "1.0.1", description="1.0.1"))
    foreign = {"package_id": pid, "version": "1.0.0", "digest": v101["digest"]}
    cold = store(with_registry, h, foreign, "dk-foreign-cold")
    assert cold.status_code == 422 and cold.json()["code"] == "digest_mismatch", cold.text
    ok = store(with_registry, h, v101, "dk-own")
    assert ok.status_code == 200 and ok.json()["handler"] == v101, ok.text
    downloads = registry.downloads()
    warm = store(with_registry, h, foreign, "dk-foreign-warm")
    assert warm.status_code == 422, warm.text
    assert warm.json()["code"] == "digest_mismatch" and f"{pid}@1.0.1" in warm.json()["detail"], warm.text
    assert registry.downloads() == downloads  # refused from the cache, nothing ran
    assert len(written(storage_dir)) == 1


def test_registry_archive_under_another_address_is_refused_and_not_cached(
    with_registry: TestClient, registry: ContractRegistry, h: SimpleNamespace
) -> None:
    pid = "jane.storage-files-moved"
    other = variant(pid, "2.0.0")
    registry.archives[(pid, "1.0.0")] = other  # registry fault: 1.0.0 serves the content of 2.0.0
    unpinned = store(with_registry, h, {"package_id": pid, "version": "1.0.0"}, "dk-moved-1")
    assert unpinned.status_code == 422 and unpinned.json()["code"] == "validation_failed", unpinned.text
    pinned = store(with_registry, h, ref(pid, other), "dk-moved-2")  # the pin is 2.0.0's content
    assert pinned.status_code == 422 and pinned.json()["code"] == "digest_mismatch", pinned.text
    assert registry.downloads() == 2  # nothing cached under the wrong address


def test_etag_that_does_not_match_the_bytes_is_refused(
    with_registry: TestClient, registry: ContractRegistry, h: SimpleNamespace
) -> None:
    archive = variant("jane.storage-files-etag")
    registry.override = lambda request: httpx.Response(
        200,
        content=archive,
        headers={"content-type": "application/zip", "etag": f'"sha256:{"1" * 64}"'},
    )
    r = store(with_registry, h, ref("jane.storage-files-etag", archive), "dk-etag")
    assert r.status_code == 422 and r.json()["code"] == "digest_mismatch", r.text
    assert "ETag" in r.json()["detail"]


# ---------------------------------------------------------------------------- package type
@pytest.mark.parametrize(
    ("change", "code", "needle"),
    [
        ({"kind": "extractor"}, "validation_failed", "not a storage package"),
        (
            {"entry": {"executor": "llm", "instructions": "p.md", "output_schema": "o.json"}},
            "validation_failed",
            "storage",
        ),
        ({"dependencies": {"python": ["requests>=2,<3"]}}, "dependency_not_allowed", "dependencies.python"),
        (
            {"dependencies": {"runtime_profile": "python-extractor@1"}},
            "dependency_not_allowed",
            "runtime_profile",
        ),
        ({"entry": {**files_package().entry, "adapter": "cassandra"}}, "validation_failed", "not installed"),
        ({"entry": {**files_package().entry, "history": False}}, "validation_failed", "history"),
        ({"entry": {**files_package().entry, "writes": "everything"}}, "validation_failed", "entry.writes"),
        ({"entry": {**files_package().entry, "format": {"raw": []}}}, "validation_failed", "entry.format"),
        (
            {"entry": {**files_package().entry, "format": {"entities": {}}}},
            "validation_failed",
            "entry.format",
        ),
        ({"input": {"accepts": "material"}}, "validation_failed", "input.accepts"),
        ({"input": {"accepts": [{}]}}, "validation_failed", "input.accepts"),
        ({"dependencies": {"unknown": "unexpected"}}, "dependency_not_allowed", "dependencies"),
    ],
)
def test_only_storage_packages_without_dependencies_are_executed(
    with_registry: TestClient,
    registry: ContractRegistry,
    h: SimpleNamespace,
    storage_dir: Path,
    change: dict[str, Any],
    code: str,
    needle: str,
) -> None:
    pid = "jane.storage-files-odd"
    archive = variant(pid, **change)
    registry.publish(pid, "1.0.0", archive)
    r = store(with_registry, h, ref(pid, archive), "dk-odd")
    assert r.status_code == 422, r.text
    assert r.json()["code"] == code and needle in r.text, r.text
    assert written(storage_dir) == []


# ---------------------------------------------------------------------------- registry failures
def _connect_error(request: httpx.Request) -> httpx.Response:
    raise httpx.ConnectError("connection refused", request=request)


@pytest.mark.parametrize(
    ("answer", "retryable"),
    [
        (_connect_error, True),
        (lambda r: httpx.Response(503, text="maintenance"), True),
        (lambda r: httpx.Response(500, text="boom"), True),
        (lambda r: httpx.Response(302, headers={"location": "http://elsewhere.test/a.zip"}), False),
    ],
    ids=["connection-refused", "503", "500", "redirect-not-followed"],
)
def test_unavailable_registry_is_upstream_unavailable(
    with_registry: TestClient,
    registry: ContractRegistry,
    h: SimpleNamespace,
    storage_dir: Path,
    answer: Callable[[httpx.Request], httpx.Response],
    retryable: bool,
) -> None:
    registry.override = answer
    archive = variant("jane.storage-files-down")
    r = store(with_registry, h, ref("jane.storage-files-down", archive), "dk-down")
    assert r.status_code == 502, r.text
    problem = r.json()
    assert problem["code"] == "upstream_unavailable" and problem["retryable"] is retryable, problem
    assert [str(q.url.host) for q in registry.requests] == ["registry.test"]  # one request, no redirect
    assert written(storage_dir) == []


def test_unknown_version_is_not_found(
    with_registry: TestClient, registry: ContractRegistry, h: SimpleNamespace
) -> None:
    r = store(with_registry, h, {"package_id": "jane.storage-files-nowhere", "version": "9.9.9"}, "dk-404")
    assert r.status_code == 404 and r.json()["code"] == "not_found", r.text
    assert "jane.storage-files-nowhere@9.9.9" in r.json()["detail"]


def test_bearer_token_goes_to_the_registry_and_nowhere_else(
    settings: Settings,
    registry: ContractRegistry,
    h: SimpleNamespace,
    caplog: pytest.LogCaptureFixture,
) -> None:
    registry.require_token = TOKEN
    fork = registry.publish("jane.storage-files-auth", "1.0.0", variant("jane.storage-files-auth"))
    caplog.set_level(logging.DEBUG)
    anonymous = settings.with_overrides(registry_url=REGISTRY_URL)
    with TestClient(build_app(anonymous, registry_transport=registry.transport)) as c:
        refused = store(c, h, fork, "dk-anon")
    assert refused.status_code == 502, refused.text
    assert refused.json()["code"] == "upstream_unavailable" and refused.json()["retryable"] is False
    authorized = Settings(
        log_format="console",
        connections_file=settings.connections_file,
        registry_url=REGISTRY_URL + "/",
        registry_token=TOKEN,
    )
    with TestClient(build_app(authorized, registry_transport=registry.transport)) as c:
        ok = store(c, h, fork, "dk-auth")
        info = c.get("/v1/info").text
    assert ok.status_code == 200, ok.text
    assert registry.requests[-1].headers["authorization"] == f"Bearer {TOKEN}"
    assert TOKEN not in caplog.text and TOKEN not in info and TOKEN not in ok.text


def test_without_registry_an_unknown_package_stays_not_found(client: TestClient, h: SimpleNamespace) -> None:
    r = store(client, h, {"package_id": "jane.storage-files-fork", "version": "1.0.0"}, "dk-none")
    assert r.status_code == 404 and r.json()["code"] == "not_found", r.text


# ---------------------------------------------------------------------------- limits
def test_archive_limits_come_from_configuration(
    settings: Settings, registry: ContractRegistry, h: SimpleNamespace, monkeypatch: pytest.MonkeyPatch
) -> None:
    big = variant("jane.storage-files-big", description="x" * 200_000)
    registry.publish("jane.storage-files-big", "1.0.0", big)
    monkeypatch.setenv("JANE_STORAGE_LIMITS__PACKAGES__MAX_ARCHIVE_BYTES", "100000")
    configured = settings.with_overrides(registry_url=REGISTRY_URL)
    with TestClient(build_app(configured, registry_transport=registry.transport)) as c:
        declared = store(c, h, ref("jane.storage-files-big", big), "dk-big")
        assert declared.status_code == 422 and declared.json()["code"] == "limit_exceeded", declared.text

        async def chunks() -> AsyncIterator[bytes]:
            for i in range(0, len(big), 4096):
                yield big[i : i + 4096]

        def chunked(request: httpx.Request) -> httpx.Response:  # no Content-Length: the stream is cut
            return httpx.Response(200, content=chunks(), headers={"content-type": "application/zip"})

        registry.override = chunked
        streamed = store(c, h, ref("jane.storage-files-big", big), "dk-big-2")
        assert streamed.status_code == 422 and streamed.json()["code"] == "limit_exceeded", streamed.text
    monkeypatch.setenv("JANE_STORAGE_LIMITS__PACKAGES__MAX_ARCHIVE_BYTES", str(10 * 1024 * 1024))
    monkeypatch.setenv("JANE_STORAGE_LIMITS__PACKAGES__MAX_UNPACKED_BYTES", "100000")
    registry.override = None
    with TestClient(build_app(configured, registry_transport=registry.transport)) as c:
        unpacked = store(c, h, ref("jane.storage-files-big", big), "dk-big-3")
    assert unpacked.status_code == 422 and "max_unpacked_bytes" in unpacked.text, unpacked.text


def test_slow_registry_hits_the_configured_timeout(
    settings: Settings, h: SimpleNamespace, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def slow(request: httpx.Request) -> httpx.Response:
        await asyncio.sleep(5)
        return httpx.Response(404)

    monkeypatch.setenv("JANE_STORAGE_LIMITS__PACKAGES__REGISTRY_REQUEST_TIMEOUT_MS", "200")
    configured = settings.with_overrides(registry_url=REGISTRY_URL)
    with TestClient(build_app(configured, registry_transport=httpx.MockTransport(slow))) as c:
        r = store(c, h, {"package_id": "jane.storage-files-slow", "version": "1.0.0"}, "dk-slow")
    assert r.status_code == 502 and r.json()["retryable"] is True, r.text
    assert "registry_request_timeout_ms=200" in r.json()["detail"]


def test_concurrent_requests_share_one_download() -> None:
    archive = variant("jane.storage-files-burst")
    calls = 0

    async def answer(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        await asyncio.sleep(0.05)
        return httpx.Response(200, content=archive, headers={"etag": f'"{digest(archive)}"'})

    packages = RegistryPackages(REGISTRY_URL, PackageLimits(), transport=httpx.MockTransport(answer))

    async def burst() -> list[StoragePackage]:
        wanted = ref("jane.storage-files-burst", archive)
        return await asyncio.gather(*(packages.get(wanted) for _ in range(8)))

    got = asyncio.run(burst())
    assert calls == packages.downloads == 1
    assert {p.digest for p in got} == {digest(archive)}
    assert packages._locks == {}


def test_cache_is_bounded_by_configuration() -> None:
    archives = {v: variant("jane.storage-files-lru", v) for v in ("1.0.0", "1.0.1", "1.0.2")}

    def answer(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=archives[request.url.path.split("/")[5]])

    packages = RegistryPackages(
        REGISTRY_URL, PackageLimits(cache_max_entries=2), transport=httpx.MockTransport(answer)
    )

    async def load(*versions: str) -> None:
        for v in versions:
            await packages.get(ref("jane.storage-files-lru", archives[v], v))

    asyncio.run(load("1.0.0", "1.0.1", "1.0.2", "1.0.2", "1.0.0"))
    assert packages.downloads == 4  # 1.0.0 was evicted by 1.0.2 and downloaded again
    assert len(packages._cache) == 2 and len(packages._by_ref) == 2


# ---------------------------------------------------------------------------- configuration
@pytest.mark.parametrize(
    "url",
    [
        "ftp://registry:8000",
        "http://user:secret@registry:8000",
        "http://registry:8000?x=1",
        "http://registry:8000/#frag",
        "http://a,b:8000",
        "registry:8000",
        "http://registry :8000",
    ],
)
def test_registry_url_must_be_a_plain_http_service_url(url: str) -> None:
    with pytest.raises(ValidationError, match="registry_url"):
        Settings(log_format="console", registry_url=url)


def test_registry_settings_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JANE_STORAGE_REGISTRY_URL", "https://registry.example.test:8443/jane/")
    monkeypatch.setenv("JANE_STORAGE_REGISTRY_TOKEN", TOKEN)
    s = Settings(log_format="console")
    assert s.registry_url == "https://registry.example.test:8443/jane"
    assert s.registry_token is not None and TOKEN not in repr(s)
    monkeypatch.setenv("JANE_STORAGE_REGISTRY_URL", "")
    assert Settings(log_format="console").registry_url is None


# ---------------------------------------------------------------------------- the real registry
class ForwardTransport(httpx.AsyncBaseTransport):
    """Sends storage's registry requests to an in-process registry app (its own TestClient thread)."""

    def __init__(self, client: TestClient) -> None:
        self.client = client

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        headers = {k: v for k, v in request.headers.items() if k.lower() in {"accept", "authorization"}}
        answer = await asyncio.to_thread(self.client.get, request.url.path, headers=headers)
        keep = {k: v for k, v in answer.headers.items() if k.lower() in {"content-type", "etag"}}
        return httpx.Response(answer.status_code, headers=keep, content=answer.content)


def test_fork_from_the_real_registry_runs_in_storage(
    settings: Settings, tmp_path: Path, h: SimpleNamespace, storage_dir: Path
) -> None:
    """Real neighbour: the registry service (WP-05, ``memory`` backend) publishes ``jane.storage-files`` with the
    storage CLI function, forks it; storage executes the fork by its registry reference (digest from the
    registry) - the case of WP-13 criterion 9 that failed with 404."""
    registry_app = pytest.importorskip("jane_registry.app")
    registry_settings = pytest.importorskip("jane_registry.settings")
    from jane_storage.packages import publish

    reg = registry_settings.Settings(
        db="memory", blob="filesystem", blob_root=tmp_path / "blobs", log_format="console"
    )
    with TestClient(registry_app.build_app(reg)) as registry:
        (outcome,) = publish(registry, [files_package()])
        assert outcome.ok, outcome
        forked = registry.post(
            "/v1/packages/jane.storage-files/forks",
            json={"new_package_id": "jane.storage-files-wp07c", "from_version": "1.0.0"},
            headers={"Idempotency-Key": "fork-wp07c"},
        )
        assert forked.status_code == 201, forked.text
        version = registry.get("/v1/packages/jane.storage-files-wp07c/versions/1.0.0").json()
        fork = {"package_id": "jane.storage-files-wp07c", "version": "1.0.0", "digest": version["digest"]}
        assert version["manifest"]["fork_of"]["package_id"] == "jane.storage-files"
        configured = settings.with_overrides(registry_url="http://registry:8000")
        with TestClient(build_app(configured, registry_transport=ForwardTransport(registry))) as storage:
            r = store(storage, h, fork, "dk-real-fork")
            assert r.status_code == 200, r.text
            result = r.json()
            assert result["status"] == "success" and result["handler"] == fork, result
            (ack,) = result["output"]["writes"]
            assert (storage_dir / ack["object"]["locator"]["path"]).read_bytes() == h.PAGE
            other = store(storage, h, {**fork, "digest": outcome.digest}, "dk-real-parent-digest")
            assert other.status_code == 422 and other.json()["code"] == "digest_mismatch", other.text


def test_package_archive_limits_and_unsafe_archives(client: TestClient, h: SimpleNamespace) -> None:
    """``package_archive`` goes through the same reader: broken zip, unsafe path, duplicates."""
    import io
    import warnings
    import zipfile

    def post_archive(archive: bytes, dk: str) -> httpx.Response:
        body = h.invocation(
            [{"kind": "material", "material": h.material()}],
            dk,
            package="jane.storage-files-local",
            package_archive={
                "kind": "inline",
                "media_type": "application/zip",
                "encoding": "base64",
                "data": base64.b64encode(archive).decode(),
            },
        )
        response: httpx.Response = h.post(client, body)
        return response

    assert post_archive(b"not a zip", "dk-pa-1").json()["code"] == "validation_failed"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("../escape.json", "{}")
    assert "unsafe path" in post_archive(buf.getvalue(), "dk-pa-2").text
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf, warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)  # zipfile warns about the duplicate it writes
        zf.writestr("jane-package.json", "{}")
        zf.writestr("jane-package.json", "{}")
    assert "duplicate entry" in post_archive(buf.getvalue(), "dk-pa-3").text
    deps = variant(
        "jane.storage-files-local", dependencies={"packages": [{"package_id": "x", "version": "1.0.0"}]}
    )
    r = post_archive(deps, "dk-pa-4")
    assert r.status_code == 422 and r.json()["code"] == "dependency_not_allowed", r.text
