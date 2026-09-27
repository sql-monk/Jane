"""Clients of neighbour services, strictly by their contracts (``contracts/openapi/*.v1.yaml``).

Only the operations the assistant needs are wrapped. Every POST with a side effect carries an
``Idempotency-Key`` derived from the assistant job, so a retry never duplicates the effect.
Long operations (``202`` + Job) are awaited with :meth:`ServiceClient.wait_for_job`.
"""

from __future__ import annotations

import base64
import contextlib
import hashlib
import io
import os
import zipfile
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

import httpx

from jane_kit.clients import ClientLimits, RemoteError, ServiceClient
from jane_kit.errors import JaneError, UpstreamUnavailable

from .settings import Settings

__all__ = [
    "Neighbours",
    "RemoteError",
    "idem_key",
]

MERGE_PATCH = {"Content-Type": "application/merge-patch+json"}


def idem_key(*parts: str) -> str:
    """Deterministic ``Idempotency-Key`` (1-255 printable ASCII) from job-scoped parts."""
    raw = "|".join(parts)
    return "asst-" + hashlib.sha256(raw.encode()).hexdigest()[:48]


class _Base:
    name = "service"

    def __init__(self, client: ServiceClient | None) -> None:
        self._client = client

    @property
    def configured(self) -> bool:
        return self._client is not None

    @property
    def c(self) -> ServiceClient:
        if self._client is None:
            raise UpstreamUnavailable(f"{self.name} is not configured for the assistant")
        return self._client

    async def _job_result(self, response: httpx.Response) -> dict[str, Any]:
        """Result of a ``202`` job (waits); ``200`` bodies are returned as is."""
        body: dict[str, Any] = response.json()
        if response.status_code != 202:
            return body
        location = response.headers.get("location") or (body.get("links") or {}).get("self")
        job = await self.c.wait_for_job(location or f"/v1/jobs/{body['job_id']}")
        if job.get("status") != "succeeded":
            err = job.get("error") or {}
            raise JaneError(
                f"{self.name} job {job.get('job_id')} {job.get('status')}: {err.get('detail') or err.get('title')}",
                code="upstream_unavailable" if err.get("retryable") else "conflict",
                details={"job": job.get("job_id"), "upstream_code": err.get("code")},
            )
        return dict(job.get("result") or {})

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()


class LlmClient(_Base):
    name = "llm"

    async def complete(self, request: Mapping[str, Any], key: str) -> dict[str, Any]:
        r = await self.c.request("POST", "/v1/completions", json=dict(request), idempotency_key=key)
        return await self._job_result(r)


