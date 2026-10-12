"""Відтворюване налаштування, запуск і перевірка оголошень через API запущеного Jane.

Конфігурація сайтів, тип сутності кожного сайту й числові ліміти — sites.json. Нові задачі мають
незалежні IDs; наявні підключення raw-files/results-mongo повторно використовуються. Команда configure
публікує пакети й записує реальні звіти тестів runtime перед схваленням екстракторів.
verify звіряє кожну отриману сутність із збереженими RAW і станом у MongoDB.
HTTP 403, порожній результат або заблокований сайт ніколи не означає успішну перевірку.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
import sys
import time
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit

import httpx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import jane_examples as ex  # noqa: E402

# RAW stays in files; entities (types ad_*) go to MongoDB, one collection per entity type.
RAW_STORAGE, ENTITY_STORAGE = "jane.storage-files", "jane.storage-mongodb"
RAW_CONNECTION, ENTITY_CONNECTION = "raw-files", "results-mongo"
CONNECTION_KINDS = {RAW_CONNECTION: "filesystem", ENTITY_CONNECTION: "mongodb"}


def load_sites(path: Path = HERE / "sites.json") -> dict[str, Any]:
    return dict(ex.read_json(path))


def source_doc(site: str, config: dict[str, Any], refs: dict[str, Any]) -> dict[str, Any]:
    entry = config["sites"][site]
    return {
        "source_id": f"classified-{site}",
        "kind": "web",
        "title": entry["title"],
        "description": f"Публічні оголошення {entry['url']}; ліміти у examples/classifieds/sites.json.",
        "locator": {"url": entry["url"]},
        "collector_rules": refs[entry["rules"]],
        "limits": config["defaults"]["source_limits"],
        "forward_unknown_to_llm": False,
        "expected_entity_types": [entry["entity_type"]],
        "labels": {"group": "classifieds", "site": site},
    }


def task_doc(site: str, config: dict[str, Any], refs: dict[str, Any]) -> dict[str, Any]:
    entry = config["sites"][site]
    return {
        "task_id": f"classifieds-{site}",
        "title": f"{entry['title']}: збір оголошень",
        "enabled": entry.get("enabled", True),
        "description": f"Збір → RAW у файлах → {entry['entity_type']} у MongoDB. Публічні сторінки, обмежений обхід.",
        "input": {"source_id": f"classified-{site}"},
        "stages": [
            {"stage_id": "collect", "kind": "collect", "collector": {"collector": "web", "mode": "full"}},
            {
                "stage_id": "store-raw",
                "kind": "handler",
                "handler": refs[RAW_STORAGE],
                "connections": {"target": RAW_CONNECTION},
                "inputs": [{"from": "collect"}],
            },
            {
                "stage_id": "extract-ads",
                "kind": "handler",
                "handler": refs[entry["extractor"]],
                "inputs": [
                    {
                        "from": "collect",
                        "when": {"field": "material.format.media_type", "op": "eq", "value": "text/html"},
                    }
                ],
            },
            {
                "stage_id": "store-ads",
                "kind": "handler",
                "handler": refs[ENTITY_STORAGE],
                "connections": {"target": ENTITY_CONNECTION},
                "inputs": [
                    {
                        "from": "extract-ads",
                        "select": "output",
                        "when": {"field": "result.status", "op": "eq", "value": "success"},
                    }
                ],
            },
        ],
        "schedule": config["defaults"]["schedule"],
        "limits": entry.get("task_limits", config["defaults"]["task_limits"]),
        "forward_unknown_to_llm": False,
        "labels": {"group": "classifieds", "site": site},
    }


def local_packages(config: dict[str, Any], sites: list[str]) -> dict[str, Path]:
    return {
        config["sites"][s][kind]: HERE / "packages" / config["sites"][s][kind]
        for s in sites
        for kind in ("extractor", "rules")
    }


def check_packages(config: dict[str, Any], sites: list[str]) -> list[str]:
    from jane_extractor_sdk.testing import run_package_tests
    from jane_registry.archive import canonical_archive, digest_of, files_from_dir

    errors: list[str] = []
    refs: dict[str, Any] = {}
    for package_id, directory in local_packages(config, sites).items():
        if not (directory / "jane-package.json").is_file():
            errors.append(f"{package_id}: package directory is missing")
            continue
        manifest = ex.read_json(directory / "jane-package.json")
        refs[package_id] = {
            "package_id": package_id,
            "version": manifest["version"],
            "digest": str(digest_of(bytes(canonical_archive(files_from_dir(directory))))),
        }
        errors.extend(f"{package_id}: {e}" for e in ex.validate("package-manifest.schema.json", manifest))
        errors.extend(f"{package_id}: {e}" for e in ex.package_json_problems(directory, manifest))
        if manifest["kind"] == "collector-rules":
            errors.extend(
                f"{package_id}: {e}"
                for e in ex.validate(
                    "collector-rules.schema.json", ex.read_json(directory / manifest["entry"]["rules"])
                )
            )
        else:
            statuses = {case["expected_status"] for case in manifest.get("tests", [])}
            if not ({"success"} <= statuses and statuses & {"empty", "unrecognized"}):
                errors.append(f"{package_id}: requires success and empty/unrecognized cases")
            errors.extend(
                f"{package_id}: {case.name}: {case.differences}"
                for case in run_package_tests(directory)
                if not case.passed
            )
    for site in sites:
        entry = config["sites"][site]
        manifest_file = HERE / "packages" / entry["extractor"] / "jane-package.json"
        if not manifest_file.is_file():
            continue
        # The extractor fixes the type; sites.json names it for the source document and verification.
        declared = [
            e["entity_type"] for e in ex.read_json(manifest_file).get("output", {}).get("entities", [])
        ]
        if declared != [entry.get("entity_type")]:
            errors.append(
                f"{site}: entity_type {entry.get('entity_type')!r} differs from {entry['extractor']} output {declared}"
            )
    for storage in (RAW_STORAGE, ENTITY_STORAGE):
        refs[storage] = {"package_id": storage, "version": "1.0.0", "digest": "sha256:" + "0" * 64}
    if not errors:
        for site in sites:
            errors.extend(
                f"{site} source: {e}"
                for e in ex.validate("source.schema.json", source_doc(site, config, refs))
            )
            errors.extend(
                f"{site} task: {e}"
                for e in ex.validate("task-config.schema.json", task_doc(site, config, refs))
            )
    return errors


def wait_job(api: ex.Api, path: str, timeout: float, poll: float) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    last_status = "unavailable"
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError(f"{path}: still {last_status} after {timeout:g}s")
        try:
            job = api.call("GET", path, timeout=remaining).json()
        except httpx.TransportError as exc:
            # GET polling is safe to retry; POST operations are never retried here.
            last_status = type(exc).__name__
        else:
            last_status = str(job["status"])
            if job["status"] in ex.TERMINAL:
                return dict(job)
        time.sleep(max(0, min(poll, deadline - time.monotonic())))


def recorded_runtime_report(
    stored: dict[str, Any], ref: dict[str, Any], manifest: dict[str, Any]
) -> dict[str, Any] | None:
    """Reuse only the latest actual manifest run for this exact archive, including sandbox results."""
    expected = {case["name"]: case["expected_status"] for case in manifest.get("tests", [])}
    records = [
        entry
        for entry in stored.get("test_reports", [])
        if entry.get("context") == "tests"
        and entry.get("runner", "").startswith("handler-runtime")
        and entry.get("report", {}).get("package") == ref
    ]
    if not records or stored.get("test_status") != "passed":
        return None
    report = records[-1]["report"]
    cases = {case["name"]: case for case in report.get("cases", [])}
    if len(expected) < 2 or report.get("failed") != 0 or report.get("passed", 0) < len(expected):
        return None
    for name, status in expected.items():
        case = cases.get(name, {})
        result = case.get("result", {})
        if (
            not case.get("passed")
            or case.get("actual_status") != status
            or result.get("handler") != ref
            or result.get("status") != status
        ):
            return None
    return dict(report)


def publish_package(
    svc: ex.Services, runtime: ex.Api, directory: Path, timeout: float, poll: float
) -> tuple[dict[str, Any], dict[str, Any]]:
    from jane_registry.archive import canonical_archive, digest_of, files_from_dir

    manifest = ex.read_json(directory / "jane-package.json")
    pid, version = manifest["package_id"], manifest["version"]
    if not pid.startswith("classifieds."):
        raise RuntimeError(f"Refusing to change package policy outside this task: {pid}")
    archive = bytes(canonical_archive(files_from_dir(directory)))
    ref = {"package_id": pid, "version": version, "digest": str(digest_of(archive))}
    svc.registry.call(
        "POST",
        "/v1/packages",
        ok=(201, 409),
        json={
            "package_id": pid,
            "kind": manifest["kind"],
            "title": manifest["title"],
            # The user authorized publishing these new task-specific LLM-generated packages.
            # Activation still requires the explicit approval below after runtime tests.
            "auto_changes_allowed": True,
        },
        headers={"Idempotency-Key": ex.key()},
    )
    current = svc.registry.call("GET", f"/v1/packages/{pid}")
    package = current.json()
    if package["kind"] != manifest["kind"]:
        raise RuntimeError(f"{pid}: existing package kind differs from the task package")
    if not package.get("auto_changes_allowed", False):
        patch = {"auto_changes_allowed": True}
        svc.registry.client.spec.validate_request(
            "PATCH", f"/v1/packages/{pid}", patch, content_type="application/merge-patch+json"
        )
        svc.registry.call(
            "PATCH",
            f"/v1/packages/{pid}",
            content=json.dumps(patch),
            headers={"If-Match": current.headers["ETag"], "Content-Type": "application/merge-patch+json"},
        )
    path = f"/v1/packages/{pid}/versions/{version}"
    existing = svc.registry.call("GET", path, ok=(200, 404))
    if existing.status_code == 200:
        stored = existing.json()
    else:
        response = svc.registry.call(
            "POST",
            f"/v1/packages/{pid}/versions",
            ok=(201, 409),
            content=archive,
            headers={"Content-Type": "application/zip", "Idempotency-Key": ex.key()},
        )
        stored = response.json() if response.status_code == 201 else svc.registry.call("GET", path).json()
    if stored["digest"] != ref["digest"]:
        raise RuntimeError(f"{pid}@{version}: registry digest differs; bump package version")
    evidence: dict[str, Any] = {"package": ref}
    if manifest["kind"] == "extractor":
        report = recorded_runtime_report(stored, ref, manifest)
        if report is not None:
            evidence["reused_runtime_test_report"] = True
            ex.log(f"{pid}: reused recorded runtime tests for {ref['digest']}")
        else:
            accepted = runtime.call(
                "POST",
                "/v1/test-runs",
                ok=(202,),
                json={"handler": ref, "tests": "all"},
                headers={"Idempotency-Key": ex.key()},
            ).json()
            ex.log(f"{pid}: accepted runtime test job {accepted['job_id']}")
            job = wait_job(runtime, f"/v1/jobs/{accepted['job_id']}", timeout, poll)
            if job["status"] != "succeeded":
                raise RuntimeError(f"{pid}: runtime test job {job['status']}: {job.get('error')}")
            report = job["result"]
            svc.registry.call(
                "POST",
                f"{path}/test-results",
                json={"runner": "handler-runtime", "context": "tests", "report": report},
                headers={"Idempotency-Key": ex.key()},
            )
        evidence["runtime_test_report"] = report
        if report["failed"] or report["passed"] < 2:
            raise RuntimeError(f"{pid}: runtime tests {report['passed']} passed, {report['failed']} failed")
        reason = "Тести маніфесту пройшли у запущеному handler-runtime; звіт збережено у registry."
    else:
        errors = ex.validate(
            "collector-rules.schema.json", ex.read_json(directory / manifest["entry"]["rules"])
        )
        if errors:
            raise RuntimeError(f"{pid}: rules schema: {errors}")
        evidence["rules_schema_valid"] = True
        reason = "Правила колектора валідні за контрактом; це не перевірка реального збору."
    if stored["status"] == "draft":
        stored = svc.registry.call(
            "POST",
            f"{path}/status",
            json={"status": "approved", "reason": reason},
            headers={"Idempotency-Key": ex.key()},
        ).json()
    if stored["status"] != "approved":
        raise RuntimeError(f"{pid}@{version}: status {stored['status']} is not approved")
    if str(digest_of(svc.registry.call("GET", f"{path}/archive").content)) != ref["digest"]:
        raise RuntimeError(f"{pid}: downloaded archive digest differs")
    return ref, evidence


def checkout_storage_refs() -> dict[str, dict[str, str]]:
    """Exact storage package versions of this checkout (the MongoDB layout of 2.x differs from 1.x)."""
    from jane_registry.archive import canonical_archive, digest_of, files_from_dir
    from jane_storage.adapters import package_dirs

    directories = package_dirs()
    refs: dict[str, dict[str, str]] = {}
    for pid in (RAW_STORAGE, ENTITY_STORAGE):
        directory = Path(directories[pid])
        refs[pid] = {
            "package_id": pid,
            "version": ex.read_json(directory / "jane-package.json")["version"],
            "digest": str(digest_of(bytes(canonical_archive(files_from_dir(directory))))),
        }
    return refs


def storage_refs(svc: ex.Services) -> dict[str, Any]:
    connections = {
        p["connection"]["connection_id"]: p["connection"]["kind"]
        for p in svc.orchestrator.pages("/v1/connections", {})
    }
    for cid, kind in CONNECTION_KINDS.items():
        if connections.get(cid) != kind:
            raise RuntimeError(f"Required existing connection {cid} ({kind}) is unavailable")
    refs = checkout_storage_refs()
    for pid, ref in refs.items():
        stored = svc.registry.call("GET", f"/v1/packages/{pid}/versions/{ref['version']}", ok=(200, 404))
        version = stored.json() if stored.status_code == 200 else {}
        if version.get("status") != "approved" or version.get("digest") != ref["digest"]:
            raise RuntimeError(
                f"{pid}@{ref['version']}: no approved storage package with this checkout's digest"
            )
    return refs


def upsert(orch: ex.Api, collection: str, doc: dict[str, Any], id_field: str) -> None:
    created = orch.call("POST", collection, ok=(201, 409), json=doc, headers={"Idempotency-Key": ex.key()})
    if created.status_code == 409:
        path = f"{collection}/{doc[id_field]}"
        current = orch.call("GET", path)
        orch.call("PUT", path, json=doc, headers={"If-Match": current.headers["ETag"]})


def configure(
    svc: ex.Services,
    runtime: ex.Api,
    config: dict[str, Any],
    sites: list[str],
    output: Path,
    timeout: float,
    poll: float,
) -> dict[str, Any]:
    errors = check_packages(config, sites)
    if errors:
        raise RuntimeError("Offline package validation failed: " + "; ".join(errors))
    release_file = output / "release.json"
    release = (
        ex.read_json(release_file)
        if release_file.is_file()
        else {"packages": {}, "package_checks": {}, "sites": {}}
    )
    release["packages"].update(storage_refs(svc))
    ex.write_json(release_file, release)
    for pid, directory in local_packages(config, sites).items():
        ref, report = publish_package(svc, runtime, directory, timeout, poll)
        release["packages"][pid] = ref
        release["package_checks"][pid] = report
        ex.write_json(release_file, release)
        ex.log(f"registry: {pid}@{ref['version']} approved; checkpoint saved")
    for site in sites:
        refs = release["packages"]
        source, task = source_doc(site, config, refs), task_doc(site, config, refs)
        upsert(svc.orchestrator, "/v1/sources", source, "source_id")
        release["sites"][site] = {
            "source": source,
            "task": task,
            "source_applied": True,
            "task_applied": False,
            "blocked_reason": config["sites"][site].get("blocked_reason"),
        }
        ex.write_json(output / f"source.{site}.json", source)
        ex.write_json(release_file, release)
        validation = svc.orchestrator.call("POST", "/v1/task-validations", json=task).json()
        if not validation["valid"]:
            raise RuntimeError(f"{site}: task validation {validation['errors']}")
        upsert(svc.orchestrator, "/v1/tasks", task, "task_id")
        release["sites"][site]["task_applied"] = True
        ex.write_json(output / f"task.{site}.json", task)
        ex.write_json(release_file, release)
    return release


def normalize(value: Any) -> str:
    return " ".join(html.unescape(str(value)).replace("\xa0", " ").split()).casefold()


def canonical_url(value: str, base: str) -> str:
    parsed = urlsplit(urljoin(base, html.unescape(value)))
    return parsed.netloc.casefold() + parsed.path.rstrip("/")


def url_matches(value: str, expected: str, base: str) -> bool:
    origin = urlsplit(base)
    root = f"{origin.scheme}://{origin.netloc}/"
    return any(canonical_url(value, variant) == expected for variant in (base, root, root + "uk/"))


def json_objects(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        return [value] + [d for child in value.values() for d in json_objects(child)]
    if isinstance(value, list):
        return [d for child in value for d in json_objects(child)]
    return []


def strings(value: Any) -> list[str]:
    if isinstance(value, dict):
        return [s for child in value.values() for s in strings(child)]
    if isinstance(value, list):
        return [s for child in value for s in strings(child)]
    return [str(value)]


def amount(value: Any) -> Decimal | None:
    try:
        return Decimal(re.sub(r"[^0-9.,-]", "", str(value)).replace(",", "."))
    except InvalidOperation:
        return None


class RawNode:
    def __init__(self, tag: str, attributes: dict[str, str], parent: RawNode | None = None) -> None:
        self.tag, self.attributes, self.parent = tag, attributes, parent
        self.content: list[RawNode | str] = []

    def nodes(self, tag: str) -> list[RawNode]:
        return [
            node
            for child in self.content
            if isinstance(child, RawNode)
            for node in ([child] if child.tag == tag else []) + child.nodes(tag)
        ]

    def text(self, separator: str = "") -> str:
        return separator.join(
            child.text(separator) if isinstance(child, RawNode) else child for child in self.content
        )

    def visible_text(self, separator: str = "") -> str:
        """DOM evidence excludes markup text; text() retains script bodies for JSON parsing."""
        return separator.join(
            child.visible_text(separator) if isinstance(child, RawNode) else child
            for child in self.content
            if not isinstance(child, RawNode) or child.tag not in {"style", "script", "svg"}
        )


class RawDocument(HTMLParser):
    def __init__(self, content: bytes) -> None:
        super().__init__(convert_charrefs=True)
        self.root = RawNode("document", {})
        self.current = self.root
        self.feed(content.decode("utf-8", errors="replace"))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = RawNode(tag, {key: value or "" for key, value in attrs}, self.current)
        self.current.content.append(node)
        if tag not in {
            "area",
            "base",
            "br",
            "col",
            "embed",
            "hr",
            "img",
            "input",
            "link",
            "meta",
            "param",
            "source",
            "track",
            "wbr",
        }:
            self.current = node

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.current.content.append(RawNode(tag, {key: value or "" for key, value in attrs}, self.current))

    def handle_endtag(self, tag: str) -> None:
        node: RawNode | None = self.current
        while node is not None and node is not self.root:
            if node.tag == tag:
                self.current = node.parent or self.root
                return
            node = node.parent

    def handle_data(self, data: str) -> None:
        self.current.content.append(data)


def currency_code(value: Any) -> str | None:
    return {
        "uah": "UAH",
        "грн": "UAH",
        "₴": "UAH",
        "usd": "USD",
        "$": "USD",
        "дол": "USD",
        "eur": "EUR",
        "€": "EUR",
        "євро": "EUR",
    }.get(normalize(value))


def json_price_matches(candidate: dict[str, Any], expected: dict[str, Any], host: str) -> bool:
    """The currency must belong to the same price map/object, not elsewhere in an advertisement."""
    expected_amount, expected_currency = amount(expected["amount"]), expected["currency"]
    price = candidate.get("price")
    if isinstance(price, dict):
        for key, value in price.items():
            if currency_code(key) == expected_currency and isinstance(value, (int, float, str)):
                return amount(value) == expected_amount
        return (
            amount(price.get("amount", price.get("price"))) == expected_amount
            and currency_code(price.get("currency", price.get("priceCurrency"))) == expected_currency
        )
    if not isinstance(price, (int, float, str)):
        return False
    if host == "dom.ria.com":
        currency = currency_code(candidate.get("currency_type"))
        if currency is None:
            currency_id = candidate.get("currencyId")
            if isinstance(currency_id, int) and not isinstance(currency_id, bool):
                currency = {1: "USD", 2: "EUR", 3: "UAH"}.get(currency_id)
    else:
        currency = currency_code(candidate.get("currency", candidate.get("priceCurrency")))
    return amount(price) == expected_amount and currency == expected_currency


def ria_price_matches(candidate: RawNode, expected: dict[str, Any], listing_id: str) -> bool:
    """Compare RIA's monetary slot within its own card, without adjacent description/model numbers."""
    for slot in candidate.nodes("span"):
        if not {"price", "js-price"} <= set(slot.attributes.get("class", "").split()):
            continue
        owner = slot.parent
        while owner is not None and not owner.attributes.get("id", "").startswith("adv_"):
            owner = owner.parent
        if owner is None or owner.attributes.get("id") != f"adv_{listing_id}":
            continue
        match = re.fullmatch(
            r"(\d(?:[\d\s.,]*\d)?)\s*(uah|грн\.?|₴|usd|\$|дол\.?|eur|€|євро)",
            normalize(slot.visible_text(separator=" ")),
        )
        if (
            match is not None
            and amount(match.group(1)) == amount(expected["amount"])
            and currency_code(match.group(2).rstrip(".")) == expected["currency"]
        ):
            return True
    return False


