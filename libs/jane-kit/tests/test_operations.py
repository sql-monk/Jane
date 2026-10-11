from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import Field

from jane_kit.auth import sha256_hex
from jane_kit.config import JaneSettings, LimitLayer, Limits, resolve_limits
from jane_kit.service import create_app


class Engine(Limits):
    workers: int = Field(default=2, ge=0)
    timeout_ms: int = Field(default=500, ge=10)


class ServiceLimits(Limits):
    engine: Engine = Engine()


def make_app(path: Path, **kwargs):
    settings = JaneSettings(operations_dir=path, **kwargs)
    limits = resolve_limits(
        ServiceLimits,
        *settings.platform_layers(),
        LimitLayer(level="platform", hard_caps={"engine": {"workers": 8}}),
    )
    app = create_app(settings, limits=limits, configure_logs=False)
    return app


def test_configuration_constraints_etag_and_restart(tmp_path):
    app = make_app(tmp_path)
    with TestClient(app) as client:
        original = client.get("/v1/configuration")
        tag = original.headers["etag"]
        assert client.put("/v1/configuration", json={"values": {}}).status_code == 428
        assert (
            client.put(
                "/v1/configuration",
                headers={"If-Match": tag},
                json={"values": {"settings.api_keys": "secret"}},
            ).status_code
            == 422
        )
        assert (
            client.put(
                "/v1/configuration", headers={"If-Match": tag}, json={"values": {"limits.engine.workers": 9}}
            ).status_code
            == 422
        )
        assert (
            client.put(
                "/v1/configuration", headers={"If-Match": tag}, json={"values": {"limits.engine.workers": -1}}
            ).status_code
            == 422
        )
        saved = client.put(
            "/v1/configuration",
            headers={"If-Match": tag},
            json={"values": {"limits.engine.workers": 3, "settings.log_level": "WARNING"}},
        )
        assert saved.status_code == 200
        assert saved.json()["pending_restart"]
        assert (
            client.put("/v1/configuration", headers={"If-Match": tag}, json={"values": {}}).status_code == 412
        )
        assert app.state.settings.log_level == "INFO"
    restarted = make_app(tmp_path)
    with TestClient(restarted) as client:
        config = client.get("/v1/configuration").json()
        assert not config["pending_restart"]
        assert restarted.state.settings.log_level == "WARNING"
        workers = next(f for f in config["fields"] if f["path"] == "limits.engine.workers")
        assert workers["value"] == 3
        assert workers["origin"] == "module"


def test_scope_and_protected_values(tmp_path):
    settings = {
        "auth_mode": "api_key",
        "api_keys": [
            {"name": "reader", "sha256": sha256_hex("read-key"), "scopes": ["modules:read"]},
            {"name": "writer", "sha256": sha256_hex("write-key"), "scopes": ["modules:write"]},
            {"name": "collector", "sha256": sha256_hex("collector-key"), "scopes": ["collector:read"]},
        ],
    }
    with TestClient(make_app(tmp_path, **settings)) as client:
        assert client.get("/v1/configuration").status_code == 401
        assert (
            client.get("/v1/telemetry", headers={"Authorization": "Bearer collector-key"}).status_code == 403
        )
        response = client.get("/v1/configuration", headers={"Authorization": "Bearer read-key"})
        assert response.status_code == 200
        assert "read-key" not in response.text and "api_keys" not in response.text
        assert (
            client.put(
                "/v1/configuration",
                headers={"Authorization": "Bearer read-key", "If-Match": response.headers["etag"]},
                json={"values": {}},
            ).status_code
            == 403
        )
        assert (
            client.put(
                "/v1/configuration",
                headers={"Authorization": "Bearer write-key", "If-Match": response.headers["etag"]},
                json={"values": {}},
            ).status_code
            == 200
        )


def test_durable_telemetry_and_unknown_metrics(tmp_path):
    app = make_app(tmp_path)
    with TestClient(app) as client:
        client.get("/v1/info")
        # Real sampler and registry, no replacement of the component under test.
        from jane_kit.operations import Operations

        sampler = Operations(app, app.state.settings, None)
        sampler.sample()
        sampler.sample()
        history = client.get("/v1/telemetry").json()
        assert history["samples"]
        assert history["samples"][-1]["values"]["materials_per_second"] is None
        assert history["samples"][-1]["values"]["http_requests_per_second"] == 0
        assert (
            client.get("/v1/telemetry?since=2026-10-12T00:00:00Z&until=2026-10-11T00:00:00Z").status_code
            == 400
        )
        assert client.get("/v1/telemetry?limit=1").status_code == 422
        count = len(history["samples"])
    with TestClient(make_app(tmp_path)) as client:
        assert len(client.get("/v1/telemetry").json()["samples"]) >= count


def test_reset_inherited_values_requires_restart(tmp_path):
    with TestClient(make_app(tmp_path)) as client:
        tag = client.get("/v1/configuration").headers["etag"]
        client.put(
            "/v1/configuration",
            headers={"If-Match": tag},
            json={"values": {"limits.engine.workers": 3, "settings.log_level": "WARNING"}},
        )
    with TestClient(make_app(tmp_path)) as client:
        initial = client.get("/v1/configuration")
        assert not initial.json()["pending_restart"]
        result = client.put(
            "/v1/configuration", headers={"If-Match": initial.headers["etag"]}, json={"values": {}}
        )
        assert result.json()["pending_restart"]
        workers = next(f for f in result.json()["fields"] if f["path"] == "limits.engine.workers")
        assert workers["inherited_value"] == 2 and workers["value"] == 3
        assert workers["origin"] == "module"
    with TestClient(make_app(tmp_path)) as client:
        result = client.get("/v1/configuration").json()
        assert not result["pending_restart"]
        assert next(f for f in result["fields"] if f["path"] == "limits.engine.workers")["value"] == 2


@pytest.mark.parametrize("value", [True, "2", 1.5])
def test_numeric_type_constraints(tmp_path, value):
    with TestClient(make_app(tmp_path)) as client:
        tag = client.get("/v1/configuration").headers["etag"]
        assert (
            client.put(
                "/v1/configuration",
                headers={"If-Match": tag},
                json={"values": {"limits.engine.workers": value}},
            ).status_code
            == 422
        )


def test_downsample_resolution_retains_history_endpoints(tmp_path):
    import json
    import time

    from jane_kit.operations import Operations

    app = make_app(tmp_path)
    sampler = Operations(app, app.state.settings, None)
    sampler.initialize()
    start = time.time() - 1000
    with sampler.connect() as db:
        db.executemany(
            "INSERT INTO samples (at,instance,document) VALUES (?,?,?)",
            [(start + i * 5, "a", json.dumps({"http_inflight": i})) for i in range(201)],
        )
    history = sampler.telemetry(None, None, 11)
    assert len(history["samples"]) == 11
    assert history["resolution_seconds"] == 100
    assert history["samples"][0]["values"]["http_inflight"] == 0
    assert history["samples"][-1]["values"]["http_inflight"] == 200
