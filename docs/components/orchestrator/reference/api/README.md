# API orchestrator.v1

> Згенеровано `scripts/docs_reference.py` з [orchestrator.v1.yaml](../../../../../contracts/openapi/orchestrator.v1.yaml). Не редагуйте вручну.

**Jane Orchestrator API**, версія `1.0.0`.

Керування оркестратором (WP-09) — споживач: адмінка (WP-12), асистент (WP-11), сторонні застосунки. Оркестратор поєднує автономні сервіси через їхні API (collector, handler, storage, registry, llm) і нічого не читає з їхніх БД. Автономні компоненти від оркестратора не залежать.

- Джерела, завдання (TaskConfig), розклади — ресурси з ETag; зміни — PUT з If-Match.
- Запуск завдання — 202 + Job (`kind: run`), деталі — `/v1/runs/{run_id}` (run_id = job_id).
- Простежуваність: матеріал → етап → результат → версія пакета (`/v1/materials/{id}/trace`).
- Реєстр підключень зберігає лише посилання на секрети й синхронізує підключення з виконавцями (`PUT /v1/connections/{id}` handler.v1).
- Активація й відкат версії пакета в етапі — окремі операції з аудитом.

Спільні правила для всіх операцій: автентифікація `Authorization: Bearer <ключ або JWT>` і scope операції, помилки `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)), ідемпотентність через `Idempotency-Key`, асинхронні операції — `202` і job, курсорна пагінація (`cursor`, `limit`, `next_cursor`).

## Операції

| Метод | Шлях | Операція | Scope | Призначення |
|---|---|---|---|---|
| GET | `/v1/health` | [getHealth](getHealth.md) | без автентифікації | Стан сервісу (liveness/readiness) |
| GET | `/v1/info` | [getServiceInfo](getServiceInfo.md) | без автентифікації | Версія, підтримувані версії API й можливості сервісу |
| GET | `/v1/sources` | [listSources](listSources.md) | `orchestrator:read`, `orchestrator:admin` | Джерела |
| POST | `/v1/sources` | [createSource](createSource.md) | `orchestrator:write`, `orchestrator:admin` | Створити джерело |
| GET | `/v1/sources/{source_id}` | [getSource](getSource.md) | `orchestrator:read`, `orchestrator:admin` | Джерело |
| PUT | `/v1/sources/{source_id}` | [replaceSource](replaceSource.md) | `orchestrator:write`, `orchestrator:admin` | Замінити джерело (включно з прапорцем «Передавати в LLM невідомі сторінки») |
| DELETE | `/v1/sources/{source_id}` | [deleteSource](deleteSource.md) | `orchestrator:write`, `orchestrator:admin` | Видалити джерело (заборонено, якщо є завдання) |
| GET | `/v1/tasks` | [listTasks](listTasks.md) | `orchestrator:read`, `orchestrator:admin` | Завдання (з фільтром за джерелом або пакетом, що використовується в етапах) |
| POST | `/v1/tasks` | [createTask](createTask.md) | `orchestrator:write`, `orchestrator:admin` | Створити завдання |
| GET | `/v1/tasks/{task_id}` | [getTask](getTask.md) | `orchestrator:read`, `orchestrator:admin` | Конфігурація завдання |
| PUT | `/v1/tasks/{task_id}` | [replaceTask](replaceTask.md) | `orchestrator:write`, `orchestrator:admin` | Замінити конфігурацію завдання (ліміти, розклад, етапи) без зміни коду |
| DELETE | `/v1/tasks/{task_id}` | [deleteTask](deleteTask.md) | `orchestrator:write`, `orchestrator:admin` | Видалити завдання (історія запусків зберігається) |
| POST | `/v1/task-validations` | [validateTask](validateTask.md) | `orchestrator:read`, `orchestrator:admin` | Перевірити конфігурацію завдання без збереження (DAG, версії, прив'язки, ліміти) |
| POST | `/v1/tasks/{task_id}/runs` | [startRun](startRun.md) | `orchestrator:write`, `orchestrator:admin` | Запустити завдання зараз |
| GET | `/v1/tasks/{task_id}/stages/{stage_id}/activations` | [listStageActivations](listStageActivations.md) | `orchestrator:read`, `orchestrator:admin` | Історія версій пакета в етапі (активації й відкати) |
| POST | `/v1/tasks/{task_id}/stages/{stage_id}/activations` | [activateStageVersion](activateStageVersion.md) | `orchestrator:write`, `orchestrator:admin` | Активувати версію пакета в етапі (або відкотити до попередньої) |
| GET | `/v1/runs` | [listRuns](listRuns.md) | `orchestrator:read`, `orchestrator:admin` | Запуски |
| GET | `/v1/runs/{run_id}` | [getRun](getRun.md) | `orchestrator:read`, `orchestrator:admin` | Стан запуску, прогрес етапів, витрати |
| POST | `/v1/runs/{run_id}/cancel` | [cancelRun](cancelRun.md) | `orchestrator:write`, `orchestrator:admin` | Скасувати запуск (те саме, що /v1/jobs/{run_id}/cancel) |
| GET | `/v1/runs/{run_id}/items` | [listRunItems](listRunItems.md) | `orchestrator:read`, `orchestrator:admin` | Елементи запуску — матеріал на етапі, спроби, результат, помилка |
| GET | `/v1/materials/{material_id}/trace` | [getMaterialTrace](getMaterialTrace.md) | `orchestrator:read`, `orchestrator:admin` | Простежуваність матеріалу — спостереження → етапи → результати → версії пакетів |
| GET | `/v1/unknown-materials` | [listUnknownMaterials](listUnknownMaterials.md) | `orchestrator:read`, `orchestrator:admin` | Матеріали без відповідного обробника (і чи були передані в LLM) |
| GET | `/v1/problem-groups` | [listProblemGroups](listProblemGroups.md) | `orchestrator:read`, `orchestrator:admin` | Проблемні матеріали, згруповані за джерелом і характером проблеми |
| PATCH | `/v1/problem-groups/{group_id}` | [updateProblemGroup](updateProblemGroup.md) | `orchestrator:write`, `orchestrator:admin` | Змінити статус групи (ignored, resolved) або прив'язати job вдосконалення |
| POST | `/v1/reprocessing` | [startReprocessing](startReprocessing.md) | `orchestrator:write`, `orchestrator:admin` | Повторно обробити збережені RAW етапами завдання |
| GET | `/v1/connections` | [listPlatformConnections](listPlatformConnections.md) | `orchestrator:read`, `orchestrator:admin` | Реєстр підключень платформи (без значень секретів) |
| GET | `/v1/connections/{connection_id}` | [getPlatformConnection](getPlatformConnection.md) | `orchestrator:read`, `orchestrator:admin` | Підключення і стан синхронізації з виконавцями |
| PUT | `/v1/connections/{connection_id}` | [putPlatformConnection](putPlatformConnection.md) | `orchestrator:admin` | Створити або замінити підключення й синхронізувати з виконавцями |
| DELETE | `/v1/connections/{connection_id}` | [deletePlatformConnection](deletePlatformConnection.md) | `orchestrator:admin` | Видалити підключення (заборонено, якщо на нього посилаються етапи) |
| GET | `/v1/limits/platform` | [getPlatformLimits](getPlatformLimits.md) | `orchestrator:read`, `orchestrator:admin` | Ліміти рівня платформи (типові значення й жорсткі стелі) |
| PUT | `/v1/limits/platform` | [putPlatformLimits](putPlatformLimits.md) | `orchestrator:admin` | Змінити ліміти платформи без зміни коду |
| GET | `/v1/limits/effective` | [getEffectiveLimits](getEffectiveLimits.md) | `orchestrator:read`, `orchestrator:admin` | Ефективні ліміти для контексту з походженням кожного значення |
| GET | `/v1/executors` | [listExecutors](listExecutors.md) | `orchestrator:read`, `orchestrator:admin` | Сервіси-виконавці, відомі оркестратору (з конфігурації), і їхній стан |
| GET | `/v1/audit-events` | [listAuditEvents](listAuditEvents.md) | `orchestrator:read`, `orchestrator:admin` | Журнал аудиту (активації, відкати, зміни конфігурацій, підключень і лімітів) |
| GET | `/v1/jobs/{job_id}` | [getJob](getJob.md) | `orchestrator:read`, `orchestrator:admin` | Стан, прогрес і результат тривалої операції |
| POST | `/v1/jobs/{job_id}/cancel` | [cancelJob](cancelJob.md) | `orchestrator:write`, `orchestrator:admin` | Запит на скасування job (ідемпотентний) |
