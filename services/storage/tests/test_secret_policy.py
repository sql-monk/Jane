"""Secret policy of connections (WP-07b): ``secret_refs`` and network addresses cannot exfiltrate secrets.

Without authentication anyone who reaches ``PUT /v1/connections/{id}`` chooses both *which* secret the executor
resolves and *where* the adapter sends it. The policy restricts ``env:`` to ``JANE_STORAGE_SECRET_ENV_PREFIX``,
``file:`` to ``JANE_STORAGE_SECRET_FILES_DIR`` and every host the adapter contacts to
``JANE_STORAGE_CONNECTION_HOST_ALLOWLIST``.
"""

from __future__ import annotations

import json
import os
import socket
import struct
import threading
import time
from collections.abc import Iterator, Mapping
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from jane_contracts.storage_adapter import AdapterError, ResolvedConnection
from jane_kit.errors import ValidationFailed
from jane_storage import connections as connections_module
from jane_storage.app import build_app
from jane_storage.policy import ConnectionPolicy, network_addresses, parse_host_port
from jane_storage.settings import Settings

USER = "jane-secret-user-7f3a"
PASSWORD = "jane-secret-password-9c1e"
FOREIGN = "db-password-not-for-storage"
NEGOTIATION = {struct.pack("!ii", 8, 80877103), struct.pack("!ii", 8, 80877104)}
"""PostgreSQL SSLRequest / GSSENCRequest."""


class Listener:
    """A TCP server standing for the attacker's host: records every connection and the first bytes sent."""

    def __init__(self) -> None:
        self.sock = socket.create_server(("127.0.0.1", 0))
        self.sock.settimeout(0.1)
        self.port = int(self.sock.getsockname()[1])
        self.received: list[bytes] = []
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                con, _ = self.sock.accept()
            except OSError:  # accept timeout
                continue
            with con:
                con.settimeout(2)
                data = b""
                try:
                    data = con.recv(4096)
                    if data in NEGOTIATION:  # decline SSL/GSS like a server without TLS; the login follows
                        con.sendall(b"N")
                        data += con.recv(4096)
                except OSError:
                    pass
                self.received.append(data)

    def wait(self, count: int, timeout: float = 5.0) -> None:
        deadline = time.monotonic() + timeout
        while len(self.received) < count and time.monotonic() < deadline:
            time.sleep(0.02)

    def close(self) -> None:
        self._stop.set()
        self._thread.join()
        self.sock.close()


@pytest.fixture
def listener() -> Iterator[Listener]:
    server = Listener()
    try:
        yield server
    finally:
        server.close()


@pytest.fixture
def secrets_dir(tmp_path: Path) -> Path:
    path = tmp_path / "secrets"
    path.mkdir()
    (path / "pg-password").write_text(PASSWORD + "\n", encoding="utf-8")
    (tmp_path / "outside").write_text(FOREIGN, encoding="utf-8")
    return path


@pytest.fixture(autouse=True)
def _env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PGPASSWORD", FOREIGN)
    monkeypatch.setenv("JANE_SECRET_PG_USER", USER)
    monkeypatch.setenv("JANE_SECRET_PG_PASSWORD", PASSWORD)


def pg(**overrides: Any) -> dict[str, Any]:
    params = {"host": "db.internal.test", "port": 5432, "database": "jane", "sslmode": "disable"}
    return {
        "connection_id": "pg",
        "kind": "postgresql",
        "params": {**params, **overrides.pop("params", {})},
        "secret_refs": {"username": "env:JANE_SECRET_PG_USER", "password": "env:JANE_SECRET_PG_PASSWORD"},
        **overrides,
    }


def with_host(value: Any) -> dict[str, Any]:
    return pg(params={"host": value})


def other(kind: str, params: Mapping[str, Any]) -> dict[str, Any]:
    return {"connection_id": "pg", "kind": kind, "params": dict(params)}


ALLOWLIST = [
    "db.internal.test:5432",
    "mongo.internal.test",
    "minio.internal.test",
    "s3.eu-central-1.amazonaws.com",
]

