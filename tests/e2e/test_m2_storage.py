"""S-M2-08: switch one orchestrated task across all six real storage adapters."""

from __future__ import annotations

import asyncio
import copy
import hashlib
import json
from collections.abc import Callable
from typing import Any

import asyncpg  # type: ignore[import-untyped]
import boto3  # type: ignore[import-untyped]
import pymssql
import pytest
from botocore.config import Config  # type: ignore[import-untyped]
from pymongo import MongoClient

from jane_e2e.clients import JaneClient
from jane_e2e.orchestration import TESTSITE, create_source, create_task, m1_task, start_run, wait_run
from jane_e2e.stack import E2EStack
from jane_e2e.steps import collector_fetch, extract, store
from jane_e2e.verify import entities, history, objects_by_source, raw_bytes
from jane_storage.keys import key_digest

pytestmark = [pytest.mark.e2e, pytest.mark.milestone("M2"), pytest.mark.criteria(3, 8, 12)]

PRODUCT = TESTSITE + "/product/phone-alpha"
ADAPTERS = (
    ("files", "jane.storage-files", "raw-files"),
    ("postgresql", "jane.storage-postgresql", "results-pg"),
    ("sqlserver", "jane.storage-sqlserver", "e2e-sqlserver"),
    ("mongodb", "jane.storage-mongodb", "e2e-mongodb"),
    ("minio", "jane.storage-minio", "e2e-minio"),
    ("s3", "jane.storage-s3", "e2e-s3"),  # SeaweedFS is the external S3 substitute.
)


def _create_sqlserver_database(stack: E2EStack) -> None:
    """The SQL Server image creates only master; adapters may create tables, but not databases."""
    con = pymssql.connect(
        server="127.0.0.1",
        port=str(stack.host_port("sqlserver")),
        user="sa",
        password=stack.env()["JANE_MSSQL_SA_PASSWORD"],
        database="master",
        autocommit=True,
        login_timeout=10,
        tds_version="7.4",
    )
    try:
        with con.cursor() as cur:
            cur.execute("IF DB_ID(N'jane_e2e') IS NULL CREATE DATABASE [jane_e2e]")
    finally:
        con.close()


def _native_files(stack: E2EStack, obj: dict[str, Any], entity: dict[str, Any], raw: bytes) -> None:
    assert stack.exec("storage", "cat", f"/var/lib/jane/storage/{obj['locator']['path']}") == raw
    path = f"/var/lib/jane/storage/entities/product/{key_digest(entity['canonical_key'])}.json"
    doc = json.loads(stack.exec("storage", "cat", path))
    assert doc["fields"] == entity["fields"]


def _native_postgres(stack: E2EStack, obj: dict[str, Any], entity: dict[str, Any], raw: bytes) -> None:
    async def query() -> None:
        con = await asyncpg.connect(
            host="127.0.0.1",
            port=stack.host_port("postgres"),
            database="jane_storage_results",
            user="jane_storage_results",
            password=stack.env()["JANE_PG_STORAGE_RESULTS_PASSWORD"],
            ssl=False,
        )
        try:
            assert (
                await con.fetchval(
                    'SELECT content FROM "e2e_results"."jane_objects" WHERE object_id=$1', obj["object_id"]
                )
                == raw
            )
            row = await con.fetchrow(
                'SELECT fields, version FROM "e2e_results"."jane_entities" '
                "WHERE entity_type=$1 AND canonical_key=$2",
                "product",
                entity["canonical_key"],
            )
            assert row is not None
            assert json.loads(row["fields"]) == entity["fields"]
            assert row["version"] == 1
        finally:
            await con.close()

    asyncio.run(query())


