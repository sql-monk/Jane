"""Running package tests through handler-runtime (``handler.v1`` ``POST /v1/test-runs``).

Drafts that are not published yet are sent as an inline archive (``package_archive``, base64 zip
up to ``limits.transfer.inline_max_bytes``); published versions by reference. Test runs never write
working data (``test_mode``). Extra cases carry materials the package does not contain (samples of
an existing extractor during onboarding, regressions on successful examples).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from jane_kit.errors import JaneError

from .clients import HandlerClient, idem_key
from .packages import PackageDraft, strip_material

__all__ = ["TestOutcome", "extra_case", "run_tests"]


@dataclass
class TestOutcome:
    context: str
    report: dict[str, Any]

    @property
    def passed(self) -> bool:
        return int(self.report.get("failed", 0)) == 0 and int(self.report.get("passed", 0)) > 0

    @property
    def pass_rate(self) -> float:
        total = int(self.report.get("passed", 0)) + int(self.report.get("failed", 0))
        return int(self.report.get("passed", 0)) / total if total else 0.0

    def failures(self) -> list[dict[str, Any]]:
        return [
            {
                k: c.get(k)
                for k in ("name", "expected_status", "actual_status", "differences")
                if c.get(k) is not None
            }
            for c in self.report.get("cases") or []
            if not c.get("passed")
        ]

    def wire(self) -> dict[str, Any]:
        return {"context": self.context, "report": self.report}


def extra_case(
    name: str,
    material: dict[str, Any],
    expected_status: str,
    entities: list[dict[str, Any]] | None = None,
    compare: str = "subset",
) -> dict[str, Any]:
    case: dict[str, Any] = {
        "name": name,
        "input": {"kind": "material", "material": strip_material(material)},
        "expected_status": expected_status,
    }
    if entities is not None:
        case["expected"] = {"entities": entities}
        case["compare"] = compare
    return case


async def run_tests(
    handler: HandlerClient,
    *,
    job_key: str,
    context: str,
    draft: PackageDraft | None = None,
    package: dict[str, Any] | None = None,
    tests: str | list[str] = "all",
    extra_cases: list[dict[str, Any]] | None = None,
    params: dict[str, Any] | None = None,
    inline_max_bytes: int,
) -> TestOutcome:
    body: dict[str, Any] = {"tests": tests}
    if draft is not None:
        ref = draft.content_ref()
        if int(ref["size_bytes"]) > inline_max_bytes:
            raise JaneError(
                f"package archive {ref['size_bytes']} bytes exceeds transfer.inline_max_bytes={inline_max_bytes}",
                code="payload_too_large",
                details={"path": "transfer.inline_max_bytes", "limit": inline_max_bytes},
            )
        body["handler"] = draft.ref
        body["package_archive"] = ref
    elif package is not None:
        body["handler"] = {k: package[k] for k in ("package_id", "version", "digest") if k in package}
    else:
        raise ValueError("draft or package is required")
    if extra_cases:
        body["extra_cases"] = extra_cases
    if params:
        body["params"] = params
    digest = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    report = await handler.test_run(body, idem_key(job_key, "test", context, digest))
    return TestOutcome(context, report)