REJECTED: list[tuple[dict[str, Any], str, str]] = [
    # secret_refs: foreign variables, files outside the secrets directory, vault
    (pg(secret_refs={"password": "env:PGPASSWORD"}), "/secret_refs/password", "secret_ref_not_allowed"),
    (
        pg(secret_refs={"password": "env:JANE_STORAGE_CONNECTIONS_FILE"}),
        "/secret_refs/password",
        "secret_ref_not_allowed",
    ),
    (pg(secret_refs={"password": "env:JANE_SECRET_"}), "/secret_refs/password", "secret_ref_not_allowed"),
    (pg(secret_refs={"password": "vault:kv/jane#pg"}), "/secret_refs/password", "secret_ref_not_allowed"),
    # hosts outside the allowlist, adapter defaults included
    (with_host("evil.example.org"), "/params/host", "host_not_allowed"),
    (pg(params={"port": 5433}), "/params/host", "host_not_allowed"),
    (pg(params={"port": "not-a-port"}), "/params/port", "host_not_allowed"),
    (
        {**pg(), "params": {"database": "jane"}},  # no host: the adapter connects to localhost
        "/params/host",
        "host_not_allowed",
    ),
    (
        other("sqlserver", {"host": "evil.example.org", "database": "jane"}),
        "/params/host",
        "host_not_allowed",
    ),
    (
        other("sqlserver", {"host": "db.internal.test", "database": "jane"}),
        "/params/host",
        "host_not_allowed",
    ),
    # hosts inside URIs / connection strings
    (
        other("mongodb", {"host": "mongodb://mongo.internal.test:27017,evil.example.org:27017/jane"}),
        "/params/host",
        "host_not_allowed",
    ),
    (other("mongodb", {"host": "mongodb+srv://evil.example.org/jane"}), "/params/host", "host_not_allowed"),
    (other("mongodb", {"host": "mongo.internal.test,evil.example.org"}), "/params/host", "host_not_allowed"),
    (
        other("minio", {"endpoint": "http://evil.example.org:9000", "bucket": "b"}),
        "/params/endpoint",
        "host_not_allowed",
    ),
    (
        other("minio", {"endpoint": "ftp://minio.internal.test", "bucket": "b"}),
        "/params/endpoint",
        "host_not_allowed",
    ),
    (other("s3", {"bucket": "b", "region": "eu-west-1"}), "/params/region", "host_not_allowed"),
    (
        other("s3", {"bucket": "b", "endpoint": "https://evil.example.org"}),
        "/params/endpoint",
        "host_not_allowed",
    ),
    # adapters unknown to the core and unused host-like params: generic keys
    (other("custom", {"uri": "https://evil.example.org/api"}), "/params/uri", "host_not_allowed"),
    (other("custom", {"dsn": "host=db.internal.test port=5432"}), "/params/dsn", "host_not_allowed"),
    (
        other("filesystem", {"base_path": "/tmp/x", "url": "http://evil.example.org"}),
        "/params/url",
        "host_not_allowed",
    ),
    # values that parsers read differently must not pass as the allow-listed host
    *(
        (with_host(value), "/params/host", "host_not_allowed")
        for value in (
            "evil.example.org\\@db.internal.test",
            "evil.example.org@db.internal.test",
            "db.internal.test/../evil",
            "db.internal.test evil.example.org",
            "db.internal.test\t",
            "db.internal.test\x00.evil.example.org",
            "db.internal.test.",
            "db.internal.test:99999",
            "db.internal.test?x=1",
            "db.internal.test,evil.example.org",
            "/var/run/postgresql",
            "[::1]",
            "",
            ["db.internal.test"],
            42,
        )
    ),
    *(
        (other("minio", {"endpoint": value, "bucket": "b"}), "/params/endpoint", "host_not_allowed")
        for value in (
            "http://minio.internal.test@evil.example.org",
            "http://evil.example.org\\@minio.internal.test",
            "http://minio.internal.test%2F@evil.example.org",
            "http://minio.internal.test,evil.example.org",
            "http://minio.internal.test :9000",
        )
    ),
]


