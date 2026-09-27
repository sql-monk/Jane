"""jane-kit against the real WP-00 contracts (``contracts/`` or ``JANE_CONTRACTS_DIR``); skipped if absent."""

from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import Field

from jane_kit.codegen import generate_client
from jane_kit.config import JaneSettings, LimitLayer, Limits, resolve_limits
from jane_kit.contracts import OpenAPISpec, build_mock_app, contracts_dir, find_specs
from jane_kit.errors import KNOWN_CODES, JaneError, NotFound
from jane_kit.jobs import Job, JobCancellation, JobProgress, JobStatus
from jane_kit.service import create_app

pytestmark = pytest.mark.contract

_FOUND = contracts_dir(Path(__file__).parent)
if _FOUND is None or not (_FOUND / "openapi" / "common.yaml").is_file():
    pytest.skip(
        "WP-00 contracts not available (set JANE_CONTRACTS_DIR or merge WP-00)", allow_module_level=True
    )
CONTRACTS: Path = _FOUND if _FOUND is not None else Path()
COMMON = OpenAPISpec.load(CONTRACTS / "openapi" / "common.yaml")
SPECS = list(find_specs(CONTRACTS / "openapi"))


def test_error_catalogue_matches_contract() -> None:
    enum = COMMON.lookup(
        (CONTRACTS / "schemas/common/problem.schema.json").resolve().as_uri() + "#/$defs/KnownErrorCode"
    ).node["enum"]
    assert set(KNOWN_CODES) == set(enum)
    doc = (CONTRACTS / "docs" / "errors.md").read_text(encoding="utf-8")
    for code, (status, retryable) in KNOWN_CODES.items():
        row = re.search(rf"^\| `{code}` \| (\d+) \| (так|ні)", doc, re.M)
        assert row, code
        assert int(row.group(1)) == status, code
        assert (row.group(2) == "так") == retryable, code


@pytest.mark.parametrize("code", sorted(KNOWN_CODES))
def test_problem_matches_schema(code: str) -> None:
    COMMON.validate_component(
        "Problem",
        JaneError("detail", code=code).to_problem("/v1/x").model_dump(mode="json", exclude_none=True),
    )


def test_job_documents_match_schema() -> None:
    from datetime import UTC, datetime

    now = datetime.now(UTC)
    for status in JobStatus:
        job = Job(
            job_id="job_1",
            kind="collection",
            status=status,
            progress=JobProgress(completed=1, total=None),
            links={"self": "/v1/jobs/job_1"},
        )
        if status == JobStatus.FAILED:
            job.error = NotFound("x").to_problem()
        if status in (JobStatus.CANCELLING, JobStatus.CANCELLED):
            job.cancellation = JobCancellation(requested_at=now, reason="r")
        if status == JobStatus.SUCCEEDED:
            job.result = {"n": 1}
        COMMON.validate_component("Job", job.wire())


def test_health_and_info_match_schema() -> None:
    client = TestClient(create_app(JaneSettings(service_name="svc"), configure_logs=False))
    COMMON.validate_component("Health", client.get("/v1/health").json())
    COMMON.validate_component("ServiceInfo", client.get("/v1/info").json())


class Crawl(Limits):
    max_depth: int = Field(default=3, ge=0)


class Transfer(Limits):
    idempotency_ttl_seconds: int = Field(default=86_400, ge=60)


class SomeLimits(Limits):
    crawl: Crawl = Crawl()
    transfer: Transfer = Transfer()


def test_effective_limits_match_schema() -> None:
    r = resolve_limits(
        SomeLimits,
        LimitLayer("platform", hard_caps={"crawl": {"max_depth": 5}}),
        LimitLayer("task", {"crawl": {"max_depth": 50}}),
    )
    schema = (CONTRACTS / "schemas/common/limits.schema.json").resolve().as_uri() + "#/$defs/EffectiveLimits"
    COMMON.validate_at(schema, r.effective(), "EffectiveLimits")


@pytest.mark.parametrize("spec_path", SPECS, ids=[p.name for p in SPECS])
def test_mock_from_real_contract_serves_valid_responses(spec_path: Path) -> None:
    spec = OpenAPISpec.load(spec_path)
    mock = TestClient(build_mock_app(spec))
    checked = 0
    for op in spec.operations:
        url = re.sub(r"\{[^}]+\}", "x", op.path)
        headers = {"Idempotency-Key": "k-1"}
        kwargs: dict[str, Any] = {"headers": headers}
        if op.spec.get("requestBody"):
            rb = spec.follow(op.loc.child("requestBody"))
            media = rb.node.get("content", {}).get("application/json")
            if media is None:
                continue
            examples = media.get("examples") or {}
            if examples:
                kwargs["json"] = spec.follow(
                    rb.child("content", "application/json", "examples", next(iter(examples)))
                ).node.get("value")
            elif "example" in media:
                kwargs["json"] = media["example"]
            else:
                continue
        r = mock.request(op.method, url, **kwargs)
        assert r.status_code < 400, (op.method, op.path, r.text[:500])
        body = r.json() if r.content else None
        spec.validate_response(op.method, url, r.status_code, body, r.headers.get("content-type"))
        checked += 1
    assert checked > 0


def test_codegen_on_real_contract(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    spec_path = next(p for p in SPECS if p.name.startswith("collector"))
    generate_client(spec_path, tmp_path / "collector_client", class_name="Collector", with_models=False)
    monkeypatch.syspath_prepend(str(tmp_path))
    sys.modules.pop("collector_client", None)
    pkg = importlib.import_module("collector_client")
    mock = build_mock_app(OpenAPISpec.load(spec_path))

    async def call() -> Any:
        async with pkg.CollectorClient("http://mock", transport=httpx.ASGITransport(app=mock)) as client:
            return await client.get_health()

    import asyncio

    assert asyncio.run(call())["status"] in {"ok", "degraded"}
