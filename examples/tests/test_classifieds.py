"""Контракти конфігурації й незалежна звірка сутностей із RAW оголошень."""

from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path
from typing import Any

import httpx
import pytest
from classifieds import setup_classifieds as setup

import jane_examples as ex
from jane_kit.contracts import ContractClient

CONFIG = setup.load_sites()
SITES = list(CONFIG["sites"])


def references() -> dict[str, Any]:
    ids = {"jane.storage-files", "jane.storage-postgresql"}
    ids.update(entry[kind] for entry in CONFIG["sites"].values() for kind in ("extractor", "rules"))
    return {pid: {"package_id": pid, "version": "1.0.0", "digest": "sha256:" + "1" * 64} for pid in ids}


@pytest.mark.parametrize("site", SITES)
def test_source_and_task_match_contract_and_preserve_raw_branch(site: str) -> None:
    source = setup.source_doc(site, CONFIG, references())
    task = setup.task_doc(site, CONFIG, references())
    assert ex.validate("source.schema.json", source) == []
    assert ex.validate("task-config.schema.json", task) == []
    assert source["expected_entity_types"] == ["classified_ad"]
    stages = {stage["stage_id"]: stage for stage in task["stages"]}
    assert stages["store-raw"]["inputs"] == [{"from": "collect"}]
    assert stages["store-raw"]["connections"] == {"target": "raw-files"}
    assert stages["store-ads"]["connections"] == {"target": "results-pg"}
    assert stages["store-ads"]["inputs"][0]["when"]["value"] == "success"
    assert task["limits"]["crawl"]["max_pages_per_run"] > 0
    assert task["schedule"]["overlap"] == "skip"


def test_disabled_site_stays_disabled_and_replacement_is_explicit() -> None:
    disabled = copy.deepcopy(CONFIG)
    disabled["sites"]["olx"]["enabled"] = False
    assert setup.task_doc("olx", disabled, references())["enabled"] is False
    assert CONFIG["sites"]["shafa"]["replaces"] == "izi"
    assert "izi" not in CONFIG["sites"]


def test_real_package_fixtures_and_schemas() -> None:
    assert setup.check_packages(CONFIG, SITES) == []


def fields() -> dict[str, Any]:
    return {
        "site": "shafa",
        "listing_id": "123",
        "title": "Синя куртка",
        "url": "https://shafa.ua/uk/123-jacket",
        "price": {"amount": 1200, "currency": "UAH"},
    }


def test_raw_card_checks_relative_url_title_and_associated_price() -> None:
    raw = '<article><a href="/uk/123-jacket">Синя куртка</a><p>1 200 грн</p></article>'.encode()
    assert setup.raw_field_check(fields(), raw, "https://shafa.ua/uk/")["verified"]


@pytest.mark.parametrize("change", ["title", "url", "price"])
def test_raw_verification_rejects_unsupported_fields(change: str) -> None:
    entity = copy.deepcopy(fields())
    if change == "price":
        entity["price"]["amount"] = 999
    else:
        entity[change] = "https://shafa.ua/uk/124-other" if change == "url" else "Червона куртка"
    raw = '<article><a href="/uk/123-jacket">Синя куртка</a><p>1 200 грн</p></article>'.encode()
    assert not setup.raw_field_check(entity, raw, "https://shafa.ua/uk/")["verified"]


def test_raw_verification_rejects_price_from_unrelated_listing() -> None:
    raw = (
        '<body><article><a href="/uk/123-jacket">Синя куртка</a><p>999 грн</p></article>'
        '<article><a href="/uk/124-other">Інша куртка</a><p>1 200 грн</p></article></body>'
    ).encode()
    assert not setup.raw_field_check(fields(), raw, "https://shafa.ua/uk/")["verified"]