def olx_price_matches(candidate: RawNode, expected: dict[str, Any], listing_id: str) -> bool:
    """An OLX price starts its own monetary slot; model numbers and nearby cards cannot corroborate it."""
    for slot in candidate.nodes("p"):
        if slot.attributes.get("data-testid") != "ad-price":
            continue
        owner = slot.parent
        while owner is not None and not (
            owner.attributes.get("data-testid") == "l-card" or owner.attributes.get("data-cy") == "l-card"
        ):
            owner = owner.parent
        if owner is None or owner.attributes.get("id") != listing_id:
            continue
        match = re.match(
            r"^(\d(?:[\d\s.,]*\d)?)\s*(uah|грн\.?|₴|usd|\$|дол\.?|eur|€|євро)(?!\w)",
            normalize(slot.visible_text(separator=" ")),
        )
        if (
            match is not None
            and amount(match.group(1)) == amount(expected["amount"])
            and currency_code(match.group(2).rstrip(".")) == expected["currency"]
        ):
            return True
    return False


def location_matches(candidate: Any, kind: str, location: str, host: str) -> bool:
    expected = normalize(location)
    if kind == "json":
        if host == "dom.ria.com":
            return normalize(candidate.get("city_name_uk", "")) == expected
        if host == "auto.ria.com":
            for info in candidate.get("basicInfo") or []:
                if not isinstance(info, dict):
                    continue
                icon = info.get("icon")
                data = icon.get("data") if isinstance(icon, dict) else None
                if (
                    isinstance(data, dict)
                    and data.get("style") == "ic_16_location"
                    and normalize(info.get("content", "")) == expected
                ):
                    return True
        return False
    for node in candidate.nodes("div") + candidate.nodes("p"):
        if host == "ria.com" and {"address", "js-state-city"} <= set(
            node.attributes.get("class", "").split()
        ):
            if normalize(node.visible_text(separator=" ")) == expected:
                return True
        elif host == "olx.ua" and node.attributes.get("data-testid") == "location-date":
            observed = re.split(r"\s+-\s+", node.visible_text(separator=" "), maxsplit=1)[0]
            if normalize(observed) == expected:
                return True
    return False


