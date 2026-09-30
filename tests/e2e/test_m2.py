"""M2 scenarios on the services already merged into main (docs/acceptance/scenarios.md).

S-M2-05a: the unknown-page part of criterion 11 on the real assistant (WP-11) and the real LLM gateway (WP-10)
with the deterministic `fake` provider (SUBSTITUTE of the external LLM). The orchestrator-driven variant S-M2-05
(routing of unknown materials in a task) is added when WP-09 is merged.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

from jane_e2e.clients import JaneClient
from jane_e2e.materials import fetch_page, standin_web_material
from jane_e2e.stack import E2EStack

pytestmark = [pytest.mark.e2e, pytest.mark.milestone("M2")]

UNKNOWN_PAGE = "/pages/event-spring-meetup"  # page_types: unknown (expected_urls.json)


def _llm_requests(llm: JaneClient) -> int:
    r = llm.api("llm").get("/v1/usage", params={"group_by": "purpose"})
    assert r.status_code == 200, r.text
    return int(r.json()["totals"]["requests"])


def _unknown_request(material: dict[str, Any], run_id: str, flag: bool) -> dict[str, Any]:
    return {
        "source_id": material["source"]["source_id"],
        "task_id": f"e2e-task-{run_id}",
        "forward_unknown_to_llm": flag,
        "material": material,
    }


@pytest.mark.criteria(11)
def test_s_m2_05a_unknown_page_goes_to_llm_only_with_flag(
    stack: E2EStack, require: Callable[..., None], client: Callable[..., JaneClient], run_id: str
) -> None:
    """Flag off: 403 access_denied_by_policy and no LLM call; flag on: the assistant calls the LLM gateway."""
    require("testsite", "llm", "assistant")
    assistant, llm = client("assistant"), client("llm")
    page = fetch_page(stack.url("testsite") + UNKNOWN_PAGE)
    assert 'content="unknown"' in page.text  # <meta name="jane:page-type" content="unknown">
    material = standin_web_material(page, source_id=f"e2e-{run_id}", observation_id=f"obs_e2e_{run_id}")

    before = _llm_requests(llm)
    off = assistant.api("assistant").post(
        "/v1/unknown-materials",
        json=_unknown_request(material, run_id, flag=False),
        headers={"Idempotency-Key": f"e2e-{run_id}-off"},
    )
    assert off.status_code == 403, off.text
    assert off.json()["code"] == "access_denied_by_policy"
    assert _llm_requests(llm) == before, "LLM was called although forward_unknown_to_llm is off"

    on = assistant.api("assistant").post(
        "/v1/unknown-materials",
        json=_unknown_request(material, run_id, flag=True),
        headers={"Idempotency-Key": f"e2e-{run_id}-on"},
    )
    assert on.status_code == 202, on.text
    job = assistant.wait_job("assistant", on.json()["job_id"])
    assert job["status"] == "succeeded", job
    assert _llm_requests(llm) > before, "flag on, but the LLM gateway saw no request"
