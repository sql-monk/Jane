"""ADR-0005 authentication (jane_kit.auth): api_key, jwt with a local JWKS, scopes, fail-closed configuration."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import threading
import time
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from jwt.algorithms import ECAlgorithm, RSAAlgorithm

from jane_kit.auth import (
    AUTHENTICATED,
    AuthConfigError,
    Authenticator,
    Principal,
    SecretRefError,
    require,
    resolve_secret_ref,
    sha256_hex,
    unmapped_routes,
)
from jane_kit.config import JaneSettings
from jane_kit.service import create_app

ISSUER = "https://idp.example.test/realms/jane"
AUDIENCE = "jane-storage"
JWKS_URL = "https://idp.example.test/realms/jane/certs"
SCOPES = {
    "GET /v1/things": "storage:read",
    "POST /v1/things": ("storage:write", "storage:admin"),
    "GET /v1/open-to-any": AUTHENTICATED,
}


def keys_doc() -> list[dict[str, Any]]:
    return [
        {"name": "reader", "sha256": sha256_hex("key-reader"), "scopes": ["storage:read"]},
        {"name": "writer", "sha256": sha256_hex("key-writer"), "scopes": ["storage:read", "storage:write"]},
        {"name": "bare", "sha256": sha256_hex("key-bare"), "scopes": [], "actor": "llm"},
    ]


def settings(**kw: Any) -> JaneSettings:
    return JaneSettings(service_name="svc", instance_id="i-1", **kw)


def build(s: JaneSettings, *, scopes: Any = SCOPES, authenticator: Authenticator | None = None) -> FastAPI:
    app = create_app(s, configure_logs=False, auth_scopes=scopes, authenticator=authenticator)

    @app.get("/v1/things")
    async def list_things() -> dict[str, str]:
        return {"ok": "list"}

    @app.post("/v1/things")
    async def add_thing() -> dict[str, str]:
        return {"ok": "add"}

    @app.get("/v1/open-to-any")
    async def any_token() -> dict[str, str]:
        return {"ok": "any"}

    return app


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# ----------------------------------------------------------------------------- api_key
@pytest.fixture
def api_client() -> Iterator[TestClient]:
    with TestClient(build(settings(auth_mode="api_key", api_keys=keys_doc()))) as c:
        yield c


def test_api_key_ok_missing_wrong_and_scope(api_client: TestClient) -> None:
    c = api_client
    assert c.get("/v1/things", headers=bearer("key-reader")).json() == {"ok": "list"}
    missing = c.get("/v1/things")
    assert missing.status_code == 401
    assert missing.headers["content-type"].startswith("application/problem+json")
    assert missing.headers["www-authenticate"] == "Bearer"
    body = missing.json()
    assert body["code"] == "unauthenticated" and body["type"] == "urn:jane:problem:unauthenticated"
    assert body["status"] == 401 and body["instance"] == "/v1/things"
    wrong = c.get("/v1/things", headers=bearer("key-nope"))
    assert wrong.status_code == 401 and wrong.json()["code"] == "unauthenticated"
    assert 'error="invalid_token"' in wrong.headers["www-authenticate"]
    basic = c.get("/v1/things", headers={"Authorization": "Basic a2V5LXJlYWRlcg=="})
    assert basic.status_code == 401
    forbidden = c.post("/v1/things", headers=bearer("key-reader"))
    assert forbidden.status_code == 403
    assert forbidden.json()["code"] == "forbidden"
    assert forbidden.json()["detail"] == "scope storage:write or storage:admin required"
    assert c.post("/v1/things", headers=bearer("key-writer")).json() == {"ok": "add"}
    # a key without scopes is still a valid token: info and "any token" operations
    assert c.get("/v1/open-to-any", headers=bearer("key-bare")).status_code == 200
    assert c.get("/v1/things", headers=bearer("key-bare")).status_code == 403


def test_health_open_info_authenticated_and_truthful(api_client: TestClient) -> None:
    c = api_client
    assert c.get("/v1/health").status_code == 200
    assert c.get("/v1/info").status_code == 401
    assert c.get("/v1/info", headers=bearer("key-bare")).json()["auth_mode"] == "api_key"
    assert c.get("/metrics").status_code == 200  # metrics_public defaults to true
    assert c.get("/openapi.json").status_code == 401
    assert c.get("/v1/unknown", headers=bearer("key-reader")).status_code == 404
    assert c.get("/v1/unknown").status_code == 401  # nothing is revealed without a token


def test_metrics_can_require_a_token() -> None:
    with TestClient(build(settings(auth_mode="api_key", api_keys=keys_doc(), metrics_public=False))) as c:
        assert c.get("/metrics").status_code == 401
        assert c.get("/metrics", headers=bearer("key-bare")).status_code == 200


def test_secret_refs_env_and_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    secret_file = tmp_path / "admin-key"
    secret_file.write_text("key-from-file\n", encoding="utf-8")
    monkeypatch.setenv("JANE_TEST_KEY_ENV", "key-from-env")
    keys = [
        {"name": "env", "secret_ref": "env:JANE_TEST_KEY_ENV", "scopes": ["storage:read"]},
        {"name": "file", "secret_ref": f"file:{secret_file}", "scopes": ["storage:read"]},
    ]
    keys_file = tmp_path / "keys.yaml"
    keys_file.write_text(
        "- name: yaml\n  sha256: " + sha256_hex("key-yaml") + "\n  scopes: [storage:read]\n", encoding="utf-8"
    )
    s = settings(auth_mode="api_key", api_keys=keys, api_keys_file=keys_file)
    with TestClient(build(s)) as c:
        for token in ("key-from-env", "key-from-file", "key-yaml"):
            assert c.get("/v1/things", headers=bearer(token)).status_code == 200, token
    assert resolve_secret_ref("env:JANE_TEST_KEY_ENV") == "key-from-env"
    with pytest.raises(SecretRefError, match="vault"):
        resolve_secret_ref("vault:kv/jane#key")


@pytest.mark.parametrize(
    ("kw", "match"),
    [
        ({"auth_mode": "api_key"}, "at least one key"),
        ({"auth_mode": "api_key", "api_keys": [{"name": "x", "scopes": []}]}, "exactly one of"),
        (
            {
                "auth_mode": "api_key",
                "api_keys": [{"name": "x", "secret_ref": "env:JANE_UNSET_X", "scopes": []}],
            },
            "JANE_UNSET_X is not set",
        ),
        (
            {
                "auth_mode": "api_key",
                "api_keys": [{"name": "x", "sha256": sha256_hex("a"), "scopes": ["Not A Scope"]}],
            },
            "service:action",
        ),
        (
            {
                "auth_mode": "api_key",
                "api_keys": [
                    {"name": "x", "sha256": sha256_hex("a"), "scopes": []},
                    {"name": "y", "sha256": sha256_hex("a"), "scopes": []},
                ],
            },
            "same value",
        ),
        ({"auth_mode": "jwt"}, "jwt_jwks_url, jwt_issuer, jwt_audience"),
        (
            {"auth_mode": "jwt", "jwt_jwks_url": JWKS_URL, "jwt_issuer": ISSUER, "jwt_audience": AUDIENCE}
            | {"jwt_algorithms": ["RS256", "HS256"]},
            "never none/HS",
        ),
        (
            {"auth_mode": "jwt", "jwt_jwks_url": "http://idp.example.test/certs"}
            | {"jwt_issuer": ISSUER, "jwt_audience": AUDIENCE},
            "https",
        ),
        ({"auth_mode": "none", "host": "0.0.0.0"}, "loopback"),
    ],
)
def test_incomplete_configuration_refuses_to_start(kw: dict[str, Any], match: str) -> None:
    with pytest.raises(AuthConfigError, match=match):
        build(settings(**kw))


def test_key_values_never_in_errors() -> None:
    with pytest.raises(AuthConfigError) as err:
        build(settings(auth_mode="api_key", api_keys=[{"name": "x", "sha256": "secret-value", "scopes": []}]))
    assert "secret-value" not in str(err.value)


def test_none_mode_is_anonymous_and_warns(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING, logger="jane.auth"), TestClient(build(settings())) as c:
        assert c.post("/v1/things").status_code == 200
        assert c.get("/v1/info").json()["auth_mode"] == "none"
    assert any("auth_mode=none" in r.getMessage() for r in caplog.records)
    remote = settings(host="0.0.0.0", auth_none_allow_remote=True)
    assert build(remote) is not None


def test_scope_table_must_cover_every_route() -> None:
    app = build(settings(auth_mode="api_key", api_keys=keys_doc()), scopes={"GET /v1/things": "storage:read"})
    assert sorted(unmapped_routes(app, {"GET /v1/things": "storage:read"})) == [
        "GET /v1/open-to-any",
        "POST /v1/things",
    ]
    with pytest.raises(AuthConfigError, match="POST /v1/things"), TestClient(app):
        pass
    # without the start-up check (no lifespan) an unmapped operation is denied, not allowed
    c = TestClient(app)
    assert c.post("/v1/things", headers=bearer("key-writer")).status_code == 403


def test_handlers_check_scopes_without_a_table() -> None:
    app = create_app(settings(auth_mode="api_key", api_keys=keys_doc()), configure_logs=False)

    @app.get("/v1/mine")
    async def mine(p: Principal = Depends(require("storage:write"))) -> dict[str, Any]:  # noqa: B008
        return {"name": p.name, "actor": p.attributes.get("actor")}

    with TestClient(app) as c:
        assert c.get("/v1/mine").status_code == 401
        assert c.get("/v1/mine", headers=bearer("key-reader")).status_code == 403
        assert c.get("/v1/mine", headers=bearer("key-writer")).json() == {"name": "writer", "actor": None}


# ----------------------------------------------------------------------------- jwt
class Idp:
    """A local identity provider: RSA and EC signing keys, JWKS served through an httpx transport."""

    def __init__(self) -> None:
        self.rsa = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.ec = ec.generate_private_key(ec.SECP256R1())
        self.published = {"rsa-1": self._jwk(self.rsa, "rsa-1"), "ec-1": self._jwk(self.ec, "ec-1")}
        self.requests = 0

    @staticmethod
    def _jwk(key: Any, kid: str) -> dict[str, Any]:
        algo = RSAAlgorithm if isinstance(key, rsa.RSAPrivateKey) else ECAlgorithm
        doc: dict[str, Any] = algo.to_jwk(key.public_key(), as_dict=True)
        return {**doc, "kid": kid, "use": "sig"}

    def jwks(self) -> dict[str, Any]:
        return {"keys": list(self.published.values())}

    def transport(self) -> httpx.MockTransport:
        def handler(request: httpx.Request) -> httpx.Response:
            assert str(request.url) == JWKS_URL
            self.requests += 1
            return httpx.Response(200, json=self.jwks())

        return httpx.MockTransport(handler)

    def token(
        self, *, kid: str = "rsa-1", alg: str = "RS256", key: Any = None, headers: Any = None, **claims: Any
    ) -> str:
        now = int(time.time())
        payload = {
            "iss": ISSUER,
            "aud": AUDIENCE,
            "sub": "svc-orchestrator",
            "iat": now,
            "exp": now + 300,
            "scope": "storage:read storage:write",
        } | claims
        payload = {k: v for k, v in payload.items() if v is not None}
        signing = key if key is not None else (self.ec if alg.startswith("ES") else self.rsa)
        return jwt.encode(payload, signing, algorithm=alg, headers={"kid": kid, **(headers or {})})


def jwt_settings(**kw: Any) -> JaneSettings:
    base: dict[str, Any] = {
        "auth_mode": "jwt",
        "jwt_jwks_url": JWKS_URL,
        "jwt_issuer": ISSUER,
        "jwt_audience": AUDIENCE,
        "jwt_jwks_refresh_cooldown_seconds": 0,
    }
    return settings(**(base | kw))


@pytest.fixture
def idp() -> Idp:
    return Idp()


@pytest.fixture
def jwt_client(idp: Idp) -> Iterator[TestClient]:
    s = jwt_settings()
    auth = Authenticator.from_settings(s, transport=idp.transport())
    with TestClient(build(s, authenticator=auth)) as c:
        yield c


def _b64(data: dict[str, Any]) -> str:
    return base64.urlsafe_b64encode(json.dumps(data).encode()).rstrip(b"=").decode()


def test_jwt_rs256_and_es256_ok(idp: Idp, jwt_client: TestClient) -> None:
    assert jwt_client.post("/v1/things", headers=bearer(idp.token())).json() == {"ok": "add"}
    assert jwt_client.get("/v1/things", headers=bearer(idp.token(kid="ec-1", alg="ES256"))).status_code == 200
    info = jwt_client.get("/v1/info", headers=bearer(idp.token(scope="")))
    assert info.json()["auth_mode"] == "jwt"
    assert idp.requests == 1  # the JWKS is cached
    listed = idp.token(scope=None, scp=["x:y"])  # no scope claim -> no scopes
    assert jwt_client.get("/v1/things", headers=bearer(listed)).status_code == 403
    as_list = jwt_settings(jwt_scope_claim="scp")
    auth = Authenticator.from_settings(as_list, transport=idp.transport())
    with TestClient(build(as_list, authenticator=auth)) as c:
        assert c.get("/v1/things", headers=bearer(idp.token(scp=["storage:read"]))).status_code == 200


@pytest.mark.parametrize(
    ("claims", "detail"),
    [
        ({"exp": int(time.time()) - 3600}, "token has expired"),
        ({"iss": "https://evil.example.test/"}, "token issuer is not accepted"),
        ({"aud": "jane-registry"}, "token audience is not accepted"),
        ({"nbf": int(time.time()) + 3600}, "token is not valid yet"),
        ({"exp": None}, "token has no exp claim"),
    ],
)
def test_jwt_rejected_claims(idp: Idp, jwt_client: TestClient, claims: dict[str, Any], detail: str) -> None:
    r = jwt_client.get("/v1/things", headers=bearer(idp.token(**claims)))
    assert r.status_code == 401 and r.json()["code"] == "unauthenticated"
    assert r.json()["detail"] == detail


def test_jwt_alg_none_and_hs256_with_public_key_are_rejected(idp: Idp, jwt_client: TestClient) -> None:
    claims = {
        "iss": ISSUER,
        "aud": AUDIENCE,
        "sub": "x",
        "exp": int(time.time()) + 300,
        "scope": "storage:read",
    }
    unsigned = f"{_b64({'alg': 'none', 'typ': 'JWT', 'kid': 'rsa-1'})}.{_b64(claims)}."
    r = jwt_client.get("/v1/things", headers=bearer(unsigned))
    assert r.status_code == 401 and "'none' is not accepted" in r.json()["detail"]
    # HS256 "signed" with the public key (PEM) as the HMAC secret: the classic key-confusion attack
    pem = idp.rsa.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    header = _b64({"alg": "HS256", "typ": "JWT", "kid": "rsa-1"})
    body = f"{header}.{_b64(claims)}"
    sig = base64.urlsafe_b64encode(hmac.new(pem, body.encode(), hashlib.sha256).digest()).rstrip(b"=")
    forged = f"{body}.{sig.decode()}"
    r = jwt_client.get("/v1/things", headers=bearer(forged))
    assert r.status_code == 401 and "'HS256' is not accepted" in r.json()["detail"]
    # RS256 header but signed by another key, and ES256 header with an RSA key id
    other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    assert jwt_client.get("/v1/things", headers=bearer(idp.token(key=other))).status_code == 401
    mixed = idp.token(kid="rsa-1", alg="ES256", key=idp.ec)
    assert jwt_client.get("/v1/things", headers=bearer(mixed)).status_code == 401
    assert jwt_client.get("/v1/things", headers=bearer("not-a-jwt")).status_code == 401


def test_jwt_unknown_kid_refreshes_jwks_once(idp: Idp) -> None:
    now = [1000.0]
    s = jwt_settings(jwt_jwks_refresh_cooldown_seconds=10)
    auth = Authenticator.from_settings(s, transport=idp.transport(), clock=lambda: now[0])
    with TestClient(build(s, authenticator=auth)) as c:
        assert c.get("/v1/things", headers=bearer(idp.token())).status_code == 200
        assert idp.requests == 1
        # the IdP rotates in a new key: the first token signed with it refreshes the JWKS once
        rotated = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        idp.published["rsa-2"] = Idp._jwk(rotated, "rsa-2")
        now[0] += 11
        assert c.get("/v1/things", headers=bearer(idp.token(kid="rsa-2", key=rotated))).status_code == 200
        assert idp.requests == 2
        # a kid the IdP does not have: one refresh after the cooldown, never one per request
        now[0] += 11
        stranger = idp.token(kid="rsa-unknown", key=rotated)
        for _ in range(3):
            r = c.get("/v1/things", headers=bearer(stranger))
            assert r.status_code == 401 and r.json()["detail"] == "token is signed with an unknown key"
        assert idp.requests == 3


def test_jwks_unavailable_is_503_not_401(idp: Idp) -> None:
    s = jwt_settings()
    down = httpx.MockTransport(lambda request: httpx.Response(503))
    with TestClient(build(s, authenticator=Authenticator.from_settings(s, transport=down))) as c:
        r = c.get("/v1/things", headers=bearer(idp.token()))
        assert r.status_code == 503 and r.json()["code"] == "service_unavailable"


def test_jwt_with_jwks_served_over_local_http(idp: Idp) -> None:
    """A real HTTP fetch (loopback only may use http://) with the configured timeout."""

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            body = json.dumps(idp.jwks()).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args: Any) -> None:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_address[1]}/certs"
        s = jwt_settings(jwt_jwks_url=url, jwt_jwks_timeout_ms=2000)
        with TestClient(build(s)) as c:
            assert c.get("/v1/things", headers=bearer(idp.token())).status_code == 200
            assert c.get("/v1/things", headers=bearer(idp.token(aud="other"))).status_code == 401
    finally:
        server.shutdown()
        server.server_close()


def test_routes_of_included_routers_are_checked_too() -> None:
    from jane_kit.jobs import JobRunner, jobs_router

    def make(table: dict[str, Any]) -> FastAPI:
        app = build(settings(auth_mode="api_key", api_keys=keys_doc()), scopes=table)
        app.include_router(jobs_router(JobRunner()))
        return app

    partial = make(SCOPES)
    assert unmapped_routes(partial, SCOPES) == ["GET /v1/jobs/{job_id}", "POST /v1/jobs/{job_id}/cancel"]
    with pytest.raises(AuthConfigError, match="/v1/jobs"), TestClient(partial):
        pass
    table = {**SCOPES, "GET /v1/jobs/{job_id}": "storage:read", "POST /v1/jobs/{job_id}/cancel": "storage:write"}
    with TestClient(make(table)) as c:
        assert c.get("/v1/jobs/job_x", headers=bearer("key-bare")).status_code == 403
        assert c.get("/v1/jobs/job_x", headers=bearer("key-reader")).status_code == 404  # authorized, no job
        assert c.post("/v1/jobs/job_x/cancel", headers=bearer("key-reader")).status_code == 403