def test_pinia_state_checks_identity_and_currency_map_independently() -> None:
    raw = (
        '<script>window.__PINIA__ = {"list":{"items":[{"id":123,"link":"https://shafa.ua/uk/123-jacket",'
        '"title":{"content":"Синя куртка"},"price":{"UAH":1200,"USD":30}}]}};</script>'
    ).encode()
    result = setup.raw_field_check(fields(), raw, "https://shafa.ua/uk/")
    assert result["verified"]
    assert result["evidence_kind"] == "json"


def test_job_timeout_and_poll_arguments_are_positive() -> None:
    with pytest.raises(SystemExit):
        setup.main(["check", "--timeout", "0"])


def test_package_discovery_stays_inside_classifieds() -> None:
    directories = setup.local_packages(CONFIG, SITES)
    assert len(directories) == len(SITES) * 2
    assert all(directory.parent == Path(setup.HERE) / "packages" for directory in directories.values())


@pytest.mark.parametrize("site", SITES)
def test_independent_checker_corroborates_every_real_expected_field(site: str) -> None:
    directory = setup.HERE / "packages" / CONFIG["sites"][site]["extractor"]
    manifest = ex.read_json(directory / "jane-package.json")
    for case in manifest["tests"]:
        if case["expected_status"] != "success":
            continue
        raw = (directory / case["input"]["file"]).read_bytes()
        expected = ex.read_json(directory / case["expected"])
        for entity in expected["entities"]:
            check = setup.raw_field_check(entity["fields"], raw, case["input"]["url"])
            assert check["verified"], (site, entity["fields"], check)
            assert set(check["checked_fields"]) == set(entity["fields"])


@pytest.mark.parametrize(
    ("field", "value"), [("site", "invented-site"), ("location", "InventedCity"), ("unsupported", "anything")]
)
def test_raw_verification_rejects_wrong_site_location_or_unknown_output(field: str, value: str) -> None:
    entity = copy.deepcopy(fields())
    entity[field] = value
    raw = '<article><a href="/uk/123-jacket">Синя куртка</a><p>1200 UAH</p><p>Kyiv</p></article>'.encode()
    assert not setup.raw_field_check(entity, raw, "https://shafa.ua/uk/")["verified"]


def test_json_currency_belongs_to_reported_price_not_other_currency_field() -> None:
    raw = (
        '<script>{"id":123,"url":"https://shafa.ua/uk/123-jacket","title":"Синя куртка",'
        '"price":1200,"currency":"USD","otherCurrency":"UAH"}</script>'
    ).encode()
    assert not setup.raw_field_check(fields(), raw, "https://shafa.ua/uk/")["verified"]


def test_currency_map_rejects_amount_of_different_currency() -> None:
    raw = (
        '<script>{"id":123,"url":"https://shafa.ua/uk/123-jacket","title":"Синя куртка",'
        '"price":{"USD":1200,"UAH":48000}}</script>'
    ).encode()
    assert not setup.raw_field_check(fields(), raw, "https://shafa.ua/uk/")["verified"]


@pytest.mark.parametrize("currency", [{"currency_type": "$"}, {"currencyId": 1}])
def test_dim_price_currency_mapping_is_bound_to_same_ad(currency: dict[str, Any]) -> None:
    entity = copy.deepcopy(fields())
    entity.update({"site": "dom.ria.com", "url": "https://dom.ria.com/uk/123-jacket", "location": "Київ"})
    record = {
        "realty_id": 123,
        "beautiful_url": "123-jacket",
        "imgSeoALT": "Синя куртка",
        "price": 1200,
        "city_name_uk": "Київ",
        **currency,
    }
    raw = (
        "<script>window.__INITIAL_STATE__=" + json.dumps(record, ensure_ascii=False) + ";</script>"
    ).encode()
    assert not setup.raw_field_check(entity, raw, "https://dom.ria.com/uk/")["verified"]
    entity["price"]["currency"] = "USD"
    assert setup.raw_field_check(entity, raw, "https://dom.ria.com/uk/")["verified"]


