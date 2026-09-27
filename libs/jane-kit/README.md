# jane-kit

Спільна бібліотека сервісів Jane. Дає однакову поведінку всім сервісам і реалізує конвенції контрактів
WP-00 (скіл `jane-contracts`): модель помилок, ідемпотентність, асинхронні job, health/info, ліміти з
успадкуванням, курсорна пагінація, `traceparent`, контрактні тести й моки, генерація клієнтів.

Підключення в сервісі (uv workspace):

```toml
[project]
dependencies = ["jane-kit"]

[tool.uv.sources]
jane-kit = { workspace = true }
```

## Модулі

| Модуль | Що дає | Контракт WP-00 |
|---|---|---|
| `jane_kit.config` | `Limits` (кожне поле з безпечним типовим значенням, інакше `TypeError`); `resolve_limits(model, *layers)` — злиття platform → source → task → stage → request, `hard_caps`, `effective()` у формі `EffectiveLimits`, `platform_limits()` у формі `PlatformLimits` (лише поля, позначені `contract_field`); `load_layer` (`PlatformLimits` у TOML/JSON/YAML), `layer_from_env`; `JaneSettings` | `schemas/common/limits.schema.json` |
| `jane_kit.errors` | `Problem`, `FieldError`, `JaneError(code=...)` і підкласи; статус і `retryable` — з каталогу `KNOWN_CODES`; обробники FastAPI (404/405/422/500 теж Problem) | `schemas/common/problem.schema.json`, `docs/errors.md` |
| `jane_kit.idempotency` | `Idempotency-Key`: повтор → збережена відповідь і `Idempotency-Replayed: true`, інше тіло → 422 `idempotency_key_reused`, паралельно → 409 `idempotency_in_progress`; протокол сховища | `common.yaml` `IdempotencyKey` |
| `jane_kit.jobs` | `202` + `Job` + `Location`; `queued/running/cancelling/succeeded/failed/cancelled`; прогрес, скасування (202 / 200 для завершених); ліміти паралельності, черги, тайм-ауту, зберігання | `schemas/common/job.schema.json`, `common.yaml` `Job`/`JobCancel` |
| `jane_kit.health` | `GET /v1/health` (`ok`/`degraded`/`down`, 503 для down), `GET /v1/info` (`ServiceInfo` з `limits` = `PlatformLimits` сервісу, якщо `create_app(limits=...)`); тайм-аут перевірок — `JaneSettings.health_check_timeout_ms` | `common.yaml` `Health`/`Info` |
| `jane_kit.pagination` | `Page[T]` (`items`, `next_cursor`), `clamp_limit`, непрозорі курсори | конвенція пагінації |
| `jane_kit.tracing` | `traceparent` (W3C): продовження траси, `trace_id` у журналах і Problem | конвенція простежуваності |
| `jane_kit.logs` | JSON-журнали в stdout, `bind_context(trace_id=..., job_id=...)` через `contextvars` | — |
| `jane_kit.metrics` | `Metrics` з окремим реєстром на застосунок, `/metrics`, HTTP-метрики за шаблоном маршруту | — |
| `jane_kit.clients` | `ServiceClient` (httpx): `timeouts.*_ms` і `RetryPolicy` з конфігурації, повтор лише для безпечних методів або з `Idempotency-Key` і лише retryable-помилок, `Retry-After`, `traceparent`, `wait_for_job` | `RetryPolicy` у limits |
| `jane_kit.contracts` | `OpenAPISpec` (OpenAPI 3.1, `$ref` між файлами, `$ref` на path items), `ContractClient` — перевіряє кожну відповідь справжнього сервісу, `build_mock_app` — мок сусіда з прикладів контракту, `contracts_dir()`, `find_specs()` | `contracts/openapi/*.v1.yaml` |
| `jane_kit.codegen` | `uv run jane-codegen client <spec> --out <pkg>/_generated/<svc>` — моделі Pydantic (datamodel-code-generator) + асинхронний клієнт на `ServiceClient` | — |
| `jane_kit.service` | `create_app(settings, capabilities=...)` — FastAPI з усім вищенаведеним; `run()` — uvicorn | — |
| `jane_kit.devstack` | `load_stack()` — порти й облікові дані стеку `just up` (для інтеграційних тестів) | — |

