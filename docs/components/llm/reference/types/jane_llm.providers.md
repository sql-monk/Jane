# Модуль `jane_llm.providers`

> Згенеровано `scripts/docs_reference.py` з [services/llm/src/jane_llm/providers/__init__.py](../../../../../services/llm/src/jane_llm/providers/__init__.py). Не редагуйте вручну.

LLM provider adapters by ``Provider.kind``.

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `ADAPTERS` | `dict[str, ProviderAdapter]` | `{'fake': FakeProvider(), 'anthropic': AnthropicProvider()}` |  |

## Реекспорт

| Назва | Визначено в |
|---|---|
| `AnthropicProvider` | [`jane_llm.providers.anthropic`](jane_llm.providers.anthropic.md) |
| `FakeProvider` | [`jane_llm.providers.fake`](jane_llm.providers.fake.md) |
| `ProviderAdapter` | [`jane_llm.providers.base`](jane_llm.providers.base.md) |
| `ProviderError` | [`jane_llm.providers.base`](jane_llm.providers.base.md) |
| `ProviderRequest` | [`jane_llm.providers.base`](jane_llm.providers.base.md) |
| `ProviderResponse` | [`jane_llm.providers.base`](jane_llm.providers.base.md) |
| `ResolvedConnection` | [`jane_llm.providers.base`](jane_llm.providers.base.md) |
