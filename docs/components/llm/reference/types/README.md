# LLM: типи й публічні члени

Generated довідник перелічує всі публічні декларації поточного source: класи/інтерфейси/протоколи, конструктори, методи, функції, поля, властивості й constants. Сторінка кожного модуля містить сигнатури, parameters/results, source links та доступність property. Ручні пояснення нижче допомагають вибрати точку розширення; generated файли змінює тільки генератор.

## Навігація

| Завдання | Типи та модулі |
|---|---|
| Повний перелік | [Generated index](generated/README.md) |
| API request models | [CompletionRequest, Provider, ModelAlias, BudgetDefinition](generated/jane_llm.models.md) |
| Completion orchestration | [Gateway, Scope, ResolvedModel](generated/jane_llm.gateway.md) |
| Власний state | [Store, MemoryStore, PostgresStore](generated/jane_llm.store.md) |
| Новий provider kind | [ProviderAdapter, ProviderRequest, ProviderResponse](generated/jane_llm.providers.base.md) |
| Fake або Anthropic | [FakeProvider](generated/jane_llm.providers.fake.md), [AnthropicProvider](generated/jane_llm.providers.anthropic.md) |
| Побудувати prompt | [prompt](generated/jane_llm.prompt.md) |
| Пакет/handler integration | [packages](generated/jane_llm.packages.md), [handler](generated/jane_llm.handler.md) |
| Settings/limits | [settings](generated/jane_llm.settings.md), [ручні конфігураційні таблиці](../../configuration.md) |

## Межі типів

CompletionRequest та конфігураційні Pydantic models строгі. ProviderRequest/ProviderResponse/ResolvedConnection — frozen dataclasses; секрети ResolvedConnection не входять у repr. ProviderAdapter.complete асинхронно повертає ProviderResponse або ProviderError із retryable. Store reserve/charge забезпечує budget/rate рішення, а не provider HTTP-клас.

## Приклад використання

[HTTP клієнт](../../quickstart.md#перша-відповідь) показує CompletionRequest без імпорту внутрішньої реалізації. При додаванні provider реалізуйте ProviderAdapter і зареєструйте його в Gateway; перевірте retry, token/cost accounting та output schema. [Будова](../../internals.md).
