# Telegram Collector: HTTP API

Джерело контракту — [collector.v1.yaml](../../../../../contracts/openapi/collector.v1.yaml). [Generated операції](generated/README.md) містять точні параметри, schemas, відповіді та приклади.

## Операції

| Група | Маршрути | Scope |
|---|---|---|
| Один матеріал | `POST /v1/fetches` | collector:fetch |
| Запуск збору | `POST /v1/collections` | collector:collect |
| Статистика, матеріали, помилки | `GET /v1/collections/{id}` та підмаршрути | collector:read |
| Правила | `POST /v1/rules/validations` | collector:validate |
| Збережений стан | `GET/DELETE /v1/states/{state_key}` | collector:read / collector:manage |
| Connections | `GET/PUT/DELETE /v1/connections...` | collector:connections |
| Jobs і cancel | `GET /v1/jobs/{id}`, `POST .../cancel` | collector:read / collector:collect |

Точна таблиця авторизації — [auth_scopes.py](../../../../../libs/jane-kit/src/jane_kit/auth_scopes.py); спільні health/info/metrics — [Jane Kit](../../../jane-kit/reference/api/README.md).

## Гарантії

POST collections потребує Idempotency-Key. Той самий key/body повертає попередній Job, конкурентний claim — 409, інше тіло — 422. Один active збір на state_key: паралельний запуск відхиляється conflict.

Матеріали читаються `after`, а не загальним query cursor. Переданий next_cursor підтверджує попередню сторінку; end_of_stream означає terminal і відсутність наступних materials, але ще потребує перевірки collection_status.

## Помилки

| Код | Дія |
|---|---|
| validation_failed | Виправити payload/rules; перевірити valid і supported |
| unauthenticated / forbidden | Token та scope |
| idempotency_key_reused | Для нового тіла взяти новий key |
| idempotency_in_progress / conflict | Обмежений backoff або дочекатися active collection |
| not_found, HTTP 410 | Retention закінчився; старий курсор непридатний |
| limit_exceeded / rate_limited / timeout | Перевірити limits та retryable |
| not_implemented | Запитано непідтриману можливість |

Окремі URL/channel помилки колекції доступні через `GET .../errors`; success job не означає відсутність кожної ресурсної помилки.