## Ліміти

Числові ліміти не зашиваються в код (plan.md §3.6). Сервіс описує модель з назвами полів контракту:

```python
class Crawl(Limits):
    max_depth: int = Field(default=3, ge=0)


class CollectorLimits(Limits):
    crawl: Crawl = Crawl()


resolved = resolve_limits(
    CollectorLimits,
    *settings.platform_layers("JANE_WEB_COLLECTOR_LIMITS__"),  # файл PlatformLimits + змінні середовища
    LimitLayer("source", source_limits, name="shop"),
    LimitLayer("task", task_limits, name="prices"),
    LimitLayer("stage", stage_limits, name="fetch"),
)
resolved.limits.crawl.max_depth  # значення
resolved.effective()  # {"limits": {...}, "provenance": {"crawl.max_depth": "task" | "hard_cap" | ...}}
```

`hard_caps` платформи обмежують результат (`min`); нижчий рівень може лише звузити стелю. Автономний
режим: ліміти із запиту — шар `LimitLayer("request", ...)`, для відмови замість обрізання —
`on_exceed="error"` (→ `limit_exceeded`).

Ліміт, що є в `limits.schema.json`, оголошуйте через `contract_field("<група>.<поле>", типове, ...)` (для
групи — `contract_field("retries", RetryPolicy())`): такі поля потрапляють у `/v1/info` → `limits`
(`PlatformLimits`: `defaults` і `hard_caps`). Специфічні для сервісу ліміти лишаються внутрішніми, бо схема
контракту строга. Ефективні ліміти з походженням для джерела/завдання/етапу рахує лише оркестратор.

Типові значення лімітів самої бібліотеки:

| Модель | Параметр | Типово |
|---|---|---|
| `JobLimits` | `max_concurrent_jobs` / `max_queued_jobs` | 4 / 1000 |
| `JobLimits` | `job_timeout_ms` / `job_retention_seconds` / `queue_full_retry_after_seconds` | 3600000 / 86400 / 1 |
| `IdempotencyLimits` | `idempotency_ttl_seconds` / `in_memory_max_entries` | 86400 / 10000 |
| `ClientLimits` | `connect_timeout_ms` / `request_timeout_ms` / `max_connections` | 5000 / 30000 / 20 |
| `ClientLimits.retries` | `max_attempts` / `initial_backoff_ms` / `max_backoff_ms` / `backoff_multiplier` / `jitter` | 4 / 200 / 10000 / 2.0 / true |
| `ClientLimits` | `job_poll_interval_ms` / `job_wait_timeout_ms` | 1000 / 3600000 |
| `PageLimits` | `default_page_size` / `max_page_size` | 50 / 500 |
| `JaneSettings` | `health_check_timeout_ms` (env `<PREFIX>HEALTH_CHECK_TIMEOUT_MS`) | 2000 |

## Кілька екземплярів

`InMemoryIdempotencyStore` і `InMemoryJobStore` — для одного екземпляра й тестів. Для кількох екземплярів
сервіс реалізує протоколи `IdempotencyStore` і `JobStore` у власній БД; решта коду не змінюється.

## Тести

```
just test jane-kit
JANE_CONTRACTS_DIR=<шлях до contracts> just test jane-kit -m contract   # проти контрактів WP-00
```

`tests/test_wp00_contracts.py` перевіряє відповідність контрактам WP-00 (каталог кодів помилок, Problem,
Job, Health, ServiceInfo, EffectiveLimits, моки й клієнт для кожного `contracts/openapi/*.v1.yaml`);
пропускається, доки `contracts/` немає в checkout.
