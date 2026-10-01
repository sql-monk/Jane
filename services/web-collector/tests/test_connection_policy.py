"""An untrusted connection or crawl rule cannot choose where a collector secret goes."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from jane_kit.errors import ServiceUnavailable, ValidationFailed
from jane_web_collector.app import build_app
from jane_web_collector.connections import ConnectionPolicy, auth_headers
from jane_web_collector.fetcher import Fetcher, FetchError, HostLimiter
from jane_web_collector.rules import RulesLoader
from jane_web_collector.settings import Rate, Retries, ServiceLimits
from jane_web_collector.testing import Site, make_settings, web_rules


def _connection(ref: str) -> dict[str, object]:
    return {
        "connection_id": "secret-site",
        "kind": "http",
        "params": {"auth_scheme": "bearer"},
        "secret_refs": {"token": ref},
    }


def test_connection_secret_refs_restricted_at_api_and_resolution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    secrets = tmp_path / "secrets"
    secrets.mkdir()
    (secrets / "token").write_text("safe-token", encoding="utf-8")
    (tmp_path / "outside").write_text("private-token", encoding="utf-8")
    monkeypatch.setenv("JANE_SECRET_SITE_TOKEN", "safe-token")
    monkeypatch.setenv("JANE_WEB_COLLECTOR_REGISTRY_URL", "private-value")
    settings = make_settings(tmp_path, secret_files_dir=secrets)
    with TestClient(build_app(settings)) as client:
        for ref in (
            "env:JANE_WEB_COLLECTOR_REGISTRY_URL",
            "env:PATH",
            f"file:{tmp_path / 'outside'}",
            f"file:{secrets / '..' / 'outside'}",
            "vault:path#token",
        ):
            response = client.put("/v1/connections/secret-site", json=_connection(ref))
            assert response.status_code == 422
            assert response.json()["errors"][0]["pointer"] == "/secret_refs/token"
        assert client.get("/v1/connections/secret-site").status_code == 404
        for ref in ("env:JANE_SECRET_SITE_TOKEN", f"file:{secrets / 'token'}"):
            assert client.put("/v1/connections/secret-site", json=_connection(ref)).status_code in (200, 201)
            assert client.post("/v1/connections/secret-site/test").json()["secrets_resolved"] == {
                "token": True
            }
        bad_host_header = {
            **_connection("env:JANE_SECRET_SITE_TOKEN"),
            "params": {"auth_scheme": "header", "header_name": "Host"},
        }
        assert client.put("/v1/connections/secret-site", json=bad_host_header).status_code == 422
        malformed_header = {
            **_connection("env:JANE_SECRET_SITE_TOKEN"),
            "params": {"auth_scheme": "header", "header_name": "X-Token\r\nX-Leak"},
        }
        assert client.put("/v1/connections/secret-site", json=malformed_header).status_code == 422
    policy = settings.connection_policy()
    assert policy.resolve("env:JANE_WEB_COLLECTOR_REGISTRY_URL") is None
    assert policy.resolve(f"file:{tmp_path / 'outside'}") is None
    with pytest.raises(ValidationFailed, match="secret reference"):
        auth_headers(
            {
                **_connection("env:JANE_SECRET_SITE_TOKEN"),
                "secret_refs": {
                    "token": "env:JANE_SECRET_SITE_TOKEN",
                    "extra": "env:JANE_WEB_COLLECTOR_REGISTRY_URL",
                },
            },
            policy,
        )


def test_origin_allowlist_is_exact_and_invalid_entries_fail_settings(tmp_path: Path) -> None:
    policy = ConnectionPolicy(origin_allowlist=("https://source.test:443",))
    assert policy.origin_allowed("https://source.test/product/1")
    for url in (
        "http://source.test/product/1",
        "https://source.test:444/product/1",
        "https://sub.source.test/product/1",
        "https://source.test.evil/product/1",
        "https://user@source.test/product/1",
    ):
        assert not policy.origin_allowed(url)
    for entry in ("source.test", "https://source.test:443/path", "https://user@source.test"):
        with pytest.raises(ValueError, match="connection_origin_allowlist"):
            make_settings(tmp_path, connection_origin_allowlist=[entry])


@pytest.mark.asyncio
async def test_secret_never_sent_to_unlisted_origin_or_redirect_target(
    caplog: pytest.LogCaptureFixture,
) -> None:
    seen: list[tuple[str, str | None]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append((str(request.url), request.headers.get("Authorization")))
        if request.url.host == "source.test" and request.url.path == "/redirect":
            return httpx.Response(302, headers={"Location": "https://elsewhere.test/target"})
        if request.url.host == "source.test" and request.url.path == "/downgrade":
            return httpx.Response(302, headers={"Location": "http://source.test/target"})
        if request.url.host == "source.test" and request.url.path == "/same":
            return httpx.Response(302, headers={"Location": "https://source.test/same-target"})
        return httpx.Response(200, content=b"ok")

    limits = ServiceLimits(rate=Rate(requests_per_second_per_host=1000, min_delay_ms_per_host=0))
    policy = ConnectionPolicy(origin_allowlist=("https://source.test",))
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler), follow_redirects=False) as client:
        fetcher = Fetcher(
            client,
            limits,
            HostLimiter(limits).session(limits),
            user_agent="JaneBot",
            auth_headers={"Authorization": "Bearer safe-token"},
            connection_policy=policy,
        )
        with pytest.raises(FetchError, match="allowlist") as denied:
            await fetcher.get("https://outside.test/secret")
        assert "safe-token" not in repr(denied.value) + caplog.text
        assert seen == []
        await fetcher.get("https://source.test/same")
        assert seen == [
            ("https://source.test/same", "Bearer safe-token"),
            ("https://source.test/same-target", "Bearer safe-token"),
        ]
        seen.clear()
        await fetcher.get("https://source.test/redirect")
        assert seen == [
            ("https://source.test/redirect", "Bearer safe-token"),
            ("https://elsewhere.test/target", None),
        ]
        seen.clear()
        await fetcher.get("https://source.test/downgrade")
        assert seen == [
            ("https://source.test/downgrade", "Bearer safe-token"),
            ("http://source.test/target", None),
        ]
        with pytest.raises(ValidationFailed, match="outside the allowlist"):
            Fetcher(
                client,
                limits,
                HostLimiter(limits).session(limits),
                user_agent="JaneBot",
                headers={"X-Client-Key": "top-secret"},
            )
        assert len(seen) == 2  # no request carrying X-Client-Key, even before a cross-origin redirect


@pytest.mark.asyncio
async def test_transport_error_and_malformed_credential_never_expose_secret(
    tmp_path: Path, site: Site, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    secret = "secret-marker\r\nX-Leaked: secret-marker"
    monkeypatch.setenv("JANE_SECRET_SITE_TOKEN", secret)
    settings = make_settings(tmp_path, connection_origin_allowlist=[site.base])
    with TestClient(build_app(settings)) as client:
        assert (
            client.put(
                "/v1/connections/secret-site", json=_connection("env:JANE_SECRET_SITE_TOKEN")
            ).status_code
            == 201
        )
        rules = web_rules(site)
        rules["fetch"] = {**rules.get("fetch", {}), "connection_id": "secret-site"}
        response = client.post(
            "/v1/fetches", json={"source_kind": "web", "url": site.url("/about"), "rules": rules}
        )
        assert response.status_code == 422
        assert response.json()["errors"][0]["pointer"] == "/secret_refs/token"
        assert "secret-marker" not in response.text + caplog.text
        assert site.requests["/about"] == 0

    limits = ServiceLimits(retries=Retries(max_attempts=1))
    policy = ConnectionPolicy(origin_allowlist=("https://source.test",))
    seen: list[httpx.Request] = []

    def transport(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        raise httpx.LocalProtocolError(f"invalid header value {secret}")

    async with httpx.AsyncClient(transport=httpx.MockTransport(transport)) as http_client:
        fetcher = Fetcher(
            http_client,
            limits,
            HostLimiter(limits).session(limits),
            user_agent="JaneBot",
            auth_headers={"Authorization": "Bearer safe-token"},
            connection_policy=policy,
        )
        with pytest.raises(FetchError, match="HTTP transport failed") as failed:
            await fetcher.get("https://source.test/item")
        assert len(seen) == 1
        assert "secret-marker" not in repr(failed.value) + failed.value.message + caplog.text
        fetcher.auth_headers = {"Authorization": f"Bearer {secret}"}
        with pytest.raises(FetchError, match="header rejected by policy") as rejected:
            await fetcher.get("https://source.test/item")
        assert len(seen) == 1  # malformed credential rejected before HTTPX sees it
        assert "secret-marker" not in repr(rejected.value) + rejected.value.message + caplog.text


@pytest.mark.asyncio
async def test_registry_credential_error_has_no_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("JANE_REGISTRY_TOKEN", "registry-secret\r\nX-Leak: registry-secret")
    loader = RulesLoader(
        rules_dir=None,
        registry_url="https://registry.test",
        registry_token_env="JANE_REGISTRY_TOKEN",
        timeout_s=1,
    )
    with pytest.raises(ServiceUnavailable, match="registry credential") as failed:
        await loader._load_registry({"package_id": "pkg", "version": "1"})
    assert "registry-secret" not in repr(failed.value)


def test_rules_cannot_supply_authentication_header(client: TestClient) -> None:
    rules = {
        "collector": "web",
        "scope": {"allowed_domains": ["source.test"]},
        "strategies": [{"type": "seed_list", "urls": ["https://source.test/"]}],
        "fetch": {"headers": {"Authorization": "Bearer private"}},
    }
    response = client.post("/v1/rules/validations", json=rules)
    assert response.status_code == 200
    assert response.json()["valid"] is False
    assert response.json()["errors"][0]["pointer"] == "/fetch/headers/Authorization"
    rules["fetch"] = {"headers": {"Host": "other-virtual-host.test"}}
    host = client.post("/v1/rules/validations", json=rules)
    assert host.json()["valid"] is False
    assert host.json()["errors"][0]["pointer"] == "/fetch/headers/Host"
    rules["fetch"] = {"headers": {"X-Client-Key": "top-secret"}}
    key = client.post("/v1/rules/validations", json=rules)
    assert key.json()["valid"] is False
    assert key.json()["errors"][0]["pointer"] == "/fetch/headers/X-Client-Key"
    rules["fetch"] = {"headers": {"Accept": "text/html\r\nX-Client-Key: top-secret"}}
    malformed = client.post("/v1/rules/validations", json=rules)
    assert malformed.json()["valid"] is False
    assert malformed.json()["errors"][0]["pointer"] == "/fetch/headers/Accept"
    assert "top-secret" not in malformed.text
