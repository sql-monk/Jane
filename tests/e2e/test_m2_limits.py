"""S-M2-09: changed limits reach a real collector on the next orchestrated run."""

from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from typing import Any

import pytest

from jane_e2e.clients import JaneClient
from jane_e2e.orchestration import TESTSITE, create_source, create_task, m1_task, start_run, wait_run
from jane_e2e.verify import site_paths


@pytest.mark.criteria(13)
@pytest.mark.milestone("M2")
def test_s_m2_09_platform_and_task_page_limits_apply_without_rebuild(
    orchestrated: JaneClient,
    client: Callable[..., JaneClient],
    extractor: dict[str, Any],
    run_id: str,
) -> None:
    """Platform 1 page, then task 2 pages; both values must affect real collection."""
    orch = orchestrated.api("orchestrator")
    collector = client("web-collector").api("collector")
    source_id, task_id = f"e2e-{run_id}-limits", f"e2e-{run_id}-limits"
    urls = [TESTSITE + path for path in site_paths("product")[:3]]
    assert len(urls) == 3

    original = orch.get("/v1/limits/platform")
    assert original.status_code == 200, original.text
    original_doc = original.json()
    current_etag = original.headers["etag"]
    try:
        platform_doc = deepcopy(original_doc)
        platform_doc.setdefault("defaults", {}).setdefault("crawl", {})["max_pages_per_run"] = 1
        changed = orch.put("/v1/limits/platform", json=platform_doc, headers={"If-Match": current_etag})
        assert changed.status_code == 200, changed.text
        current_etag = changed.headers["etag"]

        create_source(orchestrated, source_id)
        create_task(orchestrated, m1_task(task_id, source_id, urls, extractor))
        effective = orch.get("/v1/limits/effective", params={"task_id": task_id, "stage_id": "collect"})
        assert effective.status_code == 200, effective.text
        assert effective.json()["limits"]["crawl"]["max_pages_per_run"] == 1
        assert effective.json()["provenance"]["crawl.max_pages_per_run"] == "platform"

        first = wait_run(orchestrated, start_run(orchestrated, task_id))
        assert first["status"] == "succeeded", first
        assert first["counters"]["materials"] == 1, first
        first_collection = collector.get(f"/v1/collections/{first['collection_id']}")
        assert first_collection.status_code == 200, first_collection.text
        assert first_collection.json()["stats"]["fetched"] == 1
        assert first_collection.json()["effective_limits"]["crawl"]["max_pages_per_run"] == 1

        task = orch.get(f"/v1/tasks/{task_id}")
        assert task.status_code == 200, task.text
        task_doc = task.json()
        task_doc["limits"] = {**task_doc.get("limits", {}), "crawl": {"max_pages_per_run": 2}}
        updated = orch.put(f"/v1/tasks/{task_id}", json=task_doc, headers={"If-Match": task.headers["etag"]})
        assert updated.status_code == 200, updated.text
        effective = orch.get("/v1/limits/effective", params={"task_id": task_id, "stage_id": "collect"})
        assert effective.status_code == 200, effective.text
        assert effective.json()["limits"]["crawl"]["max_pages_per_run"] == 2
        assert effective.json()["provenance"]["crawl.max_pages_per_run"] == "task"

        second = wait_run(orchestrated, start_run(orchestrated, task_id))
        assert second["status"] == "succeeded", second
        assert second["counters"]["materials"] == 2, second
        second_collection = collector.get(f"/v1/collections/{second['collection_id']}")
        assert second_collection.status_code == 200, second_collection.text
        assert second_collection.json()["stats"]["fetched"] == 2
        assert second_collection.json()["effective_limits"]["crawl"]["max_pages_per_run"] == 2
    finally:
        restored = orch.put("/v1/limits/platform", json=original_doc, headers={"If-Match": current_etag})
        assert restored.status_code == 200, restored.text