def raw_field_check(fields: dict[str, Any], content: bytes, url: str) -> dict[str, Any]:
    """Independent evidence from one associated JSON object or HTML card; never re-run the extractor."""
    supported = {"site", "listing_id", "title", "url", "price", "location"}
    required = {"site", "listing_id", "title", "url"}
    if not required <= fields.keys() or not fields.keys() <= supported:
        return {"verified": False, "reason": "Missing identity fields or unsupported output fields."}
    if any(not isinstance(fields[key], str) or not fields[key].strip() for key in required):
        return {"verified": False, "reason": "Identity fields must be nonempty strings."}
    host = (urlsplit(url).hostname or "").casefold().removeprefix("www.")
    observed_site = {
        "auto.ria.com": "auto.ria.com",
        "dom.ria.com": "dom.ria.com",
        "ria.com": "ria.com",
        "shafa.ua": "shafa",
        "olx.ua": "olx",
    }.get(host)
    entity_url = urlsplit(fields["url"])
    if (
        fields["site"] != observed_site
        or (entity_url.hostname or "").casefold().removeprefix("www.") != host
        or entity_url.scheme != "https"
    ):
        return {"verified": False, "reason": "Site or URL domain does not match the collected source."}
    if "location" in fields and (not isinstance(fields["location"], str) or not fields["location"].strip()):
        return {"verified": False, "reason": "Reported location is not a nonempty string."}
    price = fields.get("price")
    if "price" in fields and (
        not isinstance(price, dict)
        or set(price) != {"amount", "currency"}
        or not isinstance(price["currency"], str)
        or price["currency"] not in {"UAH", "USD", "EUR"}
        or isinstance(price["amount"], bool)
        or not isinstance(price["amount"], (int, float))
        or amount(price["amount"]) is None
    ):
        return {"verified": False, "reason": "Reported price has an unsupported shape, amount or currency."}
    tree = RawDocument(content).root
    expected_url, expected_title = canonical_url(fields["url"], url), normalize(fields["title"])
    listing_id = str(fields["listing_id"])
    candidates: list[tuple[str, Any]] = []
    for node in tree.nodes("script"):
        try:
            doc = json.loads(node.text())
        except (ValueError, TypeError):
            state = re.search(r"(?:window\.)?__(?:PINIA|INITIAL_STATE|NUXT)__\s*=\s*", node.text())
            if not state:
                continue
            try:
                doc, _ = json.JSONDecoder().raw_decode(node.text()[state.end() :])
            except ValueError:
                continue
        for item in json_objects(doc):
            values = strings(item)
            identity = any(
                str(item.get(k, "")) == listing_id
                for k in (
                    "id",
                    "listing_id",
                    "listingId",
                    "realty_id",
                    "auto_id",
                    "productId",
                    "sku",
                    "identifier",
                )
            )
            urls_match = any(url_matches(v, expected_url, url) for v in values if "/" in v or listing_id in v)
            own_urls_match = any(
                url_matches(value, expected_url, url)
                for value in item.values()
                if isinstance(value, str) and listing_id in value
            )
            if (
                urls_match
                and (identity or own_urls_match)
                and expected_title in {normalize(v) for v in values}
            ):
                candidates.append(("json", item))
    for anchor in tree.nodes("a"):
        if canonical_url(anchor.attributes.get("href", ""), url) != expected_url:
            continue
        current_node: RawNode | None = anchor
        for _ in range(6):
            if current_node is None:
                break
            text = normalize(current_node.visible_text(separator=" "))
            links = {
                canonical_url(a.attributes["href"], url)
                for a in current_node.nodes("a")
                if "href" in a.attributes
            }
            is_card = (
                current_node.attributes.get("id") == f"adv_{listing_id}"
                or current_node.attributes.get("data-testid") == "productCard"
                or (
                    current_node.attributes.get("data-testid") == "l-card"
                    and current_node.attributes.get("id") == listing_id
                )
            )
            if (
                (
                    expected_title in text
                    or normalize(anchor.attributes.get("aria-label", "")) == expected_title
                )
                and len(text) <= 5000
                and (is_card or links <= {expected_url})
                and current_node.tag not in ("html", "body")
            ):
                candidates.append(("html", current_node))
            current_node = current_node.parent
    for kind, candidate in candidates:
        evidence = (
            json.dumps(candidate, ensure_ascii=False)
            if kind == "json"
            else candidate.visible_text(separator=" ")
        )
        if (
            not re.search(r"(?<![\w])" + re.escape(listing_id) + r"(?![\w])", fields["url"])
            and listing_id not in evidence
            and not (kind == "html" and candidate.attributes.get("id") in {listing_id, f"adv_{listing_id}"})
        ):
            continue
        price_ok = True
        if price:
            expected_amount = amount(price["amount"])
            aliases = {
                "UAH": ["uah", "грн", "₴"],
                "USD": ["usd", "$", "дол"],
                "EUR": ["eur", "€", "євро"],
            }.get(price["currency"], [price["currency"].casefold()])
            if kind == "json":
                price_ok = json_price_matches(candidate, price, host)
            elif host == "ria.com":
                price_ok = ria_price_matches(candidate, price, listing_id)
            elif host == "olx.ua":
                price_ok = olx_price_matches(candidate, price, listing_id)
            else:
                compact = normalize(evidence)
                pattern = (
                    r"\d(?:[\d\s.,]*\d)?\s*(?:uah|грн|₴|usd|\$|дол\.?|eur|€|євро)|(?:\$|€|₴)\s*\d[\d\s.,]*"
                )
                price_ok = any(
                    amount(token) == expected_amount and any(alias in normalize(token) for alias in aliases)
                    for token in re.findall(pattern, compact)
                )
        if price_ok and (
            "location" not in fields or location_matches(candidate, kind, fields["location"], host)
        ):
            return {
                "verified": True,
                "evidence_kind": kind,
                "checked_fields": ["site", "listing_id", "title", "url"]
                + (["price"] if price else [])
                + (["location"] if "location" in fields else []),
            }
    return {
        "verified": False,
        "reason": "Identity, title, URL and every reported price/location could not be corroborated within one RAW card/object.",
    }


