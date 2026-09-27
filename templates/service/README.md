# Template Service

<!-- Шаблон README за DoD plan.md §4. Після `just new-service` замініть опис і приклади на свої. -->

Призначення сервісу в одному-двох реченнях. Контракт: `contracts/template-service/` (після WP-00).

## Незалежний запуск

Без Docker (з кореня репозиторію):

```
uv sync --all-packages
uv run --package jane-template-service python -m jane_template_service
curl http://127.0.0.1:8000/health/live
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

## Конфігурація

Змінні середовища з префіксом `JANE_TEMPLATE_SERVICE_`:

| Змінна | Типово | Опис |
|---|---|---|
| `JANE_TEMPLATE_SERVICE_HOST` | `127.0.0.1` (у контейнері `0.0.0.0`) | адреса прослуховування |
| `JANE_TEMPLATE_SERVICE_PORT` | `8000` | порт |
| `JANE_TEMPLATE_SERVICE_LOG_LEVEL` | `INFO` | рівень журналу |
| `JANE_TEMPLATE_SERVICE_LOG_FORMAT` | `json` | `json` або `console` |
| `JANE_TEMPLATE_SERVICE_METRICS_ENABLED` | `true` | ендпоінт `/metrics` |
| `JANE_TEMPLATE_SERVICE_LIMITS_FILE` | — | файл лімітів платформи (TOML/JSON/YAML, таблиці `limits` і `ceilings`) |
| `JANE_TEMPLATE_SERVICE_LIMITS__<ГРУПА>__<ПАРАМЕТР>` | — | перевизначення ліміту, напр. `..._LIMITS__JOBS__MAX_CONCURRENT_JOBS=8` |

## Ліміти

Рівні: типові значення → платформа (файл, потім змінні середовища) → джерело → завдання.
Поточні значення та їхнє походження повертає `GET /v1/info`.

| Параметр | Типово | Опис |
|---|---|---|
| `jobs.max_concurrent_jobs` | 4 | job, що виконуються одночасно в одному екземплярі |
| `jobs.max_queued_jobs` | 1000 | понад це — `429 job_queue_full` |
| `jobs.job_timeout_s` | 3600 | максимальна тривалість job |
| `idempotency.ttl_s` | 86400 | скільки зберігається відповідь для повтору |
| `idempotency.max_key_length` | 255 | максимальна довжина `Idempotency-Key` |
| `idempotency.in_memory_max_entries` | 10000 | розмір сховища ключів у пам'яті |

## Приклад виклику зі стороннього застосунку

```python
import httpx

with httpx.Client(base_url="http://127.0.0.1:8000") as client:
    r = client.post("/v1/examples/jobs", json={"steps": 3}, headers={"Idempotency-Key": "demo-1"})
    job_url = r.headers["Location"]  # 202 Accepted
    print(client.get(job_url).json()["state"])  # queued | running | succeeded ...
```

## Спостережуваність

- `GET /health/live`, `GET /health/ready` (перевірки залежностей додаються через `app.state.health.add`).
- `GET /metrics` — Prometheus (`jane_http_requests_total`, `jane_http_request_duration_seconds`, ...).
- Журнали — JSON-рядки в stdout із `request_id`, `job_id`, `service`, `instance`.
- Помилки — `application/problem+json` зі стабільним `code`.
