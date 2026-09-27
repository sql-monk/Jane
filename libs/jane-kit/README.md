# jane-kit

Спільна бібліотека сервісів Jane. Дає однакову поведінку всім сервісам: конфігурація з успадкуванням
лімітів, структуровані журнали, метрики Prometheus, health, модель помилок, ідемпотентність, асинхронні
job, контрактні тести й моки, генерація клієнтів.

Підключення в сервісі (uv workspace):

```toml
[project]
dependencies = ["jane-kit"]

[tool.uv.sources]
jane-kit = { workspace = true }
```

## Модулі

| Модуль | Що дає |
|---|---|
| `jane_kit.config` | `Limits` (кожне поле з безпечним типовим значенням, інакше `TypeError`), `resolve_limits(model, *layers)` — злиття рівнів типові → платформа → джерело → завдання, стелі (`ceilings`), походження кожного значення (`explain()`); `load_layer` (TOML/JSON/YAML), `layer_from_env`; `JaneSettings` — налаштування процесу |
| `jane_kit.logs` | JSON-журнали в stdout, `bind_context(request_id=..., job_id=...)` через `contextvars` |
| `jane_kit.metrics` | `Metrics` з окремим реєстром на застосунок, `/metrics`, лічильник і гістограма HTTP за шаблоном маршруту |
| `jane_kit.health` | `/health/live`, `/health/ready`; перевірки з тайм-аутом із конфігурації |
| `jane_kit.errors` | RFC 9457 Problem Details (`application/problem+json`) зі стабільним `code`; `JaneError` та підкласи; обробники для FastAPI |
| `jane_kit.idempotency` | `Idempotency-Key`: повтор повертає збережену відповідь, інший запит із тим самим ключем — 422, паралельний — 409; сховище за протоколом |
| `jane_kit.jobs` | `202` + `job_id` + `Location`, стани `queued/running/succeeded/failed/cancelled`, прогрес, скасування, ліміти паралельності, черги й тайм-ауту |
| `jane_kit.clients` | `ServiceClient` (httpx): тайм-аути й повтори з конфігурації, повтор лише для безпечних методів або з `Idempotency-Key`, `Retry-After`, `X-Request-ID`, `wait_for_job` |
| `jane_kit.contracts` | `OpenAPISpec` (OpenAPI 3.1, `$ref` між файлами), `ContractClient` — перевіряє кожну відповідь справжнього сервісу, `build_mock_app` — мок сусіда з контракту |
| `jane_kit.codegen` | `uv run jane-codegen client <openapi.yaml> --out <pkg>/_generated/<svc>` — моделі Pydantic + асинхронний клієнт |
| `jane_kit.service` | `create_app(settings)` — FastAPI з усім вищенаведеним; `run()` — uvicorn |
| `jane_kit.devstack` | `load_stack()` — порти й облікові дані стеку, піднятого `just up` (для інтеграційних тестів) |

## Ліміти

Числові ліміти не зашиваються в код (plan.md §3.6). Сервіс описує модель:

```python
class CrawlLimits(Limits):
    concurrency: int = Field(default=4, ge=1)
    http: HttpLimits = HttpLimits()


resolved = resolve_limits(
    CrawlLimits,
    *settings.platform_layers("JANE_WEB_COLLECTOR_LIMITS__"),  # файл + змінні середовища
    LimitLayer("source", source_cfg, name="shop.example"),
    LimitLayer("job", job_cfg, name="prices"),
)
resolved.limits.concurrency  # значення
resolved.explain()  # [(шлях, значення, походження)]
```

Стеля (`ceilings`) верхнього рівня обмежує нижчі: завдання не може підняти значення вище стелі платформи
(`on_exceed="clamp"` — обрізати й записати в `clamped`, `"error"` — помилка).

Типові значення лімітів самої бібліотеки:

| Модель | Параметр | Типово |
|---|---|---|
| `JobLimits` | `max_concurrent_jobs` / `max_queued_jobs` / `job_timeout_s` | 4 / 1000 / 3600 |
| `IdempotencyLimits` | `ttl_s` / `max_key_length` / `in_memory_max_entries` | 86400 / 255 / 10000 |
| `ClientLimits` | `timeout_s` / `connect_timeout_s` / `max_retries` | 30 / 5 / 3 |
| `ClientLimits` | `backoff_base_s` / `backoff_max_s` / `max_connections` | 0.2 / 10 / 20 |
| `ClientLimits` | `job_poll_interval_s` / `job_wait_timeout_s` | 1 / 3600 |
| `HealthRegistry` | `check_timeout_s` (аргумент `create_app(health_check_timeout_s=...)`) | 2 |

## Кілька екземплярів

`InMemoryIdempotencyStore` і `InMemoryJobStore` — для одного екземпляра й тестів. Для кількох екземплярів
сервіс реалізує протоколи `IdempotencyStore` і `JobStore` у власній БД; решта коду не змінюється.

## Точки підключення WP-00

Формат помилки (`errors.py`), шляхи health (`health.py`), стани й ендпоінти job (`jobs.py`), заголовки
ідемпотентності (`idempotency.py`) і розташування контрактів (`contracts.find_specs`) узгоджуються з
`contracts/` WP-00. Кожне таке місце позначене в коді як `CONNECTION POINT (WP-00)`.

## Тести

```
just test jane-kit
```
