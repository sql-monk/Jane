"""Gateway and handler behaviour on the real app (memory store; PostgreSQL variant under ``integration``)."""

from __future__ import annotations

import asyncio
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
from jane_llm.packages import PackageLoader, build_archive, digest_of, publish, publish_request, read_dir
from jane_llm.providers import AnthropicProvider, ProviderError, ProviderRequest, ResolvedConnection
from jane_llm.settings import ServiceLimits

PACKAGE_DIR = Path(__file__).resolve().parents[1] / "packages" / "jane.llm-event-extractor"
EVENT = {"title": "Концерт", "starts_at": "2026-10-12T19:00:00+03:00", "venue": "Філармонія", "price": "free"}


def _scripted(client: TestClient, responses: list[dict[str, Any]], pricing: float = 0) -> None:
    conn = {"connection_id": "fake-scripts", "kind": "llm_provider", "params": {"responses": responses}}
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
    params: {api_base: "http://127.0.0.1:9"}
    secret_refs: {api_key: "env:JANE_TEST_ANTHROPIC_KEY"}
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
        None, "http://registry", ClientLimits(), transport=httpx.ASGITransport(app=registry)
    )
    ref = {"package_id": "jane.llm-event-extractor", "version": "1.0.0", "digest": digest_of(archive)}
    pkg = asyncio.run(loader.load(ref, None))
    assert pkg.manifest["kind"] == "llm"
    assert seen == ["/v1/packages/jane.llm-event-extractor/versions/1.0.0/archive"]
    with pytest.raises(Exception, match="digest"):
        asyncio.run(
            PackageLoader(
                None, "http://registry", ClientLimits(), transport=httpx.ASGITransport(app=registry)
            ).load({**ref, "digest": "sha256:" + "1" * 64}, None)
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
    client: TestClient,
    h: Any,
    messages_server: tuple[str, list[dict[str, Any]]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    url, received = messages_server
    monkeypatch.setenv("JANE_TEST_ANTHROPIC_KEY", "test-key-not-secret")
    conn = {
        "connection_id": "anthropic-main",
        "kind": "llm_provider",
        "params": {"api_base": url},
        "secret_refs": {"api_key": "env:JANE_TEST_ANTHROPIC_KEY"},
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
