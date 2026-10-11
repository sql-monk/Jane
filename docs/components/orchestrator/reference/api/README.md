# HTTP API Orchestrator

[Генерований каталог усіх операцій](generated/README.md) звіряється з [orchestrator.v1](../../../../../contracts/openapi/orchestrator.v1.yaml). Тут описані гарантії, помилки та читання результату.

## Конфігурація

| Операції | Результат |
|---|---|
| [listSources](generated/listSources.md), [getSource](generated/getSource.md), [createSource](generated/createSource.md), [replaceSource](generated/replaceSource.md), [deleteSource](generated/deleteSource.md) | SourceConfig та metadata ETag |
| [listTasks](generated/listTasks.md), [getTask](generated/getTask.md), [createTask](generated/createTask.md), [replaceTask](generated/replaceTask.md), [deleteTask](generated/deleteTask.md) | TaskConfig, DAG та schedule |
| [validateTask](generated/validateTask.md) | Errors/warnings без запуску |
| [listExecutors](generated/listExecutors.md) | Налаштовані roles/capabilities/health |
| [listPlatformConnections](generated/listPlatformConnections.md), [getPlatformConnection](generated/getPlatformConnection.md), [putPlatformConnection](generated/putPlatformConnection.md), [deletePlatformConnection](generated/deletePlatformConnection.md) | Own connection registry й async sync сусідам |
| [getPlatformLimits](generated/getPlatformLimits.md), [putPlatformLimits](generated/putPlatformLimits.md), [getEffectiveLimits](generated/getEffectiveLimits.md) | PlatformLimits/effective/provenance |

## Виконання й діагностика

| Операції | Поведінка |
|---|---|
| [startRun](generated/startRun.md), [getRun](generated/getRun.md), [listRuns](generated/listRuns.md) | POST → 202 Job kind=run, job_id=run_id; читання run snapshot/counts |
| [cancelRun](generated/cancelRun.md), [getJob](generated/getJob.md), [cancelJob](generated/cancelJob.md) | Стан/скасування; Job і run — різні views одного виконання |
| [listRunItems](generated/listRunItems.md), [getMaterialTrace](generated/getMaterialTrace.md) | Delivery, attempts, output refs та provenance |
| [listProblemGroups](generated/listProblemGroups.md), [updateProblemGroup](generated/updateProblemGroup.md), [listUnknownMaterials](generated/listUnknownMaterials.md) | Діагностика й ручний status проблем |
| [startReprocessing](generated/startReprocessing.md) | Новий run із RAW Storage read API |
| [activateStageVersion](generated/activateStageVersion.md), [listStageActivations](generated/listStageActivations.md) | Явна activation/rollback та history |
| [listAuditEvents](generated/listAuditEvents.md) | Хто змінив source/task/connection/activation |
| [getHealth](generated/getHealth.md), [getServiceInfo](generated/getServiceInfo.md) | Own DB, capabilities та configured limits |

## Автентифікація й запис

Bearer scopes — orchestrator:read/write/admin за операцією. Health без token; local none лише для loopback. POST із побічним ефектом вимагає Idempotency-Key; same fingerprint/key replay, інше body → 422, in-progress → 409. PUT config використовує If-Match/ETag; mismatch → 412. Lists повертають items/next_cursor, limit обрізається до configured maximum.

Run snapshot не змінюється від наступного PUT task. Connection PUT підтверджує власний registry, а не успішну синхронізацію всіх executor; читайте sync status. Activation впливає на майбутні run, а не на вже записані бізнес-сутності.

## Помилки й приклади

Schema/semantic validation повертає errors із pointer/code; TaskConfig потребує одного collect, існуючих входів і acyclic graph. Відсутні source/task/material → not_found; overlap/resource policy може відмовити запуску; non-retryable executor problem завершує item/run відповідно до engine policy.

HTTP errors — problem+json; виконаний HandlerResult.failed належить item result, не підміняє HTTP status Orchestrator. Retryable та attempts керують повтором; cancel не відкочує зовнішній ефект. Повний [каталог помилок](../../../../../contracts/docs/errors.md).

[Сторонній клієнт](../../integration.md#клієнт-запуску), [executor configuration](../../integration.md#власний-executor) і [перший pipeline](../../quickstart.md#перший-pipeline) показують фактичні входи. [Internals](../../internals.md) пояснює snapshot і stable delivery keys.