class RegistryClient(_Base):
    name = "registry"

    async def search(self, **params: str) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        cursor: str | None = None
        while True:
            query = {k: v for k, v in params.items() if v}
            if cursor:
                query["cursor"] = cursor
            page = await self.c.get_json("/v1/packages", params=query)
            items.extend(page.get("items") or [])
            cursor = page.get("next_cursor")
            if not cursor:
                return items

    async def get_package(self, package_id: str) -> dict[str, Any]:
        return dict(await self.c.get_json(f"/v1/packages/{package_id}"))

    async def get_version(self, package_id: str, version: str) -> dict[str, Any]:
        return dict(await self.c.get_json(f"/v1/packages/{package_id}/versions/{version}"))

    async def archive_files(self, package_id: str, version: str) -> tuple[dict[str, bytes], str | None]:
        """Files of a version from its archive; the ``ETag`` digest is verified when present."""
        r = await self.c.request("GET", f"/v1/packages/{package_id}/versions/{version}/archive")
        data = r.content
        etag = (r.headers.get("etag") or "").strip('"').removeprefix("W/").strip('"')
        digest = f"sha256:{hashlib.sha256(data).hexdigest()}"
        if etag.startswith("sha256:") and etag != digest:
            raise JaneError(f"archive digest mismatch for {package_id}@{version}", code="digest_mismatch")
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            files = {n: zf.read(n) for n in zf.namelist() if not n.endswith("/")}
        return files, etag or None

    async def create_package(self, body: Mapping[str, Any], key: str) -> dict[str, Any]:
        try:
            return dict(await self.c.post_json("/v1/packages", dict(body), idempotency_key=key))
        except RemoteError as exc:
            if exc.status == 409:  # already exists: reuse it
                return await self.get_package(str(body["package_id"]))
            raise

    async def publish(self, package_id: str, body: Mapping[str, Any], key: str) -> dict[str, Any]:
        return dict(
            await self.c.post_json(f"/v1/packages/{package_id}/versions", dict(body), idempotency_key=key)
        )

    async def set_status(
        self, package_id: str, version: str, status: str, reason: str, key: str
    ) -> dict[str, Any]:
        return dict(
            await self.c.post_json(
                f"/v1/packages/{package_id}/versions/{version}/status",
                {"status": status, "reason": reason[:2000]},
                idempotency_key=key,
            )
        )

    async def record_tests(
        self, package_id: str, version: str, record: Mapping[str, Any], key: str
    ) -> dict[str, Any]:
        return dict(
            await self.c.post_json(
                f"/v1/packages/{package_id}/versions/{version}/test-results",
                dict(record),
                idempotency_key=key,
            )
        )

    async def fork(self, package_id: str, body: Mapping[str, Any], key: str) -> dict[str, Any]:
        return dict(
            await self.c.post_json(f"/v1/packages/{package_id}/forks", dict(body), idempotency_key=key)
        )


class CollectorClient(_Base):
    name = "collector"

    async def fetch(self, body: Mapping[str, Any]) -> dict[str, Any]:
        return dict(await self.c.post_json("/v1/fetches", dict(body)))

    async def start_collection(self, body: Mapping[str, Any], key: str) -> dict[str, Any]:
        return dict(await self.c.post_json("/v1/collections", dict(body), idempotency_key=key))

    async def collection(self, collection_id: str) -> dict[str, Any]:
        return dict(await self.c.get_json(f"/v1/collections/{collection_id}"))

    async def materials(
        self, collection_id: str, after: str | None, limit: int, wait_ms: int
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit, "wait_ms": wait_ms}
        if after:
            params["after"] = after
        return dict(await self.c.get_json(f"/v1/collections/{collection_id}/materials", params=params))

    async def cancel(self, collection_id: str) -> None:
        try:
            await self.c.request(
                "POST", f"/v1/jobs/{collection_id}/cancel", json={"reason": "sample complete"}
            )
        except RemoteError:
            pass  # already finished or expired

    async def validate_rules(self, rules: Mapping[str, Any]) -> dict[str, Any]:
        return dict(await self.c.post_json("/v1/rules/validations", dict(rules)))


class HandlerClient(_Base):
    name = "handler-runtime"

    async def test_run(self, body: Mapping[str, Any], key: str) -> dict[str, Any]:
        r = await self.c.request("POST", "/v1/test-runs", json=dict(body), idempotency_key=key)
        return await self._job_result(r)


class OrchestratorClient(_Base):
    name = "orchestrator"

    async def get_source(self, source_id: str) -> dict[str, Any]:
        return dict(await self.c.get_json(f"/v1/sources/{source_id}"))

    async def create_source(self, body: Mapping[str, Any], key: str) -> dict[str, Any]:
        return dict(await self.c.post_json("/v1/sources", dict(body), idempotency_key=key))

    async def create_task(self, body: Mapping[str, Any], key: str) -> dict[str, Any]:
        return dict(await self.c.post_json("/v1/tasks", dict(body), idempotency_key=key))

    async def get_task(self, task_id: str) -> dict[str, Any]:
        return dict(await self.c.get_json(f"/v1/tasks/{task_id}"))

    async def tasks_using(self, package_id: str) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        cursor: str | None = None
        while True:
            params = {"package_id": package_id} | ({"cursor": cursor} if cursor else {})
            page = await self.c.get_json("/v1/tasks", params=params)
            items.extend(page.get("items") or [])
            cursor = page.get("next_cursor")
            if not cursor:
                return items

    async def activate(
        self, task_id: str, stage_id: str, body: Mapping[str, Any], key: str
    ) -> dict[str, Any]:
        return dict(
            await self.c.post_json(
                f"/v1/tasks/{task_id}/stages/{stage_id}/activations", dict(body), idempotency_key=key
            )
        )

    async def update_problem_group(self, group_id: str, patch: Mapping[str, Any]) -> dict[str, Any]:
        r = await self.c.request(
            "PATCH", f"/v1/problem-groups/{group_id}", json=dict(patch), headers=MERGE_PATCH
        )
        return dict(r.json())


