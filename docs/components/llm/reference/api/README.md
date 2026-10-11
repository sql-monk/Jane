# LLM: HTTP API

`llm.v1` визначає completions, provider/model alias administration, budgets та usage. Шлюз також реалізує handler.v1 для LLM-пакетів, managed connections і test runs.

## Операції

| Потреба | Довідник | Scopes |
|---|---|---|
| Completion sync/async | [createCompletion](generated/createCompletion.md) | llm:invoke |
| Providers/aliases read | [listProviders](generated/listProviders.md), [listModelAliases](generated/listModelAliases.md) | llm:invoke або llm:admin |
| Providers/aliases write | [операції llm.v1](generated/README.md) | llm:admin |
| Budgets / usage | [listBudgets](generated/listBudgets.md), [getUsage](generated/getUsage.md) | llm:admin |
| LLM package invocation/test | [handler.v1](../../../../../contracts/openapi/handler.v1.yaml), [handler operations](../../../handler-runtime/reference/api/generated/README.md) | handler:invoke / handler:test |
| Managed connections | handler.v1 common path items | handler:invoke / connections:write |

CompletionRequest.limits — безпосередній LlmLimits об’єкт; output відповіді може бути structured output або output_text, із valid/validation_errors/finish_reason і usage/budget. Не відкидати valid=false лише через HTTP 200. [Код моделей](../../../../../services/llm/src/jane_llm/models.py), [контракт](../../../../../contracts/openapi/llm.v1.yaml).

## Спільна поведінка

Bearer/scopes застосовує сервер; health публічний. Побічні POST мають Idempotency-Key: те саме тіло replay, інше тіло — `idempotency_key_reused`, незавершений claim — `idempotency_in_progress`. PUT використовує ETag/If-Match там, де це передбачено контрактом. Помилки HTTP — application/problem+json; client рішення приймає за code. Довгі операції повертають 202 Job/Location, polling завершується succeeded/failed/cancelled; cursor списки мають items/next_cursor.

Точні required поля, status codes, JSON pointers і приклади містять generated операції та [спільний контракт](../../../../../contracts/openapi/common.yaml). Невідомі поля результату читач терпить, документи налаштувань строгі.

## Приклади

[Fake completion](../../quickstart.md#перша-відповідь) перевірений власним локальним HTTP процесом. [Integration](../../integration.md) показує model aliases, scope і budgets; зовнішній провайдер не перевірено.
