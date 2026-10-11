# API storage.v1

> Згенеровано `scripts/docs_reference.py` з [storage.v1.yaml](../../../../../contracts/openapi/storage.v1.yaml). Не редагуйте вручну.

**Jane Storage Read API**, версія `1.0.0`.

Читання даних, записаних обробником збереження (WP-07/08). Запис іде лише через спільний протокол обробника (`handler.v1.yaml`, `POST /v1/invocations` сервісу storage). Цей API потрібен адмінці (перегляд матеріалів і результатів, ТЗ §10), оркестратору (повторна обробка збережених RAW) і стороннім застосункам. Кожен запит указує `connection_id` — конкретне підключення до сховища; сервіс storage читає лише через власні адаптери.

Простір імен: параметри етапу збереження `prefix` / `schema` / `table_prefix` (params_schema пакета) перекривають однойменні `params` підключення лише під час запису. Читання цього API бачить простір, який задають `params` самого підключення; дані з простору етапу читаються через окреме підключення з тими самими `params` (`contracts/docs/storage-adapter.md`, «Простір імен»).

Спільні правила для всіх операцій: автентифікація `Authorization: Bearer <ключ або JWT>` і scope операції, помилки `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)), ідемпотентність через `Idempotency-Key`, асинхронні операції — `202` і job, курсорна пагінація (`cursor`, `limit`, `next_cursor`).

## Операції

| Метод | Шлях | Операція | Scope | Призначення |
|---|---|---|---|---|
| GET | `/v1/health` | [getHealth](getHealth.md) | без автентифікації | Стан сервісу (liveness/readiness) |
| GET | `/v1/info` | [getServiceInfo](getServiceInfo.md) | без автентифікації | Версія, підтримувані версії API й можливості сервісу |
| GET | `/v1/entities` | [listEntities](listEntities.md) | `storage:read` | Актуальний стан сутностей |
| GET | `/v1/entity-history` | [listEntityHistory](listEntityHistory.md) | `storage:read` | Історія оновлень однієї сутності (включно із запізнілими) |
| GET | `/v1/objects` | [listObjects](listObjects.md) | `storage:read` | Збережені об'єкти (RAW, документи результатів) — для перегляду й повторної обробки |
| GET | `/v1/objects/{object_id}` | [getObject](getObject.md) | `storage:read` | Метадані збереженого об'єкта і відновлений Material для повторної обробки |
| GET | `/v1/objects/{object_id}/content` | [getObjectContent](getObjectContent.md) | `storage:read` | Вміст збереженого об'єкта (байти в оригінальному медіатипі) |

## Інші контракти модуля

- `handler.v1` — [../../../../reference/api/handler/README.md](../../../../reference/api/handler/README.md)
