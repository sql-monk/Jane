"""SQL Server adapter: registration and connection validation (no services needed, runs in `just check`)."""

from __future__ import annotations

from typing import Any

import pytest

from jane_contracts.storage_adapter import AdapterError, ResolvedConnection
from jane_storage.adapters import adapter_class, create_adapter, package_dirs
from jane_storage.packages import load_package
from jane_storage_sqlserver import SqlServerAdapter, _error_number


def test_registered_with_its_package() -> None:
    assert adapter_class("sqlserver") is SqlServerAdapter
    pkg = load_package(package_dirs()["jane.storage-sqlserver"])
    assert pkg.adapter == "sqlserver"
    assert pkg.writes == "raw_and_entities"


@pytest.mark.parametrize(
    ("params", "options"),
    [
        ({}, {}),  # no database
        ({"database": "jane"}, {"schema": "Bad-Schema"}),
        ({"database": "jane"}, {"table_prefix": "x;drop"}),
        ({"database": "jane; drop"}, {}),
    ],
)
async def test_invalid_connection_is_not_retryable(params: dict[str, Any], options: dict[str, Any]) -> None:
    with pytest.raises(AdapterError) as err:
        await create_adapter("sqlserver").open(ResolvedConnection("s", "sqlserver", params), options)
    assert err.value.retryable is False


async def test_lazy_pool_when_min_size_is_zero() -> None:
    adapter = SqlServerAdapter()
    await adapter.open(
        ResolvedConnection(
            "s", "sqlserver", {"host": "mssql.invalid", "database": "jane", "schema": "stage"}
        ),
        {"pool_min_size": 0, "table_prefix": "raw_"},
    )
    try:
        assert adapter._t("entities") == "[stage].[raw_entities]"
    finally:
        await adapter.close()


def test_error_numbers_of_both_driver_shapes() -> None:
    assert _error_number(Exception((20009, b"unable to connect"))) == 20009
    assert _error_number(Exception(18456, b"Login failed")) == 18456
    assert _error_number(Exception("text")) is None
