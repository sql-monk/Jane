from __future__ import annotations

import importlib
import sys
from pathlib import Path

import httpx
import pytest

from jane_kit.codegen import generate_client
from jane_kit.contracts import OpenAPISpec, build_mock_app

pytestmark = pytest.mark.contract

DATA = Path(__file__).parent / "data"


async def test_generated_client_talks_to_contract_mock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = generate_client(DATA / "openapi.yaml", tmp_path / "sample_client")
    assert (out / "models.py").is_file()
    source = (out / "client.py").read_text(encoding="utf-8")
    assert "async def create_item(self, *, body: Any = None, idempotency_key: str | None = None)" in source
    assert "async def get_item(self, item_id: str) -> models.Item:" in source

    monkeypatch.syspath_prepend(str(tmp_path))
    sys.modules.pop("sample_client", None)
    pkg = importlib.import_module("sample_client")
    mock = build_mock_app(OpenAPISpec.load(DATA / "openapi.yaml"))
    async with pkg.SampleServiceClient("http://mock", transport=httpx.ASGITransport(app=mock)) as client:
        item = await client.get_item("i-1")
        assert isinstance(item, pkg.models.Item)
        assert item.tags == ["a"]
        created = await client.create_item(body={"name": "n"}, idempotency_key="k")
        assert created.id == "i-1"
        listing = await client.list_items(limit=5)
        assert listing["items"][0]["name"] == "string"
