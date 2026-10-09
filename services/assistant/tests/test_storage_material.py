"""``StorageClient.material`` against every answer ``storage.v1`` allows (coordinator item of WP-15).

A RAW stored with ``format.raw = json`` is the Material document itself. Older storage returned ``getObject`` with
the content by reference (or inlined the whole document) and the client took the object bytes - the JSON
document - as the original content, labelled with the original media type. Newer storage inlines the original
content in ``material.content`` and leaves ``material`` out when it is over its inline limit. The client must
give the original content in all these cases. The storage neighbour is the contract-bound fake.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
from typing import Any

import httpx
import pytest
from assistant_fakes import World
from assistant_fakes.runtime import PRODUCT_CODE_V1
from assistant_fakes.site import material, product

from jane_assistant.clients import StorageClient
from jane_assistant.content import material_bytes
from jane_assistant.packages import extractor_draft
from jane_kit.clients import ServiceClient
from jane_kit.errors import JaneError

URL = "https://shop.example.test/product/c-300"
HTML = product("C-300", "Kettle C-300", "899", price_class="price-new")


def _json_raw(mat: dict[str, Any]) -> bytes:
    """What storage writes for ``format.raw = json`` (``jane_storage.formats.build_raw_object``)."""
    doc = json.loads(json.dumps(mat))
    doc["content"] = {"kind": "inline", "media_type": "text/html", "encoding": "utf-8", "data": HTML}
    return json.dumps(doc, ensure_ascii=False, sort_keys=True, indent=2).encode()


def _meta(mat: dict[str, Any], content: dict[str, Any]) -> dict[str, Any]:
    return {**mat, "content": content}


def _read(w: World, object_id: str) -> dict[str, Any]:
    async def run() -> dict[str, Any]:
        client = StorageClient(
            ServiceClient("http://storage.test", transport=httpx.ASGITransport(app=w.storage.app))
        )
        try:
            return await client.material("raw-files", object_id)
        finally:
            await client.aclose()

    return asyncio.run(run())


def _original(mat: dict[str, Any]) -> None:
    content = mat["content"]
    assert content["kind"] == "inline" and content["media_type"] == "text/html"
    assert asyncio.run(material_bytes(mat)) == HTML.encode()  # sha256 and size checked by the reader
    assert '"material_id"' not in content["data"]


@pytest.fixture
def mat() -> dict[str, Any]:
    return material(URL, HTML, "shop-example")


def test_html_raw_file_reference_reads_the_object_bytes(w: World, mat: dict[str, Any]) -> None:
    w.storage.put("obj_html", mat)
    got = _read(w, "obj_html")
    _original(got)
    assert got["material_id"] == mat["material_id"]
    assert len(w.storage.app.called("getObjectContent")) == 1


def test_inline_original_content_is_taken_as_is(w: World, mat: dict[str, Any]) -> None:
    """Newer storage: ``material.content`` is the original content inline - no second request."""
    data = HTML.encode()
    inline = {
        "kind": "inline",
        "media_type": "text/html",
        "encoding": "base64",
        "data": base64.b64encode(data).decode(),
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }
    w.storage.put_object("obj_new", _meta(mat, inline), _json_raw(mat), "application/json")
    _original(_read(w, "obj_new"))
    assert w.storage.app.called("getObjectContent") == []


def test_json_raw_without_material_is_read_from_the_stored_document(w: World, mat: dict[str, Any]) -> None:
    """Newer storage, content over its inline limit: no ``material`` - the stored document is the Material."""
    w.storage.put_object("obj_big", None, _json_raw(mat), "application/json")
    got = _read(w, "obj_big")
    _original(got)
    assert got["material_id"] == mat["material_id"] and got["observation_id"] == mat["observation_id"]


@pytest.mark.parametrize("old", ["blob-reference", "inline-document"])
def test_older_storage_json_raw_gives_the_original_not_the_wrapper(
    w: World, mat: dict[str, Any], old: str
) -> None:
    """The defect: the JSON document used to come back as the content, labelled ``text/html``."""
    stored = _json_raw(mat)
    if old == "blob-reference":
        ref = {
            "kind": "blob",
            "uri": "file:///var/lib/jane/raw/obj_old.json",
            "media_type": "application/json",
            "size_bytes": len(stored),
            "sha256": hashlib.sha256(stored).hexdigest(),
            "store": "persistent",
            "expires_at": None,
        }
    else:
        ref = {
            "kind": "inline",
            "media_type": "application/json",
            "encoding": "utf-8",
            "data": stored.decode(),
            "size_bytes": len(stored),
            "sha256": hashlib.sha256(stored).hexdigest(),
        }
    w.storage.put_object("obj_old", _meta(mat, ref), stored, "application/json")
    _original(_read(w, "obj_old"))


def test_object_without_material_and_not_a_material_document_is_a_clear_error(w: World) -> None:
    w.storage.put_object("obj_plain", None, HTML.encode(), "text/html")
    with pytest.raises(JaneError) as exc:
        _read(w, "obj_plain")
    assert exc.value.error_code == "not_implemented"  # not a misleading validation_failed
    assert "pass the sample inline" in (exc.value.detail or "")


def test_improvement_sees_the_original_content_of_a_json_raw_sample(w: World, mat: dict[str, Any]) -> None:
    """End to end: a problem sample by ``material_ref`` to a json RAW without ``material`` reaches the model as
    the page itself (before: the stored JSON document)."""
    draft = extractor_draft(
        package_id="catalog.product-extractor",
        version="1.2.0",
        title="Product cards",
        entity_type="product",
        key_fields=["sku"],
        entity_schema={"type": "object", "properties": {"sku": {"type": "string"}}},
        module_code=PRODUCT_CODE_V1,
        domains=["shop.example.test"],
        source_kind="web",
        media_types=["text/html"],
        job_id="seed",
        model={},
        reason="onboarding",
    )
    draft.manifest["provenance"] = {"created_by": "human"}
    w.registry.seed(draft.manifest, draft.files)
    w.storage.put_object("obj_c300", None, _json_raw(mat), "application/json")
    body = {
        "package": {"package_id": "catalog.product-extractor", "version": "1.2.0"},
        "problem_samples": [
            {"material_ref": {"storage_connection_id": "raw-files", "object_id": "obj_c300"}}
        ],
        "limits": {"max_improvement_attempts": 1},
    }
    r = w.api.post("/v1/improvement-runs", json=body, headers={"Idempotency-Key": "json-raw-1"})
    assert w.wait(r.json()["job_id"])["status"] == "succeeded"
    improve = next(q for q in w.llm.requests if q["output_schema"]["title"].endswith(".improve_extractor.v1"))
    sample = next(p for p in improve["data"] if p["name"] == "problem_p1")
    assert sample["text"] == HTML and sample["media_type"] == "text/html"
