# Template Service

<!-- Шаблон README за DoD plan.md §4. Після `just new-service` замініть опис і приклади на свої. -->

Призначення сервісу в одному-двох реченнях. Контракт: `contracts/openapi/template-service.v1.yaml`
(конвенції — скіл `jane-contracts`).

## Незалежний запуск

Без Docker (з кореня репозиторію):

```
uv sync --all-packages
uv run --package jane-template-service python -m jane_template_service
curl http://127.0.0.1:8000/v1/health
```

У Docker (контекст збірки — корінь репозиторію):

```
docker build -f templates/service/Dockerfile -t jane-template-service .
docker run --rm -p 8000:8000 jane-template-service
```

Кілька екземплярів: запустіть кілька процесів або контейнерів з різними портами
(`JANE_TEMPLATE_SERVICE_PORT`). Стан, який має бути спільним (job, ключі ідемпотентності), зберігайте у
власній БД сервісу через протоколи `JobStore` / `IdempotencyStore` з jane-kit.

## Тести

```
just test template-service                  # unit + contract
just test template-service -m integration   # потребує `just up`
```

Контрактні тести (`tests/test_contract.py`) перевіряють `/v1/health`, `/v1/info`, `/v1/jobs` і помилки
за `contracts/openapi/common.yaml`, а API сервісу — за його `*.v1.yaml` через `ContractClient`.

## Конфігурація

Змінні середовища з префіксом `JANE_TEMPLATE_SERVICE_`:

| Змінна | Типово | Опис |
|---|---|---|
| `JANE_TEMPLATE_SERVICE_HOST` | `127.0.0.1` (у контейнері `0.0.0.0`) | адреса прослуховування |
| `JANE_TEMPLATE_SERVICE_PORT` | `8000` | порт |
| `JANE_TEMPLATE_SERVICE_LOG_LEVEL` | `INFO` | рівень журналу |
| `JANE_TEMPLATE_SERVICE_LOG_FORMAT` | `json` | `json` або `console` |
| `JANE_TEMPLATE_SERVICE_METRICS_ENABLED` | `true` | ендпоінт `/metrics` |
| `JANE_TEMPLATE_SERVICE_AUTH_MODE` | `none` | значення для `/v1/info` (`none`, `api_key`, `jwt`) |
| `JANE_TEMPLATE_SERVICE_LIMITS_FILE` | — | файл `PlatformLimits` (`profile`, `defaults`, `hard_caps`; TOML/JSON/YAML) |
| `JANE_TEMPLATE_SERVICE_LIMITS__<ГРУПА>__<ПАРАМЕТР>` | — | перевизначення, напр. `..._LIMITS__JOBS__MAX_CONCURRENT_JOBS=8` |
| `JANE_TEMPLATE_SERVICE_LIMITS__HARD_CAPS__<ГРУПА>__<ПАРАМЕТР>` | — | жорстка стеля платформи |

## Ліміти

Рівні: типові значення сервісу → платформа (файл, потім змінні середовища) → джерело → завдання → етап
(→ запит в автономному режимі); `hard_caps` обмежують результат. Ефективні значення з походженням
(`EffectiveLimits`) пишуться в журнал під час старту.

| Параметр | Типово | Опис |
|---|---|---|
| `jobs.max_concurrent_jobs` | 4 | job, що виконуються одночасно в одному екземплярі |
| `jobs.max_queued_jobs` | 1000 | понад це — `503 service_unavailable` (backpressure) |
| `jobs.job_timeout_ms` | 3600000 | максимальна тривалість job (`failed`, код `timeout`) |
| `jobs.job_retention_seconds` | 86400 | скільки зберігається завершений job |
| `idempotency.idempotency_ttl_seconds` | 86400 | скільки пам'ятається `Idempotency-Key` |
| `idempotency.in_memory_max_entries` | 10000 | розмір сховища ключів у пам'яті |

## Приклад виклику зі стороннього застосунку

```python
import httpx

with httpx.Client(base_url="http://127.0.0.1:8000") as client:
    r = client.post("/v1/examples/jobs", json={"steps": 3}, headers={"Idempotency-Key": "demo-1"})
    job_url = r.headers["Location"]  # 202 Accepted
    print(client.get(job_url).json()["status"])  # queued | running | succeeded ...
```

## Спостережуваність

- `GET /v1/health` (`ok`/`degraded`/`down`; перевірки залежностей — `app.state.health.add`), `GET /v1/info`.
- `GET /metrics` — Prometheus (`jane_http_requests_total`, `jane_http_request_duration_seconds`, ...).
- Журнали — JSON-рядки в stdout із `trace_id` (з `traceparent`), `request_id`, `job_id`, `service`, `instance`.
- Помилки — `application/problem+json` зі стабільним `code` (каталог — `contracts/docs/errors.md`).