def test_location_from_other_json_ad_cannot_corroborate_this_ad() -> None:
    entity = copy.deepcopy(fields())
    entity.update({"site": "dom.ria.com", "url": "https://dom.ria.com/uk/123-jacket", "location": "Львів"})
    document = {
        "ads": [
            {
                "realty_id": 123,
                "beautiful_url": "123-jacket",
                "imgSeoALT": "Синя куртка",
                "price": 1200,
                "currency_type": "грн",
                "city_name_uk": "Київ",
            },
            {"realty_id": 124, "city_name_uk": "Львів"},
        ]
    }
    raw = ("<script>" + json.dumps(document, ensure_ascii=False) + "</script>").encode()
    assert not setup.raw_field_check(entity, raw, "https://dom.ria.com/uk/")["verified"]


def test_location_from_other_dom_card_is_rejected() -> None:
    entity = copy.deepcopy(fields())
    entity.update({"site": "ria.com", "url": "https://www.ria.com/uk/123-jacket", "location": "Львів"})
    raw = (
        '<div><div id="adv_123"><a href="/uk/123-jacket">Синя куртка</a><span>1200 грн</span><div class="address js-state-city">Київ</div></div>'
        '<div id="adv_124"><a href="/uk/124-other">Інша куртка</a><div class="address js-state-city">Львів</div></div></div>'
    ).encode()
    assert not setup.raw_field_check(entity, raw, "https://www.ria.com/uk/")["verified"]


def ria_fields() -> dict[str, Any]:
    return {
        "site": "ria.com",
        "listing_id": "239975708",
        "title": "Мобільний телефон Unihertz Tank Mini 1 8/256gb Black",
        "url": "https://www.ria.com/uk/mobylnyy-telefon-unihertz-tank-mini-1-8-239975708.html",
        "location": "Київ",
        "price": {"amount": 13039, "currency": "UAH"},
    }


def ria_card(description: str, monetary_slot: str) -> bytes:
    entity = ria_fields()
    return (
        f'<div class="ticket-clean" id="adv_{entity["listing_id"]}">'
        f'<a class="ticket-title" href="{entity["url"]}">{entity["title"]}</a>'
        f'<div class="descriptions-ticket">{description}</div>'
        f'<span class="price js-price green">{monetary_slot}</span>'
        '<div class="address js-state-city">Київ</div></div>'
    ).encode()


def test_ria_price_slot_does_not_merge_numeric_model_with_grouped_amount() -> None:
    # The live card ended its description with "13" just before the grouped price;
    # flattening the whole card had incorrectly treated "13 13 039 грн" as 1313039 UAH.
    raw = ria_card("Модель 13", '<strong class="size22">13 039</strong><span>грн</span>')
    check = setup.raw_field_check(ria_fields(), raw, "https://www.ria.com/uk/c/mobile/")
    assert check["verified"]
    assert set(check["checked_fields"]) == set(ria_fields())


@pytest.mark.parametrize("change", ["title", "url", "location", "amount", "currency"])
def test_ria_structural_price_verification_preserves_other_field_checks(change: str) -> None:
    entity = ria_fields()
    raw = ria_card("Модель 13", '<strong class="size22">13 039</strong><span>грн</span>')
    if change == "amount":
        entity["price"]["amount"] = 999
    elif change == "currency":
        entity["price"]["currency"] = "USD"
    elif change == "url":
        entity["url"] = "https://www.ria.com/uk/different-239975708.html"
    else:
        entity[change] = "Інше значення"
    assert not setup.raw_field_check(entity, raw, "https://www.ria.com/uk/c/mobile/")["verified"]


@pytest.mark.parametrize(
    "monetary_slot", ["<strong>999</strong><span>грн</span>", "<strong>13 039</strong><span>USD</span>"]
)
def test_ria_description_price_cannot_override_own_monetary_slot(monetary_slot: str) -> None:
    raw = ria_card("Попередня ціна 13 039 грн", monetary_slot)
    assert not setup.raw_field_check(ria_fields(), raw, "https://www.ria.com/uk/c/mobile/")["verified"]


