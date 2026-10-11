# Контракти: конфігурація

Параметри інструментів `contracts/tools` і рецептів `just`, змінні середовища та модель лімітів `Limits`, яку контракт задає для всіх сервісів.

## Зміст

- [Рецепти й аргументи](#рецепти-й-аргументи)
- [Змінні середовища](#змінні-середовища)
- [Заголовки моку](#заголовки-моку)
- [Модель лімітів](#модель-лімітів)

## Рецепти й аргументи

| Рецепт | Що виконує | Аргументи |
|---|---|---|
| `just contracts-check` | `check_contracts.py --no-redocly` (через `scripts/contracts_lint.py`) | `--redocly` — також Redocly, обов'язково |
| `just contracts-compat [base]` | `compat.py --self-test`, потім `compat.py --base <base>` | `base` — git-ревізія, типово `main`; `--oasdiff` — також oasdiff |
| `just contracts-mock <api>` | `mock.py <api>` | `--port` (типово `4010`), `--host` (типово `127.0.0.1`) |
| `just contracts-gen <api> <out>` | `jane-codegen client contracts/openapi/<api>.v1.yaml --out <out> --no-models` | `api` — назва файла без `.v1.yaml` |
| `just contract` | Лінтер, самоперевірка `compat.py`, тести з маркером `contract` | Зайві аргументи йдуть у pytest |

Прямий виклик скриптів:

| Команда | Параметри |
|---|---|
| `uv run contracts/tools/check_contracts.py` | Без прапорців — Redocly, якщо є `npx`; `--no-redocly` — пропустити; `--require-redocly` — помилка без Redocly (CI) |
| `uv run contracts/tools/compat.py` | `--base <ref>` (типово `main`), `--oasdiff`, `--self-test` |
| `uv run contracts/tools/mock.py <api>` | `<api>`: `collector`, `handler`, `storage`, `registry`, `orchestrator`, `llm`, `assistant`; `--port`, `--host`, `--list` — вивести маршрути й вийти |

## Змінні середовища

| Змінна | Хто читає | Вплив |
|---|---|---|
| `JANE_CONTRACTS_REDOCLY` | `scripts/contracts_lint.py` | `1` — передати `--require-redocly` (встановлено в CI job `contract`); інакше `--no-redocly` |
| `JANE_CONTRACTS_DIR` | `scripts/contracts_lint.py`, `jane_kit.contracts.contracts_dir` | Інший каталог контрактів замість `contracts/` |
| `JANE_OASDIFF_IMAGE` | `compat.py` | Інший образ oasdiff замість закріпленого `tufin/oasdiff:v1.33.0@sha256:…` |

## Заголовки моку

Мок повертає перший приклад найменшого успішного статусу операції. Інший варіант обирає заголовок `Prefer` — так само в `mock.py`, `jane_kit.contracts.build_mock_app` і Prism:

| Заголовок | Дія |
|---|---|
| `Prefer: code=404` | Відповідь із прикладу статусу `404` |
| `Prefer: example=<name>` | Приклад із назвою `<name>` |

Мок перевіряє обов'язкові заголовки (наприклад `Idempotency-Key`) і наявність обов'язкового тіла (`422` problem+json), дає `404` для невідомого шляху й `405` для іншого методу, додає `Location: /v1/jobs/<job_id>` до `202` і відкриває CORS для локальної розробки Admin UI.

## Модель лімітів

[limits.schema.json](../../../contracts/schemas/common/limits.schema.json) описує один об'єкт `Limits`, який задається на рівнях `platform → source → task → stage` (сервіс у автономному режимі приймає ще рівень запиту). Кожне поле необов'язкове; типових значень у схемі немає — їх визначають сервіси й профілі в [deploy/profiles](../../../deploy/profiles/).

| Група | Поля |
|---|---|
| `concurrency` | `max_parallel_fetches`, `max_parallel_fetches_per_host`, `max_parallel_invocations`, `max_parallel_runs_per_task`, `max_parallel_stage_items` |
| `rate` | `requests_per_second_per_host`, `min_delay_ms_per_host`, `burst_per_host`, `respect_crawl_delay` |
| `crawl` | `max_depth`, `max_pages_per_run`, `max_bytes_per_run`, `max_material_bytes`, `max_redirects`, `max_links_per_page`, `max_seed_urls`, `max_frontier_size`, `revisit_interval_seconds` |
| `timeouts` | `connect_timeout_ms`, `request_timeout_ms`, `invocation_timeout_ms`, `stage_timeout_ms`, `run_timeout_ms`, `sync_response_max_ms` |
| `retries` | `max_attempts`, `initial_backoff_ms`, `max_backoff_ms`, `backoff_multiplier`, `jitter` |
| `queue` | `max_queue_depth`, `max_inflight_materials`, `max_unacked_materials` |
| `sandbox` | `cpu_cores`, `memory_mb`, `wall_time_ms`, `max_output_bytes`, `max_processes`, `tmpfs_mb` |
| `llm` | `max_requests_per_minute`, `max_input_tokens_per_request`, `max_output_tokens_per_request`, `budget` (`amount`, `currency`, `period`), `max_improvement_attempts`, `max_onboarding_samples`, `min_onboarding_confidence` |
| `transfer` | `inline_max_bytes`, `max_request_body_bytes`, `transit_ttl_seconds`, `download_url_ttl_seconds`, `job_retention_seconds`, `idempotency_ttl_seconds` |
| `telegram` | `max_messages_per_run`, `max_media_bytes`, `max_flood_wait_seconds` |

Похідні визначення `$defs`:

- `PlatformLimits` — `{"profile", "defaults", "hard_caps"}`: типові значення й жорсткі стелі одного розгортання, однакові для всіх сервісів. Приклади — `contracts/examples/schemas/common/limits@PlatformLimits/` (`ci.json`, `dev-laptop.json`, `single-node.json`).
- `EffectiveLimits` — результат злиття з походженням кожного значення; рівні походження (`LimitLevel`): `platform`, `source`, `task`, `stage`, `request`, `hard_cap`, `runtime`.
- `RetryPolicy`, `Budget` — групи повторів і бюджету LLM.

Правила злиття:

- нижчий рівень перекриває вищий, відсутнє поле успадковується, `null` заборонено;
- після злиття кожне числове поле обмежується `hard_caps` (мінімум);
- обмеження конкретного сайту чи провайдера (`Crawl-delay`, `Retry-After`, flood-wait Telegram, ліміти LLM) лише звужують значення;
- автономний сервіс застосовує `min(ліміти запиту, власні hard_caps)`;
- сервіс показує свої типові значення й стелі в `GET /v1/info` → `limits`; ефективні ліміти джерела, завдання й етапу з походженням — лише `GET /v1/limits/effective` Orchestrator.

Нове обмеження додають новим полем `limits.schema.json` із типовим значенням у профілях, а не `maxItems` у схемі. Реалізація злиття в Python — [jane-kit: ліміти](../jane-kit/configuration.md#ліміти).
