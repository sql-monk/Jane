"""Configure hourly multilingual news analysis in an existing Jane stack."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))
import jane_examples as ex  # noqa: E402

PACKAGES = HERE / "packages"
GROUP = "news-analysis"
REGIONS = {"UA": "ukraine", "EU": "europe", "US": "usa", "RU": "russia"}


@dataclass
class NewsServices:
    registry: ex.Api
    orchestrator: ex.Api
    storage: ex.Api
    llm: ex.Api
    runtime: ex.Api

    @classmethod
    def of_stack(cls, path: Path) -> NewsServices:
        stack = ex.read_json(path)
        services = stack["services"]
        token = services.get("auth", {}).get("admin_api_key") or stack.get("env", {}).get(
            "JANE_API_KEY_ADMIN"
        )
        proxy = services.get("proxy", {}).get("url")

        def service_url(name: str) -> str:
            return f"{proxy.rstrip('/')}/api/{name}" if proxy else str(services[name]["url"])

        return cls(
            ex.Api(service_url("registry"), "registry", token=token),
            ex.Api(service_url("orchestrator"), "orchestrator", token=token),
            ex.Api(service_url("storage"), "storage", token=token),
            ex.Api(service_url("llm"), "llm", token=token),
            ex.Api(service_url("handler-runtime"), "handler", token=token),
        )

    def close(self) -> None:
        for api in (self.registry, self.orchestrator, self.storage, self.llm, self.runtime):
            api.close()


def sources() -> list[dict[str, Any]]:
    items = [*ex.read_json(HERE / "sources.web.json"), *ex.read_json(HERE / "sources.telegram.json")]
    for item in items:
        item["region"] = REGIONS.get(item["region"], item["region"])
    return items


def package_dirs() -> dict[str, Path]:
    from jane_storage.adapters import package_dirs as storage_dirs

    result = {
        ex.read_json(p / "jane-package.json")["package_id"]: p
        for p in sorted(PACKAGES.iterdir())
        if p.is_dir()
    }
    for directory in storage_dirs().values():
        manifest = ex.read_json(directory / "jane-package.json")
        if manifest["package_id"] in ex.NEWS_STORAGE_PACKAGES:
            result[manifest["package_id"]] = directory
    return result


def check_packages() -> dict[str, dict[str, str]]:
    from jane_kit.schemas import ContractSchemas
    from jane_registry.archive import canonical_archive, digest_of, files_from_dir

    schemas = ContractSchemas(ROOT / "contracts")
    refs = {}
    for pid, directory in package_dirs().items():
        manifest = ex.read_json(directory / "jane-package.json")
        schemas.validate("package-manifest.schema.json", manifest)
        if manifest["kind"] == "collector-rules":
            schemas.validate("collector-rules.schema.json", ex.read_json(directory / "rules.json"))
        archive = canonical_archive(files_from_dir(directory))
        refs[pid] = {"package_id": pid, "version": manifest["version"], "digest": str(digest_of(archive))}
    for item in sources():
        schemas.validate("source.schema.json", source_doc(item, refs))
        schemas.validate("task-config.schema.json", task_doc(item, refs))
    return refs


def publish(svc: NewsServices, refs: dict[str, dict[str, str]]) -> None:
    from jane_registry.archive import canonical_archive, files_from_dir

    for pid, directory in package_dirs().items():
        manifest = ex.read_json(directory / "jane-package.json")
        svc.registry.call(
            "POST",
            "/v1/packages",
            ok=(201, 409),
            json={
                "package_id": pid,
                "kind": manifest["kind"],
                "title": manifest["title"],
                "description": manifest.get("description", ""),
                "auto_changes_allowed": False,
            },
            headers={"Idempotency-Key": ex.key()},
        )
        path = f"/v1/packages/{pid}/versions/{manifest['version']}"
        response = svc.registry.call(
            "POST",
            f"/v1/packages/{pid}/versions",
            ok=(201, 409),
            content=bytes(canonical_archive(files_from_dir(directory))),
            headers={"Content-Type": "application/zip", "Idempotency-Key": ex.key()},
        )
        version = response.json() if response.status_code == 201 else svc.registry.call("GET", path).json()
        if version["digest"] != refs[pid]["digest"]:
            raise ValueError(f"{pid}: an immutable version already has different contents; bump its version")
        if version["status"] == "draft":
            svc.registry.call(
                "POST",
                f"{path}/status",
                json={
                    "status": "approved",
                    "reason": "News package: offline contract, extraction and evidence tests passed.",
                },
                headers={"Idempotency-Key": ex.key()},
            )
        ex.log(f"package {pid}@{manifest['version']} approved")


def source_doc(item: dict[str, Any], refs: dict[str, dict[str, str]]) -> dict[str, Any]:
    return {
        "source_id": item["source_id"],
        "kind": "web",
        "title": item["title"],
        "description": f"Щогодинний розбір новин: {item['region']}; {item['transport']}; {item['url']}",
        "locator": {"url": item["url"]},
        "collector_rules": refs[item["rules_package_id"]],
        "limits": {
            "rate": {
                "requests_per_second_per_host": 1,
                "min_delay_ms_per_host": 1000,
                "respect_crawl_delay": True,
            },
            "concurrency": {"max_parallel_fetches_per_host": 1},
        },
        "expected_entity_types": ["news_article", "news_event"],
        "forward_unknown_to_llm": False,
        "labels": {"group": GROUP, "region": item["region"], "transport": item["transport"]},
    }


def task_doc(
    item: dict[str, Any],
    refs: dict[str, dict[str, str]],
    *,
    interval: int = 3600,
    max_articles: int = 3,
    max_posts: int = 3,
    enabled: bool = True,
    first_run_at: str | None = None,
    min_grouping_confidence: float = 0.75,
) -> dict[str, Any]:
    telegram = item["transport"] == "telegram_public_web"
    prep = item.get("extractor_package_id", "news.web-article")
    params = {"source_name": item["title"], "region": item["region"], "language": item["language"]}
    if telegram:
        params["max_posts"] = max_posts
    else:
        params["source_id"] = item["source_id"]
    return {
        "task_id": item["source_id"],
        "title": f"{item['title']}: аналіз новин щогодини",
        "enabled": enabled,
        "description": "RAW → текст → багатомовний LLM → перевірені цитати, тональність і події → PostgreSQL (results-news).",
        "input": {"source_id": item["source_id"]},
        "stages": [
            {
                "stage_id": "collect",
                "kind": "collect",
                "collector": {"collector": "web", "mode": "incremental"},
            },
            {
                "stage_id": "store-raw",
                "kind": "handler",
                "handler": refs["jane.storage-files"],
                "connections": {"target": ex.RAW_CONNECTION},
                "inputs": [{"from": "collect"}],
            },
            {
                "stage_id": "prepare",
                "kind": "handler",
                "handler": refs[prep],
                "params": params,
                "inputs": [{"from": "collect"}],
                "on_failure": "fail_run",
            },
            {
                "stage_id": "analyse",
                "kind": "handler",
                "handler": refs["news.article-analysis"],
                "inputs": [
                    {"from": "prepare", "when": {"field": "result.status", "op": "eq", "value": "success"}}
                ],
                "on_failure": "fail_run",
            },
            {
                "stage_id": "verify",
                "kind": "handler",
                "handler": refs["news.article-normalize"],
                "params": {
                    "source_id": item["source_id"],
                    "source_name": item["title"],
                    "region": item["region"],
                    "source_kind": "telegram" if telegram else "web",
                    "transport": "telegram_public_web" if telegram else "rss_article",
                    "min_grouping_confidence": min_grouping_confidence,
                },
                "inputs": [
                    {"from": "analyse", "when": {"field": "result.status", "op": "eq", "value": "success"}}
                ],
                "on_failure": "fail_run",
            },
            {
                "stage_id": "store-news",
                "kind": "handler",
                "handler": refs[ex.NEWS_RESULTS_PACKAGE],
                "connections": {"target": ex.NEWS_RESULTS_CONNECTION},
                "inputs": [
                    {"from": "verify", "when": {"field": "result.status", "op": "eq", "value": "success"}}
                ],
                "on_failure": "fail_run",
            },
        ],
        "schedule": {
            "type": "interval",
            "interval_seconds": interval,
            "timezone": "Europe/Kyiv",
            "overlap": "skip",
            **({"start_at": first_run_at} if first_run_at else {}),
        },
        "limits": {
            "crawl": {
                "max_depth": 1,
                "max_pages_per_run": 1 if telegram else max_articles + 1,
                "max_links_per_page": max_articles,
                "max_material_bytes": 2_000_000,
            },
            "transfer": {"inline_max_bytes": 2_000_000},
            "llm": {"max_input_tokens_per_request": 40000, "max_output_tokens_per_request": 8192},
            "concurrency": {"max_parallel_runs_per_task": 1, "max_parallel_stage_items": 1},
        },
        "forward_unknown_to_llm": False,
        "labels": {"group": GROUP, "region": item["region"], "transport": item["transport"]},
    }


def put_owned(api: ex.Api, collection: str, identity: str, doc: dict[str, Any]) -> None:
    response = api.call("GET", f"/v1/{collection}/{identity}", ok=(200, 404))
    if response.status_code == 404:
        api.call("POST", f"/v1/{collection}", ok=(201,), json=doc, headers={"Idempotency-Key": ex.key()})
    else:
        if response.json().get("labels", {}).get("group") != GROUP:
            raise ValueError(f"Refusing to replace unrelated {collection}/{identity}")
        api.call(
            "PUT", f"/v1/{collection}/{identity}", json=doc, headers={"If-Match": response.headers["ETag"]}
        )


def apply(
    svc: NewsServices, refs: dict[str, dict[str, str]], items: list[dict[str, Any]], ns: argparse.Namespace
) -> None:
    # Use existing managed storage connections; don't replace their credentials or configuration.
    for identity in (ex.RAW_CONNECTION, ex.NEWS_RESULTS_CONNECTION):
        svc.orchestrator.call("GET", f"/v1/connections/{identity}")
    for item in items:
        task = task_doc(
            item,
            refs,
            interval=ns.interval,
            max_articles=ns.max_articles,
            max_posts=ns.max_posts,
            first_run_at=ns.first_run_at,
            min_grouping_confidence=ns.min_grouping_confidence,
        )
        put_owned(svc.orchestrator, "sources", item["source_id"], source_doc(item, refs))
        validation = svc.orchestrator.call("POST", "/v1/task-validations", json=task).json()
        if not validation["valid"]:
            raise ValueError(f"{item['source_id']}: {validation['errors']}")
        put_owned(svc.orchestrator, "tasks", task["task_id"], task)
        ex.log(f"configured {task['task_id']} interval={ns.interval}s")


def start(svc: NewsServices, items: list[dict[str, Any]], *, exact: bool = False) -> dict[str, str]:
    result = {}
    for item in items:
        body: dict[str, Any] = {"reason": "News monitoring: real source verification"}
        if exact and item.get("article_url"):
            body["input_override"] = {"urls": [item["article_url"]]}
        response = svc.orchestrator.call(
            "POST",
            f"/v1/tasks/{item['source_id']}/runs",
            ok=(202,),
            json=body,
            headers={"Idempotency-Key": ex.key()},
        )
        result[item["source_id"]] = response.json()["job_id"]
        ex.log(f"started {item['source_id']} {result[item['source_id']]}")
    return result


def verify(svc: NewsServices, items: list[dict[str, Any]]) -> dict[str, Any]:
    report: dict[str, Any] = {
        "verified_at": datetime.now(UTC).isoformat(),
        "sources": [],
        "all_verified": True,
    }
    for item in items:
        task = svc.orchestrator.call("GET", f"/v1/tasks/{item['source_id']}").json()
        records = svc.storage.pages(
            "/v1/entities",
            {
                "connection_id": ex.NEWS_RESULTS_CONNECTION,
                "entity_type": "news_article",
                "scope": item["source_id"],
            },
        )
        runs = svc.orchestrator.call(
            "GET", "/v1/runs", params={"task_id": item["source_id"], "limit": 3}
        ).json()["items"]
        verified = [r for r in records if r.get("fields", {}).get("evidence_validation") == "verified"]
        entry: dict[str, Any] = {
            "source_id": item["source_id"],
            "title": item["title"],
            "region": item["region"],
            "transport": item["transport"],
            "enabled": task.get("enabled", True),
            "schedule": task["schedule"],
            "articles": len(records),
            "verified_articles": len(verified),
            "latest_runs": [
                {k: r.get(k) for k in ("run_id", "status", "trigger", "created_at", "counters")} for r in runs
            ],
            "samples": [
                {
                    k: r["fields"].get(k)
                    for k in (
                        "url",
                        "headline",
                        "headline_ukrainian",
                        "source_name",
                        "sentiment",
                        "event_id",
                        "event_grouping",
                        "entities",
                        "evidence_validation",
                    )
                }
                for r in verified[:2]
            ],
        }
        entry["verified"] = (
            bool(verified) and task.get("enabled", True) and task["schedule"].get("interval_seconds") == 3600
        )
        report["sources"].append(entry)
        report["all_verified"] = report["all_verified"] and entry["verified"]
        ex.log(f"{item['source_id']}: {len(verified)} verified articles; enabled={entry['enabled']}")
    events = svc.storage.pages(
        "/v1/entities",
        {"connection_id": ex.NEWS_RESULTS_CONNECTION, "entity_type": "news_event", "scope": "news-events"},
    )
    report["events"] = len(events)
    return report


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "apply", "run", "verify", "export"))
    parser.add_argument("--stack-file", type=Path)
    parser.add_argument("--only", nargs="*", help="Selected news source IDs")
    parser.add_argument("--interval", type=int, default=3600)
    parser.add_argument("--max-articles", type=int, default=3)
    parser.add_argument("--max-posts", type=int, default=3)
    parser.add_argument("--first-run-at", help="Optional ISO8601 initial scheduled scan time")
    parser.add_argument("--min-grouping-confidence", type=float, default=0.75)
    parser.add_argument(
        "--exact", action="store_true", help="First-run override: one verified live article URL per site"
    )
    parser.add_argument("--output", type=Path)
    ns = parser.parse_args(argv)
    refs = check_packages()
    items = [item for item in sources() if not ns.only or item["source_id"] in ns.only]
    if ns.command in {"check", "export"}:
        output: dict[str, Any] = {
            "packages": refs,
            "sources": [source_doc(item, refs) for item in items],
            "tasks": [
                task_doc(
                    item,
                    refs,
                    interval=ns.interval,
                    max_articles=ns.max_articles,
                    max_posts=ns.max_posts,
                    first_run_at=ns.first_run_at,
                    min_grouping_confidence=ns.min_grouping_confidence,
                )
                for item in items
            ],
        }
        if ns.output:
            ns.output.parent.mkdir(parents=True, exist_ok=True)
            ex.write_json(ns.output, output)
        print(f"Validated {len(refs)} packages and {len(items)} sources/tasks")
        return 0
    if ns.stack_file is None:
        parser.error("--stack-file is required for live commands")
    svc = NewsServices.of_stack(ns.stack_file)
    try:
        if ns.command == "apply":
            publish(svc, refs)
            apply(svc, refs, items, ns)
            return 0
        output = start(svc, items, exact=ns.exact) if ns.command == "run" else verify(svc, items)
        if ns.output:
            ns.output.parent.mkdir(parents=True, exist_ok=True)
            ex.write_json(ns.output, output)
        return 0 if ns.command == "run" or output["all_verified"] else 1
    finally:
        svc.close()


if __name__ == "__main__":
    raise SystemExit(main())
