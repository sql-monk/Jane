# HTTP API Handler Runtime

[Усі операції та декларації](generated/README.md) генеруються з [handler.v1](../../../../../contracts/openapi/handler.v1.yaml). Runtime реалізує виконання Python extractor/transform, а не всі види handler із загального контракту.

## Операції

| Операція | Поведінка |
|---|---|
| [invokeHandler](generated/invokeHandler.md) | Validate/prepare, sandbox, 200 Result або 202 Job |
| [getInvocation](generated/getInvocation.md) | Збережений кінцевий Result за invocation_id |
| [startTestRun](generated/startTestRun.md) | Обрані manifest/extra cases, 202 Job із TestReport |
| [getJob](generated/getJob.md), [cancelJob](generated/cancelJob.md) | Async state; cancel також kill sandbox за label |
| [listConnections](generated/listConnections.md) | Порожні items і next_cursor=null |
| [putConnection](generated/putConnection.md) | not_implemented: Runtime не отримує credentials |
| [getConnection](generated/getConnection.md), [deleteConnection](generated/deleteConnection.md), [testConnection](generated/testConnection.md) | not_found: керованих connections немає |
| [getHealth](generated/getHealth.md), [getServiceInfo](generated/getServiceInfo.md) | Sandbox/state, profiles та configured limits |

## Invoke і replay

Body — [HandlerInvocation](../../../../../contracts/schemas/handler-invocation.schema.json). Handler посилається на exact package_id/version; optional digest фіксує bytes. Inputs мають kind material/entities/data за manifest; package_archive дозволяє роботу без Registry.

Idempotency-Key обов’язковий і дорівнює delivery.delivery_key. Збережений request/key дає replay header; завершений replay може повернути duplicate=true. Інший fingerprint — 422, in-progress — 409. Key/result retention залежить від state/TTL, memory не переживає restart.

Mode sync очікує лише sync_response_max_ms; перевищення переходить у 202, а sandbox продовжує роботу. Async одразу повертає 202. Job result — HandlerResult, GET invocation повертає лише збережений завершений Result. API scopes задає [Jane Kit](../../../jane-kit/reference/types/generated/jane_kit.auth_scopes.md); мережевий клієнт передає bearer, health без нього.

## Два рівні помилок

| Рівень | Поведінка |
|---|---|
| До виконання | HTTP problem: bad_request, validation_failed, dependency_not_allowed, digest_mismatch, not_found, upstream_unavailable |
| Engine недоступний | 503 service_unavailable та configured Retry-After |
| Після запуску пакета | HandlerResult.status=failed і failure.kind/retryable/diagnostics |
| Job інфраструктура/cancel | Job failed/cancelled, окремо від Result |

HTTP 200 не означає success. Timeout, OOM, invalid output і sandbox violation читаються із Result. Клієнт не повинен автоматично повторювати non-retryable failure новим ключем.

## Приклади й обмеження

[Python із локальним пакетом](../../integration.md#python-із-локальним-пакетом), [HTTP package_archive](../../integration.md#http-без-registry), [реальний Docker quickstart](../../quickstart.md) показують входи та перевірку результату. JSON body/поля — у [контрактному прикладі](../../../../../contracts/examples/schemas/handler-invocation/local-package-test-mode.json).

Access.network=allowlist відхиляється. Blob reads потребують roots/host allowlist; redirects відхиляються. Params/output звіряються зі schemas пакета. [Configuration](../../configuration.md) описує caps, [operations](../../operations.md) — state/recovery.
