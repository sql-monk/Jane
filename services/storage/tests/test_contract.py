"""Contract tests: responses of the real app against WP-00 contracts (skipped until contracts/ exists).

* common resources (``/v1/health``, ``/v1/info``, ``/v1/jobs``) against ``contracts/openapi/common.yaml``;
* the service API against ``contracts/openapi/storage.v1.yaml`` via ``ContractClient``
  (add calls for every operation; ``client.uncovered()`` lists the ones not exercised yet).
"""

from __future__ import annotations

import time
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jane_kit.contracts import ContractClient, OpenAPISpec, contracts_dir
from jane_storage.app import build_app
from jane_storage.settings import Settings

pytestmark = pytest.mark.contract

CONTRACTS = contracts_dir(Path(__file__).parent)
SERVICE_SPEC = CONTRACTS / "openapi" / "storage.v1.yaml" if CONTRACTS else None


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(build_app(Settings(log_format="console"))) as c:
        yield c


@pytest.fixture(scope="module")
def common() -> OpenAPISpec:
    if CONTRACTS is None or not (CONTRACTS / "openapi" / "common.yaml").is_file():
        pytest.skip("contracts/openapi/common.yaml not available (WP-00 not merged yet)")
    return OpenAPISpec.load(CONTRACTS / "openapi" / "common.yaml")


def test_common_resources_match_contract(client: TestClient, common: OpenAPISpec) -> None:
    common.validate_component("Health", client.get("/v1/health").json())
    common.validate_component("ServiceInfo", client.get("/v1/info").json())
    r = client.post("/v1/examples/jobs", json={"steps": 1}, headers={"Idempotency-Key": "c-1"})
    common.validate_component("Job", r.json())
    job_id = r.json()["job_id"]
    for _ in range(100):
        body = client.get(f"/v1/jobs/{job_id}").json()
        common.validate_component("Job", body)
        if body["status"] == "succeeded":
            break
        time.sleep(0.02)
    common.validate_component("Problem", client.get("/v1/jobs/unknown").json())
    common.validate_component(
        "Problem",
        client.post("/v1/examples/jobs", json={"steps": 0}, headers={"Idempotency-Key": "c-2"}).json(),
    )


def test_service_api_matches_contract(client: TestClient) -> None:
    if SERVICE_SPEC is None or not SERVICE_SPEC.is_file():
        pytest.skip("service contract not in contracts/openapi yet")
    api = ContractClient(OpenAPISpec.load(SERVICE_SPEC), client)
    api.get("/v1/health")
    api.get("/v1/info")