def test_put_rejects_exfiltrating_connections(tmp_path: Path, secrets_dir: Path, listener: Listener) -> None:
    rejected = [
        *REJECTED,
        (
            pg(secret_refs={"password": f"file:{tmp_path / 'outside'}"}),
            "/secret_refs/password",
            "secret_ref_not_allowed",
        ),
        (
            pg(secret_refs={"password": f"file:{secrets_dir / '..' / 'outside'}"}),
            "/secret_refs/password",
            "secret_ref_not_allowed",
        ),
        (
            pg(secret_refs={"password": f"file:{secrets_dir}"}),
            "/secret_refs/password",
            "secret_ref_not_allowed",
        ),
        (
            pg(params={"host": "127.0.0.1", "port": listener.port}),
            "/params/host",
            "host_not_allowed",
        ),
    ]
    settings = Settings(
        log_format="console", secret_files_dir=secrets_dir, connection_host_allowlist=ALLOWLIST
    )
    with TestClient(build_app(settings)) as c:
        for doc, pointer, code in rejected:
            r = c.put("/v1/connections/pg", json=doc)
            assert r.status_code == 422, (doc, r.text)
            problem = r.json()
            assert problem["code"] == "validation_failed"
            assert (problem["errors"][0]["pointer"], problem["errors"][0]["code"]) == (pointer, code), (
                doc,
                r.text,
            )
            assert FOREIGN not in r.text and PASSWORD not in r.text
            assert c.get("/v1/connections/pg").status_code == 404

        # allowed: prefixed env variable, a file inside the secrets directory, allow-listed hosts
        allowed = [
            pg(
                secret_refs={
                    "username": "env:JANE_SECRET_PG_USER",
                    "password": f"file:{secrets_dir / 'pg-password'}",
                }
            ),
            pg(secret_refs={"password": f"file:{secrets_dir / 'sub' / '..' / 'pg-password'}"}),
            with_host("DB.Internal.Test"),
            other(
                "mongodb",
                {"host": "mongodb://mongo.internal.test:27018,mongo.internal.test/jane?replicaSet=rs0"},
            ),
            other("mongodb", {"host": "mongo.internal.test", "port": 27019}),
            other("mongodb", {"host": "mongodb+srv://mongo.internal.test/jane"}),
            other("minio", {"endpoint": "http://minio.internal.test:9000", "bucket": "b"}),
            other("minio", {"bucket": "b"}),  # no endpoint: the adapter refuses to open, nothing is contacted
            other("s3", {"bucket": "b", "region": "eu-central-1"}),
            other("filesystem", {"base_path": str(tmp_path / "files")}),
        ]
        for doc in allowed:
            r = c.put("/v1/connections/pg", json=doc)
            assert r.status_code in (200, 201), (doc, r.text)
        c.put("/v1/connections/pg", json=allowed[0])
        registry = c.app.state.registry  # type: ignore[attr-defined]
        assert registry.secrets_resolved("pg") == {"username": True, "password": True}
        assert registry.resolve("pg").secrets == {"username": USER, "password": PASSWORD}
    assert listener.received == []


@pytest.mark.skipif(os.name == "nt", reason="symlinks need extra privileges on Windows")
def test_symlink_out_of_the_secrets_directory_is_rejected(tmp_path: Path, secrets_dir: Path) -> None:
    (secrets_dir / "link").symlink_to(tmp_path / "outside")
    policy = ConnectionPolicy(files_dir=secrets_dir)
    assert policy.ref_error(f"file:{secrets_dir / 'link'}") is not None
    assert policy.resolve(f"file:{secrets_dir / 'link'}") is None


def post(client: TestClient, body: dict[str, Any]) -> Any:
    return client.post(
        "/v1/invocations", json=body, headers={"Idempotency-Key": body["delivery"]["delivery_key"]}
    )


