# Моніторинг

Усі сервіси Jane мають однаковий набір засобів спостереження з бібліотеки `jane-kit`: health-check, метрики Prometheus, журнали JSON у stdout і передачу контексту трасування W3C. Власні метрики й перевірки окремих сервісів описано в `operations.md` модулів — [перелік](README.md#експлуатація-модулів).

## Зміст

- [Health](#health)
- [Інформація про сервіс](#інформація-про-сервіс)
- [Метрики Prometheus](#метрики-prometheus)
- [Журнали](#журнали)
- [Трасування](#трасування)
- [Простежуваність матеріалу в Orchestrator](#простежуваність-матеріалу-в-orchestrator)

## Health

`GET /v1/health` не потребує токена. Відповідь — `{"status", "checks": {<назва>: {"status", "message"}}}`.

| `status` | HTTP | Значення |
|---|---|---|
| `ok` | 200 | усі перевірки пройшли |
| `degraded` | 200 | некритична перевірка не пройшла |
| `down` | 503 | критична перевірка не пройшла або не вклалася в тайм-аут |

Кожна перевірка обмежена тайм-аутом `JANE_<СЕРВІС>_HEALTH_CHECK_TIMEOUT_MS` (типово 2000 мс). У поточному коді всі перевірки сервісів критичні, тому збій будь-якої дає `down`.

| Сервіс | Перевірки |
|---|---|
| Orchestrator | `database` |
| Registry | `metadata_store`, `blob_store` |
| LLM gateway | `store` |
| Assistant | `state` |
| Handler Runtime | `sandbox`, `state` |
| Web Collector, Telegram Collector | `state_store` |
| Storage | немає перевірок: `checks` порожній |

Приклад: Orchestrator і Registry, коли PostgreSQL стеку зупинено (запуск 2026-10-11, стек `jane-doc-ops`):

```text
{"status":"down","checks":{"database":{"status":"down","message":"timeout after 2.0s"}}}
HTTP 503
{"status":"down","checks":{"metadata_store":{"status":"down","message":"timeout after 2.0s"},"blob_store":{"status":"ok"}}}
HTTP 503
```

Після повторного запуску PostgreSQL обидва сервіси повернулися до `ok` без перезапуску.

Health-check контейнерів у dev-стеку викликає той самий `GET /v1/health` (`HEALTHCHECK` у Dockerfile або `healthcheck` у `infra/compose.yaml`).

## Інформація про сервіс

`GET /v1/info` потребує будь-якого дійсного токена. Відповідь містить `service`, `version`, `api_versions`, `capabilities`, `auth_mode` і `limits` — документ `PlatformLimits` з типовими значеннями й стелями лімітів сервісу, які є в контракті, та назвою профілю (`limits.profile`), якщо його задано файлом. Так перевіряють, який профіль лімітів застосовано.

## Метрики Prometheus

`GET /metrics` повертає метрики у форматі Prometheus. Типово ендпоінт відкритий без токена (`JANE_<СЕРВІС>_METRICS_PUBLIC=true`) для збору всередині розгортання; `false` вимагає дійсного токена. `JANE_<СЕРВІС>_METRICS_ENABLED=false` вимикає метрики повністю.

Спільні метрики кожного сервісу (простір імен `jane`):

| Метрика | Тип | Мітки |
|---|---|---|
| `jane_http_requests_total` | counter | `method`, `route`, `status` |
| `jane_http_request_duration_seconds` | histogram | `method`, `route` |
| `jane_http_requests_in_flight` | gauge | — |
| `jane_service_info` | gauge | `service` |

`route` — шаблон маршруту FastAPI (`/v1/sources/{source_id}`), а не фактичний шлях; запити поза маршрутами мають `route="__unmatched__"`. Запити до самого `/metrics` не рахуються.

Власні метрики сервісів:

| Сервіс | Метрика | Мітки |
|---|---|---|
| Orchestrator | `jane_orchestrator_items_total` | `outcome` |
| Orchestrator | `jane_orchestrator_runs_total` | `status` |
| Orchestrator | `jane_orchestrator_materials_total` | — |
| Orchestrator | `jane_orchestrator_backpressure_total` | — |
| Orchestrator | `jane_orchestrator_leases_reclaimed_total` | — |
| Registry | `jane_registry_publications_total` | `result` |
| Storage | `jane_storage_writes_total` | `adapter`, `status` |
| Storage | `jane_storage_failed_invocations_total` | `kind` |
| LLM gateway | `jane_llm_requests_total` | `provider`, `model`, `outcome` |
| LLM gateway | `jane_llm_budget_rejections_total` | `scope_type` |

Перелік спільних і власних метрик Orchestrator, Registry і Storage звірено з `GET /metrics` запущеного стеку 2026-10-11; метрики LLM gateway — за кодом (`services/llm/src/jane_llm/app.py`). Готових правил алертів і дашбордів у репозиторії немає. Корисні сигнали: зростання `jane_orchestrator_leases_reclaimed_total` (воркери або виконавці падають посеред виклику), `jane_storage_failed_invocations_total`, `jane_llm_budget_rejections_total`, частка відповідей `5xx` у `jane_http_requests_total`.

## Журнали

Сервіси пишуть один JSON-об'єкт на рядок у stdout. Формат задає `JANE_<СЕРВІС>_LOG_FORMAT` (`json` типово або `console`), рівень — `JANE_<СЕРВІС>_LOG_LEVEL` (типово `INFO`).

| Поле | Значення |
|---|---|
| `ts` | час UTC з мілісекундами |
| `level` | `debug`, `info`, `warning`, `error` |
| `logger` | ім'я логера, наприклад `jane.access`, `jane.service`, `jane_orchestrator.db` |
| `msg` | повідомлення |
| `service` | назва сервісу |
| `instance` | `JANE_<СЕРВІС>_INSTANCE_ID`, типово `<hostname>-<pid>-<uuid>`; унікальний для кожного старту процесу |
| `trace_id`, `request_id` | контекст запиту |
| інші поля | контекст (`job_id`, `source_id` …) і поля конкретного запису |

Журнал доступу `jane.access` пише кожен HTTP-запит, крім `/v1/health` і `/metrics`: `method`, `path`, `status`, `duration_ms`. Рядок із запущеного стеку (2026-10-11):

```text
{"ts": "2026-10-11T10:06:55.289+00:00", "level": "info", "logger": "jane.access", "msg": "request", "service": "orchestrator", "instance": "560259790ef4-1-e6c24a98c5a3495281835f4b02fcc402", "trace_id": "ad8a305d24a4df3fc6a16c87e1d78105", "request_id": "3b1fa087b5d846a6856d5b7efe951651", "method": "POST", "path": "/v1/sources", "status": 201, "duration_ms": 908.59}
```

У dev-стеку журнали читаються так:

```powershell
just logs orchestrator --tail 100
```

Корисні записи під час старту: `service starting` (версія, порт), `authentication enabled` (режим і назви ключів, без самих ключів), `schema migrated` (номер застосованої міграції Orchestrator), повідомлення про частково застосований профіль лімітів (`platform limits profile applied partially`). Секрети в журнали не потрапляють: ключі API зберігаються лише як хеші, `secret_refs` — як посилання.

## Трасування

Jane передає контекст W3C Trace Context; експорту спанів (OpenTelemetry тощо) немає.

- Сервіс бере `trace_id` із вхідного заголовка `traceparent` або створює новий і додає його до кожного запису журналу запиту.
- Клієнти `jane-kit` і виклики Orchestrator до виконавців передають `traceparent` з тим самим `trace_id` і новим span id, а також `X-Request-ID`.
- Сервіс повертає `X-Request-ID` у відповіді; відповідь-помилка `application/problem+json` містить `trace_id`.

Щоб знайти всі записи одного ланцюжка викликів, відфільтруйте журнали всіх сервісів за `trace_id`.

## Простежуваність матеріалу в Orchestrator

Окремо від журналів Orchestrator зберігає бізнес-трасу матеріалу між етапами: `GET /v1/materials/{material_id}/trace` (scope `orchestrator:read`) показує ланцюжок «спостереження → етапи → результати → версії пакетів». Стан запуску й елементів — `GET /v1/runs/{run_id}` і `GET /v1/runs/{run_id}/items`. Опис — [Orchestrator](../components/orchestrator/operations.md).
