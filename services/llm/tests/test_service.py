"""Gateway and handler behaviour on the real app (memory store; PostgreSQL variant under ``integration``)."""

from __future__ import annotations

import asyncio
import base64
import json
import threading
import time
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import httpx
import pytest
import uvicorn
from fastapi.testclient import TestClient
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from jane_kit.clients import ClientLimits
from jane_kit.contracts import OpenAPISpec, build_mock_app, contracts_dir
from jane_kit.errors import JaneError, NotFound, ValidationFailed
from jane_llm.packages import (
    DigestMismatch,
    PackageLoader,
    build_archive,
    digest_of,
    publish,
    publish_request,
    read_dir,
)
from jane_llm.providers import AnthropicProvider, ProviderError, ProviderRequest, ResolvedConnection
from jane_llm.settings import GatewayLimits, ServiceLimits

PACKAGE_DIR = Path(__file__).resolve().parents[1] / "packages" / "jane.llm-event-extractor"
EVENT = {"title": "Концерт", "starts_at": "2026-10-12T19:00:00+03:00", "venue": "Філармонія", "price": "free"}


def _scripted(client: TestClient, responses: list[dict[str, Any]], pricing: float = 0) -> None:
    conn = {
        "connection_id": "fake-scripts",
        "kind": "llm_provider",
        "params": {"provider": "fake", "responses": responses},
    }
    assert client.put("/v1/connections/fake-scripts", json=conn).status_code in {200, 201}
    provider = {
        "provider_id": "fake",
        "kind": "fake",
        "connection_id": "fake-scripts",
        "enabled": True,
        "models": [
            {
                "model_id": "fake-deterministic-1",
                "max_context_tokens": 128000,
                "supports_structured_output": True,
                "pricing": {"input_per_mtok": pricing, "output_per_mtok": pricing, "currency": "USD"},
            }
        ],
    }
    assert client.put("/v1/providers/fake", json=provider).status_code == 200


def test_health_info_metrics(client: TestClient) -> None:
    assert client.get("/v1/health").json() == {"status": "ok", "checks": {"store": {"status": "ok"}}}
    info = client.get("/v1/info").json()
    assert info["service"] == "llm"
    assert info["capabilities"]["handler_kinds"] == ["llm"]
    assert "anthropic" in info["capabilities"]["provider_kinds"]
    assert info["limits"]["defaults"]["llm"]["max_output_tokens_per_request"] == 4096


def test_schema_retries_then_invalid(client: TestClient, fake: Any, h: Any) -> None:
    _scripted(client, [{"when_data_contains": "Kettle", "output": {"page_type": "teapot"}}], pricing=1)
    r = client.post("/v1/completions", json=h.completion(max_schema_retries=1), headers=h.idem())
    body = r.json()
    assert r.status_code == 200
    assert body["valid"] is False
    assert body["validation_errors"][0]["pointer"] == "/page_type"
    assert "output_text" in body and "output" not in body
    assert len(fake.calls) == 2
    assert "Correction" in fake.calls[1].system and "teapot" not in fake.calls[1].system  # no data in hints
    usage = client.get("/v1/usage", params={"group_by": "model"}).json()
    assert usage["totals"]["requests"] == 2
    metrics = client.get("/metrics").text
    assert (
        'jane_llm_requests_total{model="fake-deterministic-1",outcome="invalid_output",provider="fake"} 2.0'
        in metrics
    )


def test_provider_failure_releases_reservation(client: TestClient, fake: Any, h: Any) -> None:
    _scripted(client, [{"when_data_contains": "Kettle", "error": "unavailable"}], pricing=1000)
    client.put(
        "/v1/budgets/task/t",
        json={
            "scope_type": "task",
            "scope_id": "t",
            "budget": {"amount": 1, "currency": "USD", "period": "total"},
        },
    )
    for _ in range(5):  # the estimate (~0.41) is released each time, so the budget never fills up
        r = client.post(
            "/v1/completions", json=h.completion(scope={"purpose": "other", "task_id": "t"}), headers=h.idem()
        )
        assert r.status_code == 502
        assert r.json()["code"] == "upstream_unavailable" and r.json()["retryable"] is True
    status = next(b for b in client.get("/v1/budgets").json()["items"] if b["scope_id"] == "t")["status"]
    assert status["spent"]["amount"] == 0
    assert len(fake.calls) == 5


