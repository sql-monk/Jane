"""Smoke test of the dev stack started by `just up`: every service answers with the generated credentials.

just up && just integration infra/tests
"""

from __future__ import annotations

import urllib.error
import urllib.request
import uuid

import pytest

from jane_kit.devstack import StackInfo, load_stack

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def stack() -> StackInfo:
    info = load_stack()
    if info is None:
        pytest.skip("dev stack is not running (`just up`)")
    return info


def test_postgres(stack: StackInfo) -> None:
    psycopg = pytest.importorskip("psycopg")
    with psycopg.connect(stack.get("postgres", "dsn"), connect_timeout=10) as conn:
        assert conn.execute("select 1").fetchone() == (1,)


def test_postgres_service_roles_cannot_enter_other_databases(stack: StackInfo) -> None:
    psycopg = pytest.importorskip("psycopg")
    names = ("handler-runtime", "orchestrator", "registry", "llm", "assistant", "storage-results")
    pg = stack.services["postgres"]
    for name in names:
        info = stack.services[f"db-{name}"]
        with psycopg.connect(info["db_dsn"], connect_timeout=5) as conn:
            assert conn.execute("SELECT current_user, current_database()").fetchone() == (
                info["db_user"],
                info["db_name"],
            )
            assert conn.execute(
                "SELECT rolsuper, rolcreatedb, rolcreaterole FROM pg_roles WHERE rolname = current_user"
            ).fetchone() == (False, False, False)
        for other in (
            "jane",
            "postgres",
            "template1",
            *(stack.services[f"db-{n}"]["db_name"] for n in names if n != name),
        ):
            with pytest.raises(psycopg.OperationalError, match="permission denied for database"):
                psycopg.connect(
                    host=pg["host"],
                    port=pg["port"],
                    user=info["db_user"],
                    password=info["db_password"],
                    dbname=other,
                    connect_timeout=5,
                )


def test_sqlserver(stack: StackInfo) -> None:
    pymssql = pytest.importorskip("pymssql")
    s = stack.services["sqlserver"]
    conn = pymssql.connect(
        server=s["host"], port=str(s["port"]), user=s["user"], password=s["password"], login_timeout=10
    )
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1")
        assert cur.fetchone() == (1,)
    finally:
        conn.close()


def test_mongodb(stack: StackInfo) -> None:
    pymongo = pytest.importorskip("pymongo")
    client = pymongo.MongoClient(stack.get("mongodb", "uri"), serverSelectionTimeoutMS=10_000)
    try:
        assert client.admin.command("ping")["ok"] == 1
    finally:
        client.close()


@pytest.mark.parametrize("name", ["minio", "s3"])
def test_object_storage_roundtrip(stack: StackInfo, name: str) -> None:
    boto3 = pytest.importorskip("boto3")
    s = stack.services[name]
    client = boto3.client(
        "s3",
        endpoint_url=s["endpoint"],
        aws_access_key_id=s["access_key"],
        aws_secret_access_key=s["secret_key"],
        region_name=s.get("region", "us-east-1"),
    )
    bucket = f"jane-smoke-{uuid.uuid4().hex[:8]}"
    client.create_bucket(Bucket=bucket)
    client.put_object(Bucket=bucket, Key="raw/page.html", Body=b"<html>ok</html>", ContentType="text/html")
    assert client.get_object(Bucket=bucket, Key="raw/page.html")["Body"].read() == b"<html>ok</html>"
    client.delete_object(Bucket=bucket, Key="raw/page.html")
    client.delete_bucket(Bucket=bucket)


def test_object_storage_rejects_wrong_credentials(stack: StackInfo) -> None:
    boto3 = pytest.importorskip("boto3")
    botocore = pytest.importorskip("botocore.exceptions")
    for name in ("minio", "s3"):
        client = boto3.client(
            "s3",
            endpoint_url=stack.get(name, "endpoint"),
            aws_access_key_id="wrong",
            aws_secret_access_key="wrong-secret",
            region_name="us-east-1",
        )
        with pytest.raises(botocore.ClientError):
            client.list_buckets()


def test_testsite_direct_and_through_proxy(stack: StackInfo) -> None:
    with urllib.request.urlopen(stack.url("testsite") + "/robots.txt", timeout=5) as r:
        assert b"Disallow: /private/" in r.read()
    with urllib.request.urlopen(stack.url("proxy") + "/testsite/", timeout=5) as r:
        assert b'href="/testsite/catalog/"' in r.read()
    with urllib.request.urlopen(stack.url("proxy") + "/_proxy/health", timeout=5) as r:
        assert r.status == 200
        assert "frame-ancestors 'none'" in r.headers["Content-Security-Policy"]
        assert r.headers["X-Content-Type-Options"] == "nosniff"
    with urllib.request.urlopen(stack.url("proxy") + "/config.json", timeout=5) as r:
        assert b'"api_base": "/api"' in r.read()
        assert r.headers["Cache-Control"] == "no-store"
    with pytest.raises(urllib.error.HTTPError) as unknown:
        urllib.request.urlopen(stack.url("proxy") + "/api/no-such-service/v1/health", timeout=5)
    assert unknown.value.code == 404