def test_no_secret_reaches_a_host_outside_the_allowlist(
    tmp_path: Path, secrets_dir: Path, listener: Listener, h: SimpleNamespace
) -> None:
    evil = pg(params={"host": "127.0.0.1", "port": listener.port})
    evil["connection_id"] = "evil"
    conns = tmp_path / "connections.json"
    conns.write_text(json.dumps({"connections": [evil]}), encoding="utf-8")

    # 1. Not allow-listed: PUT → 422. The same connection from the config file (bypassing the API) is kept,
    #    but gets no secrets and is rejected wherever it would be used.
    settings = Settings(log_format="console", connections_file=conns, secret_files_dir=secrets_dir)
    with TestClient(build_app(settings)) as c:
        r = c.put("/v1/connections/evil2", json={**evil, "connection_id": "evil2"})
        assert r.status_code == 422
        assert r.json()["errors"][0]["code"] == "host_not_allowed"
        assert c.get("/v1/connections/evil").status_code == 200

        test = c.post("/v1/connections/evil/test")
        assert test.status_code == 200
        assert test.json()["ok"] is False
        assert test.json()["secrets_resolved"] == {"username": False, "password": False}
        assert "host_not_allowed" in test.json()["message"]

        body = h.invocation(
            [{"kind": "entities", "entities": [h.entity()]}],
            "dk-evil",
            package="jane.storage-postgresql",
            target="evil",
        )
        inv = post(c, body)
        assert inv.status_code == 422, inv.text
        assert inv.json()["errors"][0]["code"] == "host_not_allowed"
        assert inv.json()["errors"][0]["pointer"] == "/connections/target"

        read = c.get("/v1/entities", params={"connection_id": "evil", "entity_type": "product"})
        assert read.status_code == 422
        assert read.json()["errors"][0] == {**read.json()["errors"][0], "parameter": "connection_id"}
        assert read.json()["errors"][0]["code"] == "host_not_allowed"

        with pytest.raises(ValidationFailed, match="secret policy"):
            c.app.state.registry.resolve("evil")  # type: ignore[attr-defined]
        for resp in (r, test, inv, read):
            assert USER not in resp.text and PASSWORD not in resp.text
    time.sleep(0.3)
    assert listener.received == []

    # 2. Control: allow-listed, the adapter does contact the host and sends the login to it — so the empty
    #    listener above proves the policy, not a broken connection.
    allowed = Settings(
        log_format="console",
        connections_file=conns,
        secret_files_dir=secrets_dir,
        connection_host_allowlist=[f"127.0.0.1:{listener.port}"],
    )
    with TestClient(build_app(allowed)) as c:
        test = c.post("/v1/connections/evil/test")
        assert test.status_code == 200
        assert test.json()["secrets_resolved"] == {"username": True, "password": True}
        assert test.json()["ok"] is False  # the listener is not PostgreSQL
        assert PASSWORD not in test.text
    listener.wait(1)
    assert any(USER.encode() in data for data in listener.received), listener.received


class LeakyAdapter:
    """Neighbour stand-in (``StorageAdapter`` from contracts): a driver error echoing the login."""

    kind = "postgresql"
    capabilities = frozenset({"objects", "entities", "history"})

    async def open(self, connection: ResolvedConnection, options: Mapping[str, Any]) -> None:
        secrets = connection.secrets
        raise AdapterError(
            f"login failed for user {secrets['username']!r} (dsn postgresql://{secrets['username']}:"
            f"{secrets['password']}@db.internal.test/jane)",
            retryable=True,
        )

    async def close(self) -> None:
        return None


def test_adapter_errors_do_not_reveal_secret_values(
    monkeypatch: pytest.MonkeyPatch, secrets_dir: Path
) -> None:
    monkeypatch.setattr(connections_module, "create_adapter", lambda kind: LeakyAdapter())
    settings = Settings(
        log_format="console",
        secret_files_dir=secrets_dir,
        connection_host_allowlist=["db.internal.test:5432"],
    )
    with TestClient(build_app(settings)) as c:
        assert c.put("/v1/connections/pg", json=pg()).status_code == 201
        test = c.post("/v1/connections/pg/test")
        assert test.json()["ok"] is False
        assert test.json()["secrets_resolved"] == {"username": True, "password": True}
        assert "login failed for user '***'" in test.json()["message"]
        read = c.get("/v1/entities", params={"connection_id": "pg", "entity_type": "product"})
        assert read.status_code == 502  # upstream_unavailable
        assert "login failed for user '***'" in read.json()["detail"]
        for resp in (test, read):
            assert USER not in resp.text and PASSWORD not in resp.text