def test_ria_price_slot_from_another_card_cannot_corroborate_own_price() -> None:
    raw = ria_card("Модель 13", "<strong>999</strong><span>грн</span>")
    raw += (
        '<div class="ticket-clean" id="adv_238060287">'
        '<a href="/uk/other-238060287.html">Інший телефон</a>'
        '<span class="price js-price">13 039 грн</span></div>'
    ).encode()
    assert not setup.raw_field_check(ria_fields(), raw, "https://www.ria.com/uk/c/mobile/")["verified"]


def test_olx_numeric_dom_id_and_timestamp_location_are_corroborated() -> None:
    entity = {
        "site": "olx",
        "listing_id": "12345",
        "title": "Синя куртка",
        "url": "https://www.olx.ua/uk/d/obyavlenie/jacket-IDabcde.html",
        "location": "Київ",
        "price": {"amount": 1200, "currency": "UAH"},
    }
    raw = (
        '<div data-testid="l-card" id="12345"><a href="/uk/d/obyavlenie/jacket-IDabcde.html" aria-label="Синя куртка">Синя куртка</a>'
        '<p data-testid="ad-price">1200 грн</p><p data-testid="location-date">Київ - Сьогодні о 14:00</p></div>'
    ).encode()
    assert setup.raw_field_check(entity, raw, "https://www.olx.ua/uk/")["verified"]
    entity["location"] = "Львів"
    assert not setup.raw_field_check(entity, raw, "https://www.olx.ua/uk/")["verified"]


def test_polling_retries_get_transport_failure_and_preserves_job() -> None:
    requests: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if len(requests) == 1:
            raise httpx.ReadError("Disconnected", request=request)
        return httpx.Response(
            200,
            json={
                "job_id": "testjob",
                "kind": "test_run",
                "status": "succeeded",
                "created_at": "2026-10-11T00:00:00Z",
            },
        )

    api = ex.Api("http://test.invalid", "handler")
    api.http.close()
    api.http = httpx.Client(base_url="http://test.invalid", transport=httpx.MockTransport(respond))
    api.client = ContractClient(ex.spec("handler"), api.http)
    try:
        assert setup.wait_job(api, "/v1/jobs/testjob", 1, 0.001)["status"] == "succeeded"
        assert len(requests) == 2
        assert all(request.method == "GET" for request in requests)
    finally:
        api.close()


def test_polling_transport_failures_end_at_overall_timeout() -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Unavailable", request=request)

    api = ex.Api("http://test.invalid", "handler")
    api.http.close()
    api.http = httpx.Client(base_url="http://test.invalid", transport=httpx.MockTransport(respond))
    api.client = ContractClient(ex.spec("handler"), api.http)
    try:
        with pytest.raises(TimeoutError, match="ConnectError"):
            setup.wait_job(api, "/v1/jobs/testjob", 0.01, 0.001)
    finally:
        api.close()


def saved_services() -> dict[str, Any]:
    return {
        "services": {
            name: {"url": f"http://127.0.0.1:{port}"}
            for name, port in (
                ("registry", 50001),
                ("orchestrator", 50002),
                ("storage", 50003),
                ("handler-runtime", 50004),
            )
        },
        "env": {"JANE_API_KEY_ADMIN": "fake-test-key"},
    }


