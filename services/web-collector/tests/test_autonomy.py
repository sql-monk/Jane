"""WP-02 «Готово, коли»: the API works without the orchestrator.

The collector runs as its own process with only its state directory; a "third-party application" uses
plain HTTP (httpx) — no orchestrator, extractor, storage or registry is running. Rules come inline or from
a local package directory (``JANE_WEB_COLLECTOR_RULES_DIR``).
"""

from __future__ import annotations

import json
from pathlib import Path

import httpx
from jsonschema import Draft202012Validator

from jane_kit.contracts import OpenAPISpec
from jane_web_collector.testing import FAST_LIMITS, Site, drain, start, wait_done, web_rules

from .conftest import REPO_ROOT, ServiceFactory

SPEC = OpenAPISpec.load(REPO_ROOT / "contracts" / "openapi" / "collector.v1.yaml")
MATERIAL = (REPO_ROOT / "contracts" / "schemas" / "material.schema.json").resolve().as_uri()


def _valid_material(material: dict[str, object]) -> None:
    errors = list(Draft202012Validator({"$ref": MATERIAL}, registry=SPEC.registry).iter_errors(material))
    assert errors == [], [e.message for e in errors]


def _local_package(root: Path, site: Site) -> dict[str, str]:
    ref = {"package_id": "testsite.web-rules", "version": "1.0.0"}
    folder = root / ref["package_id"] / ref["version"]
    folder.mkdir(parents=True)
    manifest = {
        "schema_version": "1",
        "package_id": ref["package_id"],
        "version": ref["version"],
        "kind": "collector-rules",
        "title": "testsite rules",
        "entry": {"collector": "web", "rules": "rules.json"},
        "tests": [],
        "provenance": {"created_by": "human"},
    }
    (folder / "jane-package.json").write_text(json.dumps(manifest), encoding="utf-8")
    (folder / "rules.json").write_text(json.dumps(web_rules(site)), encoding="utf-8")
    return ref


def test_third_party_app_uses_collector_without_orchestrator(
    service_factory: ServiceFactory, site: Site, tmp_path: Path, expected_sets: dict[str, set[str]]
) -> None:
    ref = _local_package(tmp_path / "rules", site)
    svc = service_factory(JANE_WEB_COLLECTOR_RULES_DIR=str(tmp_path / "rules"))
    svc.start()
    with httpx.Client(base_url=svc.base, timeout=10) as api:
        assert api.get("/v1/health").json()["status"] == "ok"
        info = api.get("/v1/info").json()
        assert info["service"] == "web-collector"
        assert {"seed_list", "recursive"} <= set(info["capabilities"]["strategies"])
        assert info["capabilities"]["unsupported_strategies"] == ["llm_explore"]

        # rules check without running anything
        check = api.post("/v1/rules/validations", json=web_rules(site)).json()
        assert check["valid"] is True and check["supported"] is True

        # one synchronous fetch
        r = api.post("/v1/fetches", json={"source_kind": "web", "url": site.url("/product/phone-alpha")})
        assert r.status_code == 200, r.text
        _valid_material(r.json())
        assert r.json()["locator"]["canonical_url"] == site.url("/product/phone-alpha")

        # a full crawl with rules from the local package (autonomous mode, no registry)
        cid = start(
            api, {"source_kind": "web", "source_id": "testsite", "rules_ref": ref, "limits": FAST_LIMITS}
        )
        materials = drain(api, cid)
        view = wait_done(api, cid)
    assert view["status"] == "succeeded"
    assert view["rules"] == ref
    for m in materials:
        _valid_material(m)
        assert m["collector"]["rules"] == ref
    assert {m["locator"]["canonical_url"] for m in materials} == site.canonical(expected_sets["recursive"])
    # nothing but the collector's own state directory was used
    assert (svc.state_dir / "state.db").is_file()


def test_fetch_respects_robots_without_rules(service_factory: ServiceFactory, site: Site) -> None:
    svc = service_factory()
    svc.start()
    with httpx.Client(base_url=svc.base, timeout=10) as api:
        r = api.post("/v1/fetches", json={"source_kind": "web", "url": site.url("/private/admin")})
        assert r.status_code == 403
        assert r.json()["code"] == "access_denied_by_policy"
        r = api.post("/v1/fetches", json={"source_kind": "web", "url": site.url("/missing-page")})
        assert r.status_code == 502
        assert r.json()["code"] == "source_unavailable"
        assert r.json()["details"]["http_status"] == 404
    assert site.requests["/private/admin"] == 0