def _native_sqlserver(stack: E2EStack, obj: dict[str, Any], entity: dict[str, Any], raw: bytes) -> None:
    con = pymssql.connect(
        server="127.0.0.1",
        port=str(stack.host_port("sqlserver")),
        user="sa",
        password=stack.env()["JANE_MSSQL_SA_PASSWORD"],
        database="jane_e2e",
        login_timeout=10,
        tds_version="7.4",
    )
    try:
        with con.cursor() as cur:
            cur.execute("SELECT content FROM [e2e].[jane_objects] WHERE object_id=%s", (obj["object_id"],))
            row = cur.fetchone()
            assert row is not None and bytes(row[0]) == raw  # type: ignore[arg-type]
            cur.execute(
                "SELECT doc FROM [e2e].[jane_entities] WHERE entity_type=%s AND key_hash=%s",
                ("product", key_digest(entity["canonical_key"])),
            )
            row = cur.fetchone()
            assert row is not None
            assert json.loads(row[0])["fields"] == entity["fields"]  # type: ignore[arg-type]
    finally:
        con.close()


def _native_mongodb(stack: E2EStack, obj: dict[str, Any], entity: dict[str, Any], raw: bytes) -> None:
    env = stack.env()
    mongo: MongoClient[Any] = MongoClient(
        "127.0.0.1",
        stack.host_port("mongodb"),
        username=env["JANE_MONGO_USER"],
        password=env["JANE_MONGO_PASSWORD"],
        authSource="admin",
    )
    try:
        db = mongo["jane_e2e"]
        doc = db["jane_objects"].find_one({"_id": obj["object_id"]})
        assert doc is not None and doc["sha256"] == obj["sha256"]
        chunks = db["jane_object_chunks"].find({"object_id": obj["object_id"]}).sort("n", 1)
        assert b"".join(bytes(part["data"]) for part in chunks) == raw
        state = db["jane_entities"].find_one({"_id": f"product|{key_digest(entity['canonical_key'])}"})
        assert state is not None and state["fields"] == entity["fields"]
    finally:
        mongo.close()


def _native_s3(stack: E2EStack, kind: str, obj: dict[str, Any], entity: dict[str, Any], raw: bytes) -> None:
    env = stack.env()
    service = "minio" if kind == "minio" else "s3"
    access = "JANE_MINIO_ACCESS_KEY" if service == "minio" else "JANE_S3_ACCESS_KEY"
    secret = "JANE_MINIO_SECRET_KEY" if service == "minio" else "JANE_S3_SECRET_KEY"
    s3 = boto3.client(
        "s3",
        endpoint_url=stack.url(service),
        region_name="us-east-1",
        aws_access_key_id=env[access],
        aws_secret_access_key=env[secret],
        config=Config(s3={"addressing_style": "path"}),
    )
    bucket = obj["locator"]["bucket"]
    assert s3.get_object(Bucket=bucket, Key=obj["locator"]["key"])["Body"].read() == raw
    key = f"e2e/entities/product/{key_digest(entity['canonical_key'])}.json"
    state = json.loads(s3.get_object(Bucket=bucket, Key=key)["Body"].read())
    assert state["fields"] == entity["fields"]


def _assert_native(
    stack: E2EStack, kind: str, obj: dict[str, Any], entity: dict[str, Any], raw: bytes
) -> None:
    if kind == "files":
        _native_files(stack, obj, entity, raw)
    elif kind == "postgresql":
        _native_postgres(stack, obj, entity, raw)
    elif kind == "sqlserver":
        _native_sqlserver(stack, obj, entity, raw)
    elif kind == "mongodb":
        _native_mongodb(stack, obj, entity, raw)
    else:
        _native_s3(stack, kind, obj, entity, raw)