def verify_site(
    svc: ex.Services, runtime: ex.Api, config: dict[str, Any], site: str, run: dict[str, Any]
) -> dict[str, Any]:
    source_id = f"classified-{site}"
    report: dict[str, Any] = {
        "site": site,
        "source_id": source_id,
        "run": ex.run_summary(run),
        "verified": False,
        "errors": [],
        "samples": [],
    }
    if not config["sites"][site].get("enabled", True):
        report["errors"].append(config["sites"][site].get("blocked_reason", "Site disabled"))
        return report
    if run["status"] != "succeeded":
        report["errors"].append(f"Run status {run['status']}")
    task = svc.orchestrator.call("GET", f"/v1/tasks/classifieds-{site}").json()
    report["packages"] = {s["stage_id"]: s["handler"] for s in task["stages"] if "handler" in s}
    items = svc.orchestrator.pages(f"/v1/runs/{run['run_id']}/items", {"stage_id": "extract-ads"})
    entity_type = config["sites"][site]["entity_type"]
    raw = svc.storage.pages("/v1/objects", {"connection_id": RAW_CONNECTION, "source_id": source_id})
    raw_by_obs = {r["material"]["observation_id"]: r for r in raw if r.get("material")}
    states = svc.storage.pages(
        "/v1/entities",
        {"connection_id": ENTITY_CONNECTION, "entity_type": entity_type, "scope": source_id},
    )
    states_by_key = {state["canonical_key"]: state for state in states}
    report.update(
        {
            "raw_objects": len(raw),
            "persisted_entities": len(states),
            "extraction_items": len(items),
            "checked_entities": 0,
        }
    )
    checked_raw: dict[str, tuple[bytes, str]] = {}
    for item in items:
        if item.get("status") != "completed" or item.get("result_status") not in ("success", "empty"):
            report["errors"].append(
                f"Item {item['item_id']}: {item.get('status')}/{item.get('result_status')}"
            )
            continue
        result = runtime.call("GET", f"/v1/invocations/{item['invocation_id']}").json()
        for entity in (result.get("output") or {}).get("entities", []):
            if entity.get("entity_type") != entity_type:
                report["errors"].append(
                    f"{entity['key']}: entity type {entity.get('entity_type')!r}, not {entity_type}"
                )
                continue
            obs = entity["observation"]["observation_id"]
            saved = raw_by_obs.get(obs)
            if not saved:
                report["errors"].append(f"{entity['key']}: collected observation has no persisted RAW")
                continue
            if obs not in checked_raw:
                obj_id = saved["object"]["object_id"]
                detail = svc.storage.call(
                    "GET", f"/v1/objects/{obj_id}", params={"connection_id": RAW_CONNECTION}
                ).json()
                response = svc.storage.call(
                    "GET", f"/v1/objects/{obj_id}/content", params={"connection_id": RAW_CONNECTION}
                )
                original = response.content
                expected_sha = detail.get("material", {}).get("revision", {}).get("content_sha256")
                if not expected_sha or hashlib.sha256(original).hexdigest() != expected_sha:
                    report["errors"].append(f"RAW {obj_id}: missing or mismatching SHA-256")
                checked_raw[obs] = original, saved["material"].get("url", config["sites"][site]["url"])
            key = (
                entity["key"]["scope"]
                + "|"
                + json.dumps(
                    entity["key"]["natural"], sort_keys=True, separators=(",", ":"), ensure_ascii=False
                )
            )
            state = states_by_key.get(key)
            if state is None or any(state["fields"].get(k) != v for k, v in entity["fields"].items()):
                report["errors"].append(f"{key}: MongoDB state does not match extracted fields")
                continue
            if any(
                (state.get("field_orders", {}).get(k) or {}).get("observation_id") != obs
                for k in entity["fields"]
            ):
                history = svc.storage.pages(
                    "/v1/entity-history",
                    {"connection_id": ENTITY_CONNECTION, "entity_type": entity_type, "key": key},
                )
                if not any(h["record"]["observation"]["observation_id"] == obs for h in history):
                    report["errors"].append(f"{key}: produced observation missing in MongoDB history")
                    continue
            check = raw_field_check(entity["fields"], *checked_raw[obs])
            if not check["verified"]:
                report["errors"].append(f"{key}: {check['reason']}")
                continue
            report["checked_entities"] += 1
            if len(report["samples"]) < 3:
                report["samples"].append(
                    {
                        "fields": entity["fields"],
                        "observation": entity["observation"],
                        "raw_object_id": saved["object"]["object_id"],
                        **check,
                    }
                )
    report["checked_raw_objects"] = len(checked_raw)
    if not report["checked_entities"]:
        report["errors"].append("No actual entities were obtained and verified against persisted RAW.")
    report["verified"] = not report["errors"]
    return report