def test_docker_mapping_ignores_stale_snapshot_and_is_fresh_on_every_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stack = saved_services()
    original = copy.deepcopy(stack)
    services = {str(index) * 12: name for index, name in enumerate(stack["services"], start=1)}
    inspection_count = 0

    def run(args: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        nonlocal inspection_count
        assert args[0] == "docker"
        assert kwargs.get("shell", False) is False
        if args[1] == "ps":
            assert "label=com.docker.compose.project=jane-demo" in args
            output = "\n".join(f"{identifier} {name}" for identifier, name in services.items())
            output += "\nffffffffffff other-service\n"
        else:
            assert args[1] == "inspect"
            assert set(args[4:]) == set(services)
            assert "Environment" not in args[3] and ".Config.Env" not in args[3]
            inspection_count += 1
            output = "\n".join(
                f"{identifier} jane-demo {name} "
                + json.dumps(
                    {
                        "8000/tcp": [
                            {"HostIp": "127.0.0.1", "HostPort": str(58000 + inspection_count * 10 + index)}
                        ]
                    }
                )
                for index, (identifier, name) in enumerate(services.items())
            )
        return subprocess.CompletedProcess(args, 0, stdout=output, stderr="")

    monkeypatch.setattr(subprocess, "run", run)
    first = setup.service_urls("jane-demo", stack)
    second = setup.service_urls("jane-demo", stack)
    assert first["registry"] == "http://127.0.0.1:58010"
    assert second["registry"] == "http://127.0.0.1:58020"
    assert all(first[name] != info["url"] for name, info in stack["services"].items())
    assert stack == original


def test_unavailable_docker_requires_explicit_snapshot_option(monkeypatch: pytest.MonkeyPatch) -> None:
    def unavailable(args: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        raise FileNotFoundError("Docker is unavailable")

    monkeypatch.setattr(subprocess, "run", unavailable)
    stack = saved_services()
    with pytest.raises(RuntimeError, match="saved URLs were not used"):
        setup.service_urls("jane-demo", stack)
    urls = setup.service_urls("jane-demo", stack, use_snapshot=True)
    assert urls == {name: info["url"] for name, info in stack["services"].items()}


@pytest.mark.parametrize(
    "problem", ["wrong-project", "missing-published-runtime", "duplicate-published-runtime"]
)
def test_service_mapping_rejects_unscoped_or_ambiguous_containers(
    monkeypatch: pytest.MonkeyPatch, problem: str
) -> None:
    services = {str(index) * 12: name for index, name in enumerate(saved_services()["services"], start=1)}
    if problem == "duplicate-published-runtime":
        services["555555555555"] = "handler-runtime"

    def run(args: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        if args[1] == "ps":
            output = "\n".join(f"{identifier} {name}" for identifier, name in services.items())
        else:
            project = "other-project" if problem == "wrong-project" else "jane-demo"
            output = "\n".join(
                f"{identifier} {project} {name} "
                + json.dumps(
                    {
                        "8000/tcp": None
                        if problem == "missing-published-runtime" and name == "handler-runtime"
                        else [{"HostIp": "127.0.0.1", "HostPort": str(58000 + index)}]
                    }
                )
                for index, (identifier, name) in enumerate(services.items())
            )
        return subprocess.CompletedProcess(args, 0, stdout=output, stderr="")

    monkeypatch.setattr(subprocess, "run", run)
    with pytest.raises(
        RuntimeError, match=r"outside the selected Compose project|expected one running published API"
    ):
        setup.service_urls("jane-demo", saved_services())


def runtime_report(ref: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "package": ref,
        "passed": len(manifest["tests"]),
        "failed": 0,
        "cases": [
            {
                "name": case["name"],
                "passed": True,
                "actual_status": case["expected_status"],
                "result": {
                    "invocation_id": f"test_{index}",
                    "handler": ref,
                    "handler_kind": "extractor",
                    "status": case["expected_status"],
                    "inputs": [],
                    "started_at": "2026-10-11T00:00:00Z",
                    "finished_at": "2026-10-11T00:00:01Z",
                },
            }
            for index, case in enumerate(manifest["tests"])
        ],
    }


def deployment_neighbors() -> tuple[ex.Services, ex.Api, dict[str, Any]]:
    """Service neighbors expose contract-validated HTTP responses; setup functions themselves run unchanged."""
    from jane_registry.archive import canonical_archive, digest_of, files_from_dir

    manifests, archives, versions = {}, {}, {}
    for pid, directory in setup.local_packages(CONFIG, ["shafa"]).items():
        manifest = ex.read_json(directory / "jane-package.json")
        archive = bytes(canonical_archive(files_from_dir(directory)))
        ref = {"package_id": pid, "version": manifest["version"], "digest": str(digest_of(archive))}
        manifests[pid], archives[pid] = manifest, archive
        versions[pid] = {
            **ref,
            "status": "approved",
            "test_status": "passed",
            "created_at": "2026-10-11T00:00:00Z",
        }
        if manifest["kind"] == "extractor":
            versions[pid]["test_reports"] = [
                {"runner": "handler-runtime", "context": "tests", "report": runtime_report(ref, manifest)}
            ]
    for pid in ("jane.storage-files", "jane.storage-postgresql"):
        versions[pid] = {
            "package_id": pid,
            "version": "1.0.0",
            "digest": "sha256:" + "1" * 64,
            "status": "approved",
            "test_status": "passed",
            "created_at": "2026-10-11T00:00:00Z",
        }
    state: dict[str, Any] = {
        "failure": None,
        "events": [],
        "sources": {},
        "tasks": {},
        "runtime_requests": [],
    }

    def registry(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if request.method == "POST" and path == "/v1/packages":
            return httpx.Response(
                409,
                json={
                    "type": "urn:jane:problem:package_exists",
                    "title": "Package already exists",
                    "status": 409,
                    "code": "package_exists",
                },
                headers={"Content-Type": "application/problem+json"},
            )
        parts = path.split("/")
        pid = parts[3]
        if len(parts) == 4:
            manifest = manifests[pid]
            return httpx.Response(
                200,
                json={
                    "package_id": pid,
                    "kind": manifest["kind"],
                    "title": manifest["title"],
                    "auto_changes_allowed": True,
                    "deprecated": False,
                    "created_at": "2026-10-11T00:00:00Z",
                    "updated_at": "2026-10-11T00:00:00Z",
                },
            )
        if len(parts) == 5:
            return httpx.Response(200, json={"items": [versions[pid]], "next_cursor": None})
        if len(parts) == 6:
            return httpx.Response(200, json=versions[pid])
        if parts[-1] == "archive":
            if state["failure"] == "rules-download" and manifests[pid]["kind"] == "collector-rules":
                raise httpx.ReadError("Interrupted after the extractor approval", request=request)
            return httpx.Response(200, content=archives[pid], headers={"Content-Type": "application/zip"})
        raise AssertionError(f"Unexpected registry mutation/read {request.method} {path}")

    def orchestrator(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        state["events"].append((request.method, path))
        if path == "/v1/connections":
            return httpx.Response(
                200,
                json={
                    "items": [
                        {"connection": {"connection_id": cid, "kind": kind}, "executors": []}
                        for cid, kind in (("raw-files", "filesystem"), ("results-pg", "postgresql"))
                    ],
                    "next_cursor": None,
                },
            )
        body = json.loads(request.content) if request.content else None
        if path == "/v1/task-validations":
            assert isinstance(body, dict)
            exists = body["input"]["source_id"] in state["sources"]
            valid = exists and state["failure"] != "task-validation"
            return httpx.Response(
                200,
                json={
                    "valid": valid,
                    "errors": []
                    if valid
                    else [
                        {
                            "pointer": "/input/source_id",
                            "code": "not_found",
                            "message": "Source does not exist",
                        }
                    ],
                },
            )
        if path in ("/v1/sources", "/v1/tasks"):
            assert isinstance(body, dict)
            collection, id_field = (
                ("sources", "source_id") if path.endswith("sources") else ("tasks", "task_id")
            )
            state[collection][body[id_field]] = body
            return httpx.Response(201, json=body, headers={"ETag": '"one"'})
        raise AssertionError(f"Unexpected orchestrator mutation/read {request.method} {path}")

    def runtime(request: httpx.Request) -> httpx.Response:
        state["runtime_requests"].append((request.method, request.url.path))
        raise AssertionError("An approved exact-digest package with actual passed tests must not be retested")

    def api(name: str, respond: Any) -> ex.Api:
        instance = ex.Api(f"http://{name}.invalid", name)
        instance.http.close()
        instance.http = httpx.Client(
            base_url=f"http://{name}.invalid", transport=httpx.MockTransport(respond)
        )
        instance.client = ContractClient(ex.spec(name), instance.http)
        return instance

    svc = ex.Services(api("registry", registry), api("orchestrator", orchestrator), api("storage", runtime))
    return svc, api("handler", runtime), state


def test_configure_applies_source_before_validation_and_recovers_registry_reports(tmp_path: Path) -> None:
    svc, runtime, state = deployment_neighbors()
    try:
        release = setup.configure(svc, runtime, CONFIG, ["shafa"], tmp_path, 1, 0.001)
        assert state["events"].index(("POST", "/v1/sources")) < state["events"].index(
            ("POST", "/v1/task-validations")
        )
        assert release["sites"]["shafa"]["source_applied"] is True
        assert release["sites"]["shafa"]["task_applied"] is True
        assert release["package_checks"]["classifieds.shafa-ads"]["reused_runtime_test_report"] is True
        assert state["runtime_requests"] == []
        assert ex.read_json(tmp_path / "release.json") == release
    finally:
        runtime.close()
        svc.close()


@pytest.mark.parametrize("failure", ["rules-download", "task-validation"])
def test_configure_preserves_approved_pins_and_partial_site_after_failure(
    tmp_path: Path, failure: str
) -> None:
    svc, runtime, state = deployment_neighbors()
    state["failure"] = failure
    try:
        with pytest.raises((httpx.ReadError, RuntimeError)):
            setup.configure(svc, runtime, CONFIG, ["shafa"], tmp_path, 1, 0.001)
        checkpoint = ex.read_json(tmp_path / "release.json")
        assert "classifieds.shafa-ads" in checkpoint["packages"]
        assert checkpoint["package_checks"]["classifieds.shafa-ads"]["runtime_test_report"]["passed"] == 2
        if failure == "rules-download":
            assert "classifieds.shafa-rules" not in checkpoint["packages"]
        else:
            assert checkpoint["sites"]["shafa"]["source_applied"] is True
            assert checkpoint["sites"]["shafa"]["task_applied"] is False
        assert state["runtime_requests"] == []
    finally:
        runtime.close()
        svc.close()


@pytest.mark.parametrize("problem", ["missing-report", "wrong-digest", "failed-latest", "missing-result"])
def test_approved_status_cannot_replace_actual_exact_digest_test_proof(problem: str) -> None:
    manifest = ex.read_json(setup.HERE / "packages" / "classifieds.shafa-ads" / "jane-package.json")
    ref = {
        "package_id": manifest["package_id"],
        "version": manifest["version"],
        "digest": "sha256:" + "1" * 64,
    }
    report = runtime_report(ref, manifest)
    stored: dict[str, Any] = {
        "status": "approved",
        "test_status": "passed",
        "test_reports": [{"runner": "handler-runtime", "context": "tests", "report": report}],
    }
    if problem == "missing-report":
        stored["test_reports"] = []
    elif problem == "wrong-digest":
        report["package"] = {**ref, "digest": "sha256:" + "2" * 64}
    elif problem == "failed-latest":
        latest = copy.deepcopy(report)
        latest["failed"] = 1
        stored["test_reports"].append({"runner": "handler-runtime", "context": "tests", "report": latest})
    else:
        del report["cases"][0]["result"]
    assert setup.recorded_runtime_report(stored, ref, manifest) is None
