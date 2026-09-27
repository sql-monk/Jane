"""Deterministic fake of the LLM gateway (``llm.v1`` ``POST /v1/completions``).

The "model" is a pure function of the request: it dispatches on ``output_schema.title``
(``jane.assistant.<step>.v1``) and reads the data parts. Scenario knobs make it misbehave the way a
prompt-injected or weak model would (off-source URLs, forbidden imports, breaking changes), so the
assistant's guards are exercised. It is independent of WP-10's fake provider on purpose.
"""

from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .base import ContractFake, FakeRequest, Reply, problem
from .runtime import PRODUCT_CODE_V1, PRODUCT_CODE_V2, PRODUCT_CODE_V2_BREAKING, run_code

__all__ = ["FakeLlm"]

_META = re.compile(r'<meta name="jane:page-type" content="([a-z_]+)"')
ENTITY_BY_TYPE = {"product": "product", "event": "event", "article": "article"}
FIELDS = {
    "product": [
        {"name": "sku", "type": "string", "coverage": 1.0, "examples": ["A-100"]},
        {"name": "title", "type": "string", "coverage": 1.0},
        {"name": "price", "type": "money", "coverage": 1.0},
    ],
    "article": [
        {"name": "title", "type": "string", "coverage": 1.0},
        {"name": "published_at", "type": "datetime", "coverage": 1.0},
    ],
    "event": [
        {"name": "title", "type": "string", "coverage": 1.0},
        {"name": "starts_at", "type": "datetime", "coverage": 1.0},
    ],
}


def _type_of(text: str) -> str:
    if m := _META.search(text):
        return m.group(1)
    if "#event" in text:
        return "event"
    if "#ad" in text:
        return "ad"
    return "other"


def _material_of(text: str) -> dict[str, Any]:
    body = text.split("\n\n", 1)[1] if text.startswith("url: ") else text
    return {
        "source": {"kind": "web"},
        "content": {"kind": "inline", "encoding": "utf-8", "media_type": "text/html", "data": body},
    }


@dataclass
class Knobs:
    evil_proposals: bool = True
    only_evil_proposals: bool = False
    bad_code_first: bool = False
    improve_code: str = PRODUCT_CODE_V2
    improve_schema_change: str = "none"
    improve_suggested: list[str] = field(default_factory=list)
    improve_invalid: bool = False
    cost: float = 0.01
    delay_s: float = 0.0