def service_urls(
    project: str, stack: dict[str, Any], *, use_snapshot: bool = False, timeout: float = 10
) -> dict[str, str]:
    """Read current API mappings for this Compose project; never read container environment values."""
    required = {"registry", "orchestrator", "storage", "handler-runtime"}
    if use_snapshot:
        urls = {name: str(stack["services"][name]["url"]) for name in required}
        ex.log("Using saved service URLs (--use-snapshot); current Docker mappings are not verified.")
        return urls
    deadline = time.monotonic() + timeout

    def docker(args: list[str]) -> str:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError("Docker service discovery exceeded its timeout")
        try:
            response = subprocess.run(  # noqa: S603 - fixed Docker commands with separate, non-shell arguments.
                ["docker", *args],  # noqa: S607 - Docker comes from the cross-platform PATH.
                capture_output=True,
                text=True,
                check=True,
                timeout=remaining,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise RuntimeError(
                f"Docker service discovery failed ({type(exc).__name__}); saved URLs were not used. "
                "Use --use-snapshot only to explicitly accept unverified saved mappings."
            ) from exc
        return response.stdout

    discovered: dict[str, str] = {}
    listing = docker(
        [
            "ps",
            "--filter",
            f"label=com.docker.compose.project={project}",
            "--format",
            '{{.ID}} {{.Label "com.docker.compose.service"}}',
        ]
    )
    for line in listing.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1] in required:
            if not re.fullmatch(r"[0-9a-f]{12,64}", parts[0]):
                raise RuntimeError("Docker returned an invalid container ID during service discovery")
            discovered[parts[0]] = parts[1]
    if not discovered:
        raise RuntimeError(f"No running API containers found for Compose project {project}; snapshot ignored")
    inspection = docker(
        [
            "inspect",
            "--format",
            '{{.Id}} {{index .Config.Labels "com.docker.compose.project"}} {{index .Config.Labels "com.docker.compose.service"}} {{json .NetworkSettings.Ports}}',
            *discovered,
        ]
    )
    candidates: dict[str, list[str]] = {name: [] for name in required}
    for line in inspection.splitlines():
        parts = line.split(" ", 3)
        if len(parts) != 4:
            raise RuntimeError("Docker returned malformed service mapping metadata")
        container_id, found_project, service, encoded_ports = parts
        requested = [
            short for short, name in discovered.items() if container_id.startswith(short) and name == service
        ]
        if found_project != project or not requested or service not in required:
            raise RuntimeError("Docker service mapping is outside the selected Compose project")
        try:
            ports = json.loads(encoded_ports)
        except ValueError as exc:
            raise RuntimeError(f"Docker returned invalid port metadata for {service}") from exc
        # These four Jane APIs use container port 8000; only the published host port changes.
        bindings = ports.get("8000/tcp") or []
        ipv4 = [binding for binding in bindings if binding.get("HostIp") in {"127.0.0.1", "0.0.0.0", ""}]  # noqa: S104 - read existing metadata; no listening socket is created.
        ipv6 = [binding for binding in bindings if binding.get("HostIp") in {"::1", "::"}]
        for binding in ipv4 or ipv6:
            port = str(binding.get("HostPort", ""))
            if not port.isdigit() or not 1 <= int(port) <= 65535:
                raise RuntimeError(f"Docker returned an invalid published API port for {service}")
            host = "127.0.0.1" if ipv4 else "[::1]"
            candidates[service].append(f"http://{host}:{port}")
    urls = {}
    for service, values in candidates.items():
        if len(values) != 1:
            raise RuntimeError(
                f"{service}: expected one running published API in project {project}, found {len(values)}; snapshot ignored"
            )
        urls[service] = values[0]
    return urls


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "configure", "start", "wait", "verify", "demo"))
    parser.add_argument("--project", default="jane-demo")
    parser.add_argument("--stack-dir", type=Path, default=ex.STACK_DIR)
    parser.add_argument("--config", type=Path, default=HERE / "sites.json")
    parser.add_argument("--site", action="append", help="Repeat for a subset of sites")
    parser.add_argument("--output-dir", type=Path, default=ex.STACK_DIR / "classifieds")
    parser.add_argument("--timeout", type=float, default=900)
    parser.add_argument("--poll-seconds", type=float, default=2)
    parser.add_argument(
        "--discovery-timeout",
        type=float,
        default=10,
        help="Overall timeout for read-only Docker port discovery",
    )
    parser.add_argument(
        "--use-snapshot",
        action="store_true",
        help="Explicitly use saved URLs without verifying current Docker mappings",
    )
    parser.add_argument("--run-id", help="Explicit run for a single --site in wait/verify")
    ns = parser.parse_args(argv)
    if ns.timeout <= 0 or ns.poll_seconds <= 0 or ns.discovery_timeout <= 0:
        parser.error("timeout, poll-seconds and discovery-timeout must be positive")
    config = load_sites(ns.config)
    sites = ns.site or list(config["sites"])
    if any(site not in config["sites"] for site in sites) or (ns.run_id and len(sites) != 1):
        parser.error("Unknown site, or --run-id requires one --site")
    if ns.command == "check":
        errors = check_packages(config, sites)
        print(json.dumps({"sites": sites, "errors": errors}, ensure_ascii=True))
        return int(bool(errors))
    ns.output_dir.mkdir(parents=True, exist_ok=True)
    stack = ex.read_json(ns.stack_dir / f"stack-{ns.project}.json")
    urls = service_urls(ns.project, stack, use_snapshot=ns.use_snapshot, timeout=ns.discovery_timeout)
    token = (stack.get("env") or {}).get("JANE_API_KEY_ADMIN")
    svc = ex.Services(
        ex.Api(urls["registry"], "registry", token=token),
        ex.Api(urls["orchestrator"], "orchestrator", token=token),
        ex.Api(urls["storage"], "storage", token=token),
    )
    runtime = ex.Api(urls["handler-runtime"], "handler", token=token)
    ex.write_json(
        ns.output_dir / "service-discovery.json",
        {
            "project": ns.project,
            "mode": "snapshot" if ns.use_snapshot else "docker",
            "verified": not ns.use_snapshot,
            "urls": urls,
        },
    )
    try:
        if ns.command in ("configure", "demo"):
            configure(svc, runtime, config, sites, ns.output_dir, ns.timeout, ns.poll_seconds)
        if ns.command == "configure":
            return 0
        runs_file = ns.output_dir / "runs.json"
        runs = ex.read_json(runs_file) if runs_file.is_file() else {}
        if ns.run_id:
            runs[sites[0]] = ns.run_id
        if ns.command in ("start", "demo"):
            for site in sites:
                if config["sites"][site].get("enabled", True):
                    runs[site] = ex.start_run(
                        svc.orchestrator, f"classifieds-{site}", "Перевірка публічного збору оголошень"
                    )
                    ex.log(f"{site}: started run {runs[site]}")
            ex.write_json(runs_file, runs)
        if ns.command == "start":
            return 0
        failed = False
        for site in sites:
            if not config["sites"][site].get("enabled", True):
                report = {
                    "site": site,
                    "verified": False,
                    "errors": [config["sites"][site].get("blocked_reason", "Site disabled")],
                }
            elif site not in runs:
                report = {
                    "site": site,
                    "verified": False,
                    "errors": ["No recorded run; execute start or provide --run-id"],
                }
            else:
                path = f"/v1/runs/{runs[site]}"
                run = (
                    wait_job(svc.orchestrator, path, ns.timeout, ns.poll_seconds)
                    if ns.command in ("wait", "demo")
                    else svc.orchestrator.call("GET", path).json()
                )
                report = verify_site(svc, runtime, config, site, run)
            ex.write_json(ns.output_dir / f"verification.{site}.json", report)
            failed |= not report["verified"]
            print(
                json.dumps(
                    {
                        "site": site,
                        "verified": report["verified"],
                        "checked_entities": report.get("checked_entities", 0),
                        "errors": report["errors"],
                    },
                    ensure_ascii=True,
                ),
                flush=True,
            )
        return int(failed)
    finally:
        runtime.close()
        svc.close()


if __name__ == "__main__":
    raise SystemExit(main())
