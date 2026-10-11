# API collector.v1

> Згенеровано `scripts/docs_reference.py` з [collector.v1.yaml](../../../../contracts/openapi/collector.v1.yaml). Не редагуйте вручну.

**Jane Collector API**, версія `1.0.0`.

Спільний контракт колекторів (Web Collector — WP-02/03, Telegram Collector — WP-04). Колектор працює автономно: сторонній застосунок може отримати матеріали без оркестратора, екстрактора чи сервісу збереження (ТЗ §4, критерій 1).

Потік матеріалів — **pull із курсором і backpressure**: `POST /v1/collections` запускає збір (202 + Job), споживач читає `GET /v1/collections/{id}/materials?after=<cursor>`. Запит з `after=C` підтверджує всі матеріали до C включно; непідтверджені матеріали видаються повторно (at-least-once, споживач дедуплікує за `observation_id`). Якщо непідтверджених більше за `limits.queue.max_unacked_materials`, колектор призупиняє обхід. Стан обходу (черга, дедуплікація, курсори Telegram) зберігається в сховищі колектора, тож після рестарту збір продовжується.

Керовані підключення (обліковий запис Telegram, HTTP-автентифікація сайту) — ті самі операції `/v1/connections`, що й у спільному протоколі обробника (`common.yaml#/components/pathItems/Connection*`): оркестратор синхронізує визначення без секретів, колектор розв'язує `secret_refs` у своєму середовищі. Конвенція `params` для `kind=http` (Web Collector): `auth_scheme` = `bearer` (`secret_refs.token` → `Authorization: Bearer …`), `basic` (`secret_refs.username` і `secret_refs.password`) або `header` (`params.header_name` — ім'я заголовка, крім `Host`, `Content-Length`, `Transfer-Encoding`; `secret_refs.value` — значення). Облікові дані йдуть лише на origin зі списку, дозволеного оператором колектора, і не переносяться переадресацією на інший origin чи з HTTPS на HTTP. Для `kind=telegram_account`: `params.api_id`, `secret_refs.api_hash`, `secret_refs.session`.

Кілька екземплярів колектора можуть ділити одне сховище стану (той самий вузол, спільний каталог). Будь-яка операція, що звертається до сховища, може отримати `503 service_unavailable` (`retryable: true`, `Retry-After`), якщо інший екземпляр тримає блокування сховища довше за налаштований час очікування колектора; запит можна повторити без змін.

Спільні правила для всіх операцій: автентифікація `Authorization: Bearer <ключ або JWT>` і scope операції, помилки `application/problem+json` ([модель помилок](../../../../contracts/docs/errors.md)), ідемпотентність через `Idempotency-Key`, асинхронні операції — `202` і job, курсорна пагінація (`cursor`, `limit`, `next_cursor`).

## Операції

| Метод | Шлях | Операція | Scope | Призначення |
|---|---|---|---|---|
| GET | `/v1/health` | [getHealth](getHealth.md) | без автентифікації | Стан сервісу (liveness/readiness) |
| GET | `/v1/info` | [getServiceInfo](getServiceInfo.md) | без автентифікації | Версія, підтримувані версії API й можливості сервісу |
| POST | `/v1/fetches` | [fetchMaterial](fetchMaterial.md) | `collector:run` | Синхронно отримати один матеріал |
| POST | `/v1/collections` | [startCollection](startCollection.md) | `collector:run` | Запустити збір (асинхронно) |
| GET | `/v1/collections/{collection_id}` | [getCollection](getCollection.md) | `collector:read` | Стан і статистика збору |
| GET | `/v1/collections/{collection_id}/materials` | [listCollectionMaterials](listCollectionMaterials.md) | `collector:read` | Забрати матеріали після курсора (і підтвердити попередні) |
| GET | `/v1/collections/{collection_id}/errors` | [listCollectionErrors](listCollectionErrors.md) | `collector:read` | Помилки й пропуски окремих URL/повідомлень |
| POST | `/v1/rules/validations` | [validateRules](validateRules.md) | `collector:read`, `collector:run` | Перевірити правила колектора без запуску |
| GET | `/v1/states/{state_key}` | [getCollectorState](getCollectorState.md) | `collector:read` | Стан обходу/курсори, збережені колектором |
| DELETE | `/v1/states/{state_key}` | [resetCollectorState](resetCollectorState.md) | `collector:run` | Скинути збережений стан (наступний збір — з нуля) |
| GET | `/v1/connections` | [listConnections](listConnections.md) | `connections:write`, `collector:read` | Підключення, відомі цьому виконавцю |
| GET | `/v1/connections/{connection_id}` | [getConnection](getConnection.md) | `connections:write`, `collector:read` | Прочитати підключення |
| PUT | `/v1/connections/{connection_id}` | [putConnection](putConnection.md) | `connections:write` | Створити або замінити підключення (секрети — лише посиланнями) |
| DELETE | `/v1/connections/{connection_id}` | [deleteConnection](deleteConnection.md) | `connections:write` | Видалити підключення |
| POST | `/v1/connections/{connection_id}/test` | [testConnection](testConnection.md) | `connections:write` | Перевірити підключення й розв'язання секретів |
| GET | `/v1/jobs/{job_id}` | [getJob](getJob.md) | `collector:read` | Стан, прогрес і результат тривалої операції |
| POST | `/v1/jobs/{job_id}/cancel` | [cancelJob](cancelJob.md) | `collector:run` | Запит на скасування job (ідемпотентний) |