class FakeLlm:
    def __init__(self, contracts: Path) -> None:
        self.app = ContractFake(contracts / "openapi" / "llm.v1.yaml", "llm")
        self.knobs = Knobs()
        self.requests: list[dict[str, Any]] = []
        self.spent_by_scope: dict[str, float] = {}
        self._generate_calls = 0
        self.app.on("createCompletion")(self.complete)

    def steps(self) -> list[str]:
        return [str(r["output_schema"]["title"]).split(".")[2] for r in self.requests]

    async def complete(self, req: FakeRequest) -> Reply:
        body = req.json
        self.requests.append(body)
        if self.knobs.delay_s:
            await asyncio.sleep(self.knobs.delay_s)
        budget = ((body.get("limits") or {}).get("budget") or {}).get("amount")
        if budget is not None and float(budget) < self.knobs.cost:
            return problem(
                429,
                "budget_exhausted",
                "LLM budget exhausted",
                retryable=False,
                details={"scope_type": "task"},
            )
        step = str(body["output_schema"]["title"]).split(".")[2]
        data = {p["name"]: p.get("text", "") for p in body.get("data") or []}
        output = getattr(self, f"_{step}")(data)
        return Reply(
            200,
            {
                "completion_id": f"cmp_{len(self.requests):06d}",
                "model": {"provider_id": "fake", "model_id": "fake-deterministic-1"},
                "output": output,
                "valid": True,
                "validation_errors": [],
                "finish_reason": "stop",
                "usage": {
                    "input_tokens": sum(len(t) for t in data.values()) // 4,
                    "output_tokens": 50,
                    "cost": {"amount": self.knobs.cost, "currency": "USD"},
                },
            },
        )

    # ------------------------------------------------------------------ steps
    def _classify(self, data: dict[str, str]) -> dict[str, Any]:
        return {
            "items": [
                {"name": n, "material_type": _type_of(t), "confidence": 0.9}
                for n, t in data.items()
                if re.fullmatch(r"m\d+", n)
            ]
        }

    def _analyze(self, data: dict[str, str]) -> dict[str, Any]:
        context = json.loads(data["context"])
        types = sorted(context["material_types"])
        entities = [
            {"entity_type": ENTITY_BY_TYPE[t], "material_type": t, "fields": FIELDS[ENTITY_BY_TYPE[t]]}
            for t in types
            if t in ENTITY_BY_TYPE
        ]
        return {
            "source_kind": "web",
            "discovery_methods": ["sitemap", "recursive", "llm_explore"],
            "entities": entities,
        }

    def _propose(self, data: dict[str, str]) -> dict[str, Any]:
        hints = json.loads(data["hints"])
        host = next(iter(hints.get("shapes") or {"shop.example.test/": []})).split("/", 1)[0]
        good = {
            "title": "Sitemap + product pages",
            "summary": "Full catalogue through the sitemap.",
            "recommended": True,
            "strategies": [{"type": "sitemap", "urls": [f"https://{host}/sitemap.xml"]}],
            "sections": [{"section_id": "product", "patterns": [f"{host}/product/**"]}],
            "exclude": [f"{host}/news/**"],
            "risks": ["sitemap may omit discontinued products"],
        }
        evil = {
            "title": "Recursive crawl",
            "summary": "Crawl from the home page.",
            "strategies": [
                {"type": "recursive", "seeds": [f"https://{host}/", "https://evil.example.org/"]},
                {"type": "llm_explore", "goal": "anything"},
                {"type": "seed_list", "urls": ["https://evil.example.org/steal"]},
            ],
            "sections": [
                {"section_id": "product", "patterns": [f"{host}/product/**", "evil.example.org/**"]}
            ],
            "risks": ["recursion finds pages missing from the sitemap"],
        }
        if self.knobs.only_evil_proposals:
            return {
                "proposals": [
                    {
                        "title": "Evil",
                        "strategies": [{"type": "seed_list", "urls": ["https://evil.example.org/"]}],
                    }
                ]
            }
        return {"proposals": [good, evil] if self.knobs.evil_proposals else [good]}

    def _expectations(
        self, code: str, data: dict[str, str], prefixes: tuple[str, ...]
    ) -> list[dict[str, Any]]:
        out = []
        for name, text in data.items():
            if name.startswith(prefixes):
                result = run_code(code, _material_of(text))
                exp = {
                    "name": name,
                    "expected_status": result["status"] if result["status"] != "failed" else "empty",
                }
                if result.get("entities"):
                    exp["entities"] = [
                        {"entity_type": e["entity_type"], "fields": e["fields"]} for e in result["entities"]
                    ]
                out.append(exp)
        return out

    def _generate_extractor(self, data: dict[str, str]) -> dict[str, Any]:
        self._generate_calls += 1
        code = PRODUCT_CODE_V1
        if self.knobs.bad_code_first and self._generate_calls == 1:
            code = "import socket\n" + code
        return {
            "module_code": code,
            "entity_schema": {
                "type": "object",
                "properties": {
                    "sku": {"type": "string"},
                    "title": {"type": "string"},
                    "price": {"type": "object"},
                },
                "required": ["sku"],
            },
            "key_fields": ["sku"],
            "expectations": self._expectations(code, data, ("sample_", "neg_")),
        }

    def _improve_extractor(self, data: dict[str, str]) -> dict[str, Any]:
        files = json.loads(data["files"])
        manifest = json.loads(data["package"])
        module_path = "src/" + manifest["entry"]["module"].replace(".", "/") + ".py"
        assert module_path in files
        code = self.knobs.improve_code
        if self.knobs.improve_invalid:
            code = "import subprocess\n" + code
        exps = []
        for name, text in data.items():
            if name.startswith("problem_") and name != "problems":
                result = run_code(code, _material_of(text))
                exp = {"name": name.removeprefix("problem_"), "expected_status": result["status"]}
                if result.get("entities"):
                    exp["entities"] = [
                        {"entity_type": e["entity_type"], "fields": e["fields"]} for e in result["entities"]
                    ]
                exps.append(exp)
        return {
            "files": {module_path: code},
            "expectations": exps,
            "change_summary": "Support .price-new selector.",
            "schema_change": self.knobs.improve_schema_change,
            "suggested_entity_types": list(self.knobs.improve_suggested),
        }

    def _classify_unknown(self, data: dict[str, str]) -> dict[str, Any]:
        t = _type_of(data["material"])
        return {
            "material_type": t,
            "confidence": 0.9 if t != "other" else 0.3,
            "relevant": t in {"event", "product", "article", "job"},
            "entity_types": [t] if t in {"event", "product", "article", "job"} else [],
            "navigation": t == "category",
        }


def _unused() -> None:  # keep FIELDS/PRODUCT_CODE_V2_BREAKING importable for tests
    _ = PRODUCT_CODE_V2_BREAKING
