"""Fixtures: the registry app on two backends.

* ``memory`` - in-process metadata store + filesystem blobs in ``tmp_path`` (unit tier, no services);
* ``real`` - PostgreSQL + MinIO of the dev stack (``@pytest.mark.integration``): its own database
  ``jane_registry_test_<hex>`` per session, its own schema per test, its own bucket per session.
  Start with ``just up --project jane-wp05 postgres minio`` and run
  ``just integration --project jane-wp05 services/registry``.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from jane_kit.devstack import StackInfo, load_stack
from jane_registry.app import build_app
from jane_registry.settings import Settings
from jane_registry.testing import TEST_PROFILE


@pytest.fixture
def profile_file(tmp_path: Path) -> Path:
    path = tmp_path / "python-extractor-1.json"
    path.write_text(json.dumps(TEST_PROFILE), encoding="utf-8")
    return path


@dataclass
class RealBackend:
    stack: StackInfo
    dsn: str
    bucket: str

    def settings(self, schema: str, **extra: Any) -> Settings:
        minio = self.stack.services["minio"]
        values: dict[str, Any] = {
            "log_format": "console",
            "db": "postgres",
            "db_url": self.dsn,
            "db_schema": schema,
            "blob": "s3",
            "blob_bucket": self.bucket,
            "s3_endpoint_url": minio["endpoint"],
            "s3_access_key": minio["access_key"],
            "s3_secret_key": minio["secret_key"],
            **extra,
        }
        return Settings(**values)


@pytest.fixture(scope="session")
def real_backend() -> Iterator[RealBackend]:
    stack = load_stack()
    if stack is None or not {"postgres", "minio"} <= set(stack.services):
        pytest.skip("dev stack with postgres and minio is not running (just up postgres minio)")
    import boto3  # type: ignore[import-untyped]
    import psycopg

    pg = stack.services["postgres"]
    database = f"jane_registry_test_{uuid.uuid4().hex[:8]}"
    with psycopg.connect(pg["dsn"], autocommit=True) as admin:
        admin.execute(f'CREATE DATABASE "{database}"')
    dsn = f"postgresql://{pg['user']}:{pg['password']}@{pg['host']}:{pg['port']}/{database}"
    bucket = f"jane-registry-test-{uuid.uuid4().hex[:8]}"
    backend = RealBackend(stack, dsn, bucket)
    try:
        yield backend
    finally:
        minio = stack.services["minio"]
        s3 = boto3.client(
            "s3",
            endpoint_url=minio["endpoint"],
            aws_access_key_id=minio["access_key"],
            aws_secret_access_key=minio["secret_key"],
            region_name="us-east-1",
        )
        try:
            for obj in s3.list_objects_v2(Bucket=bucket).get("Contents", []):
                s3.delete_object(Bucket=bucket, Key=obj["Key"])
            s3.delete_bucket(Bucket=bucket)
        except Exception:
            pass
        with psycopg.connect(pg["dsn"], autocommit=True) as admin:
            admin.execute(f'DROP DATABASE IF EXISTS "{database}" WITH (FORCE)')


@dataclass
class Backend:
    name: str
    make_settings: Any

    def settings(self, **extra: Any) -> Settings:
        settings: Settings = self.make_settings(**extra)
        return settings

    def client(self, **extra: Any) -> TestClient:
        return TestClient(build_app(self.settings(**extra)))


@pytest.fixture(params=["memory", pytest.param("real", marks=pytest.mark.integration)])
def backend(request: pytest.FixtureRequest, tmp_path: Path, profile_file: Path) -> Backend:
    common = {"runtime_profiles": [str(profile_file)], "log_format": "console"}
    if request.param == "memory":

        def make(**extra: Any) -> Settings:
            return Settings(
                db="memory", blob="filesystem", blob_root=tmp_path / "blobs", **{**common, **extra}
            )

        return Backend("memory", make)
    real: RealBackend = request.getfixturevalue("real_backend")
    schema = f"t_{uuid.uuid4().hex[:12]}"

    def make_real(**extra: Any) -> Settings:
        return real.settings(schema, **{**common, **extra})

    return Backend("real", make_real)


@pytest.fixture
def client(backend: Backend) -> Iterator[TestClient]:
    with backend.client() as c:
        yield c


def unique(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def uid() -> Any:
    return unique