class StorageClient(_Base):
    name = "storage"

    async def material(self, connection_id: str, object_id: str) -> dict[str, Any]:
        """Material of a stored RAW object with its content inlined (UTF-8 text or base64)."""
        params = {"connection_id": connection_id}
        detail = await self.c.get_json(f"/v1/objects/{object_id}", params=params)
        material = dict(detail.get("material") or {})
        if not material:
            raise JaneError(f"stored object {object_id} has no material", code="validation_failed")
        r = await self.c.request("GET", f"/v1/objects/{object_id}/content", params=params)
        media = (material.get("format") or {}).get("media_type") or "application/octet-stream"
        try:
            content = {"kind": "inline", "media_type": media, "encoding": "utf-8", "data": r.content.decode()}
        except UnicodeDecodeError:
            content = {
                "kind": "inline",
                "media_type": media,
                "encoding": "base64",
                "data": base64.b64encode(r.content).decode(),
            }
        content["sha256"] = hashlib.sha256(r.content).hexdigest()
        content["size_bytes"] = len(r.content)
        material["content"] = content
        return material


@dataclass
class Neighbours:
    llm: LlmClient
    registry: RegistryClient
    collectors: dict[str, CollectorClient]
    handler: HandlerClient
    orchestrator: OrchestratorClient
    storage: StorageClient
    _extra: list[ServiceClient] = field(default_factory=list)

    def collector(self, source_kind: str) -> CollectorClient:
        client = self.collectors.get(source_kind)
        if client is None:
            return CollectorClient(None)
        return client

    @classmethod
    def from_settings(
        cls,
        settings: Settings,
        limits: ClientLimits,
        transports: Mapping[str, httpx.AsyncBaseTransport] | None = None,
    ) -> Neighbours:
        """Clients for configured URLs. ``transports`` (tests) maps a neighbour name to an ASGI
        transport; the URL then only provides the base."""
        transports = transports or {}
        headers: dict[str, str] = {}
        if settings.service_token_env and (token := os.environ.get(settings.service_token_env)):
            headers["Authorization"] = f"Bearer {token}"

        def make(name: str, url: str | None) -> ServiceClient | None:
            if url is None and name not in transports:
                return None
            return ServiceClient(
                url or f"http://{name}.test", limits, headers=headers, transport=transports.get(name)
            )

        return cls(
            llm=LlmClient(make("llm", settings.llm_url)),
            registry=RegistryClient(make("registry", settings.registry_url)),
            collectors={
                "web": CollectorClient(make("collector_web", settings.collector_web_url)),
                "telegram": CollectorClient(make("collector_telegram", settings.collector_telegram_url)),
            },
            handler=HandlerClient(make("handler", settings.handler_runtime_url)),
            orchestrator=OrchestratorClient(make("orchestrator", settings.orchestrator_url)),
            storage=StorageClient(make("storage", settings.storage_url)),
        )

    async def aclose(self) -> None:
        for c in (
            self.llm,
            self.registry,
            *self.collectors.values(),
            self.handler,
            self.orchestrator,
            self.storage,
        ):
            await c.aclose()
