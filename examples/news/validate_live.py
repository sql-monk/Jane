"""Validate real news through autonomous service APIs, with durable checkpoints."""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import httpx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import setup_news as news  # noqa: E402

import jane_examples as ex  # noqa: E402

PAIR_BBC_URL = "https://www.bbc.co.uk/news/articles/cw33x4y8k82no"
PAIR_SOURCES = {"news-web-bbc", "news-web-npr"}


def save(path: Path, document: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def prepared_content_binding(previous: list[dict[str, Any]], current: list[dict[str, Any]]) -> str:
    """Compare every prepared field, never a subset of quotes or a topic signature."""
    before = [entity["fields"] for entity in previous]
    after = [entity["fields"] for entity in current]
    original_encoded = json.dumps(before, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    encoded = json.dumps(after, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if not before or original_encoded != encoded:
        raise ValueError("Prepared article fields changed; cached analysis cannot be reused")
    return hashlib.sha256(encoded).hexdigest()


def local_package(package_id: str, analysis_profile: str = "cheap") -> tuple[dict[str, str], dict[str, Any]]:
    from jane_registry.archive import canonical_archive, digest_of, files_from_dir

    directory = news.package_dirs()[package_id]
    manifest = ex.read_json(directory / "jane-package.json")
    files = files_from_dir(directory)
    if package_id == "news.article-analysis" and analysis_profile != "cheap":
        manifest["provenance"]["based_on"] = {"package_id": package_id, "version": manifest["version"]}
        package_id += f".validation-{analysis_profile}"
        manifest["package_id"] = package_id
        manifest["entry"]["model"] = analysis_profile
        manifest["provenance"]["change_summary"] = (
            "Explicit validation profile; production instructions/schema unchanged."
        )
        files["jane-package.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode(
            "utf-8"
        )
    archive = bytes(canonical_archive(files))
    reference = {
        "package_id": package_id,
        "version": manifest["version"],
        "digest": str(digest_of(archive)),
    }
    content = {
        "kind": "inline",
        "media_type": "application/zip",
        "encoding": "base64",
        "data": base64.b64encode(archive).decode("ascii"),
        "size_bytes": len(archive),
        "sha256": hashlib.sha256(archive).hexdigest(),
    }
    return reference, content


class Validation:
    def __init__(self, ns: argparse.Namespace) -> None:
        self.ns = ns
        stack = ex.read_json(ns.stack_file)
        services = stack["services"]
        proxy = str(services.get("proxy", {}).get("url") or "")
        if urlsplit(proxy).scheme not in {"http", "https"} or not urlsplit(proxy).hostname:
            raise ValueError("Live validation requires the existing stack proxy URL")
        token = services.get("auth", {}).get("admin_api_key") or stack.get("env", {}).get(
            "JANE_API_KEY_ADMIN"
        )
        self.apis = {
            name: ex.Api(f"{proxy.rstrip('/')}/api/{service}", contract, timeout_s=ns.timeout, token=token)
            for name, service, contract in (
                ("collector", "web-collector", "collector"),
                ("runtime", "handler-runtime", "handler"),
                ("llm", "llm", "handler"),
                ("gateway", "llm", "llm"),
                ("storage", "storage", "handler"),
                ("storage_read", "storage", "storage"),
            )
        }
        self.cache: Path = ns.cache_dir
        self.cache.mkdir(parents=True, exist_ok=True)
        metadata = self.cache / "session.json"
        if metadata.exists():
            self.session = ex.read_json(metadata)
            if self.session.get("proxy_url") != proxy:
                raise ValueError("The cache belongs to another proxy URL; use a fresh --cache-dir")
        else:
            self.session = {
                "run_id": "news-validation-" + uuid.uuid4().hex,
                "created_at": datetime.now(UTC).isoformat(),
                "proxy_url": proxy,
                "delivery": "autonomous API validation; scheduled task execution is checked separately",
            }
            save(metadata, self.session)
        request_config = {
            "max_posts": ns.max_posts,
            "max_material_bytes": ns.max_material_bytes,
            "max_input_tokens": ns.max_input_tokens,
            "max_output_tokens": ns.max_output_tokens,
            "min_grouping_confidence": ns.min_grouping_confidence,
            "analysis_profile": ns.analysis_profile,
        }
        self.session["request_config"] = request_config
        save(metadata, self.session)
        self.requested_source_ids: set[str] = set()
        self.packages: dict[str, tuple[dict[str, str], dict[str, Any]]] = {}

    def close(self) -> None:
        for api in self.apis.values():
            api.close()

    def call(self, api: Any, method: str, path: str, *, ok: tuple[int, ...] = (200,), **kwargs: Any) -> Any:
        if "json" in kwargs:
            api.client.spec.validate_request(method, path, kwargs["json"])
        for attempt in range(self.ns.request_attempts):
            try:
                response = api.http.request(method, path, **kwargs)
            except httpx.TransportError:
                if attempt + 1 == self.ns.request_attempts:
                    raise
                time.sleep(self.ns.retry_delay)
                continue
            if response.status_code in {502, 503, 504} and attempt + 1 < self.ns.request_attempts:
                time.sleep(self.ns.retry_delay)
                continue
            try:
                body = response.json() if response.content else None
            except ValueError:
                body = response.text
            api.client.spec.validate_response(
                method, path, response.status_code, body, response.headers.get("content-type")
            )
            if response.status_code not in ok:
                raise RuntimeError(f"{method} {path} -> {response.status_code}: {response.text[:2000]}")
            return response
        raise AssertionError("request_attempts must be positive")

    def pages(self, api: Any, path: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        cursor: str | None = None
        while True:
            query = {**params, "limit": 500, **({"cursor": cursor} if cursor else {})}
            document = self.call(api, "GET", path, params=query).json()
            result.extend(document["items"])
            cursor = document.get("next_cursor")
            if not cursor:
                return result

    def invoke(
        self,
        service: str,
        package_id: str,
        inputs: list[dict[str, Any]],
        item: dict[str, Any],
        stage: str,
        *,
        params: dict[str, Any] | None = None,
        connections: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        if package_id not in self.packages:
            self.packages[package_id] = local_package(package_id, self.ns.analysis_profile)
        reference, archive = self.packages[package_id]
        generation = self.ns.analysis_generation if stage in {"analyse", "verify", "store-news"} else ""
        identity = (
            "|".join((self.session["run_id"], item["source_id"], stage, reference["digest"], generation))
            if generation
            else "|".join((self.session["run_id"], item["source_id"], stage, reference["digest"]))
        )
        delivery_key = hashlib.sha256(identity.encode("utf-8")).hexdigest()
        invocation = {
            "handler": reference,
            "package_archive": archive,
            "inputs": inputs,
            "params": params or {},
            "connections": connections or {},
            "context": {
                "trace": {
                    "trace_id": hashlib.sha256(self.session["run_id"].encode("utf-8")).hexdigest()[:32],
                    "run_id": self.session["run_id"],
                    "task_id": item["source_id"],
                    "source_id": item["source_id"],
                    "stage_id": stage,
                },
                "test_mode": False,
                "requested_by": "news-live-validation",
            },
            "delivery": {"delivery_key": delivery_key},
            "limits": {
                "transfer": {"inline_max_bytes": self.ns.max_material_bytes},
                "llm": {
                    "max_input_tokens_per_request": self.ns.max_input_tokens,
                    "max_output_tokens_per_request": self.ns.max_output_tokens,
                },
            },
            "mode": "async",
        }
        original_checkpoint = self.cache / item["source_id"] / f"{stage}.json"
        suffix = (
            f"-{self.ns.analysis_generation}"
            if self.ns.analysis_generation and stage in {"analyse", "verify", "store-news"}
            else ""
        )
        checkpoint = original_checkpoint.with_name(f"{stage}{suffix}.json")
        if (
            stage == "analyse"
            and self.ns.reuse_cached_analysis
            and original_checkpoint.exists()
            and not checkpoint.exists()
        ):
            previous = ex.read_json(original_checkpoint)
            result = self.successful_result(stage, previous["result"])
            expected_material = inputs[0]["material"]["material_id"]
            expected_urls = {entity["fields"]["url"] for entity in inputs[0]["entities"]}
            actual_entities = result.get("output", {}).get("entities", [])
            if not actual_entities or any(
                entity.get("observation", {}).get("material_id") != expected_material
                or entity.get("fields", {}).get("url") not in expected_urls
                for entity in actual_entities
            ):
                raise ValueError(
                    "Cached analysis does not belong to the same prepared article and original material"
                )
            return result
        request_sha256 = hashlib.sha256(
            json.dumps(invocation, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        if checkpoint.exists():
            cached = ex.read_json(checkpoint)
            if cached.get("package") != reference:
                raise ValueError(f"{stage}: package changed after checkpoint; use a fresh --cache-dir")
            if cached.get("request_sha256") not in (None, request_sha256):
                raise ValueError(f"{stage}: input or parameters changed; use a fresh --cache-dir")
            if cached.get("request_sha256") is None:
                if not self.ns.adopt_legacy_checkpoints:
                    raise ValueError(
                        f"{stage}: checkpoint lacks request binding; explicit legacy adoption is required"
                    )
                cached["request_sha256"] = request_sha256
                save(checkpoint, cached)
            if "result" in cached:
                return self.successful_result(stage, cached["result"])
        else:
            cached = {"package": reference, "delivery_key": delivery_key, "request_sha256": request_sha256}
            save(checkpoint, cached)
        api = self.apis[service]
        if "job_id" not in cached:
            response = self.call(
                api,
                "POST",
                "/v1/invocations",
                ok=(200, 202),
                json=invocation,
                headers={"Idempotency-Key": delivery_key},
            )
            body = response.json()
            if response.status_code == 200:
                cached["result"] = body
            else:
                cached["job_id"] = body["job_id"]
            save(checkpoint, cached)
        deadline = time.monotonic() + self.ns.job_timeout
        while "result" not in cached:
            job = self.call(api, "GET", f"/v1/jobs/{cached['job_id']}").json()
            if job["status"] == "succeeded":
                if not isinstance(job.get("result"), dict):
                    raise ValueError(f"{stage}: completed job has no inline HandlerResult")
                cached["result"] = job["result"]
                save(checkpoint, cached)
                break
            if job["status"] in {"failed", "cancelled"}:
                error = job.get("error") or {}
                recovery = int(cached.get("pure_recoveries", 0))
                if (
                    service == "runtime"
                    and stage in {"prepare", "verify"}
                    and error.get("status") == 503
                    and error.get("retryable")
                    and recovery < self.ns.pure_job_recoveries
                ):
                    recovery += 1
                    recovery_key = hashlib.sha256(
                        f"{delivery_key}|confirmed-503|{recovery}".encode()
                    ).hexdigest()
                    recovered = {**invocation, "delivery": {"delivery_key": recovery_key}}
                    response = self.call(
                        api,
                        "POST",
                        "/v1/invocations",
                        ok=(200, 202),
                        json=recovered,
                        headers={"Idempotency-Key": recovery_key},
                    )
                    cached.setdefault("failed_jobs", []).append({"job_id": cached["job_id"], "error": error})
                    cached["pure_recoveries"] = recovery
                    body = response.json()
                    if response.status_code == 200:
                        cached["result"] = body
                    else:
                        cached["job_id"] = body["job_id"]
                    save(checkpoint, cached)
                    deadline = time.monotonic() + self.ns.job_timeout
                    continue
                raise ValueError(f"{stage}: job {job['status']}: {job.get('error')}")
            if time.monotonic() > deadline:
                raise TimeoutError(f"{stage}: job remains {job['status']}; checkpoint retained for resume")
            time.sleep(self.ns.poll_seconds)
        return self.successful_result(stage, cached["result"])

    @staticmethod
    def successful_result(stage: str, document: dict[str, Any]) -> dict[str, Any]:
        result = dict(document)
        if result.get("status") != "success":
            raise ValueError(
                f"{stage}: {result.get('status')}: {result.get('failure') or result.get('unrecognized')}"
            )
        return result

    def fetch(self, item: dict[str, Any]) -> dict[str, Any]:
        checkpoint = self.cache / item["source_id"] / "material.json"
        rules = ex.read_json(news.PACKAGES / item["rules_package_id"] / "rules.json")
        body = {
            "source_kind": "web",
            "source_id": item["source_id"],
            "url": item.get("article_url") or item["url"],
            "rules": rules,
            "content_delivery": "inline",
            "limits": {
                "crawl": {"max_material_bytes": self.ns.max_material_bytes},
                "transfer": {"inline_max_bytes": self.ns.max_material_bytes},
            },
        }
        request_checkpoint = checkpoint.with_name("fetch-request.json")
        if request_checkpoint.exists() and ex.read_json(request_checkpoint) != body:
            raise ValueError("Source URL or fetch rules changed after checkpoint; use a fresh --cache-dir")
        if checkpoint.exists():
            if not request_checkpoint.exists() and not self.ns.adopt_legacy_checkpoints:
                raise ValueError("Cached fetch lacks request binding; explicit legacy adoption is required")
            material = dict(ex.read_json(checkpoint))
            if material.get("locator", {}).get("url") != body["url"]:
                raise ValueError("Cached material belongs to another source URL; use a fresh --cache-dir")
            save(request_checkpoint, body)
            return material
        save(request_checkpoint, body)
        material = self.call(self.apis["collector"], "POST", "/v1/fetches", json=body).json()
        save(checkpoint, material)
        return dict(material)

    def source(self, item: dict[str, Any]) -> dict[str, Any]:
        material = self.fetch(item)
        raw = self.invoke(
            "storage",
            "jane.storage-files",
            [{"kind": "material", "material": material}],
            item,
            "store-raw",
            connections={"target": "raw-files"},
        )
        raw_writes = raw.get("output", {}).get("writes", [])
        if not any(
            write.get("status") in {"written", "duplicate"}
            and write.get("object", {}).get("sha256") == material["content"]["sha256"]
            and write.get("object", {}).get("size_bytes") == material["content"]["size_bytes"]
            and write.get("target", {}).get("connection_id") == "raw-files"
            for write in raw_writes
        ):
            raise ValueError("RAW storage did not acknowledge the same original material")
        telegram = item["transport"] == "telegram_public_web"
        params = {"source_name": item["title"], "region": item["region"], "language": item["language"]}
        if telegram:
            params["max_posts"] = self.ns.max_posts
        else:
            params["source_id"] = item["source_id"]
        prepared = self.invoke(
            "runtime",
            item.get("extractor_package_id", "news.web-article"),
            [{"kind": "material", "material": material}],
            item,
            "prepare",
            params=params,
        )
        entities = prepared.get("output", {}).get("entities") or []
        if not entities:
            raise ValueError("prepare: no article entities")
        if self.ns.stop_before_llm:
            return {"source_id": item["source_id"], "prepared_articles": len(entities), "status": "prepared"}
        reuse = self.reused_analysis(item, entities, material)
        analyzed = (
            reuse[0]
            if reuse
            else self.invoke(
                "llm",
                "news.article-analysis",
                [
                    {
                        "kind": "entities",
                        "entities": entities,
                        "material": material,
                        "from_invocation_id": prepared["invocation_id"],
                    }
                ],
                item,
                "analyse",
            )
        )
        verified = self.invoke(
            "runtime",
            "news.article-normalize",
            [
                {
                    "kind": "entities",
                    "entities": analyzed["output"]["entities"],
                    "material": material,
                    "from_invocation_id": analyzed["invocation_id"],
                }
            ],
            item,
            "verify",
            params={
                "source_id": item["source_id"],
                "source_name": item["title"],
                "region": item["region"],
                "source_kind": "telegram" if telegram else "web",
                "transport": "telegram_public_web" if telegram else "rss_article",
                "min_grouping_confidence": self.ns.min_grouping_confidence,
            },
        )
        stored = self.invoke(
            "storage",
            ex.NEWS_RESULTS_PACKAGE,
            [
                {
                    "kind": "entities",
                    "entities": verified["output"]["entities"],
                    "material": material,
                    "from_invocation_id": verified["invocation_id"],
                }
            ],
            item,
            "store-news",
            connections={"target": ex.NEWS_RESULTS_CONNECTION},
        )
        expected = {
            entity["fields"]["url"]
            for entity in verified["output"]["entities"]
            if entity["entity_type"] == "news_article"
        }
        current = self.pages(
            self.apis["storage_read"],
            "/v1/entities",
            {
                "connection_id": ex.NEWS_RESULTS_CONNECTION,
                "entity_type": "news_article",
                "scope": item["source_id"],
            },
        )
        matched = [record for record in current if record.get("fields", {}).get("url") in expected]
        if {record["fields"]["url"] for record in matched} != expected or not expected:
            raise ValueError("Stored news articles are absent from the public storage read API")
        if any(record["fields"].get("evidence_validation") != "verified" for record in matched):
            raise ValueError("Stored news articles include unverified evidence")
        receipt = {
            "source_id": item["source_id"],
            "title": item["title"],
            "region": item["region"],
            "transport": item["transport"],
            "status": "verified",
            "analysis_profile": (
                analyzed["handler"]["package_id"].split(".validation-", 1)[1]
                if ".validation-" in analyzed["handler"]["package_id"]
                else "cheap"
            ),
            "cached_analysis_reuse": reuse[1] if reuse else None,
            "validation_run_id": self.session["run_id"],
            "verified_at": datetime.now(UTC).isoformat(),
            "material_id": material["material_id"],
            "observation_id": material["observation_id"],
            "fetched_at": material["fetched_at"],
            "original": {
                "url": material["locator"]["url"],
                "final_url": material["locator"].get("final_url"),
                "sha256": material["content"]["sha256"],
                "size_bytes": material["content"]["size_bytes"],
                "format": material.get("format"),
                "http_status": material.get("http", {}).get("status"),
            },
            "prepared_articles": len(entities),
            "verified_articles": len(matched),
            "invocations": {
                "store-raw": raw["invocation_id"],
                "prepare": prepared["invocation_id"],
                "analyse": analyzed["invocation_id"],
                "verify": verified["invocation_id"],
                "store-news": stored["invocation_id"],
            },
            "packages": [
                raw["handler"],
                prepared["handler"],
                analyzed["handler"],
                verified["handler"],
                stored["handler"],
            ],
            "raw_writes": raw_writes,
            "llm_usage": analyzed.get("usage", {}).get("llm"),
            "jobs": self.jobs_for_receipt(
                self.cache / item["source_id"],
                {
                    "store-raw": raw["invocation_id"],
                    "prepare": prepared["invocation_id"],
                    "analyse": analyzed["invocation_id"],
                    "verify": verified["invocation_id"],
                    "store-news": stored["invocation_id"],
                },
            ),
            "articles": [
                {
                    key: record["fields"].get(key)
                    for key in (
                        "url",
                        "headline",
                        "headline_ukrainian",
                        "summary",
                        "source_language",
                        "published_at",
                        "sentiment",
                        "entities",
                        "event",
                        "event_id",
                        "event_grouping",
                        "evidence_validation",
                    )
                }
                for record in matched
            ],
        }
        if reuse and reuse[1].get("original_job_id"):
            receipt["jobs"]["analyse"] = reuse[1]["original_job_id"]
        save(self.cache / item["source_id"] / "receipt.json", receipt)
        return receipt

    def reused_analysis(
        self, item: dict[str, Any], entities: list[dict[str, Any]], material: dict[str, Any]
    ) -> tuple[dict[str, Any], dict[str, Any]] | None:
        if not self.ns.reuse_analysis_from:
            return None
        for directory in reversed(self.ns.reuse_analysis_from):
            source = directory / item["source_id"]
            if not (source / "analyse.json").exists():
                continue
            prepared = self.successful_result("prepare", ex.read_json(source / "prepare.json")["result"])
            digest = prepared_content_binding(prepared["output"]["entities"], entities)
            original_material = ex.read_json(source / "material.json")
            if original_material["locator"]["url"] != material["locator"]["url"]:
                raise ValueError("Cached analysis belongs to another original source URL")
            analysis_checkpoint = ex.read_json(source / "analyse.json")
            result = copy.deepcopy(self.successful_result("analyse", analysis_checkpoint["result"]))
            records = result.get("output", {}).get("entities") or []
            if not records:
                raise ValueError("Cached analysis produced no news articles")
            original_observations = [copy.deepcopy(record.get("observation", {})) for record in records]
            observation = {
                "observation_id": material["observation_id"],
                "observed_at": material["fetched_at"],
                "material_id": material["material_id"],
                "content_sha256": material["content"]["sha256"],
            }
            for record in records:
                if record.get("observation", {}).get("material_id") != original_material["material_id"]:
                    raise ValueError("Cached analysis material provenance does not match its original RAW")
                record["observation"] = dict(observation)
            return result, {
                "kind": "identical_prepared_fields",
                "original_invocation_id": result["invocation_id"],
                "original_job_id": analysis_checkpoint.get("job_id"),
                "original_handler": result["handler"],
                "original_observations": original_observations,
                "original_raw_objects": [
                    write["object"]
                    for write in ex.read_json(source / "store-raw.json")["result"]["output"]["writes"]
                    if write.get("object", {}).get("sha256") == original_material["content"]["sha256"]
                ],
                "original_raw_sha256": original_material["content"]["sha256"],
                "fresh_raw_sha256": material["content"]["sha256"],
                "prepared_fields_sha256": digest,
                "llm_called_on_fresh_raw": False,
            }
        raise ValueError("No successful original analysis exists in --reuse-analysis-from")

    @staticmethod
    def jobs_for_receipt(directory: Path, invocations: dict[str, str]) -> dict[str, str]:
        jobs = {}
        for checkpoint in directory.glob("*.json"):
            if checkpoint.stem in {"material", "receipt", "fetch-request"}:
                continue
            document = ex.read_json(checkpoint)
            invocation_id = document.get("result", {}).get("invocation_id")
            if document.get("job_id"):
                for stage, expected in invocations.items():
                    if invocation_id == expected:
                        jobs[stage] = document["job_id"]
        return jobs

    def read_receipt(self, source_id: str) -> dict[str, Any]:
        for directory in reversed([self.cache, *self.ns.additional_receipts]):
            path = directory / source_id / "receipt.json"
            if not path.exists():
                continue
            receipt = dict(ex.read_json(path))
            receipt["jobs"] = self.jobs_for_receipt(path.parent, receipt.get("invocations", {}))
            reuse = receipt.get("cached_analysis_reuse") or {}
            if reuse.get("original_job_id"):
                receipt["jobs"]["analyse"] = reuse["original_job_id"]
            receipt["validation_run_id"] = (
                receipt.get("validation_run_id") or ex.read_json(directory / "session.json")["run_id"]
            )
            expected = {article["url"]: article for article in receipt.get("articles", [])}
            records = self.pages(
                self.apis["storage_read"],
                "/v1/entities",
                {
                    "connection_id": ex.NEWS_RESULTS_CONNECTION,
                    "entity_type": "news_article",
                    "scope": source_id,
                },
            )
            current = {
                record["fields"]["url"]: record["fields"]
                for record in records
                if record.get("fields", {}).get("url") in expected
            }
            if not expected or set(current) != set(expected):
                raise ValueError("Receipt articles are absent from the current public storage API")
            for url, article in current.items():
                if article.get("evidence_validation") != "verified" or article.get("event_id") != expected[
                    url
                ].get("event_id"):
                    raise ValueError("Stored verification or event identity changed after the recorded chain")
            receipt["storage_rechecked_at"] = datetime.now(UTC).isoformat()
            return receipt
        raise ValueError("No completed source receipt exists")

    def report(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        pair = [
            item
            for item in results
            if item.get("source_id") in PAIR_SOURCES and item.get("status") == "verified"
        ]
        event_ids = {
            article["event_id"]
            for item in pair
            for article in item.get("articles", [])
            if article.get("event_id")
        }
        pair_verified = (
            len(pair) == 2
            and len(event_ids) == 1
            and all(
                any(article.get("event_id") in event_ids for article in item.get("articles", []))
                for item in pair
            )
        )
        complete = {item["source_id"] for item in results} == self.requested_source_ids
        stored_events: list[dict[str, Any]] = []
        if complete and pair_verified:
            records = self.pages(
                self.apis["storage_read"],
                "/v1/entities",
                {
                    "connection_id": ex.NEWS_RESULTS_CONNECTION,
                    "entity_type": "news_event",
                    "scope": "news-events",
                },
            )
            stored_events = [
                {
                    key: record["fields"].get(key)
                    for key in (
                        "event_id",
                        "canonical",
                        "identity_kind",
                        "grouping_method",
                        "identity_confidence",
                    )
                }
                for record in records
                if record.get("fields", {}).get("event_id") in event_ids
            ]
            pair_verified = {event["event_id"] for event in stored_events} == event_ids
        cost = 0.0
        for directory in {self.cache.resolve(), *(value.resolve() for value in self.ns.additional_receipts)}:
            for checkpoint in directory.glob("*/analyse*.json"):
                usage = ex.read_json(checkpoint).get("result", {}).get("usage", {}).get("llm", {})
                if usage.get("cost", {}).get("currency") == "USD":
                    cost += float(usage["cost"]["amount"])
        return {
            **self.session,
            "verified_at": datetime.now(UTC).isoformat(),
            "requested_source_ids": sorted(self.requested_source_ids),
            "selected_sources": len(self.requested_source_ids),
            "completed_sources": len(results),
            "verified_sources": sum(item.get("status") == "verified" for item in results),
            "all_verified": complete
            and bool(results)
            and all(item.get("status") == "verified" for item in results),
            "sources": [self.public_receipt(item) for item in results],
            "total_llm_cost_usd": round(cost, 8),
            "real_cross_source_pair": {
                "requested": self.ns.pair and self.requested_source_ids >= PAIR_SOURCES,
                "verified": pair_verified,
                "source_ids": sorted(PAIR_SOURCES),
                "event_ids": sorted(event_ids),
                "stored_events": stored_events,
            },
        }

    @staticmethod
    def public_receipt(result: dict[str, Any]) -> dict[str, Any]:
        receipt = {key: value for key, value in result.items() if key != "articles"}
        if "raw_writes" in receipt:
            receipt["raw_writes"] = [
                {key: value for key, value in write.items() if key != "delivery_key"}
                for write in receipt["raw_writes"]
            ]
        receipt["articles"] = []
        for article in result.get("articles", []):
            value = {
                key: article.get(key)
                for key in (
                    "url",
                    "headline",
                    "headline_ukrainian",
                    "source_language",
                    "published_at",
                    "event_id",
                    "event_grouping",
                    "evidence_validation",
                )
            }
            value["sentiment"] = {
                key: article.get("sentiment", {}).get(key) for key in ("label", "confidence")
            }
            value["entities"] = [
                {
                    key: entity.get(key)
                    for key in ("name", "canonical_name", "type", "role", "attitude", "attitude_confidence")
                }
                for entity in article.get("entities", [])
            ]
            value["event_identity_kind"] = article.get("event", {}).get("identity_kind", "actor_action")
            value["event_identity_confidence"] = article.get("event", {}).get("identity_confidence")
            receipt["articles"].append(value)
        return receipt


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stack-file", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path, default=news.ROOT / ".jane/news-livevalidation")
    parser.add_argument("--output", type=Path, default=HERE / "verification.live.json")
    parser.add_argument("--only", nargs="*")
    parser.add_argument(
        "--pair", action="store_true", help="Use the same Riyadh airport event for BBC and NPR"
    )
    parser.add_argument("--stop-before-llm", action="store_true")
    parser.add_argument("--max-posts", type=int, default=1)
    parser.add_argument("--max-material-bytes", type=int, default=2_000_000)
    parser.add_argument("--max-input-tokens", type=int, default=40000)
    parser.add_argument("--max-output-tokens", type=int, default=8192)
    parser.add_argument("--timeout", type=float, default=120)
    parser.add_argument("--job-timeout", type=float, default=300)
    parser.add_argument("--poll-seconds", type=float, default=2)
    parser.add_argument("--request-attempts", type=int, default=4)
    parser.add_argument("--retry-delay", type=float, default=2)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Recheck completed receipts through storage reads; no collection, analysis or writes",
    )
    parser.add_argument(
        "--additional-receipts",
        type=Path,
        action="append",
        default=[],
        help="Overlay completed receipts from another validation cache",
    )
    parser.add_argument("--min-grouping-confidence", type=float, default=0.75)
    parser.add_argument(
        "--reuse-analysis-from",
        type=Path,
        action="append",
        default=[],
        help="Reuse an actual prior analysis only if all freshly prepared article fields are identical",
    )
    parser.add_argument(
        "--analysis-profile",
        choices=("cheap", "default", "strong"),
        default="cheap",
        help="A non-cheap choice creates a separately named self-contained validation package",
    )
    parser.add_argument(
        "--pure-job-recoveries",
        type=int,
        default=1,
        help="Reissue only confirmed runtime jobs failed with retryable 503",
    )
    parser.add_argument(
        "--analysis-generation",
        default="",
        help="Separate new analysis/verification checkpoints while retaining RAW/prepared inputs",
    )
    parser.add_argument(
        "--reuse-cached-analysis",
        action="store_true",
        help="Revalidate successful original analyses without a second LLM call",
    )
    parser.add_argument(
        "--adopt-legacy-checkpoints",
        action="store_true",
        help="Explicitly adopt this driver's pre-fingerprint checkpoints once",
    )
    ns = parser.parse_args(argv)
    if ns.analysis_generation and not all(
        character.isalnum() or character in "-." for character in ns.analysis_generation
    ):
        parser.error("--analysis-generation must contain letters, digits, dash or dot")
    selected = [item for item in news.sources() if not ns.only or item["source_id"] in ns.only]
    if ns.pair:
        for item in selected:
            if item["source_id"] == "news-web-bbc":
                item["article_url"] = PAIR_BBC_URL
    validation = Validation(ns)
    validation.requested_source_ids = {item["source_id"] for item in selected}
    results = []
    try:

        def execute(item: dict[str, Any]) -> dict[str, Any]:
            ex.log(f"direct validation {item['source_id']} starting")
            try:
                result = (
                    validation.read_receipt(item["source_id"]) if ns.report_only else validation.source(item)
                )
            except Exception as exc:
                result = {
                    "source_id": item["source_id"],
                    "status": "failed",
                    "error_type": type(exc).__name__,
                    "error": str(exc)[:2000],
                }
            ex.log(f"direct validation {item['source_id']}: {result['status']}")
            return result

        with ThreadPoolExecutor(max_workers=ns.workers) as pool:
            futures = [pool.submit(execute, item) for item in selected]
            for future in as_completed(futures):
                results.append(future.result())
                save(ns.output, validation.report(results))
        report = validation.report(results)
        save(ns.output, report)
        if ns.stop_before_llm:
            return 0 if all(item["status"] == "prepared" for item in results) else 1
        return (
            0
            if report["all_verified"]
            and (
                not report["real_cross_source_pair"]["requested"]
                or report["real_cross_source_pair"]["verified"]
            )
            else 1
        )
    finally:
        validation.close()


if __name__ == "__main__":
    raise SystemExit(main())
