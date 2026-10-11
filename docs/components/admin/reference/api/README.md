# Admin: API інтеграцій

Admin не публікує власного серверного API. Його HTTP клієнти використовують сім OpenAPI контрактів Jane й common path items.

## Контракти

| Контракт | Довідник | Екрани |
|---|---|---|
| orchestrator.v1 | [Orchestrator API](../../../orchestrator/reference/api/README.md) | Джерела, завдання, запуски, проблеми, ліміти, аудит |
| registry.v1 | [Registry API](../../../registry/reference/api/README.md) | Пакети, версії, форки, diff |
| storage.v1 | [Storage API](../../../storage/reference/api/README.md) | Оригінали, результати й history |
| llm.v1 | [LLM API](../../../llm/reference/api/README.md) | Providers, aliases, budgets, usage |
| handler.v1 | [Handler Runtime API](../../../handler-runtime/reference/api/README.md) | Tests, invocations, connections |
| assistant.v1 | [Assistant API](../../../assistant/reference/api/README.md) | Onboarding і поліпшення |
| collector.v1 | [Web Collector API](../../../web-collector/reference/api/README.md) | Collector connections/rules, collection інтеграція |

[Generated client types](../types/generated/README.md) генеруються з [contracts/openapi](../../../../../contracts/openapi/). Base URL формується за runtime config; [proxy інтеграція](../../integration.md#реальний-proxy).

## Заголовки й помилки

ApiClient передає Authorization Bearer, Idempotency-Key для POST, If-Match для редакторів та підтримує ETag. ProblemResponse із code/status/trace_id перетворюється на [ApiProblem](../types/generated/api.problem.md). Користувацький повтор після 412 має перечитати версію; blind overwrite UI не повинен виконувати.

## Jobs і preview

JobPanel опитує server Job API за polling config і показує result/error/progress. Закриття сторінки не скасовує серверний job; cancel — явний API запит. Preview stored object використовує Range до preview_max_bytes, тому вміст може бути лише уривком.

## Приклад конфігурації

[Runtime config](../../configuration.md#застосування) і [мінімальний запуск](../../quickstart.md) показують підключення інтерфейсу. Для стороннього клієнта готові [Python приклади Storage](../../../storage/quickstart.md#перший-запис), [LLM](../../../llm/quickstart.md#перша-відповідь) та [Assistant](../../../assistant/quickstart.md#прямий-виклик).
