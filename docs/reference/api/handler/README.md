# API handler.v1

> Згенеровано `scripts/docs_reference.py` з [handler.v1.yaml](../../../../contracts/openapi/handler.v1.yaml). Не редагуйте вручну.

**Jane Handler Protocol**, версія `1.0.0`.

Спільний протокол обробника. Реалізують: handler-runtime (екстрактори й Python-перетворення, WP-06), storage (обробник збереження, WP-07/08), llm (LLM-обробник, WP-10). Оркестратор (WP-09) викликає будь-який тип однаково; сторонній застосунок — так само, без оркестратора.

Семантика доставки — **at-least-once з ідемпотентністю**: заголовок `Idempotency-Key` дорівнює `delivery.delivery_key`. Повтор із тим самим ключем повертає збережений `HandlerResult` (`duplicate: true`) без повторного ефекту (без повторного запису, без повторного витрачання бюджету LLM). Виконавець пам'ятає ключі щонайменше `limits.transfer.idempotency_ttl_seconds`; обробник збереження додатково зберігає delivery_key разом із записом безстроково.

Помилка виконання обробника — `200` зі `status: failed`; HTTP-помилка означає, що виклик не відбувся. Можливості конкретного виконавця (типи обробників, профілі runtime, адаптери, підтримка підключень) — `GET /v1/info` → `capabilities`.

**Підключення необов'язкові.** `/v1/connections*` обов'язкові лише для виконавця з керованими підключеннями (`capabilities.connections: true`, наприклад storage і llm). Виконавець без підключень (`capabilities.connections: false`, наприклад handler-runtime: екстрактори не отримують облікових даних) їх не потребує: клієнт (оркестратор) не синхронізує йому реєстр, якщо виконавця оголошено так у конфігурації клієнта, — це основний спосіб. Якщо виконавець ці шляхи має, він відповідає як handler-runtime: `GET /v1/connections` — порожня сторінка, `PUT` — 501 `not_implemented`, решта — 404. Лише ця явна відповідь 501 `not_implemented` на `PUT` означає «підключення не використовуються», а не збій синхронізації; 404/405 на `PUT` (шлях недоступний, наприклад ingress під час рестарту) — видимий збій синхронізації.

Спільні правила для всіх операцій: автентифікація `Authorization: Bearer <ключ або JWT>` і scope операції, помилки `application/problem+json` ([модель помилок](../../../../contracts/docs/errors.md)), ідемпотентність через `Idempotency-Key`, асинхронні операції — `202` і job, курсорна пагінація (`cursor`, `limit`, `next_cursor`).

## Операції

| Метод | Шлях | Операція | Scope | Призначення |
|---|---|---|---|---|
| GET | `/v1/health` | [getHealth](getHealth.md) | без автентифікації | Стан сервісу (liveness/readiness) |
| GET | `/v1/info` | [getServiceInfo](getServiceInfo.md) | без автентифікації | Версія, підтримувані версії API й можливості сервісу |
| POST | `/v1/invocations` | [invokeHandler](invokeHandler.md) | `handler:invoke` | Виконати обробник над вхідними даними |
| GET | `/v1/invocations/{invocation_id}` | [getInvocation](getInvocation.md) | `handler:invoke` | Прочитати збережений результат виклику |
| POST | `/v1/test-runs` | [startTestRun](startTestRun.md) | `handler:test` | Прогнати тести пакета без запису в робочі дані |
| GET | `/v1/connections` | [listConnections](listConnections.md) | `connections:write`, `handler:invoke` | Підключення, відомі цьому виконавцю |
| GET | `/v1/connections/{connection_id}` | [getConnection](getConnection.md) | `connections:write`, `handler:invoke` | Прочитати підключення |
| PUT | `/v1/connections/{connection_id}` | [putConnection](putConnection.md) | `connections:write` | Створити або замінити підключення (секрети — лише посиланнями) |
| DELETE | `/v1/connections/{connection_id}` | [deleteConnection](deleteConnection.md) | `connections:write` | Видалити підключення |
| POST | `/v1/connections/{connection_id}/test` | [testConnection](testConnection.md) | `connections:write` | Перевірити підключення й розв'язання секретів |
| GET | `/v1/jobs/{job_id}` | [getJob](getJob.md) | `handler:invoke`, `handler:test` | Стан, прогрес і результат тривалої операції |
| POST | `/v1/jobs/{job_id}/cancel` | [cancelJob](cancelJob.md) | `handler:invoke`, `handler:test` | Запит на скасування job (ідемпотентний) |
