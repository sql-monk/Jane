# Storage: HTTP API

Storage одночасно реалізує читання storage.v1 і виконання storage-пакетів через handler.v1. Довідник читання не замінює окремий handler контракт.

## Операції

| Потреба | Контракт / довідник | Scopes |
|---|---|---|
| Entity state/history | [storage.v1](../../../../../contracts/openapi/storage.v1.yaml), [згенеровані операції](generated/README.md) | storage:read |
| Objects metadata/content/Range | [getObject](generated/getObject.md), [getObjectContent](generated/getObjectContent.md) | storage:read |
| Invoke/read invocation | [handler.v1](../../../../../contracts/openapi/handler.v1.yaml), [handler API довідник](../../../handler-runtime/reference/api/generated/README.md) | handler:invoke |
| Test run | handler.v1 | handler:test |
| Connections read/write/test | Спільні path items handler.v1 | handler:invoke / connections:write |
| Jobs | handler.v1 | handler:invoke або handler:test |

[Таблиця scopes реалізації](../../../../../libs/jane-kit/src/jane_kit/auth_scopes.py). Пакет/params/connections звіряються до виконання; adapter failure може бути HTTP 200 із HandlerResult.status=failed.

## Спільна поведінка

Bearer/scopes застосовує сервер; health публічний. Побічні POST мають Idempotency-Key: те саме тіло replay, інше тіло — `idempotency_key_reused`, незавершений claim — `idempotency_in_progress`. PUT використовує ETag/If-Match там, де це передбачено контрактом. Помилки HTTP — application/problem+json; client рішення приймає за code. Довгі операції повертають 202 Job/Location, polling завершується succeeded/failed/cancelled; cursor списки мають items/next_cursor.

Точні required поля, status codes, JSON pointers і приклади містять generated операції та [спільний контракт](../../../../../contracts/openapi/common.yaml). Невідомі поля результату читач терпить, документи налаштувань строгі.

## Приклади

[Перевірений прямий Python-клієнт](../../quickstart.md#перший-запис) показує write/read/replay реального filesystem. [Integration](../../integration.md) пояснює storage bindings, timeout-to-202 і заміну адаптера; [configuration](../../configuration.md) задає transport/limits.
