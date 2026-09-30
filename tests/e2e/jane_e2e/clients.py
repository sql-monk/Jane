"""Contract-validating clients for the real services of the stack.

Every request body and every response of a real service is checked against its OpenAPI contract in
``contracts/openapi`` (``jane_kit.contracts.ContractClient``): an acceptance scenario fails not only on wrong
behaviour but also on any divergence from the contract.
"""

from __future__ import annotations

import time
from functools import cache
from pathlib import Path
from typing import Any

import httpx

from jane_kit.contracts import ContractClient, OpenAPISpec

__all__ = ["API_OF_SERVICE", "JaneClient", "spec"]

CONTRACTS = Path(__file__).resolve().parents[3] / "contracts" / "openapi"

# Which contract each service of the stack implements.
API_OF_SERVICE = {
    "storage": ("handler", "storage"),  # handler protocol for writes + storage read API
    "handler-runtime": ("handler",),
    "web-collector": ("collector",),
    "telegram-collector": ("collector",),
    "registry": ("registry",),
    "orchestrator": ("orchestrator",),
    "llm": ("handler", "llm"),
    "assistant": ("assistant",),
}

TERMINAL_JOB_STATES = frozenset({"succeeded", "failed", "cancelled"})


@cache
def spec(api: str) -> OpenAPISpec:
    return OpenAPISpec.load(CONTRACTS / f"{api}.v1.yaml")


class JaneClient:
    """HTTP client of one service instance; ``api(name)`` validates against that contract."""

    def __init__(self, base_url: str, timeout_s: float = 120.0) -> None:
        self.base_url = base_url
        self.http = httpx.Client(base_url=base_url, timeout=timeout_s)
        self._clients: dict[str, ContractClient] = {}

    def close(self) -> None:
        self.http.close()

    def api(self, name: str) -> ContractClient:
        if name not in self._clients:
            self._clients[name] = ContractClient(spec(name), self.http)
        return self._clients[name]

    # ---------------------------------------------------------------- common protocol helpers
    def wait_job(
        self, api: str, job_id: str, timeout_s: float = 300.0, poll_s: float = 0.5
    ) -> dict[str, Any]:
        deadline = time.monotonic() + timeout_s
        while True:
            job: dict[str, Any] = self.api(api).get(f"/v1/jobs/{job_id}").json()
            if job["status"] in TERMINAL_JOB_STATES:
                return job
            if time.monotonic() > deadline:
                raise TimeoutError(f"job {job_id} still {job['status']} after {timeout_s}s")
            time.sleep(poll_s)

    def invoke(self, body: dict[str, Any], *, api: str = "handler") -> tuple[int, dict[str, Any]]:
        """``POST /v1/invocations`` with ``Idempotency-Key`` = ``delivery.delivery_key`` (handler.v1).

        A ``202`` (async or slow sync call) is followed to the terminal job; returns the HTTP status of the
        first response and the ``HandlerResult``.
        """
        key = body["delivery"]["delivery_key"]
        r = self.api(api).post("/v1/invocations", json=body, headers={"Idempotency-Key": key})
        if r.status_code == 202:
            job = self.wait_job(api, r.json()["job_id"])
            assert job["status"] == "succeeded", job
            return r.status_code, dict(job["result"])
        assert r.status_code == 200, r.text
        return r.status_code, dict(r.json())