def test_rate_limit_per_scope(client: TestClient, h: Any) -> None:
    client.put(
        "/v1/budgets/source/shop",
        json={"scope_type": "source", "scope_id": "shop", "max_requests_per_minute": 2},
    )
    body = h.completion(scope={"purpose": "other", "source_id": "shop"})
    codes = [client.post("/v1/completions", json=body, headers=h.idem()) for _ in range(3)]
    assert [c.status_code for c in codes] == [200, 200, 429]
    assert codes[2].json()["code"] == "rate_limited" and "Retry-After" in codes[2].headers


def test_input_limit_from_config(
    make_client: Callable[..., TestClient], h: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("JANE_LLM_LIMITS__LLM__MAX_INPUT_TOKENS_PER_REQUEST", "50")
    client = make_client()
    r = client.post("/v1/completions", json=h.completion(), headers=h.idem())
    assert r.status_code == 422 and r.json()["code"] == "limit_exceeded"


def test_output_tokens_are_bounded(
    make_client: Callable[..., TestClient], fake: Any, h: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("JANE_LLM_LIMITS__HARD_CAPS__LLM__MAX_OUTPUT_TOKENS_PER_REQUEST", "10")
    client = make_client()
    body = h.completion(max_output_tokens=500, limits={"max_output_tokens_per_request": 400})
    assert client.post("/v1/completions", json=body, headers=h.idem()).status_code == 200
    assert fake.calls[-1].max_output_tokens == 10


def test_package_tests_pass_via_test_runs(client: TestClient, h: Any) -> None:
    _scripted(client, [{"when_data_contains": "Концерт", "output": {"events": [EVENT]}}])
    run = client.post(
        "/v1/test-runs",
        json={"handler": {"package_id": "jane.llm-event-extractor", "version": "1.0.0"}, "tests": "all"},
        headers=h.idem(),
    )
    job_id = run.json()["job_id"]
    for _ in range(200):
        job = client.get(f"/v1/jobs/{job_id}").json()
        if job["status"] == "succeeded":
            break
        time.sleep(0.02)
    report = job["result"]
    assert (report["passed"], report["failed"]) == (2, 0), json.dumps(report, ensure_ascii=False)[:2000]
    assert all(c["result"]["test_mode"] for c in report["cases"])
    usage = client.get("/v1/usage").json()
    assert usage["items"] and all(i["test_mode"] for i in usage["items"])


def test_invocation_result_links_input_and_version(client: TestClient, h: Any) -> None:
    _scripted(client, [{"when_data_contains": "Концерт", "output": {"events": [EVENT]}}])
    material = json.loads((PACKAGE_DIR / "tests" / "concert" / "material.json").read_text(encoding="utf-8"))
    inv = {
        "handler": {"package_id": "jane.llm-event-extractor", "version": "1.0.0"},
        "inputs": [{"kind": "material", "material": material}],
        "context": {"trace": {"source_id": "news-tg", "task_id": "events", "run_id": "run_1"}},
        "delivery": {"delivery_key": "d-1"},
    }
    res = client.post("/v1/invocations", json=inv, headers={"Idempotency-Key": "d-1"}).json()
    assert res["status"] == "success"
    assert res["handler"]["digest"] == digest_of(build_archive(read_dir(PACKAGE_DIR)))
    assert res["inputs"] == [
        {
            "kind": "material",
            "material_id": material["material_id"],
            "observation_id": material["observation_id"],
            "content_sha256": material["revision"]["content_sha256"],
        }
    ]
    entity = res["output"]["entities"][0]
    assert entity["key"] == {"scope": "news-tg", "natural": {"message": material["material_id"]}}
    assert entity["observation"]["observation_id"] == material["observation_id"]
    assert entity["fields"]["venue"] == "Філармонія"
    assert res["output"]["data"] == {"events": [EVENT]}
    assert res["usage"]["llm"]["provider"] == "fake"
    other = client.post(
        "/v1/invocations", json={**inv, "params": {"x": 1}}, headers={"Idempotency-Key": "d-1"}
    )
    assert other.status_code == 422 and other.json()["code"] == "idempotency_key_reused"


def test_invalid_entity_is_schema_mismatch(client: TestClient, h: Any) -> None:
    _scripted(client, [{"when_data_contains": "Концерт", "output": {"events": [{"venue": "no title"}]}}])
    material = json.loads((PACKAGE_DIR / "tests" / "concert" / "material.json").read_text(encoding="utf-8"))
    inv = {
        "handler": {"package_id": "jane.llm-event-extractor", "version": "1.0.0"},
        "inputs": [{"kind": "material", "material": material}],
        "delivery": {"delivery_key": "d-2"},
    }
    res = client.post("/v1/invocations", json=inv, headers={"Idempotency-Key": "d-2"}).json()
    assert res["status"] == "failed"
    assert res["failure"]["kind"] == "schema_mismatch"
    assert res["diagnostics"]["validation_errors"]


def test_seed_file(make_client: Callable[..., TestClient], tmp_path: Path) -> None:
    seed = tmp_path / "seed.yaml"
    seed.write_text(
        """
connections:
  - connection_id: anthropic-main
    kind: llm_provider
    secret_refs: {api_key: "env:JANE_SECRET_TEST_ANTHROPIC_KEY"}
providers:
  - provider_id: anthropic
    kind: anthropic
    connection_id: anthropic-main
    enabled: true
    models:
      - {model_id: claude-haiku-4-5, pricing: {input_per_mtok: 1, output_per_mtok: 5, currency: USD}}
model_aliases:
  - {alias: cheap, provider_id: anthropic, model_id: claude-haiku-4-5}
budgets:
  - {scope_type: platform, scope_id: platform, budget: {amount: 20, currency: USD, period: day}}
""",
        encoding="utf-8",
    )
    client = make_client(settings={"seed_file": seed})
    aliases = {a["alias"]: a for a in client.get("/v1/model-aliases").json()["items"]}
    assert aliases["cheap"]["provider_id"] == "anthropic"
    assert aliases["default"]["provider_id"] == "fake"
    budgets = client.get("/v1/budgets").json()["items"]
    assert budgets[0]["budget"]["amount"] == 20
    tested = client.post("/v1/connections/anthropic-main/test").json()
    assert tested["secrets_resolved"] == {"api_key": False}


def test_example_seed_is_valid(make_client: Callable[..., TestClient]) -> None:
    example = Path(__file__).resolve().parents[1] / "config" / "seed.example.yaml"
    client = make_client(settings={"seed_file": example})
    assert {p["provider_id"] for p in client.get("/v1/providers").json()["items"]} >= {"anthropic", "fake"}


# ---------------------------------------------------------------- connection secret policy (review 1)
def test_connection_policy_rejects_exfiltration(
    make_client: Callable[..., TestClient], tmp_path: Path, fake: Any, h: Any
) -> None:
    secrets_dir = tmp_path / "secrets"
    secrets_dir.mkdir()
    client = make_client(settings={"secret_files_dir": secrets_dir})

    def put(params: dict[str, Any] | None, refs: dict[str, str]) -> Any:
        conn: dict[str, Any] = {"connection_id": "evil", "kind": "llm_provider", "secret_refs": refs}
        if params is not None:
            conn["params"] = params
        return client.put("/v1/connections/evil", json=conn)

    cases = {
        "env outside prefix": put(None, {"api_key": "env:PATH"}),
        "file outside dir": put(None, {"api_key": f"file:{tmp_path / 'other.txt'}"}),
        "file traversal": put(None, {"api_key": f"file:{secrets_dir}/../other.txt"}),
        "vault": put(None, {"api_key": "vault:kv/llm#key"}),
        "foreign api_base": put({"api_base": "https://attacker.example"}, {"api_key": "env:JANE_SECRET_X"}),
        "look-alike api_base": put(
            {"api_base": "https://api.anthropic.com.attacker.example"}, {"api_key": "env:JANE_SECRET_X"}
        ),
    }
    for name, r in cases.items():
        assert r.status_code == 422, name
        assert r.json()["errors"][0]["code"] in {"secret_ref_not_allowed", "api_base_not_allowed"}, name
    assert client.get("/v1/connections").json()["items"] == []
    ok = put(
        {"api_base": "https://api.anthropic.com/"},
        {"api_key": "env:JANE_SECRET_X", "b": f"file:{secrets_dir / 'k'}"},
    )
    assert ok.status_code == 201

    # A connection stored behind the API's back (old data, direct DB edit) is still refused at call time.
    store = client.app.state.store  # type: ignore[attr-defined]
    store.put_doc(
        "connection",
        "legacy",
        {
            "connection_id": "legacy",
            "kind": "llm_provider",
            "params": {"api_base": "https://attacker.example"},
            "secret_refs": {"api_key": "env:JANE_SECRET_X"},
        },
    )
    provider = {
        "provider_id": "anthropic",
        "kind": "anthropic",
        "connection_id": "legacy",
        "enabled": True,
        "models": [
            {
                "model_id": "claude-opus-5",
                "pricing": {"input_per_mtok": 5, "output_per_mtok": 25, "currency": "USD"},
            }
        ],
    }
    assert client.put("/v1/providers/anthropic", json=provider).status_code == 200
    r = client.post("/v1/completions", json=h.completion(model="anthropic/claude-opus-5"), headers=h.idem())
    assert r.status_code == 422 and "api_base" in r.json()["detail"]
    tested = client.post("/v1/connections/legacy/test").json()
    assert tested["ok"] is False and tested["secrets_resolved"] == {"api_key": False}


def test_package_archive_limits(make_client: Callable[..., TestClient], h: Any) -> None:
    import base64
    import io
    import zipfile

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("jane-package.json", "{}")
        zf.writestr("big.txt", b"0" * 5_000_000)  # compresses to a few KB
    client = make_client()
    archive = {
        "kind": "inline",
        "media_type": "application/zip",
        "encoding": "base64",
        "data": base64.b64encode(buf.getvalue()).decode(),
    }
    inv = {
        "handler": {"package_id": "x.y", "version": "1.0.0"},
        "package_archive": archive,
        "inputs": [{"kind": "data", "data": {}}],
        "delivery": {"delivery_key": "zip-1"},
    }
    import os

    os.environ["JANE_LLM_LIMITS__GATEWAY__MAX_PACKAGE_BYTES"] = "1000000"
    try:
        small = make_client()
    finally:
        del os.environ["JANE_LLM_LIMITS__GATEWAY__MAX_PACKAGE_BYTES"]
    r = small.post("/v1/invocations", json=inv, headers={"Idempotency-Key": "zip-1"})
    assert r.status_code == 422 and "max_package_bytes" in r.json()["detail"]
    r = client.post("/v1/invocations", json=inv, headers={"Idempotency-Key": "zip-2"})
    assert r.status_code == 422 and "max_package_bytes" not in r.json()["detail"]  # passes the size limit


# ---------------------------------------------------------------- registry (neighbour)
def test_publish_to_registry_contract_mock() -> None:
    root = contracts_dir(Path(__file__).parent)
    if root is None:
        pytest.skip("contracts/ not available")
    mock = build_mock_app(OpenAPISpec.load(root / "openapi" / "registry.v1.yaml"))
    calls: list[tuple[str, str]] = []

    async def app(scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] == "http":
            calls.append((scope["method"], scope["path"]))
        await mock(scope, receive, send)

    body = publish_request(PACKAGE_DIR)
    assert body["manifest"]["kind"] == "llm" and "jane-package.json" not in body["files"]
    result = asyncio.run(publish(PACKAGE_DIR, "http://registry", transport=httpx.ASGITransport(app=app)))
    # The contract mock rejects (422) requests that do not match registry.v1, so reaching here means both
    # the PackageCreate and the PublishRequest bodies are valid.
    assert calls == [("POST", "/v1/packages"), ("POST", "/v1/packages/jane.llm-event-extractor/versions")]
    assert "package_id" in result


def test_loader_fetches_from_registry_and_checks_digest(tmp_path: Path) -> None:
    archive = build_archive(read_dir(PACKAGE_DIR))
    seen: list[str] = []

    async def archive_endpoint(request: Request) -> Response:
        seen.append(request.url.path)
        return Response(archive, media_type="application/zip", headers={"ETag": f'"{digest_of(archive)}"'})

    registry = Starlette(routes=[Route("/v1/packages/{pid}/versions/{v}/archive", archive_endpoint)])
    loader = PackageLoader(
        None,
        "http://registry",
        ClientLimits(),
        limits=GatewayLimits(),
        transport=httpx.ASGITransport(app=registry),
    )
    ref = {"package_id": "jane.llm-event-extractor", "version": "1.0.0", "digest": digest_of(archive)}
    pkg = asyncio.run(loader.load(ref, None))
    assert pkg.manifest["kind"] == "llm"
    assert seen == ["/v1/packages/jane.llm-event-extractor/versions/1.0.0/archive"]
    with pytest.raises(Exception, match="digest"):
        asyncio.run(
            PackageLoader(
                None,
                "http://registry",
                ClientLimits(),
                limits=GatewayLimits(),
                transport=httpx.ASGITransport(app=registry),
            ).load({**ref, "digest": "sha256:" + "1" * 64}, None)
        )


# Package identity on a cache hit (WP-10c, defect 1 of WP-13 criterion 9): the cache keyed by digest only saves
# fetching and unpacking, so an invocation gets the same answer on a cold and a warm loader.
CACHE_PKG = "test.llm-cache-identity"


def _version_archive(package_id: str, version: str, note: bytes = b"") -> bytes:
    """Archive of the built-in LLM package re-labelled ``package_id@version`` (``note`` changes its prompt)."""
    files = read_dir(PACKAGE_DIR)
    manifest = json.loads(files["jane-package.json"])
    manifest.update(package_id=package_id, version=version)
    files["jane-package.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    files["prompts/instructions.md"] += note
    return build_archive(files)


def _registry_archives(archives: dict[tuple[str, str], bytes], seen: list[str]) -> Starlette:
    """Registry neighbour: ``downloadPackageArchive`` of registry.v1 (zip, ``ETag`` = digest, 404 problem)."""
    root = contracts_dir(Path(__file__).parent)
    spec = OpenAPISpec.load(root / "openapi" / "registry.v1.yaml") if root is not None else None

    async def archive_endpoint(request: Request) -> Response:
        if spec is not None:
            assert spec.operation("GET", request.url.path).operation_id == "downloadPackageArchive"
        seen.append(request.url.path)
        data = archives.get((request.path_params["pid"], request.path_params["v"]))
        if data is None:
            problem = {"type": "urn:jane:problem:not_found", "title": "Not found", "status": 404}
            return JSONResponse({**problem, "code": "not_found"}, status_code=404)
        return Response(data, media_type="application/zip", headers={"ETag": f'"{digest_of(data)}"'})

    return Starlette(routes=[Route("/v1/packages/{pid}/versions/{v}/archive", archive_endpoint)])


def _inline(data: bytes) -> dict[str, Any]:
    return {
        "kind": "inline",
        "media_type": "application/zip",
        "encoding": "base64",
        "data": base64.b64encode(data).decode("ascii"),
    }


def test_loader_cache_hit_requires_the_referenced_package_and_version() -> None:
    v100 = _version_archive(CACHE_PKG, "1.0.0")
    v101 = _version_archive(CACHE_PKG, "1.0.1", b"\nKeep the summary under twenty words.\n")
    d100, d101 = digest_of(v100), digest_of(v101)
    seen: list[str] = []
    registry = _registry_archives({(CACHE_PKG, "1.0.0"): v100, (CACHE_PKG, "1.0.1"): v101}, seen)
    loader = PackageLoader(
        None,
        "http://registry",
        ClientLimits(),
        limits=GatewayLimits(),
        transport=httpx.ASGITransport(app=registry),
    )
    foreign = {"package_id": CACHE_PKG, "version": "1.0.0", "digest": d101}
    other_id = {"package_id": f"{CACHE_PKG}-other", "version": "1.0.1", "digest": d101}

    def refused(ref: dict[str, str]) -> JaneError:
        with pytest.raises(JaneError) as exc:
            asyncio.run(loader.load(ref, None))
        return exc.value

    cold = (type(refused(foreign)), type(refused(other_id)))
    assert cold == (DigestMismatch, NotFound)
    pkg = asyncio.run(loader.load({"package_id": CACHE_PKG, "version": "1.0.1", "digest": d101}, None))
    assert (pkg.version, pkg.digest) == ("1.0.1", d101)
    fetched = len(seen)
    # The pinned reference itself is served from the cache (no registry call).
    assert (
        asyncio.run(loader.load({"package_id": CACHE_PKG, "version": "1.0.1", "digest": d101}, None)) is pkg
    )
    assert len(seen) == fetched

    # Warm cache: 1.0.1 with digest d101 is cached, yet a reference to 1.0.0 (or to another package id) with
    # d101 gets exactly the cold answer instead of running the cached 1.0.1.
    warm_foreign, warm_other = refused(foreign), refused(other_id)
    assert (type(warm_foreign), type(warm_other)) == cold
    assert (
        warm_foreign.error_code == "digest_mismatch"
        and d100 in str(warm_foreign)
        and d101 in str(warm_foreign)
    )
    assert seen[fetched:] == [
        f"/v1/packages/{CACHE_PKG}/versions/1.0.0/archive",
        f"/v1/packages/{CACHE_PKG}-other/versions/1.0.1/archive",
    ]
    assert asyncio.run(
        loader.load({"package_id": CACHE_PKG, "version": "1.0.0", "digest": d100}, None)
    ).version == ("1.0.0")


def test_loader_verifies_package_archive_also_when_the_digest_is_cached() -> None:
    v100 = _version_archive(CACHE_PKG, "1.0.0")
    v101 = _version_archive(CACHE_PKG, "1.0.1", b"\nShorter.\n")
    d101 = digest_of(v101)
    loader = PackageLoader(None, None, ClientLimits(), limits=GatewayLimits())
    ran = asyncio.run(
        loader.load({"package_id": CACHE_PKG, "version": "1.0.1", "digest": d101}, _inline(v101))
    )
    assert ran.version == "1.0.1"

    # The request's archive is what would run: it is read and verified even though d101 is cached.
    with pytest.raises(DigestMismatch):  # archive 1.0.0 under a reference to 1.0.0 pinned to d101
        asyncio.run(loader.load({"package_id": CACHE_PKG, "version": "1.0.0", "digest": d101}, _inline(v100)))
    with pytest.raises(ValidationFailed, match="requested"):  # archive 1.0.0 under a reference to 1.0.1
        asyncio.run(loader.load({"package_id": CACHE_PKG, "version": "1.0.1", "digest": d101}, _inline(v100)))
    again = asyncio.run(
        loader.load({"package_id": CACHE_PKG, "version": "1.0.1", "digest": d101}, _inline(v101))
    )
    assert again is ran  # the same archive reuses the unpacked package


def test_loader_does_not_answer_a_reference_with_a_package_seen_only_in_an_archive(tmp_path: Path) -> None:
    v101 = _version_archive(CACHE_PKG, "1.0.1")
    pinned = {"package_id": CACHE_PKG, "version": "1.0.1", "digest": digest_of(v101)}
    seen: list[str] = []
    registry = _registry_archives({}, seen)  # the version is not published
    loader = PackageLoader(
        tmp_path,
        "http://registry",
        ClientLimits(),
        limits=GatewayLimits(),
        transport=httpx.ASGITransport(app=registry),
    )
    with pytest.raises(NotFound):  # cold: neither the local directory nor the registry has it
        asyncio.run(loader.load(pinned, None))
    assert asyncio.run(loader.load(pinned, _inline(v101))).version == "1.0.1"
    # Warm: the request archive's package is not a lookup result, so a reference alone still gets the cold answer.
    with pytest.raises(NotFound):
        asyncio.run(loader.load(pinned, None))
    assert seen == [f"/v1/packages/{CACHE_PKG}/versions/1.0.1/archive"] * 2


@pytest.fixture
def registry_server() -> Iterator[tuple[str, dict[tuple[str, str], bytes], list[str]]]:
    """The registry neighbour over real HTTP, for the gateway app (its loader uses ``JANE_LLM_REGISTRY_URL``)."""
    archives: dict[tuple[str, str], bytes] = {}
    seen: list[str] = []
    config = uvicorn.Config(_registry_archives(archives, seen), host="127.0.0.1", port=0, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    while not server.started:
        time.sleep(0.02)
    port = server.servers[0].sockets[0].getsockname()[1]
    yield f"http://127.0.0.1:{port}", archives, seen
    server.should_exit = True
    thread.join(timeout=5)


def test_invocation_refuses_a_foreign_digest_also_after_caching_it(
    make_client: Callable[..., TestClient],
    registry_server: tuple[str, dict[tuple[str, str], bytes], list[str]],
    tmp_path: Path,
) -> None:
    """The scenario of the WP-13 e2e (criterion 9): the package exists only in the registry."""
    url, archives, _ = registry_server
    v100 = _version_archive(CACHE_PKG, "1.0.0")
    v101 = _version_archive(CACHE_PKG, "1.0.1", b"\nKeep the summary under twenty words.\n")
    archives.update({(CACHE_PKG, "1.0.0"): v100, (CACHE_PKG, "1.0.1"): v101})
    client = make_client(settings={"registry_url": url, "packages_dir": tmp_path})
    material = json.loads((PACKAGE_DIR / "tests" / "concert" / "material.json").read_text(encoding="utf-8"))

    def invoke(handler: dict[str, str], key: str) -> httpx.Response:
        body = {
            "handler": handler,
            "inputs": [{"kind": "material", "material": material}],
            "context": {"test_mode": True},
            "delivery": {"delivery_key": key},
        }
        response: httpx.Response = client.post("/v1/invocations", json=body, headers={"Idempotency-Key": key})
        return response

    pinned = {"package_id": CACHE_PKG, "version": "1.0.1", "digest": digest_of(v101)}
    foreign = {**pinned, "version": "1.0.0"}
    cold = invoke(foreign, "cache-cold")
    assert (cold.status_code, cold.json()["code"]) == (422, "digest_mismatch")
    warm = invoke(pinned, "cache-warm")
    assert warm.status_code == 200 and warm.json()["handler"] == pinned
    again = invoke(foreign, "cache-again")
    assert (again.status_code, again.json().get("code"), again.json().get("handler")) == (
        422,
        "digest_mismatch",
        None,
    )


# ---------------------------------------------------------------- Anthropic adapter (local stand-in server)
@pytest.fixture
def messages_server() -> Iterator[tuple[str, list[dict[str, Any]]]]:
    received: list[dict[str, Any]] = []

    async def messages(request: Request) -> Response:
        received.append({"headers": dict(request.headers), "body": await request.json()})
        if request.headers.get("x-api-key") != "test-key-not-secret":
            return JSONResponse(
                {"type": "error", "error": {"type": "authentication_error", "message": "bad"}},
                status_code=401,
            )
        return JSONResponse(
            {
                "id": "msg_1",
                "type": "message",
                "role": "assistant",
                "model": received[-1]["body"]["model"],
                "content": [{"type": "text", "text": '{"page_type": "product"}'}],
                "stop_reason": "end_turn",
                "stop_sequence": None,
                "usage": {"input_tokens": 120, "output_tokens": 9},
            }
        )

    app = Starlette(routes=[Route("/v1/messages", messages, methods=["POST"])])
    config = uvicorn.Config(app, host="127.0.0.1", port=0, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    while not server.started:
        time.sleep(0.02)
    port = server.servers[0].sockets[0].getsockname()[1]
    yield f"http://127.0.0.1:{port}", received
    server.should_exit = True
    thread.join(timeout=5)


def test_anthropic_adapter_request_shape(messages_server: tuple[str, list[dict[str, Any]]]) -> None:
    url, received = messages_server
    conn = ResolvedConnection(
        "anthropic-main", "llm_provider", {"api_base": url}, {"api_key": "test-key-not-secret"}
    )
    schema = {
        "type": "object",
        "properties": {"page_type": {"type": "string"}},
        "required": ["page_type"],
        "additionalProperties": False,
    }
    req = ProviderRequest("claude-opus-5", "SYSTEM", "USER DATA", 256, schema, 0.0, structured_output=True)
    resp = asyncio.run(AnthropicProvider().complete(req, conn, ServiceLimits()))
    assert (resp.text, resp.input_tokens, resp.output_tokens, resp.finish_reason) == (
        '{"page_type": "product"}',
        120,
        9,
        "stop",
    )
    body = received[0]["body"]
    assert body["model"] == "claude-opus-5" and body["max_tokens"] == 256
    assert body["system"] == "SYSTEM"
    assert body["messages"] == [{"role": "user", "content": "USER DATA"}]
    assert body["output_config"] == {"format": {"type": "json_schema", "schema": schema}}
    assert "temperature" not in body
    assert received[0]["headers"]["x-api-key"] == "test-key-not-secret"
    bad = ResolvedConnection("anthropic-main", "llm_provider", {"api_base": url}, {"api_key": "wrong"})
    with pytest.raises(ProviderError) as exc:
        asyncio.run(AnthropicProvider().complete(req, bad, ServiceLimits()))
    assert exc.value.retryable is False
    with pytest.raises(ProviderError):
        asyncio.run(AnthropicProvider().complete(req, None, ServiceLimits()))


def test_gateway_with_anthropic_provider(
    make_client: Callable[..., TestClient],
    h: Any,
    messages_server: tuple[str, list[dict[str, Any]]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    url, received = messages_server
    client = make_client(settings={"provider_api_base_allowlist": [url]})
    monkeypatch.setenv("JANE_SECRET_TEST_ANTHROPIC_KEY", "test-key-not-secret")
    conn = {
        "connection_id": "anthropic-main",
        "kind": "llm_provider",
        "params": {"api_base": url},
        "secret_refs": {"api_key": "env:JANE_SECRET_TEST_ANTHROPIC_KEY"},
    }
    assert client.put("/v1/connections/anthropic-main", json=conn).status_code == 201
    assert client.post("/v1/connections/anthropic-main/test").json()["ok"] is True
    provider = {
        "provider_id": "anthropic",
        "kind": "anthropic",
        "connection_id": "anthropic-main",
        "enabled": True,
        "models": [
            {
                "model_id": "claude-opus-5",
                "max_context_tokens": 1000000,
                "supports_structured_output": True,
                "pricing": {"input_per_mtok": 5, "output_per_mtok": 25, "currency": "USD"},
            }
        ],
    }
    assert client.put("/v1/providers/anthropic", json=provider).status_code == 200
    r = client.post("/v1/completions", json=h.completion(model="anthropic/claude-opus-5"), headers=h.idem())
    body = r.json()
    assert r.status_code == 200 and body["output"] == {"page_type": "product"}
    assert body["usage"]["cost"]["amount"] == pytest.approx((120 * 5 + 9 * 25) / 1_000_000)
    assert "Kettle A-100" in received[-1]["body"]["messages"][0]["content"]
    assert "Kettle A-100" not in received[-1]["body"]["system"]
    assert "test-key-not-secret" not in json.dumps(client.get("/v1/connections/anthropic-main").json())
