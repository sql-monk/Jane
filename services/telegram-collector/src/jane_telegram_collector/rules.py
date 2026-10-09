"""Collector rules of the Telegram Collector: what this implementation supports, on top of the shared parts.

Schema validation (``collector.v1`` and ``collector-rules.schema.json``, ``oneOf`` errors explained by the
discriminator) and loading by ``rules_ref`` (local package directory or archive, then the package registry, with
``digest`` and ``files[].sha256`` checks, a registry token that must be a valid HTTP header value, no transport
details in errors) are jane-kit's shared :mod:`jane_kit.rules` (R17).
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from jane_kit.errors import FieldError
from jane_kit.rules import CollectorSchemas, RulesReport
from jane_kit.rules import RulesLoader as _KitRulesLoader

__all__ = ["ContractSchemas", "RulesLoader", "RulesReport", "validate_rules"]

PREFIX = "JANE_TELEGRAM_COLLECTOR_"


class ContractSchemas(CollectorSchemas):
    """JSON Schemas of ``collector.v1`` (with cross-file ``$ref``) for request and rules validation."""

    @classmethod
    def for_service(cls, configured: Path | None) -> ContractSchemas:
        return cls.locate_collector(configured, setting=f"{PREFIX}CONTRACTS_DIR", start=Path(__file__).parent)


class RulesLoader(_KitRulesLoader):
    """Rules of a ``rules_ref``: ``JANE_TELEGRAM_COLLECTOR_RULES_DIR``, then ``..._REGISTRY_URL``."""

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


def validate_rules(schemas: ContractSchemas, rules: Any) -> RulesReport:
    """Schema validation + what this implementation supports (web rules are valid but not executed here)."""
    errors = schemas.rules_errors(rules)
    warnings: list[FieldError] = []
    if errors or not isinstance(rules, Mapping):
        return RulesReport(False, False, errors, warnings)
    if rules.get("collector") != "telegram":
        warnings.append(
            FieldError(
                pointer="/collector", message="telegram-collector executes only collector=telegram rules"
            )
        )
        return RulesReport(True, False, errors, warnings)
    if not (rules.get("history") or {}).get("enabled", True) and not any(
        (rules.get("updates") or {}).get(k, True) for k in ("new_messages", "edits")
    ):
        warnings.append(
            FieldError(
                pointer="/updates", message="history and updates are disabled: collections emit nothing"
            )
        )
    if (rules.get("media") or {}).get("kinds") and not (rules.get("media") or {}).get("download", False):
        warnings.append(
            FieldError(pointer="/media/kinds", message="media.kinds has no effect without media.download")
        )
    return RulesReport(True, True, errors, warnings)
