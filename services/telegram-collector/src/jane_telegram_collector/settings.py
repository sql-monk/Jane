"""Settings and limits of the service. Every limit has a safe default documented in README.md."""

from __future__ import annotations

from pydantic_settings import SettingsConfigDict

from jane_kit.config import JaneSettings, LimitLayer, Limits, ResolvedLimits, resolve_limits
from jane_kit.idempotency import IdempotencyLimits
from jane_kit.jobs import JobLimits

ENV_PREFIX = "JANE_TELEGRAM_COLLECTOR_"


class Settings(JaneSettings):
    model_config = SettingsConfigDict(env_prefix=ENV_PREFIX, extra="ignore", env_nested_delimiter="__")

    service_name: str = "telegram-collector"


class ServiceLimits(Limits):
    """Limits of this service. Use contract names (``limits.schema.json``) for limits that exist there."""

    jobs: JobLimits = JobLimits()
    idempotency: IdempotencyLimits = IdempotencyLimits()


def resolve_service_limits(settings: Settings, *extra: LimitLayer) -> ResolvedLimits[ServiceLimits]:
    """Defaults <- platform file (``..._LIMITS_FILE``) <- ``JANE_TELEGRAM_COLLECTOR_LIMITS__*`` <- ``extra``
    (source/task/stage/request layers)."""
    return resolve_limits(ServiceLimits, *settings.platform_layers(f"{ENV_PREFIX}LIMITS__"), *extra)