def test_policy_settings_from_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    defaults = Settings()
    assert defaults.secret_env_prefix == "JANE_SECRET_"
    assert defaults.secret_files_dir == Path("/run/secrets")
    assert defaults.connection_host_allowlist == []

    monkeypatch.setenv("JANE_STORAGE_CONNECTION_HOST_ALLOWLIST", '["postgres:5432", "MinIO"]')
    monkeypatch.setenv("JANE_STORAGE_SECRET_ENV_PREFIX", "MYAPP_SECRET_")
    monkeypatch.setenv("JANE_STORAGE_SECRET_FILES_DIR", "")
    policy = Settings().connection_policy()
    assert policy.ref_error("env:MYAPP_SECRET_PG") is None
    assert policy.ref_error("env:JANE_SECRET_PG") is not None
    assert policy.ref_error(f"file:{tmp_path / 'x'}") == "file: references are disabled"
    assert policy.violations(other("postgresql", {"host": "postgres"})) == []
    assert policy.violations(other("minio", {"endpoint": "https://minio:9443"})) == []
    assert [e.code for e in policy.violations(other("postgresql", {"host": "postgres", "port": 6432}))] == [
        "host_not_allowed"
    ]

    monkeypatch.setenv("JANE_STORAGE_CONNECTION_HOST_ALLOWLIST", '["http://postgres:5432"]')
    with pytest.raises(ValidationError, match="hostname or hostname:port"):
        Settings()


@pytest.mark.parametrize(
    ("kind", "params", "expected"),
    [
        ("postgresql", {}, ["localhost:5432"]),
        ("postgresql", {"host": "postgres", "port": "6432"}, ["postgres:6432"]),
        ("sqlserver", {"host": "sqlserver"}, ["sqlserver:1433"]),
        ("mongodb", {"host": "mongodb"}, ["mongodb:27017"]),
        ("mongodb", {"host": "mongodb:27018"}, ["mongodb:27018"]),
        ("mongodb", {"host": "mongodb://a:1,b/x?tls=true", "port": 27020}, ["a:1", "b:27020"]),
        ("mongodb", {"host": "mongodb+srv://cluster.example.org/x"}, ["cluster.example.org"]),
        ("s3", {"bucket": "b"}, ["s3.us-east-1.amazonaws.com:443"]),
        ("s3", {"bucket": "b", "region": "eu-central-1"}, ["s3.eu-central-1.amazonaws.com:443"]),
        ("s3", {"bucket": "b", "endpoint": "http://s3:8333"}, ["s3:8333"]),
        ("minio", {"bucket": "b", "endpoint": "https://minio"}, ["minio:443"]),
        ("minio", {"bucket": "b"}, []),
        ("filesystem", {"base_path": "/var/lib/jane"}, []),
        (
            "custom",
            {"hosts": ["a:1", "https://b/x"], "endpoint_url": "grpc://c:50051"},
            ["a:1", "b:443", "c:50051"],
        ),
    ],
)
def test_network_addresses_of_the_adapters(kind: str, params: dict[str, Any], expected: list[str]) -> None:
    found, problems = network_addresses(kind, params)
    assert problems == []
    assert [str(a) for a in found] == expected


def test_parse_host_port() -> None:
    assert parse_host_port("Postgres:5432") == ("postgres", 5432)
    assert parse_host_port("10.0.0.5") == ("10.0.0.5", None)
    assert parse_host_port("jane_postgres_1") == ("jane_postgres_1", None)
    for bad in (
        "",
        "a:0",
        "a:65536",
        "-a",
        "a-",
        "a..b",
        "a.",
        "a b",
        "a/b",
        "[::1]",
        "a@b",
        "a\\b",
        "ä.test",
    ):
        assert parse_host_port(bad) is None, bad
    with pytest.raises(ValueError, match="hostname or hostname:port"):
        ConnectionPolicy(host_allowlist=("https://postgres",))
