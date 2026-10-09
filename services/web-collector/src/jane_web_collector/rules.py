"""Collector rules of the Web Collector: what this implementation supports, on top of the shared parts.

Schema validation (``collector.v1`` and ``collector-rules.schema.json``, ``oneOf`` errors explained by the
discriminator) and loading by ``rules_ref`` (local package directory or archive, then the package registry, with
``digest`` and ``files[].sha256`` checks) are jane-kit's shared :mod:`jane_kit.rules` (R17).
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from jane_kit.errors import FieldError
from jane_kit.rules import CollectorSchemas, RulesReport
from jane_kit.rules import RulesLoader as _KitRulesLoader

from .connections import header_value_safe, is_safe_rule_header
from .discovery.registry import RESERVED_TYPES, Registry

__all__ = ["ContractSchemas", "RulesLoader", "RulesReport", "validate_rules"]

PREFIX = "JANE_WEB_COLLECTOR_"


class ContractSchemas(CollectorSchemas):
    """JSON Schemas of ``collector.v1`` (with cross-file ``$ref``) for request and rules validation."""

    @classmethod
    def for_service(cls, configured: Path | None) -> ContractSchemas:
        return cls.locate_collector(configured, setting=f"{PREFIX}CONTRACTS_DIR", start=Path(__file__).parent)


class RulesLoader(_KitRulesLoader):
    """Rules of a ``rules_ref``: ``JANE_WEB_COLLECTOR_RULES_DIR``, then ``JANE_WEB_COLLECTOR_REGISTRY_URL``."""

    def __init__(
        self,
        *,
        rules_dir: Path | None,
        registry_url: str | None,
        registry_token_env: str | None,
        timeout_s: float,
    ) -> None:
        super().__init__(
            rules_dir=rules_dir,
            registry_url=registry_url,
            registry_token_env=registry_token_env,
            timeout_s=timeout_s,
            settings_prefix=PREFIX,
        )


def validate_rules(schemas: ContractSchemas, registry: Registry, rules: Any) -> RulesReport:
    """Schema validation + what this implementation supports (unsupported strategies, telegram rules)."""
    errors = schemas.rules_errors(rules)
    warnings: list[FieldError] = []
    supported = True
    if errors or not isinstance(rules, Mapping):
        return RulesReport(False, False, errors, warnings)
    if rules.get("collector") != "web":
        warnings.append(
            FieldError(pointer="/collector", message="web-collector executes only collector=web rules")
        )
        return RulesReport(True, False, errors, warnings)
    for name, value in ((rules.get("fetch") or {}).get("headers") or {}).items():
        if not is_safe_rule_header(name):
            errors.append(
                FieldError(
                    pointer=f"/fetch/headers/{name}",
                    code="secret_detected",
                    message="only Accept, Accept-Language and Cache-Control are allowed in source rules",
                )
            )
        elif not header_value_safe(value):
            errors.append(
                FieldError(
                    pointer=f"/fetch/headers/{name}",
                    message="header value must contain only visible ASCII without control characters",
                )
            )
    if errors:
        return RulesReport(False, False, errors, warnings)
    has_depth = "max_depth" in ((rules.get("limits") or {}).get("crawl") or {})
    for i, strategy in enumerate(rules.get("strategies") or []):
        kind = strategy.get("type")
        # api_feed method=POST/body and emit_items_as_materials are executed since WP-16 (R22,
        # DiscoveryContext 1.1): no "unsupported" warning for them any more.
        if kind in RESERVED_TYPES:
            supported = False
            warnings.append(
                FieldError(
                    pointer=f"/strategies/{i}",
                    code="unsupported_strategy",
                    message=f"strategy {kind} is not executed by the collector (ADR-0010: LLM exploration is done by the assistant)",
                )
            )
        elif not registry.supported(kind):
            supported = False
            warnings.append(
                FieldError(
                    pointer=f"/strategies/{i}",
                    code="unsupported_strategy",
                    message=f"strategy {kind} is not available in this collector build",
                )
            )
        elif (
            kind == "recursive"
            and not has_depth
            and "max_depth" not in ((strategy.get("limits") or {}).get("crawl") or {})
        ):
            warnings.append(
                FieldError(
                    pointer=f"/strategies/{i}",
                    message="recursive strategy without max_depth inherits limits.crawl.max_depth",
                )
            )
    return RulesReport(True, supported, errors, warnings)