def _redeliver(
    stack: E2EStack,
    storage: JaneClient,
    collector: JaneClient,
    runtime: JaneClient,
    kind: str,
    package: str,
    connection: str,
    run_id: str,
) -> None:
    """Replay identical handler requests, then check one RAW and one entity/history in this backend."""
    source_id = f"e2e-{run_id}-{kind}-redelivery"
    material = collector_fetch(collector, PRODUCT, source_id)
    body, first = store(
        storage,
        package_id=package,
        connection=connection,
        inputs=[{"kind": "material", "material": material}],
        run_id=run_id,
        stage_id=f"store-raw-{kind}",
        key_part=material["observation_id"],
    )
    assert first["status"] == "success", first
    (ack,) = first["output"]["writes"]
    assert ack["status"] == "written", ack
    _, again = storage.invoke(body)
    assert again["duplicate"] is True and again["output"]["writes"][0]["status"] == "duplicate"
    (listed,) = objects_by_source(storage, connection, source_id)
    assert listed["object"]["object_id"] == ack["object"]["object_id"]

    _, extracted = extract(runtime, material, f"{run_id}-{kind}")
    assert extracted["status"] == "success", extracted
    entity_body, first_entity = store(
        storage,
        package_id=package,
        connection=connection,
        inputs=[
            {
                "kind": "entities",
                "entities": extracted["output"]["entities"],
                "from_invocation_id": extracted["invocation_id"],
            }
        ],
        run_id=run_id,
        stage_id=f"store-products-{kind}",
        key_part=extracted["invocation_id"],
    )
    assert first_entity["status"] == "success", first_entity
    assert first_entity["output"]["writes"][0]["status"] == "written"
    _, again_entity = storage.invoke(entity_body)
    assert again_entity["duplicate"] is True
    assert again_entity["output"]["writes"][0]["status"] == "duplicate"
    (state,) = entities(storage, connection, source_id)
    assert state["version"] == 1
    assert len(history(storage, connection, state["canonical_key"])) == 1
    _assert_native(stack, kind, ack["object"], state, raw_bytes(material))


@pytest.mark.criteria(3, 8, 12)
def test_s_m2_08_all_storage_adapters_via_task_revision(
    stack: E2EStack,
    require: Callable[..., None],
    orchestrated: JaneClient,
    client: Callable[..., JaneClient],
    extractor: dict[str, Any],
    run_id: str,
) -> None:
    require("sqlserver", "mongodb", "minio", "s3")
    _create_sqlserver_database(stack)
    orch = orchestrated.api("orchestrator")
    storage = client("storage")
    collector = client("web-collector")
    runtime = client("handler-runtime")
    source_id, task_id = f"e2e-{run_id}-adapters", f"e2e-{run_id}-adapters"
    create_source(orchestrated, source_id)
    create_task(orchestrated, m1_task(task_id, source_id, [PRODUCT], extractor))

    for kind, package, connection in ADAPTERS:
        current = orch.get(f"/v1/tasks/{task_id}")
        assert current.status_code == 200, current.text
        task = copy.deepcopy(current.json())
        before = copy.deepcopy(task)
        for stage in task["stages"]:
            if stage["stage_id"] in {"store-raw", "store-products"}:
                stage["handler"]["package_id"] = package
                stage["connections"]["target"] = connection
        # Collector input, extractor and its digest, images, bindings, and every other field stay fixed.
        for old, new in zip(before["stages"], task["stages"], strict=True):
            if old["stage_id"] in {"store-raw", "store-products"}:
                old["handler"]["package_id"] = package
                old["connections"]["target"] = connection
            assert old == new
        updated = orch.put(f"/v1/tasks/{task_id}", json=task, headers={"If-Match": current.headers["etag"]})
        assert updated.status_code == 200, updated.text
        run = wait_run(orchestrated, start_run(orchestrated, task_id))
        assert run["status"] == "succeeded", (kind, run)
        assert run["task_etag"] == updated.headers["etag"]
        objects = objects_by_source(storage, connection, source_id)
        states = entities(storage, connection, source_id)
        assert len(objects) == len(states) == 1, (kind, objects, states)
        obj, state = objects[0]["object"], states[0]
        assert state["fields"]["sku"] == "phone-alpha"
        assert state["version"] == 1
        assert len(history(storage, connection, state["canonical_key"])) == 1
        content = storage.api("storage").get(
            f"/v1/objects/{obj['object_id']}/content", params={"connection_id": connection}
        )
        assert content.status_code == 200, content.text
        assert hashlib.sha256(content.content).hexdigest() == obj["sha256"]
        _assert_native(stack, kind, obj, state, content.content)
        _redeliver(stack, storage, collector, runtime, kind, package, connection, run_id)
